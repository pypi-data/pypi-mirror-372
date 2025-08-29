# Import Rust functions directly from the compiled extension
try:
    # Use relative import to avoid shadowing the package name
    from . import blazemetrics as _ext
    (
        rouge_score,
        bleu,
        bert_score_similarity,
        chrf_score,
        token_f1,
        jaccard,
        moverscore_greedy_py,
        meteor_score,
        wer_score,
    ) = (
        _ext.rouge_score,
        _ext.bleu,
        _ext.bert_score_similarity,
        _ext.chrf_score,
        _ext.token_f1,
        _ext.jaccard,
        _ext.moverscore_greedy_py,
        _ext.meteor,
        _ext.wer,
    )
    # Provide public names expected by users
    moverscore_greedy = moverscore_greedy_py
    meteor = meteor_score
    wer = wer_score
except ImportError as e:
    # Fallback for development or when extension not built
    raise ImportError(
        "blazemetrics extension not found. "
        "Build the Rust extension via 'maturin develop' or install with 'pip install -e .'"
    ) from e

from .metrics import compute_text_metrics, aggregate_samples
from .exporters import MetricsExporters
from .monitor import monitor_stream_sync, monitor_stream_async
from .guardrails import Guardrails, guardrails_check, max_similarity_to_unsafe
from .guardrails_pipeline import monitor_tokens_sync, monitor_tokens_async, map_large_texts, enforce_stream_sync

import os
from typing import Optional

# Expose package version for `blazemetrics.__version__`
try:
    from importlib.metadata import version as _pkg_version  # Python 3.8+
    __version__ = _pkg_version("blazemetrics")
except Exception:
    # Fallback if package metadata is unavailable (e.g., editable installs without metadata)
    __version__ = os.environ.get("BLAZEMETRICS_VERSION", "0.0.0")

__all__ = [
    "rouge_score",
    "bleu",
    "bert_score_similarity",
    "chrf_score",
    "token_f1",
    "jaccard",
    "moverscore_greedy",
    "meteor",
    "wer",
    "compute_text_metrics",
    "aggregate_samples",
    "MetricsExporters",
    "monitor_stream_sync",
    "monitor_stream_async",
    "Guardrails",
    "guardrails_check",
    "monitor_tokens_sync",
    "monitor_tokens_async",
    "map_large_texts",
    "enforce_stream_sync",
    "set_parallel",
    "get_parallel",
    "set_parallel_threshold",
    "get_parallel_threshold",
    "max_similarity_to_unsafe",
]

__doc__ = """
BlazeMetrics: High-performance NLP evaluation metrics with a Rust core.
"""

# Parallelism controls (propagated to Rust via environment variables)
_ENV_PAR = "BLAZEMETRICS_PARALLEL"
_ENV_PAR_TH = "BLAZEMETRICS_PAR_THRESHOLD"


def set_parallel(enabled: bool) -> None:
    os.environ[_ENV_PAR] = "1" if enabled else "0"


def get_parallel() -> bool:
    return os.environ.get(_ENV_PAR, "1") != "0"


def set_parallel_threshold(threshold: int) -> None:
    if threshold < 1:
        threshold = 1
    os.environ[_ENV_PAR_TH] = str(threshold)


def get_parallel_threshold(default: int = 512) -> int:
    try:
        return int(os.environ.get(_ENV_PAR_TH, str(default)))
    except Exception:
        return default 