from typing import List, Dict, Tuple, Optional
from blazemetrics import (
    rouge_score,
    bleu,
    chrf_score,
    token_f1,
    jaccard,
    meteor,
    wer,
)

try:
    from nltk.stem.porter import PorterStemmer
except Exception:
    PorterStemmer = None


def _normalize_texts(texts: List[str], lowercase: bool, stemming: bool) -> List[str]:
    if not lowercase and not stemming:
        return texts
    stemmer = PorterStemmer() if stemming and PorterStemmer is not None else None
    out = []
    for t in texts:
        s = t.lower() if lowercase else t
        if stemmer is not None:
            s = " ".join(stemmer.stem(tok) for tok in s.split())
        out.append(s)
    return out


def batch_text_metrics(
    candidates: List[str],
    references: List[List[str]],
    include: List[str] = ("rouge1", "rouge2", "rougeL", "bleu", "chrf", "meteor", "wer", "token_f1", "jaccard"),
    lowercase: bool = False,
    stemming: bool = False,
) -> Dict[str, List[float]]:
    # Apply normalization to flat lists
    norm_cands = _normalize_texts(candidates, lowercase, stemming)
    norm_refs = [ _normalize_texts(r, lowercase, stemming) for r in references ]

    out: Dict[str, List[float]] = {}
    if any(m in include for m in ("rouge1", "rouge2", "rougeL")):
        if "rouge1" in include:
            out["rouge1_f1"] = [t[2] for t in rouge_score(norm_cands, norm_refs, score_type="rouge_n", n=1)]
        if "rouge2" in include:
            out["rouge2_f1"] = [t[2] for t in rouge_score(norm_cands, norm_refs, score_type="rouge_n", n=2)]
        if "rougeL" in include:
            out["rougeL_f1"] = [t[2] for t in rouge_score(norm_cands, norm_refs, score_type="rouge_l")]
    if "bleu" in include:
        out["bleu"] = bleu(norm_cands, norm_refs)
    if "chrf" in include:
        out["chrf"] = chrf_score(norm_cands, norm_refs)
    if "meteor" in include:
        out["meteor"] = meteor(norm_cands, norm_refs)
    if "wer" in include:
        out["wer"] = wer(norm_cands, norm_refs)
    if "token_f1" in include:
        out["token_f1"] = token_f1(norm_cands, norm_refs)
    if "jaccard" in include:
        out["jaccard"] = jaccard(norm_cands, norm_refs)
    return out


def aggregate_metrics(sample_metrics: Dict[str, List[float]]) -> Dict[str, float]:
    agg: Dict[str, float] = {}
    for k, v in sample_metrics.items():
        if not v:
            agg[k] = 0.0
        else:
            agg[k] = float(sum(v) / len(v))
    return agg


def aggregate_corpus(sample_metrics: Dict[str, List[float]], weights: Optional[List[float]] = None) -> Dict[str, float]:
    # Weighted average fallback to uniform
    agg: Dict[str, float] = {}
    for k, vals in sample_metrics.items():
        if not vals:
            agg[k] = 0.0
            continue
        if weights and len(weights) == len(vals):
            s = sum(v * w for v, w in zip(vals, weights))
            agg[k] = float(s / sum(weights))
        else:
            agg[k] = float(sum(vals) / len(vals))
    return agg


def format_report(agg: Dict[str, float]) -> str:
    keys = sorted(agg.keys())
    lines = ["Metric,Value"]
    for k in keys:
        lines.append(f"{k},{agg[k]:.4f}")
    return "\n".join(lines) 