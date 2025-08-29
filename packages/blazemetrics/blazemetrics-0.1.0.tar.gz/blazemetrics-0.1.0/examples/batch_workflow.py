import time
import csv
from typing import List
from examples.helpers import batch_text_metrics, aggregate_metrics, format_report

# Dummy model generating candidates (replace with your model call)
def generate_predictions(prompts: List[str], epoch: int) -> List[str]:
    return [p.replace("t", "t").strip() for p in prompts]


def main():
    prompts = [f"t{i} t{i+1} t{i+2}" for i in range(100)]
    references = [[f"t{i} t{i+1} t{i+3}"] for i in range(100)]

    with open("training_metrics.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "metric", "value"])

        for epoch in range(1, 6):
            t0 = time.perf_counter()
            preds = generate_predictions(prompts, epoch)
            sample_metrics = batch_text_metrics(preds, references)
            agg = aggregate_metrics(sample_metrics)
            for k, v in agg.items():
                writer.writerow([epoch, k, f"{v:.4f}"])
            t1 = time.perf_counter()
            print(f"Epoch {epoch}: computed metrics in {(t1-t0)*1000:.1f} ms")
            print(format_report(agg))


if __name__ == "__main__":
    main() 