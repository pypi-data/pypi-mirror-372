use rayon::prelude::*;
use regex::{Regex, RegexBuilder};
use aho_corasick::{AhoCorasick, AhoCorasickBuilder};
use serde_json::Value as JsonValue;
use jsonschema::{JSONSchema};
use unicode_normalization::UnicodeNormalization;
use once_cell::sync::Lazy;
use std::sync::{Mutex, Arc};
use std::collections::HashMap;

#[derive(Clone)]
pub struct BlocklistConfig {
    pub patterns: Vec<String>,
    pub case_insensitive: bool,
}

static EMAIL_RE: Lazy<regex::Regex> = Lazy::new(|| {
    RegexBuilder::new(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        .build()
        .unwrap()
});

static PHONE_RE: Lazy<regex::Regex> = Lazy::new(|| {
    RegexBuilder::new(r"(?x)
        (?:\+?\d{1,3}[\s-]?)?      # country
        (?:\(?\d{3}\)?[\s-]?)     # area
        \d{3}[\s-]?\d{4}           # local
    ")
    .build()
    .unwrap()
});

static CREDIT_RE: Lazy<regex::Regex> = Lazy::new(|| {
    RegexBuilder::new(r"\b(?:\d[ -]*?){13,19}\b").build().unwrap()
});

static SSN_RE: Lazy<regex::Regex> = Lazy::new(|| {
    RegexBuilder::new(r"\b\d{3}-\d{2}-\d{4}\b").build().unwrap()
});

// Caches for automata/regex vectors keyed by patterns + flags
static BLOCKLIST_CACHE: Lazy<Mutex<HashMap<String, Arc<AhoCorasick>>>> = Lazy::new(|| Mutex::new(HashMap::new()));
static REGEX_CACHE: Lazy<Mutex<HashMap<String, Arc<Vec<Regex>>>>> = Lazy::new(|| Mutex::new(HashMap::new()));

fn cache_key(patterns: &[String], ci: bool) -> String {
    let mut pats = patterns.to_vec();
    pats.sort();
    format!("ci={};{}", ci, pats.join("|"))
}

fn get_blocklist_ac(patterns: &[String], ci: bool) -> Arc<AhoCorasick> {
    let key = cache_key(patterns, ci);
    if let Some(ac) = BLOCKLIST_CACHE.lock().ok().and_then(|m| m.get(&key).cloned()) {
        return ac;
    }
    let pats = if ci { patterns.iter().map(|p| p.to_lowercase()).collect::<Vec<_>>() } else { patterns.to_vec() };
    let built = AhoCorasickBuilder::new().ascii_case_insensitive(ci).build(pats).expect("failed to build AC");
    let ac = Arc::new(built);
    if let Ok(mut m) = BLOCKLIST_CACHE.lock() { m.insert(key, ac.clone()); }
    ac
}

fn get_regex_vec(patterns: &[String], ci: bool) -> Arc<Vec<Regex>> {
    let key = cache_key(patterns, ci);
    if let Some(v) = REGEX_CACHE.lock().ok().and_then(|m| m.get(&key).cloned()) {
        return v;
    }
    let compiled: Vec<Regex> = patterns.iter().map(|p| {
        RegexBuilder::new(p).case_insensitive(ci).build().expect("invalid regex")
    }).collect();
    let arc = Arc::new(compiled);
    if let Ok(mut m) = REGEX_CACHE.lock() { m.insert(key, arc.clone()); }
    arc
}

#[inline]
fn is_small(n: usize) -> bool { n < 512 }

pub fn blocklist_any(texts: &[String], config: &BlocklistConfig) -> Vec<bool> {
    if config.patterns.is_empty() {
        return vec![false; texts.len()];
    }
    let ac = get_blocklist_ac(&config.patterns, config.case_insensitive);
    if is_small(texts.len()) {
        texts.iter().map(|t| ac.find(t).is_some()).collect()
    } else {
        texts.par_iter().map(|t| ac.find(t).is_some()).collect()
    }
}

#[derive(Clone)]
pub struct RegexConfig {
    pub patterns: Vec<String>,
    pub case_insensitive: bool,
}

pub fn regex_any(texts: &[String], config: &RegexConfig) -> Vec<bool> {
    if config.patterns.is_empty() {
        return vec![false; texts.len()];
    }
    let regexes = get_regex_vec(&config.patterns, config.case_insensitive);
    if is_small(texts.len()) {
        texts.iter().map(|t| regexes.iter().any(|re| re.is_match(t))).collect()
    } else {
        texts.par_iter().map(|t| regexes.iter().any(|re| re.is_match(t))).collect()
    }
}

pub fn pii_redact(texts: &[String]) -> Vec<String> {
    if is_small(texts.len()) {
        texts
            .iter()
            .map(|t| {
                let mut s = EMAIL_RE.replace_all(t, "[REDACTED_EMAIL]").into_owned();
                s = PHONE_RE.replace_all(&s, "[REDACTED_PHONE]").into_owned();
                s = CREDIT_RE.replace_all(&s, "[REDACTED_CARD]").into_owned();
                s = SSN_RE.replace_all(&s, "[REDACTED_SSN]").into_owned();
                s
            })
            .collect()
    } else {
        texts
            .par_iter()
            .map(|t| {
                let mut s = EMAIL_RE.replace_all(t, "[REDACTED_EMAIL]").into_owned();
                s = PHONE_RE.replace_all(&s, "[REDACTED_PHONE]").into_owned();
                s = CREDIT_RE.replace_all(&s, "[REDACTED_CARD]").into_owned();
                s = SSN_RE.replace_all(&s, "[REDACTED_SSN]").into_owned();
                s
            })
            .collect()
    }
}

pub fn safety_score_quick(texts: &[String]) -> Vec<f32> {
    let hate = ["slur", "racist", "bigot", "nazi", "kkk"];
    let sexual = ["porn", "sexual", "nude", "xxx", "explicit"];
    let violence = ["kill", "murder", "stab", "bomb", "shoot"];
    let selfharm = ["suicide", "self harm", "kill myself", "cutting", "overdose"];

    let ac_hate = AhoCorasickBuilder::new().ascii_case_insensitive(true).build(&hate).expect("failed to build AC for hate");
    let ac_sex = AhoCorasickBuilder::new().ascii_case_insensitive(true).build(&sexual).expect("failed to build AC for sexual");
    let ac_viol = AhoCorasickBuilder::new().ascii_case_insensitive(true).build(&violence).expect("failed to build AC for violence");
    let ac_sh = AhoCorasickBuilder::new().ascii_case_insensitive(true).build(&selfharm).expect("failed to build AC for self-harm");

    if is_small(texts.len()) {
        texts
            .iter()
            .map(|t| {
                let mut score = 0.0f32;
                if ac_hate.find(t).is_some() { score += 0.4; }
                if ac_sex.find(t).is_some() { score += 0.2; }
                if ac_viol.find(t).is_some() { score += 0.3; }
                if ac_sh.find(t).is_some() { score += 0.6; }
                if score > 1.0 { 1.0 } else { score }
            })
            .collect()
    } else {
        texts
            .par_iter()
            .map(|t| {
                let mut score = 0.0f32;
                if ac_hate.find(t).is_some() { score += 0.4; }
                if ac_sex.find(t).is_some() { score += 0.2; }
                if ac_viol.find(t).is_some() { score += 0.3; }
                if ac_sh.find(t).is_some() { score += 0.6; }
                if score > 1.0 { 1.0 } else { score }
            })
            .collect()
    }
}

// JSON Schema validation and basic repair (best-effort)
pub fn json_validate(texts: &[String], schema_json: &str) -> (Vec<bool>, Vec<String>) {
    let compiled = JSONSchema::compile(&serde_json::from_str::<JsonValue>(schema_json).expect("invalid schema")).expect("schema compile error");
    texts
        .par_iter()
        .map(|t| {
            let normalized = t.nfc().collect::<String>();
            let parsed: Result<JsonValue, _> = serde_json::from_str(&normalized);
            match parsed {
                Ok(v) => {
                    let valid = compiled.is_valid(&v);
                    (valid, normalized)
                }
                Err(_) => {
                    // best-effort repair: wrap as string JSON
                    let repaired = serde_json::to_string(&normalized).unwrap_or_else(|_| "\"\"".to_string());
                    let reparsed: Result<JsonValue, _> = serde_json::from_str(&repaired);
                    let valid = reparsed.as_ref().map(|vv| compiled.is_valid(vv)).unwrap_or(false);
                    (valid, repaired)
                }
            }
        })
        .unzip()
}

// Prompt-injection / jailbreak heuristics and unicode spoofing
pub fn detect_injection_spoof(texts: &[String]) -> Vec<bool> {
    static INDICATORS_AC: Lazy<aho_corasick::AhoCorasick> = Lazy::new(|| {
        let indicators = [
            "ignore previous", "disregard above", "override system", "act as", "jailbreak",
            "developer mode", "no restrictions", "bypass safety", "do anything now",
        ];
        AhoCorasickBuilder::new().ascii_case_insensitive(true).build(&indicators).expect("failed to build AC for indicators")
    });
    if is_small(texts.len()) {
        texts
            .iter()
            .map(|t| {
                let hit = INDICATORS_AC.find(t).is_some();
                let normalized = t.nfc().collect::<String>();
                let spoof = !t.chars().all(|c| c.is_ascii()) && normalized != *t;
                hit || spoof
            })
            .collect()
    } else {
        texts
            .par_iter()
            .map(|t| {
                let hit = INDICATORS_AC.find(t).is_some();
                let normalized = t.nfc().collect::<String>();
                let spoof = !t.chars().all(|c| c.is_ascii()) && normalized != *t;
                hit || spoof
            })
            .collect()
    }
}

// ANN-like: compute max cosine similarity against unsafe exemplars (small sets) in parallel
pub fn max_cosine_similarity(
    candidates: &[Vec<f32>],
    exemplars: &[Vec<f32>],
) -> Vec<f32> {
    if exemplars.is_empty() { return vec![0.0; candidates.len()]; }
    let exemplars_norm: Vec<Vec<f32>> = exemplars
        .iter()
        .map(|v| {
            let mut n = 0.0f32;
            for x in v { n += x * x; }
            let n = n.sqrt().max(1e-9);
            v.iter().map(|x| x / n).collect::<Vec<f32>>()
        })
        .collect();
    candidates
        .par_iter()
        .map(|c| {
            let mut n = 0.0f32;
            for x in c { n += x * x; }
            let n = n.sqrt().max(1e-9);
            let cand: Vec<f32> = c.iter().map(|x| x / n).collect();
            let mut best = -1.0f32;
            for e in &exemplars_norm {
                let mut dot = 0.0f32;
                for (a, b) in cand.iter().zip(e.iter()) { dot += a * b; }
                if dot > best { best = dot; }
            }
            best.max(0.0)
        })
        .collect()
} 