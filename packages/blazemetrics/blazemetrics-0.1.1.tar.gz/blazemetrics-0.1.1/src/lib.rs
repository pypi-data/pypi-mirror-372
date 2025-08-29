use pyo3::prelude::*;
use numpy::PyReadonlyArray2;
use ndarray::{Axis, Array2, ArrayView2};
use rayon::prelude::*;

mod common;
mod rouge;
mod bleu;
mod chrf;
mod similarity;
mod wer;
mod meteor_metric;
mod moverscore;
mod guardrails;

// Wrapper for ROUGE scores
#[pyfunction]
fn rouge_score(
    py: Python,
    candidates: Vec<String>,
    references: Vec<Vec<String>>,
    score_type: &str,
    n: Option<usize>,
) -> PyResult<Vec<(f64, f64, f64)>> {
    let result = py.allow_threads(|| {
        match score_type {
            "rouge_n" => {
                let n_val = n.unwrap_or(1);
                common::parallel_process(&candidates, &references, |c, r| rouge::rouge_n(c, r, n_val))
            }
            "rouge_l" => {
                common::parallel_process(&candidates, &references, rouge::rouge_l)
            }
            _ => panic!("Invalid ROUGE type. Use 'rouge_n' or 'rouge_l'."),
        }
    });
    Ok(result)
}

// Wrapper for BLEU score
#[pyfunction(name = "bleu")]
fn bleu_score_py(
    py: Python,
    candidates: Vec<String>,
    references: Vec<Vec<String>>,
    max_n: Option<usize>,
) -> PyResult<Vec<f64>> {
    let n = max_n.unwrap_or(4);
    let result = py.allow_threads(|| {
        common::parallel_process(&candidates, &references, |c, r| bleu::bleu_score(c, r, n))
    });
    Ok(result)
}

// chrF metric
#[pyfunction]
fn chrf_score(
    py: Python,
    candidates: Vec<String>,
    references: Vec<Vec<String>>,
    max_n: Option<usize>,
    beta: Option<f64>,
) -> PyResult<Vec<f64>> {
    let n = max_n.unwrap_or(6);
    let b = beta.unwrap_or(2.0);
    let result = py.allow_threads(|| {
        common::parallel_process(&candidates, &references, |c, r| chrf::chrf(c, r, n, b))
    });
    Ok(result)
}

// Token-level F1
#[pyfunction]
fn token_f1(
    py: Python,
    candidates: Vec<String>,
    references: Vec<Vec<String>>,
) -> PyResult<Vec<f64>> {
    let result = py.allow_threads(|| {
        common::parallel_process(&candidates, &references, |c, r| similarity::token_f1_best(c, r))
    });
    Ok(result)
}

// Jaccard similarity over tokens
#[pyfunction]
fn jaccard(
    py: Python,
    candidates: Vec<String>,
    references: Vec<Vec<String>>,
) -> PyResult<Vec<f64>> {
    let result = py.allow_threads(|| {
        common::parallel_process(&candidates, &references, |c, r| similarity::jaccard_best(c, r))
    });
    Ok(result)
}

// Highly optimized BERTScore similarity calculation (synchronous)
#[pyfunction]
fn bert_score_similarity(
    _py: Python,
    candidates: PyReadonlyArray2<'_, f32>,
    references: PyReadonlyArray2<'_, f32>,
) -> PyResult<(f32, f32, f32)> {
    let cands_view = candidates.as_array();
    let refs_view = references.as_array();

    // Normalize embeddings
    let cands_norm = normalize_embeddings(cands_view);
    let refs_norm = normalize_embeddings(refs_view);

    // Cosine similarity via matrix multiplication
    let similarity_matrix = cands_norm.dot(&refs_norm.t());

    // Get max similarity for each token
    let precision_scores: Vec<f32> = similarity_matrix
        .axis_iter(Axis(0))
        .into_par_iter()
        .map(|row| row.fold(f32::NEG_INFINITY, |a, &b| a.max(b)))
        .collect();
    
    let recall_scores: Vec<f32> = similarity_matrix
        .axis_iter(Axis(1))
        .into_par_iter()
        .map(|col| col.fold(f32::NEG_INFINITY, |a, &b| a.max(b)))
        .collect();

    let p_mean = if precision_scores.is_empty() { 0.0 } else { precision_scores.iter().sum::<f32>() / precision_scores.len() as f32 };
    let r_mean = if recall_scores.is_empty() { 0.0 } else { recall_scores.iter().sum::<f32>() / recall_scores.len() as f32 };
    let f1 = if p_mean + r_mean == 0.0 { 0.0 } else { 2.0 * p_mean * r_mean / (p_mean + r_mean) };

    Ok((p_mean, r_mean, f1))
}

// MoverScore (greedy variant)
#[pyfunction]
fn moverscore_greedy_py(
    _py: Python,
    candidates: PyReadonlyArray2<'_, f32>,
    references: PyReadonlyArray2<'_, f32>,
) -> PyResult<(f32, f32, f32)> {
    let c = candidates.as_array();
    let r = references.as_array();
    Ok(moverscore::moverscore_greedy(c, r))
}

// METEOR-lite
#[pyfunction(name = "meteor")]
fn meteor_score(
    py: Python,
    candidates: Vec<String>,
    references: Vec<Vec<String>>,
    alpha: Option<f64>,
    beta: Option<f64>,
    gamma: Option<f64>,
) -> PyResult<Vec<f64>> {
    let a = alpha.unwrap_or(0.9);
    let b = beta.unwrap_or(3.0);
    let g = gamma.unwrap_or(0.5);
    let result = py.allow_threads(|| {
        common::parallel_process(&candidates, &references, |c, r| meteor_metric::meteor_lite(c, r, a, b, g))
    });
    Ok(result)
}

// WER
#[pyfunction(name = "wer")]
fn wer_score(
    py: Python,
    candidates: Vec<String>,
    references: Vec<Vec<String>>,
) -> PyResult<Vec<f64>> {
    let result = py.allow_threads(|| {
        common::parallel_process(&candidates, &references, |c, r| wer::wer(c, r))
    });
    Ok(result)
}

// Guardrails exposed functions
#[pyfunction]
fn guard_blocklist(
    py: Python,
    texts: Vec<String>,
    patterns: Vec<String>,
    case_insensitive: Option<bool>,
) -> PyResult<Vec<bool>> {
    let ci = case_insensitive.unwrap_or(true);
    let result = py.allow_threads(|| {
        let cfg = guardrails::BlocklistConfig { patterns, case_insensitive: ci };
        guardrails::blocklist_any(&texts, &cfg)
    });
    Ok(result)
}

#[pyfunction]
fn guard_regex(
    py: Python,
    texts: Vec<String>,
    patterns: Vec<String>,
    case_insensitive: Option<bool>,
) -> PyResult<Vec<bool>> {
    let ci = case_insensitive.unwrap_or(true);
    let result = py.allow_threads(|| {
        let cfg = guardrails::RegexConfig { patterns, case_insensitive: ci };
        guardrails::regex_any(&texts, &cfg)
    });
    Ok(result)
}

#[pyfunction]
fn guard_pii_redact(py: Python, texts: Vec<String>) -> PyResult<Vec<String>> {
    let result = py.allow_threads(|| guardrails::pii_redact(&texts));
    Ok(result)
}

#[pyfunction]
fn guard_safety_score(py: Python, texts: Vec<String>) -> PyResult<Vec<f32>> {
    let result = py.allow_threads(|| guardrails::safety_score_quick(&texts));
    Ok(result)
}

// New LLM-specific guardrails
#[pyfunction]
fn guard_json_validate(
    py: Python,
    texts: Vec<String>,
    schema_json: String,
) -> PyResult<(Vec<bool>, Vec<String>)> {
    let result = py.allow_threads(|| guardrails::json_validate(&texts, &schema_json));
    Ok(result)
}

#[pyfunction]
fn guard_detect_injection_spoof(py: Python, texts: Vec<String>) -> PyResult<Vec<bool>> {
    let result = py.allow_threads(|| guardrails::detect_injection_spoof(&texts));
    Ok(result)
}

#[pyfunction]
fn guard_max_cosine_similarity(
    _py: Python,
    candidates: PyReadonlyArray2<'_, f32>,
    exemplars: PyReadonlyArray2<'_, f32>,
) -> PyResult<Vec<f32>> {
    let c: Vec<Vec<f32>> = candidates.as_array().rows().into_iter().map(|r| r.to_vec()).collect();
    let e: Vec<Vec<f32>> = exemplars.as_array().rows().into_iter().map(|r| r.to_vec()).collect();
    Ok(guardrails::max_cosine_similarity(&c, &e))
}

// Helper for normalizing embeddings
fn normalize_embeddings(embeddings: ArrayView2<f32>) -> Array2<f32> {
    let mut normalized_embeddings = embeddings.to_owned();
    normalized_embeddings
        .axis_iter_mut(Axis(0))
        .into_par_iter()
        .for_each(|mut row| {
            let norm = row.dot(&row).sqrt();
            if norm > 1e-9 {
                row /= norm;
            }
        });
    normalized_embeddings
}


#[pymodule]
fn blazemetrics(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rouge_score, m)?)?;
    m.add_function(wrap_pyfunction!(bleu_score_py, m)?)?;
    m.add_function(wrap_pyfunction!(chrf_score, m)?)?;
    m.add_function(wrap_pyfunction!(token_f1, m)?)?;
    m.add_function(wrap_pyfunction!(jaccard, m)?)?;
    m.add_function(wrap_pyfunction!(bert_score_similarity, m)?)?;
    m.add_function(wrap_pyfunction!(moverscore_greedy_py, m)?)?;
    m.add_function(wrap_pyfunction!(meteor_score, m)?)?;
    m.add_function(wrap_pyfunction!(wer_score, m)?)?;
    // Guardrails
    m.add_function(wrap_pyfunction!(guard_blocklist, m)?)?;
    m.add_function(wrap_pyfunction!(guard_regex, m)?)?;
    m.add_function(wrap_pyfunction!(guard_pii_redact, m)?)?;
    m.add_function(wrap_pyfunction!(guard_safety_score, m)?)?;
    m.add_function(wrap_pyfunction!(guard_json_validate, m)?)?;
    m.add_function(wrap_pyfunction!(guard_detect_injection_spoof, m)?)?;
    m.add_function(wrap_pyfunction!(guard_max_cosine_similarity, m)?)?;
    Ok(())
}