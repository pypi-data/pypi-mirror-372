use std::collections::{HashMap, HashSet};
use super::common::{get_str_ngrams, whitespace_tokenize};

// Calculate ROUGE-N score for a single candidate/reference pair.
fn rouge_n_single(
    candidate_ngrams: &HashMap<Vec<String>, usize>,
    reference_ngrams: &HashMap<Vec<String>, usize>,
) -> (f64, f64, f64) {
    let mut overlapping_count = 0;
    let mut reference_total = 0;
    let mut candidate_total = 0;

    let candidate_keys: HashSet<_> = candidate_ngrams.keys().collect();
    let reference_keys: HashSet<_> = reference_ngrams.keys().collect();

    for ngram in candidate_keys.intersection(&reference_keys) {
        overlapping_count += std::cmp::min(
            *candidate_ngrams.get(*ngram).unwrap_or(&0),
            *reference_ngrams.get(*ngram).unwrap_or(&0),
        );
    }

    for count in reference_ngrams.values() {
        reference_total += count;
    }
    for count in candidate_ngrams.values() {
        candidate_total += count;
    }

    let recall = if reference_total == 0 { 0.0 } else { overlapping_count as f64 / reference_total as f64 };
    let precision = if candidate_total == 0 { 0.0 } else { overlapping_count as f64 / candidate_total as f64 };
    let f1 = if recall + precision == 0.0 { 0.0 } else { 2.0 * (precision * recall) / (precision + recall) };

    (precision, recall, f1)
}

// Public function to compute ROUGE-N for a batch.
pub fn rouge_n(
    candidate: &str,
    references: &[String],
    n: usize,
) -> (f64, f64, f64) {
    let cand_tokens = whitespace_tokenize(candidate);
    let cand_ngrams = get_str_ngrams(n, &cand_tokens);

    let mut best_f1 = 0.0;
    let mut best_scores = (0.0, 0.0, 0.0);

    for reference in references {
        let ref_tokens = whitespace_tokenize(reference);
        let ref_ngrams = get_str_ngrams(n, &ref_tokens);
        let (p, r, f1) = rouge_n_single(&cand_ngrams, &ref_ngrams);

        if f1 > best_f1 {
            best_f1 = f1;
            best_scores = (p, r, f1);
        }
    }
    best_scores
}

// Longest Common Subsequence algorithm implementation.
fn lcs(a: &[&str], b: &[&str]) -> usize {
    let mut lengths = vec![0; b.len() + 1];
    for token_a in a {
        let mut prev = 0;
        for (j, token_b) in b.iter().enumerate() {
            let temp = lengths[j + 1];
            if token_a == token_b {
                lengths[j + 1] = prev + 1;
            } else {
                lengths[j + 1] = std::cmp::max(lengths[j + 1], lengths[j]);
            }
            prev = temp;
        }
    }
    lengths[b.len()]
}

// Public function to compute ROUGE-L for a batch.
pub fn rouge_l(
    candidate: &str,
    references: &[String],
) -> (f64, f64, f64) {
    let cand_tokens = whitespace_tokenize(candidate);
    
    let mut best_f1 = 0.0;
    let mut best_scores = (0.0, 0.0, 0.0);

    for reference in references {
        let ref_tokens = whitespace_tokenize(reference);
        let lcs_len = lcs(&cand_tokens, &ref_tokens) as f64;

        let recall = if ref_tokens.is_empty() { 0.0 } else { lcs_len / ref_tokens.len() as f64 };
        let precision = if cand_tokens.is_empty() { 0.0 } else { lcs_len / cand_tokens.len() as f64 };
        let f1 = if recall + precision == 0.0 { 0.0 } else { 2.0 * (precision * recall) / (precision + recall) };

        if f1 > best_f1 {
            best_f1 = f1;
            best_scores = (precision, recall, f1);
        }
    }
    best_scores
}