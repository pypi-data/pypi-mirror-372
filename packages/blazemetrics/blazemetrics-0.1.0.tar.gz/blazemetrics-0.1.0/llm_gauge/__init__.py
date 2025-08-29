from .blazemetrics import (
    rouge_score,
    bleu,
    bert_score_similarity,
    chrf_score,
    token_f1,
    jaccard,
    moverscore_greedy_py as moverscore_greedy,
    meteor,
    wer,
)
from .metrics import compute_text_metrics, aggregate_samples
from .exporters import MetricsExporters
from .monitor import monitor_stream_sync, monitor_stream_async
from .guardrails import Guardrails, guardrails_check
from .guardrails_pipeline import monitor_tokens_sync, monitor_tokens_async, map_large_texts, enforce_stream_sync

import os
from typing import Optional

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