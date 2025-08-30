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

import os
from typing import Optional

# Lightweight lazy loader to avoid importing heavier helpers unless used
__lazy_modules__ = {
    "metrics": ".metrics",
    "exporters": ".exporters",
    "monitor": ".monitor",
    "guardrails": ".guardrails",
    "guardrails_pipeline": ".guardrails_pipeline",
}

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

# Expose package version for `blazemetrics.__version__`
try:
    from importlib.metadata import version as _pkg_version  # Python 3.8+
    __version__ = _pkg_version("blazemetrics")
except Exception:
    # Fallback if package metadata is unavailable (e.g., editable installs without metadata)
    __version__ = os.environ.get("BLAZEMETRICS_VERSION", "0.0.0")

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


# Lazy attribute access for submodules to keep import time minimal
def __getattr__(name: str):
    if name in ("compute_text_metrics", "aggregate_samples"):
        from .metrics import compute_text_metrics, aggregate_samples
        globals().update({
            "compute_text_metrics": compute_text_metrics,
            "aggregate_samples": aggregate_samples,
        })
        return globals()[name]
    if name in ("MetricsExporters",):
        from .exporters import MetricsExporters
        globals().update({"MetricsExporters": MetricsExporters})
        return globals()[name]
    if name in ("monitor_stream_sync", "monitor_stream_async"):
        from .monitor import monitor_stream_sync, monitor_stream_async
        globals().update({
            "monitor_stream_sync": monitor_stream_sync,
            "monitor_stream_async": monitor_stream_async,
        })
        return globals()[name]
    if name in ("Guardrails", "guardrails_check", "max_similarity_to_unsafe"):
        from .guardrails import Guardrails, guardrails_check, max_similarity_to_unsafe
        globals().update({
            "Guardrails": Guardrails,
            "guardrails_check": guardrails_check,
            "max_similarity_to_unsafe": max_similarity_to_unsafe,
        })
        return globals()[name]
    if name in (
        "monitor_tokens_sync",
        "monitor_tokens_async",
        "map_large_texts",
        "enforce_stream_sync",
    ):
        from .guardrails_pipeline import (
            monitor_tokens_sync,
            monitor_tokens_async,
            map_large_texts,
            enforce_stream_sync,
        )
        globals().update({
            "monitor_tokens_sync": monitor_tokens_sync,
            "monitor_tokens_async": monitor_tokens_async,
            "map_large_texts": map_large_texts,
            "enforce_stream_sync": enforce_stream_sync,
        })
        return globals()[name]
    raise AttributeError(name) 