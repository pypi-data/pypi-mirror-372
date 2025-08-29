import asyncio
import random
from typing import Dict, List
from examples.helpers import batch_text_metrics, aggregate_metrics
from examples.exporters import MetricsExporters

DEFAULT_THRESHOLDS: Dict[str, float] = {
    "bleu": 0.20,
    "rouge1_f1": 0.35,
    "chrf": 0.30,
    "wer": 0.35,
}

async def async_model_response(prompt: str) -> str:
    await asyncio.sleep(0.001)
    return prompt.replace("asked", "answered")

async def generate_stream(n: int = 300) -> List[tuple[str, List[str]]]:
    data = []
    for i in range(n):
        data.append((f"user asked {i}", [f"answer for {i}"]))
    return data

async def monitor(thresholds: Dict[str, float] = DEFAULT_THRESHOLDS, export_prom: str | None = None, export_statsd: str | None = None):
    exporters = MetricsExporters(prometheus_gateway=export_prom, statsd_addr=export_statsd)
    window_size = 100
    preds: List[str] = []
    refs: List[List[str]] = []

    stream = await generate_stream(500)
    for i, (prompt, ref) in enumerate(stream):
        pred = await async_model_response(prompt)
        preds.append(pred)
        refs.append(ref)
        if len(preds) < window_size:
            continue
        preds = preds[-window_size:]
        refs = refs[-window_size:]

        sm = batch_text_metrics(preds, refs, include=["bleu", "rouge1", "chrf", "wer"], lowercase=True)
        agg = aggregate_metrics(sm)

        exporters.export(agg, labels={"service": "demo", "window": str(window_size)})

        alerts = []
        if agg.get("bleu", 1.0) < thresholds.get("bleu", 0.0):
            alerts.append(f"BLEU {agg['bleu']:.3f} < {thresholds['bleu']}")
        if agg.get("rouge1_f1", 1.0) < thresholds.get("rouge1_f1", 0.0):
            alerts.append(f"ROUGE-1 {agg['rouge1_f1']:.3f} < {thresholds['rouge1_f1']}")
        if agg.get("chrf", 1.0) < thresholds.get("chrf", 0.0):
            alerts.append(f"chrF {agg['chrf']:.3f} < {thresholds['chrf']}")
        if agg.get("wer", 0.0) > thresholds.get("wer", 1.0):
            alerts.append(f"WER {agg['wer']:.3f} > {thresholds['wer']}")

        print(f"i={i} agg={ {k: round(v,3) for k,v in agg.items()} }")
        if alerts:
            print("ALERT:", "; ".join(alerts))

        await asyncio.sleep(0.005)


def main():
    asyncio.run(monitor())


if __name__ == "__main__":
    main() 