import time
import random
import numpy as np
import warnings
import argparse
import json
import os
import re
from typing import Dict, List, Tuple, Any, Optional

# Warnings control
warnings.filterwarnings("ignore", category=RuntimeWarning)
np.seterr(all='ignore')

# External baselines (optional)
try:
    import nltk
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.translate.meteor_score import meteor_score as nltk_meteor
except Exception:
    nltk = None

try:
    import sacrebleu
except Exception:
    sacrebleu = None

try:
    from rouge_score import rouge_scorer
except Exception:
    rouge_scorer = None

try:
    import jiwer
except Exception:
    jiwer = None

# Guard against NumPy 2.x incompatibility in some torch/bert-score builds
bertscore_score = None
try:
    _np_major = int(np.__version__.split('.')[0])
    if _np_major < 2:
        from bert_score import score as bertscore_score  # type: ignore
    else:
        print("bert-score baseline skipped (NumPy>=2 detected; many torch wheels incompatible)")
except Exception:
    bertscore_score = None

try:
    from moverscore_v2 import get_idf_dict, word_mover_score
except Exception:
    word_mover_score = None

# Our package
from blazemetrics import (
    rouge_score as rg_rouge,
    bleu as rg_bleu,
    chrf_score as rg_chrf,
    meteor as rg_meteor,
    wer as rg_wer,
    bert_score_similarity as rg_bertsim,
    moverscore_greedy as rg_moverscore,
    compute_text_metrics as rg_compute_all,
    Guardrails as RG_Guardrails,
)


def gen_corpus(n=2000, vocab=500, seed=123):
    rng = random.Random(seed)
    def sentence(min_len=5, max_len=20):
        length = rng.randint(min_len, max_len)
        return " ".join(f"t{rng.randint(1, vocab)}" for _ in range(length))
    candidates = [sentence() for _ in range(n)]
    references = [[sentence()] for _ in range(n)]
    return candidates, references


def timeit(fn, repeat=3, warmup=1):
    for _ in range(warmup):
        fn()
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        out = fn()
        t1 = time.perf_counter()
        times.append(t1 - t0)
    return min(times), sum(times)/len(times)


# Baseline wrappers

def bleu_nltk(cands, refs):
    ch = SmoothingFunction().method1
    scores = []
    for c, rlist in zip(cands, refs):
        ref_tokens = [r.split() for r in rlist]
        cand_tokens = c.split()
        scores.append(sentence_bleu(ref_tokens, cand_tokens, smoothing_function=ch))
    return scores


def rouge_rouge_score_pkg(cands, refs):
    try:
        scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)
    except Exception:
        return ([], [], [])
    out_r1, out_r2, out_rl = [], [], []
    for c, rlist in zip(cands, refs):
        best_r1f, best_r2f, best_rlf = 0.0, 0.0, 0.0
        for r in rlist:
            try:
                s = scorer.score(r, c)
            except Exception:
                continue
            best_r1f = max(best_r1f, s.get('rouge1', None).fmeasure if s.get('rouge1', None) else 0.0)
            best_r2f = max(best_r2f, s.get('rouge2', None).fmeasure if s.get('rouge2', None) else 0.0)
            best_rlf = max(best_rlf, s.get('rougeL', None).fmeasure if s.get('rougeL', None) else 0.0)
        out_r1.append(best_r1f)
        out_r2.append(best_r2f)
        out_rl.append(best_rlf)
    return out_r1, out_r2, out_rl


def chrf_sacrebleu(cands, refs):
    scores = []
    for c, rlist in zip(cands, refs):
        try:
            s = sacrebleu.sentence_chrf(c, rlist)
        except TypeError:
            # Fallback older API
            s = sacrebleu.sentence_chrf(c, rlist)
        scores.append(s.score / 100.0)
    return scores


def meteor_nltk(cands, refs):
    out = []
    for c, rlist in zip(cands, refs):
        c_tok = c.split()
        r_tok_lists = [r.split() for r in rlist]
        out.append(max(nltk_meteor([rt], c_tok) for rt in r_tok_lists))
    return out


def wer_jiwer(cands, refs):
    out = []
    for c, rlist in zip(cands, refs):
        best = 1.0
        for r in rlist:
            best = min(best, jiwer.wer(r, c))
        out.append(best)
    return out


def bertscore_baseline(cands, refs):
    flat_refs = [rlist[0] for rlist in refs]
    P, R, F1 = bertscore_score(cands, flat_refs, lang="en", rescale_with_baseline=False)
    return P.numpy().tolist(), R.numpy().tolist(), F1.numpy().tolist()


# Guard for moverscore on NumPy 2.x (requires torch)
word_mover_score = word_mover_score if ('word_mover_score' in globals() and int(np.__version__.split('.')[0]) < 2) else None
if word_mover_score is None:
    print("moverscore baseline skipped (requires torch and often incompatible with NumPy>=2)")


def moverscore_baseline(cands, refs):
    flat_refs = [rlist[0] for rlist in refs]
    idf_cand = get_idf_dict(cands)
    idf_ref = get_idf_dict(flat_refs)
    scores = word_mover_score(flat_refs, cands, idf_ref, idf_cand)
    return scores


# Duplicate def retained for compatibility; keep the latest definition
# def moverscore_baseline(...): pass


def _make_guardrails_texts(n=2000, seed=123):
    rng = random.Random(seed)
    samples = []
    emails = [f"user{i}@example.com" for i in range(50)]
    phones = [f"+1-{rng.randint(200,999)}-{rng.randint(100,999)}-{rng.randint(1000,9999)}" for _ in range(50)]
    toxic = ["idiot", "stupid", "kill", "hate"]
    for i in range(n):
        parts = [f"token{rng.randint(1,1000)}" for _ in range(rng.randint(5,20))]
        if rng.random() < 0.2:
            parts.append(rng.choice(emails))
        if rng.random() < 0.15:
            parts.append(rng.choice(phones))
        if rng.random() < 0.1:
            parts.append(rng.choice(toxic))
        samples.append(" ".join(parts))
    return samples


def python_guardrails_baseline(texts, blocklist, regexes, case_insensitive=True):
    flags_block = []
    flags_regex = []
    redacted = []
    ci = re.IGNORECASE if case_insensitive else 0
    comp_regex = [re.compile(p, ci) for p in regexes]
    # very naive redaction for emails/phones
    email_re = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
    phone_re = re.compile(r"\+?\d[\d\- ]{7,}\d")
    for t in texts:
        t_l = t.lower() if case_insensitive else t
        flags_block.append(any(b in (t_l if case_insensitive else t) for b in (b.lower() for b in blocklist)))
        flags_regex.append(any(r.search(t) is not None for r in comp_regex))
        rtxt = email_re.sub("[REDACTED_EMAIL]", t)
        rtxt = phone_re.sub("[REDACTED_PHONE]", rtxt)
        redacted.append(rtxt)
    # dummy scores to align structure
    out = {
        "blocked": flags_block,
        "regex_flagged": flags_regex,
        "redacted": redacted,
        "safety_score": [0.0] * len(texts),
        "injection_spoof": [False] * len(texts),
    }
    return out


def _pick_baseline(rows: List[Tuple[str, float, float]]) -> Optional[str]:
    # Prefer the first non blazemetrics entry, else the slowest overall
    for nm, _, _ in rows:
        if 'blazemetrics' not in nm.lower():
            return nm
    if rows:
        return sorted(rows, key=lambda x: x[2], reverse=True)[0][0]
    return None


def _compute_speedups(rows: List[Tuple[str, float, float]], baseline_name: Optional[str]) -> List[Tuple[str, float, float, Optional[float]]]:
    # Returns list of (name, tmin, tavg, speedup)
    baseline_avg = None
    if baseline_name is not None:
        for nm, tmin, tavg in rows:
            if nm == baseline_name:
                baseline_avg = tavg
                break
    out = []
    for nm, tmin, tavg in rows:
        sp = (baseline_avg / tavg) if (baseline_avg is not None and tavg > 0) else None
        out.append((nm, tmin, tavg, sp))
    return out


def _write_csv_md(results: Dict[str, List[Tuple[str, float, float]]], csv_path: Optional[str], md_path: Optional[str]) -> None:
    try:
        if csv_path:
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            with open(csv_path, 'w') as f:
                f.write("metric,impl,min_ms,avg_ms,speedup_vs_baseline\n")
                for metric, rows in results.items():
                    base = _pick_baseline(rows)
                    rows_sp = _compute_speedups(rows, base)
                    for nm, tmin, tavg, sp in rows_sp:
                        f.write(f"{metric},{nm},{tmin*1000:.3f},{tavg*1000:.3f},{(sp if sp is not None else '')}\n")
        if md_path:
            os.makedirs(os.path.dirname(md_path), exist_ok=True)
            with open(md_path, 'w') as f:
                f.write("# Benchmark Summary\n\n")
                for metric, rows in results.items():
                    base = _pick_baseline(rows)
                    f.write(f"## {metric}\n\n")
                    f.write("| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |\n")
                    f.write("|---|---:|---:|---:|\n")
                    for nm, tmin, tavg, sp in _compute_speedups(rows, base):
                        sp_str = f"{sp:.2f}x" if sp is not None else "N/A"
                        f.write(f"| {nm} | {tmin*1000:.1f} | {tavg*1000:.1f} | {sp_str} |\n")
    except Exception as e:
        print(f"CSV/Markdown export failed: {e}")


def summarize(results, plot=True, csv_path: Optional[str] = None, md_path: Optional[str] = None):
    # results: dict metric -> list of (name, min_ms, avg_ms)
    print("\n=== Runtime Summary (lower is better) ===")
    winners = {}
    for metric, rows in results.items():
        print(f"\n{metric}:")
        rows_sorted = sorted(rows, key=lambda x: x[2])
        base_name = _pick_baseline(rows_sorted)
        for name, tmin, tavg, sp in _compute_speedups(rows_sorted, base_name):
            sp_str = f"  |  {sp:.2f}× vs baseline" if sp is not None else ""
            print(f"  {name:26s}  min={tmin*1000:8.1f} ms  avg={tavg*1000:8.1f} ms{sp_str}")
        if rows_sorted:
            best = rows_sorted[0]
            if len(rows_sorted) > 1:
                second = rows_sorted[1]
                gain = (second[2] - best[2]) / second[2] * 100.0
                winners[metric] = (best[0], gain)
            else:
                winners[metric] = (best[0], 0.0)
    print("\n=== Winners ===")
    for metric, (name, gain) in winners.items():
        print(f"{metric}: {name} wins by {gain:.1f}% over next best")

    # CSV / Markdown
    _write_csv_md(results, csv_path=csv_path, md_path=md_path)

    # Single combined plot with improved style
    try:
        if not plot:
            return
        import matplotlib.pyplot as plt
        from matplotlib import rcParams
        rcParams.update({
            'axes.grid': True,
            'grid.alpha': 0.25,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'figure.facecolor': 'white',
        })
        palette = ["#5B8FF9", "#61DDAA", "#65789B", "#F6BD16", "#7262fd", "#78D3F8", "#9661BC"]

        metrics = list(results.keys())
        cols = 2
        rows = (len(metrics) + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(14, 3.2 * rows))
        if rows == 1 and cols == 1:
            axes = [[axes]]
        elif rows == 1:
            axes = [axes]
        for idx, metric in enumerate(metrics):
            ax = axes[idx // cols][idx % cols]
            rows_data = sorted(results[metric], key=lambda r: r[2])
            names = [r[0] for r in rows_data]
            avgs = [r[2]*1000 for r in rows_data]
            colors = [palette[i % len(palette)] for i in range(len(names))]
            bars = ax.bar(names, avgs, color=colors)
            ax.set_ylabel("Avg time (ms)")
            ax.set_title(metric)
            ax.tick_params(axis='x', rotation=25)
            # annotate bars
            for b, v in zip(bars, avgs):
                ax.text(b.get_x() + b.get_width()/2, v, f"{v:.1f}", ha='center', va='bottom', fontsize=8)
        for j in range(len(metrics), rows*cols):
            axes[j // cols][j % cols].axis('off')
        plt.tight_layout()
        out_dir = os.path.join(os.path.dirname(__file__), 'images')
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'benchmark_overview.png')
        plt.savefig(out_path, dpi=200, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved combined plot: {out_path}")
    except Exception as e:
        print(f"Plot creation skipped: {e}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark blazemetrics vs baselines")
    parser.add_argument("--n", type=int, default=2000, help="Number of samples")
    parser.add_argument("--repeat", type=int, default=3, help="Timing repeats")
    parser.add_argument("--warmup", type=int, default=1, help="Warmup iterations")
    parser.add_argument("--no-plot", action="store_true", help="Disable plots")
    parser.add_argument("--save", type=str, default=None, help="Optional path to save JSON results")
    parser.add_argument("--csv", type=str, default=None, help="Optional path to save CSV summary")
    parser.add_argument("--md", type=str, default=None, help="Optional path to save Markdown summary")
    parser.add_argument("--parallel", type=int, default=1, help="Enable Rust parallelism (1) or disable (0)")
    parser.add_argument("--par-threshold", type=int, default=512, help="Min batch size to use parallelism in Rust")
    args = parser.parse_args()

    # Apply parallelism configuration to Rust core via env vars
    os.environ["BLAZEMETRICS_PARALLEL"] = str(args.parallel)
    os.environ["BLAZEMETRICS_PAR_THRESHOLD"] = str(args.par_threshold)

    print("--- Benchmark blazemetrics vs Python baselines ---")
    n = args.n
    cands, refs = gen_corpus(n=n)

    results: Dict[str, List[Tuple[str, float, float]]] = {}

    # BLEU
    rows: List[Tuple[str, float, float]] = []
    if nltk is not None:
        t_min, t_avg = timeit(lambda: bleu_nltk(cands, refs), repeat=args.repeat, warmup=args.warmup)
        rows.append(("nltk BLEU", t_min, t_avg))
    else:
        print("NLTK not available; skipping BLEU baseline")
    t_min, t_avg = timeit(lambda: rg_bleu(cands, refs, max_n=4), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics BLEU", t_min, t_avg))
    results["BLEU"] = rows

    # ROUGE
    rows = []
    if rouge_scorer is not None:
        t_min, t_avg = timeit(lambda: rouge_rouge_score_pkg(cands, refs), repeat=args.repeat, warmup=args.warmup)
        rows.append(("rouge-score (1/2/L)", t_min, t_avg))
    else:
        print("rouge-score not available; skipping ROUGE baseline")
    t_min, t_avg = timeit(lambda: rg_rouge(cands, refs, score_type="rouge_n", n=1), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics ROUGE-1", t_min, t_avg))
    t_min, t_avg = timeit(lambda: rg_rouge(cands, refs, score_type="rouge_n", n=2), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics ROUGE-2", t_min, t_avg))
    t_min, t_avg = timeit(lambda: rg_rouge(cands, refs, score_type="rouge_l"), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics ROUGE-L", t_min, t_avg))
    results["ROUGE"] = rows

    # chrF
    rows = []
    if sacrebleu is not None:
        t_min, t_avg = timeit(lambda: chrf_sacrebleu(cands, refs), repeat=args.repeat, warmup=args.warmup)
        rows.append(("sacrebleu chrF", t_min, t_avg))
    else:
        print("sacrebleu not available; skipping chrF baseline")
    t_min, t_avg = timeit(lambda: rg_chrf(cands, refs, max_n=6, beta=2.0), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics chrF", t_min, t_avg))
    results["chrF"] = rows

    # METEOR
    rows = []
    if nltk is not None:
        try:
            t_min, t_avg = timeit(lambda: meteor_nltk(cands, refs), repeat=args.repeat, warmup=args.warmup)
            rows.append(("nltk METEOR", t_min, t_avg))
        except LookupError:
            print("nltk METEOR skipped (requires wordnet); run nltk.download('wordnet') to enable")
        except Exception as e:
            print(f"nltk METEOR baseline error: {e}; skipping")
    else:
        print("nltk not available; skipping METEOR baseline")
    t_min, t_avg = timeit(lambda: rg_meteor(cands, refs), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics METEOR-lite", t_min, t_avg))
    results["METEOR"] = rows

    # WER
    rows = []
    if jiwer is not None:
        t_min, t_avg = timeit(lambda: wer_jiwer(cands, refs), repeat=args.repeat, warmup=args.warmup)
        rows.append(("jiwer WER", t_min, t_avg))
    else:
        print("jiwer not available; skipping WER baseline")
    t_min, t_avg = timeit(lambda: rg_wer(cands, refs), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics WER", t_min, t_avg))
    results["WER"] = rows

    # BERTScore-like similarity
    rows = []
    if bertscore_score is not None:
        t_min, t_avg = timeit(lambda: bertscore_baseline(cands[:128], refs[:128]), repeat=args.repeat, warmup=args.warmup)
        rows.append(("bert-score P/R/F1", t_min, t_avg))
    else:
        print("bert-score not available; skipping BERTScore baseline")
    # Compare our similarity kernel on random embeddings
    E1 = np.random.rand(256, 768).astype(np.float32)
    E2 = np.random.rand(256, 768).astype(np.float32)
    t_min, t_avg = timeit(lambda: rg_bertsim(E1, E2), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics BERT-sim", t_min, t_avg))
    results["BERTScore-sim"] = rows

    # MoverScore
    rows = []
    if word_mover_score is not None:
        t_min, t_avg = timeit(lambda: moverscore_baseline(cands[:256], refs[:256]), repeat=args.repeat, warmup=args.warmup)
        rows.append(("moverscore", t_min, t_avg))
    else:
        print("moverscore not available; skipping baseline")
    # Our greedy moverscore on embeddings (random)
    E1 = np.random.rand(256, 768).astype(np.float32)
    E2 = np.random.rand(256, 768).astype(np.float32)
    t_min, t_avg = timeit(lambda: rg_moverscore(E1, E2), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics mover-greedy", t_min, t_avg))
    results["MoverScore"] = rows

    # Guardrails (overall vs python baseline)
    rows = []
    texts = _make_guardrails_texts(n=n)
    blocklist = ["idiot", "stupid", "hate", "kill"]
    regexes = [r"[\w.+-]+@[\w-]+\.[\w.-]+", r"\+?\d[\d\- ]{7,}\d"]
    t_min, t_avg = timeit(lambda: python_guardrails_baseline(texts, blocklist, regexes), repeat=args.repeat, warmup=args.warmup)
    rows.append(("python guardrails", t_min, t_avg))
    rg_gr = RG_Guardrails(blocklist=blocklist, regexes=regexes, redact_pii=True, safety=True)
    t_min, t_avg = timeit(lambda: rg_gr.check(texts), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics Guardrails (full)", t_min, t_avg))
    results["Guardrails"] = rows

    # Guardrails sub-features (isolation benchmarks)
    # Blocklist only
    rows = []
    rg_block = RG_Guardrails(blocklist=blocklist, regexes=[], redact_pii=False, safety=False, detect_injection_spoof=False)
    t_min, t_avg = timeit(lambda: rg_block.check(texts), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics blocklist-only", t_min, t_avg))
    if blocklist:
        # naive python substring match baseline
        def _py_block():
            flags = []
            bl = [b.lower() for b in blocklist]
            for t in texts:
                tl = t.lower()
                flags.append(any(b in tl for b in bl))
            return flags
        t_min, t_avg = timeit(_py_block, repeat=args.repeat, warmup=args.warmup)
        rows.append(("python blocklist-only", t_min, t_avg))
    results["Guardrails-blocklist"] = rows

    # Regex only
    rows = []
    rg_regex = RG_Guardrails(blocklist=[], regexes=regexes, redact_pii=False, safety=False, detect_injection_spoof=False)
    t_min, t_avg = timeit(lambda: rg_regex.check(texts), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics regex-only", t_min, t_avg))
    def _py_regex():
        ci = re.IGNORECASE
        comp = [re.compile(p, ci) for p in regexes]
        return [any(rx.search(t) for rx in comp) for t in texts]
    t_min, t_avg = timeit(_py_regex, repeat=args.repeat, warmup=args.warmup)
    rows.append(("python regex-only", t_min, t_avg))
    results["Guardrails-regex"] = rows

    # PII redaction only
    rows = []
    rg_redact = RG_Guardrails(blocklist=[], regexes=[], redact_pii=True, safety=False, detect_injection_spoof=False)
    t_min, t_avg = timeit(lambda: rg_redact.check(texts), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics redact-only", t_min, t_avg))
    def _py_redact():
        email_re = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
        phone_re = re.compile(r"\+?\d[\d\- ]{7,}\d")
        out = []
        for t in texts:
            rtxt = email_re.sub("[REDACTED_EMAIL]", t)
            rtxt = phone_re.sub("[REDACTED_PHONE]", rtxt)
            out.append(rtxt)
        return out
    t_min, t_avg = timeit(_py_redact, repeat=args.repeat, warmup=args.warmup)
    rows.append(("python redact-only", t_min, t_avg))
    results["Guardrails-redact"] = rows

    # Safety score only
    rows = []
    rg_safety = RG_Guardrails(blocklist=[], regexes=[], redact_pii=False, safety=True, detect_injection_spoof=False)
    t_min, t_avg = timeit(lambda: rg_safety.check(texts), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics safety-only", t_min, t_avg))
    # No direct baseline; include a simple python heuristic as rough comparator
    def _py_safety():
        cues = ["hate", "kill", "stupid", "idiot", "violence", "attack"]
        out = []
        for t in texts:
            tl = t.lower()
            out.append(sum(tl.count(c) for c in cues)/max(1, len(tl)))
        return out
    t_min, t_avg = timeit(_py_safety, repeat=args.repeat, warmup=args.warmup)
    rows.append(("python safety-only", t_min, t_avg))
    results["Guardrails-safety"] = rows

    # JSON schema only
    rows = []
    json_schema = '{"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}'
    # texts here should be json-like for fairness; construct small json strings
    json_texts = [json.dumps({"name": f"user{i}", "id": i}) if i % 2 == 0 else "{}" for i in range(n)]
    rg_json = RG_Guardrails(blocklist=[], regexes=[], redact_pii=False, safety=False, json_schema=json_schema, detect_injection_spoof=False)
    t_min, t_avg = timeit(lambda: rg_json.check(json_texts), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics json-validate-only", t_min, t_avg))
    # Simple python json validation baseline using jsonschema if available; otherwise naive
    try:
        import jsonschema  # type: ignore
        schema_obj = json.loads(json_schema)
        def _py_json_valid():
            out_valid = []
            for t in json_texts:
                try:
                    obj = json.loads(t)
                    jsonschema.validate(obj, schema_obj)  # type: ignore
                    out_valid.append(True)
                except Exception:
                    out_valid.append(False)
            return out_valid
        t_min, t_avg = timeit(_py_json_valid, repeat=args.repeat, warmup=args.warmup)
        rows.append(("python jsonschema validate", t_min, t_avg))
    except Exception:
        pass
    results["Guardrails-json"] = rows

    # Injection/spoof only (others off)
    rows = []
    rg_inj = RG_Guardrails(blocklist=[], regexes=[], redact_pii=False, safety=False, detect_injection_spoof=True)
    t_min, t_avg = timeit(lambda: rg_inj.check(texts), repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics injection/spoof-only", t_min, t_avg))
    # Provide a light python comparator (very naive)
    def _py_injection():
        cues = ["ignore previous", "system:", "[system]", "\u202e"]
        return [any(c in t.lower() for c in cues) for t in texts]
    t_min, t_avg = timeit(_py_injection, repeat=args.repeat, warmup=args.warmup)
    rows.append(("python injection/spoof-only", t_min, t_avg))
    results["Guardrails-injection"] = rows

    # All-in-one metrics API
    rows = []
    def _run_all_metrics():
        return rg_compute_all(cands, refs, include=["bleu", "rouge1", "rouge2", "rougeL", "chrf", "meteor", "wer"])  # type: ignore
    t_min, t_avg = timeit(_run_all_metrics, repeat=args.repeat, warmup=args.warmup)
    rows.append(("blazemetrics compute_text_metrics", t_min, t_avg))
    results["All-Metrics"] = rows

    summarize(results, plot=(not args.no_plot), csv_path=args.csv, md_path=args.md)

    if args.save:
        try:
            with open(args.save, 'w') as f:
                json.dump({k: [(n, t1, t2) for (n, t1, t2) in v] for k, v in results.items()}, f, indent=2)
            print(f"Saved JSON results to {args.save}")
        except Exception as e:
            print(f"Failed to save results: {e}")

    # Spot-check correlations on small subset
    small_c = cands[:10]
    small_r = refs[:10]
    if nltk is not None:
        b1 = bleu_nltk(small_c, small_r)
        b2 = rg_bleu(small_c, small_r, max_n=4)
        print(f"BLEU corr on 10: {np.corrcoef(b1, b2)[0,1]:.4f}")


if __name__ == "__main__":
    main()