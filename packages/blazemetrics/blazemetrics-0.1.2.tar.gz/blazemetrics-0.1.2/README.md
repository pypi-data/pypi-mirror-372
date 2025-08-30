# BlazeMetrics 🔥

[![PyPI version](https://badge.fury.io/py/blazemetrics.svg)](https://pypi.org/project/blazemetrics/)
[![Python versions](https://img.shields.io/pypi/pyversions/blazemetrics.svg)](https://pypi.org/project/blazemetrics/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Wheels](https://img.shields.io/badge/wheels-available-brightgreen.svg)](https://pypi.org/project/blazemetrics/#files)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1No3vlPCIuZuAJfpK09xbaDyuveJ2LKfs?usp=sharing)

**BlazeMetrics** is a Python library designed to be the fastest implementation of standard NLP evaluation metrics, powered by a highly optimized Rust core. It leverages Rust's performance, memory safety, and true parallelism to offer significant speedups over pure Python implementations, especially on large datasets.

## ✨ Key Features

-   **Blazing Fast**: Core logic is written in Rust, compiled to native code, and parallelized with [Rayon](https://github.com/rayon-rs/rayon) to use all available CPU cores.
-   **NumPy Integration**: Efficiently handles numerical data like embeddings via NumPy, with matrix operations accelerated by Rust's `ndarray`.
-   **No GIL**: CPU-bound tasks run on the Rust backend without being constrained by Python's Global Interpreter Lock (GIL).
-   **Simple API**: A clean, intuitive API that feels familiar to Python developers.
-   **Extensible**: Designed with a clear path for adding new, high-performance metrics.
-   **New: LLM Guardrails**: Ultra-fast guardrails (blocklists, regex policies, PII redaction, lightweight safety scoring) implemented in Rust for streaming and batch workflows.
-   **New: LLM Guardrails++**: JSON Schema validation & auto-repair, prompt-injection/jailbreak heuristics, Unicode spoof detection, and ANN-like unsafe similarity — all blazing fast.

## 🚀 Installation

### End users (pip install)

Most users can just install from PyPI and do not need Rust:

```bash
pip install blazemetrics
```

Prebuilt wheels are published for Linux (manylinux2014), macOS, and Windows across Python 3.8–3.12 via CI. On supported platforms, `pip` will download a wheel and skip any Rust compilation. If you still see a build step, it likely means a wheel for your exact Python/OS/arch wasn’t available yet.

### Building from source only for (developers/contributors)

If a wheel is not available for your platform, or if you install from source (e.g., `git clone` or `pip install -e .`), the Rust toolchain is required to build the native extension:

```bash
# Install Rust (one time)
curl --proto '=https' --tlsv1.2 -sSf https://rustup.rs | sh

# From a cloned repo
pip install -e .
```

### Maintainers: building wheels

We use GitHub Actions to build wheels for Linux, macOS, and Windows and publish them on tagged releases. To build locally or for custom targets:

```bash
# Build wheels (example for Linux manylinux2014)
maturin build --release --compatibility manylinux2014 -o dist

# Upload
maturin upload dist/*
```

## ⚡ Quickstart

The API is straightforward. Provide a list of candidate strings and a list of reference lists.

```python
import numpy as np
from blazemetrics import rouge_score, bleu, bert_score_similarity, chrf_score, token_f1, jaccard, meteor, wer

candidates = ["the cat sat on the mat", "the dog ate the homework"]
references = [
    ["the cat was on the mat"],
    ["the dog did my homework"]
]

# ROUGE
rouge_2_scores = rouge_score(candidates, references, score_type="rouge_n", n=2)
rouge_l_scores = rouge_score(candidates, references, score_type="rouge_l")

# BLEU
bleu_scores = bleu(candidates, references)

# chrF
chrf_scores = chrf_score(candidates, references, max_n=6, beta=2.0)

# Token-level metrics
print(token_f1(candidates, references))
print(jaccard(candidates, references))

# METEOR-lite and WER
print(meteor(candidates, references))
print(wer(candidates, references))

# BERTScore similarity kernel (requires embeddings)
cand_embeddings = np.random.rand(5, 768).astype(np.float32)
ref_embeddings = np.random.rand(8, 768).astype(np.float32)
print(bert_score_similarity(cand_embeddings, ref_embeddings))
```

## 🛡️ LLM Guardrails (New)

High-performance guardrails accelerated by Rust and parallelized with Rayon. Ideal for streaming moderation, batch post-processing, and preflight checks.

- Blocklist matching via Aho–Corasick (case-insensitive option)
- Regex policy checks (precompiled DFA)
- PII redaction (email, phone, card, SSN)
- Lightweight safety score heuristic (hate/sexual/violence/self-harm cues)
- JSON Schema validation with best-effort auto-repair
- Prompt-injection / jailbreak heuristics and Unicode spoofing detection
- ANN-like unsafe similarity: fast cosine max vs exemplar bank

```python
from blazemetrics import Guardrails, guardrails_check

texts = [
    "My email is alice@example.com and my SSN is 123-45-6789.",
    "I will bomb the building.",
]

gr = Guardrails(
    blocklist=["bomb", "terror"],
    regexes=[r"\b\d{3}-\d{2}-\d{4}\b"],
    case_insensitive=True,
    redact_pii=True,
    safety=True,
    json_schema='{"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}'
)
print(gr.check(texts))
```

### Streaming guardrails and enforcement

- Sync token monitoring: `monitor_tokens_sync(tokens_iter, rails, every_n_tokens=25)`
- Async token monitoring: `monitor_tokens_async(async_tokens, rails, every_n_tokens=25)`
- Multiprocessing batch mapper: `map_large_texts(texts, rails, processes=..., chunk_size=...)`
- Enforcement wrapper: `enforce_stream_sync(tokens_iter, rails, replacement="[BLOCKED]", safety_threshold=0.6)`

Examples:
- `examples/openai_stream_guardrails.py` (OpenAI Chat Completions streaming)
- `examples/claude_stream_guardrails.py` (Anthropic Claude streaming)

## ⚙️ Parallelism Controls (Rayon overhead vs throughput)

The Rust core uses Rayon to parallelize CPU-heavy work. Parallelism isn’t always faster on very small batches due to scheduling overhead. You can control this globally:

- Environment variables (affects all functions):
  - `BLAZEMETRICS_PARALLEL`: `1` to enable (default), `0` to disable
- `BLAZEMETRICS_PAR_THRESHOLD`: minimum batch size to parallelize (default `512`)

- Python API:

```python
from blazemetrics import set_parallel, get_parallel, set_parallel_threshold, get_parallel_threshold

set_parallel(True)                 # enable or disable
set_parallel_threshold(512)        # switch to sequential below threshold
print(get_parallel(), get_parallel_threshold())
```

- Benchmark CLI (for experiments):

```bash
python examples/benchmark.py --n 5000 --repeat 3 --warmup 1 --parallel 1 --par-threshold 512
python examples/benchmark.py --n 200  --repeat 3 --warmup 1 --parallel 0
```

Guidance:
- Set a higher threshold or disable parallelism for small inputs (e.g., streaming with tiny micro-batches).
- Leave parallelism on for large datasets to maximize throughput.

## 👷 Batch Workflow Example

See `examples/batch_workflow.py` for integrating metrics into training/evaluation loops. It demonstrates:
- Computing batch metrics efficiently in Rust
- Aggregating per-epoch metrics
- Writing results to `training_metrics.csv`

Run:
```bash
python examples/batch_workflow.py
```

## 📈 Live Monitoring Example (Production-like)

See `examples/live_monitoring.py` for a simulated streaming setup with a rolling window and alerts.
- Maintains a 100-sample window
- Computes a fast subset of metrics (`BLEU`, `ROUGE-1`, `chrF`, `WER`)
- Emits alerts on threshold breaches (latency-friendly)

Run:
```bash
python examples/live_monitoring.py
```

## 📊 Benchmarking

See `examples/benchmark.py` for a fair, reproducible benchmark comparing `blazemetrics` with popular Python implementations (when installed):
- ROUGE (`rouge-score`), BLEU (`nltk`), chrF (`sacrebleu`), METEOR (`nltk`), WER (`jiwer`), BERTScore (`bert-score`), and MoverScore (`moverscore_v2`)
- Cleanly skips baselines if dependencies or resources are missing
- Saves a single combined overview chart at `examples/images/benchmark_overview.png`

Parallelism flags available in the benchmark:

```bash
python examples/benchmark.py --parallel {0,1} --par-threshold 512
```

## 📓 Showcase Notebooks (Open in Colab)

Open the end-to-end showcase notebooks directly in Colab:

- **01 — Installation and Setup**: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1No3vlPCIuZuAJfpK09xbaDyuveJ2LKfs?usp=sharing)
- **02 — Core Metrics Showcase**: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1gABpSf0rWjFSjJdMyYqXgbHOGhA4FyFI?usp=sharing)
- **03 — Guardrails Showcase**: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/19ZpqxQl7yvvxSd7FsnB603IbwOdx5NoT?usp=sharing)
- **04 — Streaming Monitoring**: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/17Mzd2p1oUfw0hjIHGw-E6jL5V3XITdhX?usp=sharing)
- **05 — Production Workflows**: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Vi86d3WPtG9p3V2RmxSHWt4wXxJ049Qe?usp=sharing)
- **06 — Performance Benchmarking**: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/18gDd3bRHE0v_MjJMeLnW3wMCALrcFKMa?usp=sharing)

## 🔧 How to Add a New Metric

`blazemetrics` is designed to be easily extensible. To add your own custom metric:

1.  Implement the logic in Rust under `src/`, using Rayon for parallel batch processing.
2.  Expose a `#[pyfunction]` in `src/lib.rs`, releasing the GIL for CPU-bound work.
3.  Rebuild: `pip install -e .` or `maturin develop`.

## ⚖️ License

This project is licensed under the MIT License.
