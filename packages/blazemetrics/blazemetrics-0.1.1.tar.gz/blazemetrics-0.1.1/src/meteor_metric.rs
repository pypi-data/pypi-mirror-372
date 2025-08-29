use crate::common::whitespace_tokenize;
use std::collections::{HashMap, HashSet};

fn align_matches(candidate: &[&str], reference: &[&str]) -> (usize, usize) {
    // Return (matches, chunks)
    let mut ref_indices: HashMap<&str, Vec<usize>> = HashMap::new();
    for (j, tok) in reference.iter().enumerate() {
        ref_indices.entry(tok).or_default().push(j);
    }

    // Greedy left-to-right matching to earliest available ref index
    let mut used: HashSet<usize> = HashSet::new();
    let mut aligned: Vec<usize> = Vec::new();

    for tok in candidate.iter() {
        if let Some(list) = ref_indices.get_mut(tok) {
            if let Some(&idx) = list.iter().find(|&&k| !used.contains(&k)) {
                used.insert(idx);
                aligned.push(idx);
            }
        }
    }

    if aligned.is_empty() {
        return (0, 0);
    }

    aligned.sort_unstable();
    let matches = aligned.len();
    let mut chunks = 1usize;
    for w in aligned.windows(2) {
        if w[1] != w[0] + 1 { chunks += 1; }
    }
    (matches, chunks)
}

pub fn meteor_lite(candidate: &str, references: &[String], alpha: f64, beta: f64, gamma: f64) -> f64 {
    let cand_tokens = whitespace_tokenize(candidate);
    let mut best: f64 = 0.0;
    for r in references {
        let ref_tokens = whitespace_tokenize(r);
        if cand_tokens.is_empty() && ref_tokens.is_empty() { best = best.max(1.0); continue; }
        if cand_tokens.is_empty() || ref_tokens.is_empty() { best = best.max(0.0); continue; }

        let (m, ch) = align_matches(&cand_tokens, &ref_tokens);
        if m == 0 { best = best.max(0.0); continue; }
        let p = m as f64 / cand_tokens.len() as f64;
        let rr = m as f64 / ref_tokens.len() as f64;
        // Fmean: (P*R)/((1-alpha)*P + alpha*R)
        let denom = (1.0 - alpha) * p + alpha * rr;
        let fmean = if denom == 0.0 { 0.0 } else { (p * rr) / denom };
        let penalty = gamma * ((ch as f64 / m as f64).powf(beta));
        let score = (1.0 - penalty) * fmean;
        if score > best { best = score; }
    }
    best
} 