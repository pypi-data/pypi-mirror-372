import time
import numpy as np
from blazemetrics import bert_score_similarity


def random_embeddings(num_tokens, dim, seed):
    rng = np.random.default_rng(seed)
    return rng.random((num_tokens, dim), dtype=np.float32)


def main():
    print("--- Advanced Embeddings Example (BERTScore Similarity) ---")

    dims = 768
    sizes = [(32, 40), (128, 140), (512, 520)]  # (cand_tokens, ref_tokens)

    for i, (c_tokens, r_tokens) in enumerate(sizes, 1):
        cand = random_embeddings(c_tokens, dims, seed=123 + i)
        ref = random_embeddings(r_tokens, dims, seed=456 + i)

        t0 = time.perf_counter()
        p, r, f1 = bert_score_similarity(cand, ref)
        t1 = time.perf_counter()
        print(f"Case {i}: {c_tokens}x{dims} vs {r_tokens}x{dims} -> P={p:.4f} R={r:.4f} F1={f1:.4f} | {(t1-t0)*1000:.2f} ms")


if __name__ == "__main__":
    main() 