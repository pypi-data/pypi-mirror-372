from typing import List, Dict, Optional
import time
import asyncio
from .metrics import compute_text_metrics, aggregate_samples
from .exporters import MetricsExporters

DEFAULT_INCLUDE = ["bleu", "rouge1", "chrf", "wer"]


def monitor_stream_sync(
    stream: List[tuple[str, List[str]]],
    window_size: int = 100,
    include: Optional[List[str]] = None,
    thresholds: Optional[Dict[str, float]] = None,
    lowercase: bool = False,
    stemming: bool = False,
    prometheus_gateway: Optional[str] = None,
    statsd_addr: Optional[str] = None,
) -> None:
    include = include or DEFAULT_INCLUDE
    thresholds = thresholds or {}
    exporters = MetricsExporters(prometheus_gateway=prometheus_gateway, statsd_addr=statsd_addr)

    preds: List[str] = []
    refs: List[List[str]] = []
    for i, (prompt, ref) in enumerate(stream):
        # Users inject their own model call here; we pass prompt through for example
        pred = prompt
        preds.append(pred)
        refs.append(ref)
        if len(preds) < window_size:
            continue
        preds = preds[-window_size:]
        refs = refs[-window_size:]

        sm = compute_text_metrics(preds, refs, include=include, lowercase=lowercase, stemming=stemming)
        agg = aggregate_samples(sm)
        exporters.export(agg, labels={"window": str(window_size)})

        alerts = []
        for k, v in agg.items():
            if k == "wer":
                if v > thresholds.get(k, 1.0):
                    alerts.append(f"{k} {v:.3f} > {thresholds[k]}")
            else:
                if v < thresholds.get(k, 0.0):
                    alerts.append(f"{k} {v:.3f} < {thresholds[k]}")
        if alerts:
            print("ALERT:", "; ".join(alerts))


async def monitor_stream_async(
    stream: List[tuple[str, List[str]]],
    window_size: int = 100,
    include: Optional[List[str]] = None,
    thresholds: Optional[Dict[str, float]] = None,
    lowercase: bool = False,
    stemming: bool = False,
    prometheus_gateway: Optional[str] = None,
    statsd_addr: Optional[str] = None,
    delay_s: float = 0.0,
) -> None:
    include = include or DEFAULT_INCLUDE
    thresholds = thresholds or {}
    exporters = MetricsExporters(prometheus_gateway=prometheus_gateway, statsd_addr=statsd_addr)

    preds: List[str] = []
    refs: List[List[str]] = []
    for i, (prompt, ref) in enumerate(stream):
        pred = prompt
        preds.append(pred)
        refs.append(ref)
        if len(preds) < window_size:
            if delay_s:
                await asyncio.sleep(delay_s)
            continue
        preds = preds[-window_size:]
        refs = refs[-window_size:]

        sm = compute_text_metrics(preds, refs, include=include, lowercase=lowercase, stemming=stemming)
        agg = aggregate_samples(sm)
        exporters.export(agg, labels={"window": str(window_size)})

        alerts = []
        for k, v in agg.items():
            if k == "wer":
                if v > thresholds.get(k, 1.0):
                    alerts.append(f"{k} {v:.3f} > {thresholds[k]}")
            else:
                if v < thresholds.get(k, 0.0):
                    alerts.append(f"{k} {v:.3f} < {thresholds[k]}")
        if alerts:
            print("ALERT:", "; ".join(alerts))

        if delay_s:
            await asyncio.sleep(delay_s) 