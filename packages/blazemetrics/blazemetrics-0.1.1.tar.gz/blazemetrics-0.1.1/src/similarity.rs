use std::collections::HashSet;
use crate::common::whitespace_tokenize;

fn token_f1_pair(candidate: &str, reference: &str) -> f64 {
    let cand_tokens = whitespace_tokenize(candidate);
    let ref_tokens = whitespace_tokenize(reference);

    if cand_tokens.is_empty() && ref_tokens.is_empty() { return 1.0; }
    if cand_tokens.is_empty() || ref_tokens.is_empty() { return 0.0; }

    // Use multiset via counts
    use std::collections::HashMap;
    let mut cand_counts: HashMap<&str, usize> = HashMap::new();
    let mut ref_counts: HashMap<&str, usize> = HashMap::new();
    for t in cand_tokens { *cand_counts.entry(t).or_insert(0) += 1; }
    for t in ref_tokens { *ref_counts.entry(t).or_insert(0) += 1; }

    let mut overlap: usize = 0;
    let mut cand_total: usize = 0;
    let mut ref_total: usize = 0;

    for (t, c) in cand_counts.iter() {
        cand_total += *c;
        if let Some(r) = ref_counts.get(t) { overlap += std::cmp::min(*c, *r); }
    }
    for c in ref_counts.values() { ref_total += *c; }

    let precision = if cand_total == 0 { 0.0 } else { overlap as f64 / cand_total as f64 };
    let recall = if ref_total == 0 { 0.0 } else { overlap as f64 / ref_total as f64 };
    if precision + recall == 0.0 { 0.0 } else { 2.0 * precision * recall / (precision + recall) }
}

pub fn token_f1_best(candidate: &str, references: &[String]) -> f64 {
    let mut best = 0.0;
    for r in references {
        let s = token_f1_pair(candidate, r);
        if s > best { best = s; }
    }
    best
}

fn jaccard_pair(candidate: &str, reference: &str) -> f64 {
    let cset: HashSet<&str> = whitespace_tokenize(candidate).into_iter().collect();
    let rset: HashSet<&str> = whitespace_tokenize(reference).into_iter().collect();
    if cset.is_empty() && rset.is_empty() { return 1.0; }
    if cset.is_empty() || rset.is_empty() { return 0.0; }
    let intersection = cset.intersection(&rset).count() as f64;
    let union = (cset.len() + rset.len()) as f64 - intersection;
    if union == 0.0 { 0.0 } else { intersection / union }
}

pub fn jaccard_best(candidate: &str, references: &[String]) -> f64 {
    let mut best = 0.0;
    for r in references {
        let s = jaccard_pair(candidate, r);
        if s > best { best = s; }
    }
    best
} 