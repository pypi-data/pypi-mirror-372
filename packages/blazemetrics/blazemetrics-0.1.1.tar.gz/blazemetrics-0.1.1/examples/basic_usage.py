import numpy as np
import time

# Ensure the library is installed or in the PYTHONPATH
try:
    from blazemetrics import rouge_score, bleu, bert_score_similarity, chrf_score, token_f1, jaccard
except ImportError:
    print("Please install the package first, e.g., 'pip install .' ")
    exit()


def main():
    """Demonstrates the usage of all metrics in the blazemetrics library."""

    print("--- blazemetrics Usage Example ---")

    # --- Sample Data ---
    candidates = [
        "the quick brown fox jumps over the lazy dog",
        "a good book is a great friend",
        "hello world"
    ]
    references = [
        ["a quick brown fox leaps over the lazy dog"],
        ["a good book is a true friend forever"],
        ["hello to the world"]
    ]

    print(f"\nCandidates: {candidates}")
    print(f"References: {references}\n")
    
    # --- 1. ROUGE Score ---
    print("--- Calculating ROUGE Scores ---")
    
    # ROUGE-1 (Unigram)
    start_time = time.perf_counter()
    r1_scores = rouge_score(candidates, references, score_type="rouge_n", n=1)
    end_time = time.perf_counter()
    print(f"ROUGE-1 Scores: {r1_scores} (took {(end_time - start_time)*1000:.2f} ms)")

    # ROUGE-2 (Bigram)
    start_time = time.perf_counter()
    r2_scores = rouge_score(candidates, references, score_type="rouge_n", n=2)
    end_time = time.perf_counter()
    print(f"ROUGE-2 Scores: {r2_scores} (took {(end_time - start_time)*1000:.2f} ms)")

    # ROUGE-L (Longest Common Subsequence)
    start_time = time.perf_counter()
    rl_scores = rouge_score(candidates, references, score_type="rouge_l")
    end_time = time.perf_counter()
    print(f"ROUGE-L Scores: {rl_scores} (took {(end_time - start_time)*1000:.2f} ms)")


    # --- 2. BLEU Score ---
    print("\n--- Calculating BLEU Score ---")
    start_time = time.perf_counter()
    bleu_scores = bleu(candidates, references, max_n=4)
    end_time = time.perf_counter()
    print(f"BLEU Scores: {bleu_scores} (took {(end_time - start_time)*1000:.2f} ms)")

    # --- 3. chrF ---
    print("\n--- Calculating chrF ---")
    start_time = time.perf_counter()
    chrf_scores = chrf_score(candidates, references, max_n=6, beta=2.0)
    end_time = time.perf_counter()
    print(f"chrF Scores: {chrf_scores} (took {(end_time - start_time)*1000:.2f} ms)")

    # --- 4. Token-level metrics ---
    print("\n--- Calculating Token-level Metrics ---")
    start_time = time.perf_counter()
    token_f1_scores = token_f1(candidates, references)
    end_time = time.perf_counter()
    print(f"Token F1 Scores: {token_f1_scores} (took {(end_time - start_time)*1000:.2f} ms)")

    start_time = time.perf_counter()
    jaccard_scores = jaccard(candidates, references)
    end_time = time.perf_counter()
    print(f"Jaccard Scores: {jaccard_scores} (took {(end_time - start_time)*1000:.2f} ms)")


    # --- 5. BERTScore (Similarity Calculation) ---
    print("\n--- Calculating BERTScore Similarity ---")
    print("Note: This requires pre-computed embeddings.")
    
    # Create random embeddings to simulate real ones
    # In a real scenario, you would use a model like BERT to get these.
    # Dimensions: (num_tokens, embedding_dim)
    np.random.seed(42)
    cand_embeddings = np.random.rand(15, 768).astype(np.float32) # 15 tokens
    ref_embeddings = np.random.rand(20, 768).astype(np.float32)  # 20 tokens
    
    start_time = time.perf_counter()
    p, r, f1 = bert_score_similarity(cand_embeddings, ref_embeddings)
    end_time = time.perf_counter()

    print(f"BERTScore: Precision={p:.4f}, Recall={r:.4f}, F1={f1:.4f}")
    print(f"(Similarity calculation took {(end_time - start_time)*1000:.2f} ms)")


if __name__ == "__main__":
    main()