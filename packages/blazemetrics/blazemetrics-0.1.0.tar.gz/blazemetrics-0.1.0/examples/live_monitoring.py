import time
import random
from collections import deque
from typing import List, Deque, Dict
from examples.helpers import batch_text_metrics, aggregate_metrics

ALERT_THRESHOLDS = {
    "bleu": 0.15,
    "rouge1_f1": 0.30,
    "chrf": 0.25,
    "wer": 0.40,  # lower is better; we alert if above this
}


def simulate_stream(n=500, seed=123) -> List[tuple[str, List[str]]]:
    rng = random.Random(seed)
    data = []
    for i in range(n):
        prompt = f"user asked {i}"
        # simulate ground-truth changes
        ref = [f"answer for {i}"]
        data.append((prompt, ref))
    return data


def model_response(prompt: str) -> str:
    # placeholder for a real model call
    return prompt.replace("asked", "answered")


def main():
    window: Deque[tuple[str, List[str]]] = deque(maxlen=100)
    history: List[Dict[str, float]] = []

    for i, (prompt, ref) in enumerate(simulate_stream(300)):
        pred = model_response(prompt)
        window.append((pred, ref))
        if len(window) < window.maxlen:
            continue
        candidates = [p for p, _ in window]
        refs = [r for _, r in window]
        sm = batch_text_metrics(candidates, refs, include=["bleu", "rouge1", "chrf", "wer"])  # fast subset
        agg = aggregate_metrics(sm)
        history.append(agg)

        alerts = []
        if agg.get("bleu", 1.0) < ALERT_THRESHOLDS["bleu"]:
            alerts.append(f"BLEU drop: {agg['bleu']:.3f}")
        if agg.get("rouge1_f1", 1.0) < ALERT_THRESHOLDS["rouge1_f1"]:
            alerts.append(f"ROUGE-1 drop: {agg['rouge1_f1']:.3f}")
        if agg.get("chrf", 1.0) < ALERT_THRESHOLDS["chrf"]:
            alerts.append(f"chrF drop: {agg['chrf']:.3f}")
        if agg.get("wer", 0.0) > ALERT_THRESHOLDS["wer"]:
            alerts.append(f"WER spike: {agg['wer']:.3f}")

        print(f"t={i}: metrics={ {k: round(v,3) for k,v in agg.items()} }")
        if alerts:
            print("ALERT:", "; ".join(alerts))
        time.sleep(0.01)


if __name__ == "__main__":
    main() 