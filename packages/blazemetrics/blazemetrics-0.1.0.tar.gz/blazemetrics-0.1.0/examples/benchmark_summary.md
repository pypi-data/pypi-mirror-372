# Benchmark Summary

## BLEU

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| nltk BLEU | 7.6 | 7.6 | 1.00x |
| blazemetrics BLEU | 0.7 | 0.7 | 10.16x |
## ROUGE

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| rouge-score (1/2/L) | 8.5 | 8.5 | 1.00x |
| blazemetrics ROUGE-1 | 0.4 | 0.4 | 23.08x |
| blazemetrics ROUGE-2 | 0.4 | 0.4 | 20.75x |
| blazemetrics ROUGE-L | 0.2 | 0.2 | 50.07x |
## chrF

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| sacrebleu chrF | 10.6 | 10.6 | 1.00x |
| blazemetrics chrF | 2.1 | 2.1 | 4.93x |
## METEOR

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| nltk METEOR | 2553.0 | 2553.0 | 1.00x |
| blazemetrics METEOR-lite | 0.3 | 0.3 | 7700.09x |
## WER

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| jiwer WER | 5.2 | 5.2 | 1.00x |
| blazemetrics WER | 0.2 | 0.2 | 21.96x |
## BERTScore-sim

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| blazemetrics BERT-sim | 58.2 | 58.2 | 1.00x |
## MoverScore

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| blazemetrics mover-greedy | 3.8 | 3.8 | 1.00x |
## Guardrails

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| python guardrails | 4.9 | 4.9 | 1.00x |
| blazemetrics Guardrails (full) | 25.7 | 25.7 | 0.19x |
## Guardrails-blocklist

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| blazemetrics blocklist-only | 0.1 | 0.1 | 2.96x |
| python blocklist-only | 0.2 | 0.2 | 1.00x |
## Guardrails-regex

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| blazemetrics regex-only | 0.2 | 0.2 | 7.22x |
| python regex-only | 1.4 | 1.4 | 1.00x |
## Guardrails-redact

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| blazemetrics redact-only | 0.2 | 0.2 | 14.15x |
| python redact-only | 2.8 | 2.8 | 1.00x |
## Guardrails-safety

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| blazemetrics safety-only | 0.7 | 0.7 | 0.31x |
| python safety-only | 0.2 | 0.2 | 1.00x |
## Guardrails-json

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| blazemetrics json-validate-only | 4.4 | 4.4 | 1.00x |
## Guardrails-injection

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| blazemetrics injection/spoof-only | 0.4 | 0.4 | 0.31x |
| python injection/spoof-only | 0.1 | 0.1 | 1.00x |
## All-Metrics

| Impl | Min (ms) | Avg (ms) | Speedup vs Baseline |
|---|---:|---:|---:|
| blazemetrics compute_text_metrics | 8.9 | 8.9 | 1.00x |
