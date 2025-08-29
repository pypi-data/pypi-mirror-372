use std::collections::HashMap;
use rayon::prelude::*;
use once_cell::sync::Lazy;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};

static PARALLEL_ENABLED: Lazy<AtomicBool> = Lazy::new(|| {
    let env = std::env::var("BLAZEMETRICS_PARALLEL").unwrap_or_else(|_| "1".to_string());
    let val = env != "0";
    AtomicBool::new(val)
});

static PARALLEL_SMALL_THRESHOLD: Lazy<AtomicUsize> = Lazy::new(|| {
    let env = std::env::var("BLAZEMETRICS_PAR_THRESHOLD").ok().and_then(|s| s.parse::<usize>().ok()).unwrap_or(512);
    AtomicUsize::new(env)
});

#[inline]
pub fn is_parallel_enabled() -> bool {
    PARALLEL_ENABLED.load(Ordering::Relaxed)
}

#[inline]
pub fn small_threshold() -> usize {
    PARALLEL_SMALL_THRESHOLD.load(Ordering::Relaxed)
}

pub fn set_parallel_enabled(enabled: bool) {
    PARALLEL_ENABLED.store(enabled, Ordering::Relaxed);
}

pub fn set_parallel_threshold(threshold: usize) {
    PARALLEL_SMALL_THRESHOLD.store(threshold, Ordering::Relaxed);
}

// Generate n-grams from a sequence of string tokens using owned Vec<String> keys.
pub fn get_str_ngrams(n: usize, tokens: &[&str]) -> HashMap<Vec<String>, usize> {
    let mut ngrams: HashMap<Vec<String>, usize> = HashMap::new();
    for window in tokens.windows(n) {
        let key: Vec<String> = window.iter().map(|s| (*s).to_string()).collect();
        *ngrams.entry(key).or_insert(0) += 1;
    }
    ngrams
}

// A simple whitespace tokenizer.
pub fn whitespace_tokenize(text: &str) -> Vec<&str> {
    text.split_whitespace().collect()
}

// Process batches using optional parallelism based on global flags and threshold.
pub fn parallel_process<U, F>(
    candidates: &[String],
    references: &[Vec<String>],
    metric_fn: F,
) -> Vec<U>
where
    U: Send,
    F: Fn(&str, &[String]) -> U + Sync,
{
    let use_par = is_parallel_enabled() && candidates.len() >= small_threshold();
    if use_par {
        candidates
            .par_iter()
            .zip(references.par_iter())
            .map(|(candidate, refs)| metric_fn(candidate, refs))
            .collect()
    } else {
        candidates
            .iter()
            .zip(references.iter())
            .map(|(candidate, refs)| metric_fn(candidate, refs))
            .collect()
    }
}