use std::collections::HashMap;

fn char_ngrams(text: &str, n: usize) -> HashMap<Vec<char>, usize> {
    let chars: Vec<char> = text.chars().collect();
    let mut counts: HashMap<Vec<char>, usize> = HashMap::new();
    if n == 0 || chars.len() < n { return counts; }
    for window in chars.windows(n) {
        let key: Vec<char> = window.to_vec();
        *counts.entry(key).or_insert(0) += 1;
    }
    counts
}

fn chrf_single(candidate: &str, reference: &str, max_n: usize, beta: f64) -> f64 {
    let mut precisions: Vec<f64> = Vec::with_capacity(max_n);
    let mut recalls: Vec<f64> = Vec::with_capacity(max_n);

    for n in 1..=max_n {
        let cand_counts = char_ngrams(candidate, n);
        let ref_counts = char_ngrams(reference, n);

        let mut overlap: usize = 0;
        let mut cand_total: usize = 0;
        let mut ref_total: usize = 0;

        for count in cand_counts.values() { cand_total += *count; }
        for count in ref_counts.values() { ref_total += *count; }

        for (ng, c_count) in cand_counts.iter() {
            if let Some(r_count) = ref_counts.get(ng) {
                overlap += std::cmp::min(*c_count, *r_count);
            }
        }

        let p = if cand_total == 0 { 0.0 } else { overlap as f64 / cand_total as f64 };
        let r = if ref_total == 0 { 0.0 } else { overlap as f64 / ref_total as f64 };
        precisions.push(p);
        recalls.push(r);
    }

    let p_avg = if precisions.is_empty() { 0.0 } else { precisions.iter().sum::<f64>() / precisions.len() as f64 };
    let r_avg = if recalls.is_empty() { 0.0 } else { recalls.iter().sum::<f64>() / recalls.len() as f64 };

    if p_avg == 0.0 && r_avg == 0.0 { return 0.0; }
    let beta_sq = beta * beta;
    (1.0 + beta_sq) * p_avg * r_avg / (beta_sq * p_avg + r_avg)
}

pub fn chrf(candidate: &str, references: &[String], max_n: usize, beta: f64) -> f64 {
    let mut best = 0.0;
    for reference in references {
        let score = chrf_single(candidate, reference, max_n, beta);
        if score > best { best = score; }
    }
    best
} 