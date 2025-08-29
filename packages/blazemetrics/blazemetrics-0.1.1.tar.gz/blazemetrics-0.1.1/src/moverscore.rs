use ndarray::{ArrayView2, Axis};
use rayon::prelude::*;

fn normalize_rows(mut m: ndarray::Array2<f32>) -> ndarray::Array2<f32> {
    m.axis_iter_mut(Axis(0)).for_each(|mut row| {
        let n = row.dot(&row).sqrt();
        if n > 1e-9 { row /= n; }
    });
    m
}

fn greedy_alignment_f1(sim: &ndarray::Array2<f32>) -> (f32, f32, f32) {
    // precision: for each cand token, best unmatched ref
    let n_c = sim.nrows();
    let n_r = sim.ncols();
    if n_c == 0 || n_r == 0 { return (0.0, 0.0, 0.0); }

    let mut used_r = vec![false; n_r];
    let mut p_sum = 0.0f32;
    for i in 0..n_c {
        let mut best = -1.0f32;
        let mut best_j = None;
        for j in 0..n_r {
            if used_r[j] { continue; }
            let v = sim[(i, j)];
            if v > best { best = v; best_j = Some(j); }
        }
        if let Some(j) = best_j { used_r[j] = true; p_sum += best.max(0.0); }
    }
    let p = p_sum / n_c as f32;

    // recall: for each ref token, best unmatched cand
    let mut used_c = vec![false; n_c];
    let mut r_sum = 0.0f32;
    for j in 0..n_r {
        let mut best = -1.0f32;
        let mut best_i = None;
        for i in 0..n_c {
            if used_c[i] { continue; }
            let v = sim[(i, j)];
            if v > best { best = v; best_i = Some(i); }
        }
        if let Some(i) = best_i { used_c[i] = true; r_sum += best.max(0.0); }
    }
    let r = r_sum / n_r as f32;

    let f1 = if p + r == 0.0 { 0.0 } else { 2.0 * p * r / (p + r) };
    (p, r, f1)
}

pub fn moverscore_greedy(cand: ArrayView2<f32>, refm: ArrayView2<f32>) -> (f32, f32, f32) {
    let c_norm = normalize_rows(cand.to_owned());
    let r_norm = normalize_rows(refm.to_owned());
    let sim = c_norm.dot(&r_norm.t());
    greedy_alignment_f1(&sim)
} 