use crate::common::whitespace_tokenize;

fn levenshtein(a: &[&str], b: &[&str]) -> usize {
    let n = a.len();
    let m = b.len();
    if n == 0 { return m; }
    if m == 0 { return n; }
    let mut prev: Vec<usize> = (0..=m).collect();
    let mut curr: Vec<usize> = vec![0; m + 1];
    for i in 1..=n {
        curr[0] = i;
        for j in 1..=m {
            let cost = if a[i - 1] == b[j - 1] { 0 } else { 1 };
            curr[j] = std::cmp::min(
                std::cmp::min(curr[j - 1] + 1, prev[j] + 1),
                prev[j - 1] + cost,
            );
        }
        std::mem::swap(&mut prev, &mut curr);
    }
    prev[m]
}

pub fn wer(candidate: &str, references: &[String]) -> f64 {
    let cand_tokens = whitespace_tokenize(candidate);
    let mut best = 1.0;
    for r in references {
        let ref_tokens = whitespace_tokenize(r);
        let dist = levenshtein(&cand_tokens, &ref_tokens);
        let denom = ref_tokens.len().max(1) as f64;
        let score = dist as f64 / denom;
        if score < best { best = score; }
    }
    best
} 