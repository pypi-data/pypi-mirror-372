use std::collections::HashMap;
use super::common::{get_str_ngrams, whitespace_tokenize};

pub fn bleu_score(
    candidate: &str,
    references: &[String],
    max_n: usize,
) -> f64 {
    let cand_tokens = whitespace_tokenize(candidate);
    let cand_len = cand_tokens.len();

    // Find the reference with the closest length
    let closest_ref_len = references
        .iter()
        .map(|r| whitespace_tokenize(r).len())
        .min_by_key(|&len| (len as i32 - cand_len as i32).abs())
        .unwrap_or(0);
    
    // Brevity Penalty
    let brevity_penalty = if cand_len > closest_ref_len {
        1.0
    } else {
        (1.0 - closest_ref_len as f64 / cand_len as f64).exp()
    };

    let mut log_bleu: f64 = 0.0;
    for n in 1..=max_n {
        let cand_ngrams = get_str_ngrams(n, &cand_tokens);
        
        let mut max_ref_counts: HashMap<Vec<String>, usize> = HashMap::new();
        for reference in references {
            let ref_tokens = whitespace_tokenize(reference);
            let ref_ngrams = get_str_ngrams(n, &ref_tokens);
            for (ngram, count) in ref_ngrams {
                let entry = max_ref_counts.entry(ngram).or_insert(0);
                *entry = std::cmp::max(*entry, count);
            }
        }
        
        let mut clipped_count: usize = 0;
        let mut total_count: usize = 0;
        
        for (ngram, count) in &cand_ngrams {
            total_count += count;
            if let Some(ref_count) = max_ref_counts.get(ngram) {
                clipped_count += std::cmp::min(*count, *ref_count);
            }
        }

        let precision = if total_count == 0 { 0.0 } else { clipped_count as f64 / total_count as f64 };
        
        if precision > 0.0 {
            log_bleu += precision.ln();
        } else {
            // If any precision is 0, the score is 0. Handle by returning early.
            return 0.0;
        }
    }

    brevity_penalty * (log_bleu / max_n as f64).exp()
}