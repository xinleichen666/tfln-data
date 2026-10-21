#!/usr/bin/env python3
"""
qkernel_budget · Bot A
Classical numerical sim: block-fidelity kernel vs baselines under
partition mismatch and label flips.

Fixed seeds. Classical closed-form kernels only — no statevector.
Re-runnable from empty data/: writes data/summary.json and paper/fig/*.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC, LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score
from sklearn.metrics.pairwise import rbf_kernel, laplacian_kernel, polynomial_kernel

# ---------------------------------------------------------------------------
# Paths & seeds
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "paper" / "fig"

SEEDS = {
    "master": 20261013,
    "data_order3_bal": 101,
    "data_order3_unbal": 102,
    "data_order4_bal": 103,
    "data_order4_unbal": 104,
    "split": 777,
    "svm": 42,
}

N_TRAIN = 400
N_TEST = 200
N_TOTAL = N_TRAIN + N_TEST
FLIP_RATES = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
# mismatch: number of feature indices shifted when forming wrong blocks
MISMATCH_SHIFTS = [0, 1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
# Thin-slab data: NN geometry uninformative; labels from block products
# ---------------------------------------------------------------------------
def _block_products(X: np.ndarray, blocks: List[slice]) -> np.ndarray:
    """φ_b = ∏_{j∈b} tanh(x_j)  → shape (n, n_blocks)."""
    cols = []
    for sl in blocks:
        cols.append(np.prod(np.tanh(X[:, sl]), axis=1, keepdims=True))
    return np.hstack(cols)


def make_blocks(n_features: int, order: int) -> List[slice]:
    assert n_features % order == 0
    return [slice(i, i + order) for i in range(0, n_features, order)]


def wrong_blocks(n_features: int, order: int, shift: int) -> List[slice]:
    """Cyclically shift feature indices, then cut consecutive blocks of `order`."""
    idx = np.arange(n_features)
    idx = np.roll(idx, shift)
    # Rebuild blocks on rolled order: features reordered then sliced
    # Equivalent: blocks on original coords with shifted starts
    starts = [(s + shift) % n_features for s in range(0, n_features, order)]
    # For non-wrapping consecutive blocks after roll, use reordered matrix approach
    # We return slices on ORIGINAL indices via roll-map — handled in kernel by permute
    return starts  # special: list of starts; see permute helper


def apply_shift_permute(X: np.ndarray, shift: int) -> np.ndarray:
    """Permute columns so consecutive blocks on permuted X = shifted partition."""
    return np.roll(X, shift, axis=1)


def synthesize_thin_slab(
    n_samples: int,
    order: int,
    n_blocks: int,
    seed: int,
    balanced: bool,
) -> Tuple[np.ndarray, np.ndarray, List[slice], Dict]:
    """
    Thin-slab construction:
    - Coordinates ~ N(0,1) then lightly clipped; Euclidean NN distances similar across classes.
    - Label from sparse high-order block products: y = sign(φ_0 * φ_1) for order>=3
      (two-block sparse product); if unbalanced, threshold on a continuous score.
    """
    rng = np.random.default_rng(seed)
    n_features = order * n_blocks
    blocks = make_blocks(n_features, order)

    # Isotropic slab: all coords similar scale → metric kernels see little class geometry
    X = rng.normal(0.0, 1.0, size=(n_samples, n_features))
    # Soft clip to keep products from exploding
    X = np.clip(X, -2.5, 2.5)

    phi = _block_products(X, blocks)  # (n, n_blocks)
    # Sparse: use product of first two block features (high-order interaction)
    score = phi[:, 0] * phi[:, 1]
    if n_blocks >= 3:
        # add weak third block contribution (still sparse)
        score = score + 0.15 * phi[:, 2]

    if balanced:
        y = (score >= 0).astype(int)
        # Force exact balance by flipping nearest-to-threshold points if needed
        n_pos = int(y.sum())
        target = n_samples // 2
        if n_pos > target:
            pos_idx = np.where(y == 1)[0]
            order_idx = pos_idx[np.argsort(np.abs(score[pos_idx]))]
            y[order_idx[: n_pos - target]] = 0
        elif n_pos < target:
            neg_idx = np.where(y == 0)[0]
            order_idx = neg_idx[np.argsort(np.abs(score[neg_idx]))]
            y[order_idx[: target - n_pos]] = 1
    else:
        # Unbalanced ~70/30 via percentile threshold
        thr = np.percentile(score, 30)
        y = (score >= thr).astype(int)

    meta = {
        "n_features": n_features,
        "order": order,
        "n_blocks": n_blocks,
        "balanced": balanced,
        "seed": seed,
        "pos_frac": float(y.mean()),
        "label_rule": "sign/threshold of sparse block-product score φ0*φ1(+0.15φ2)",
    }
    return X, y, blocks, meta


def nn_distance_stats(X: np.ndarray, y: np.ndarray) -> Dict:
    """Diagnose thin-slab: mean NN distance within vs across class (train subset)."""
    from sklearn.neighbors import NearestNeighbors

    n = min(len(X), 300)
    Xs, ys = X[:n], y[:n]
    nn = NearestNeighbors(n_neighbors=2).fit(Xs)
    dist, _ = nn.kneighbors(Xs)
    nn1 = dist[:, 1]
    # same-class fraction among NN
    nn_full = NearestNeighbors(n_neighbors=2).fit(Xs)
    _, idx = nn_full.kneighbors(Xs)
    same = (ys[idx[:, 1]] == ys).mean()
    return {
        "mean_nn_dist": float(nn1.mean()),
        "std_nn_dist": float(nn1.std()),
        "nn_same_class_frac": float(same),
    }


# ---------------------------------------------------------------------------
# Kernels (classical closed form)
# ---------------------------------------------------------------------------
def block_fidelity_kernel(X: np.ndarray, Y: np.ndarray, blocks: List[slice]) -> np.ndarray:
    """
    Block-fidelity kernel (classical closed form):
      K(x,y) = ∏_b (1 + φ_b(x) φ_b(y)) / 2
    with φ_b = ∏_{j∈b} tanh(x_j) ∈ (-1,1).
    Interpretable as product of single-qubit fidelities on block-product encodings.
    O(n_blocks * n * m) — NEVER a full Hilbert statevector.
    """
    phi_x = _block_products(X, blocks)
    phi_y = _block_products(Y, blocks)
    # (n, m, b) → product over blocks
    # K_ij = ∏_b (1 + phi_x[i,b] * phi_y[j,b]) / 2
    # Use log-sum for stability then exp — but values in (0,1], product fine for small b
    n, m = X.shape[0], Y.shape[0]
    K = np.ones((n, m), dtype=np.float64)
    for b in range(phi_x.shape[1]):
        K *= 0.5 * (1.0 + np.outer(phi_x[:, b], phi_y[:, b]))
    # Numerical floor
    return np.clip(K, 1e-15, 1.0)


def true_product_features(X: np.ndarray, blocks: List[slice]) -> np.ndarray:
    return _block_products(X, blocks)


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------
def flip_labels(y: np.ndarray, rate: float, seed: int) -> np.ndarray:
    if rate <= 0:
        return y.copy()
    rng = np.random.default_rng(seed)
    y2 = y.copy()
    n_flip = int(round(rate * len(y2)))
    idx = rng.choice(len(y2), size=n_flip, replace=False)
    y2[idx] = 1 - y2[idx]
    return y2


def eval_kernel_svm(
    K_train: np.ndarray,
    K_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> Dict[str, float]:
    clf = SVC(kernel="precomputed", C=1.0, random_state=SEEDS["svm"])
    clf.fit(K_train, y_train)
    pred = clf.predict(K_test)
    return {
        "accuracy": float(accuracy_score(y_test, pred)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
    }


def eval_linear_on_features(
    Xtr: np.ndarray, Xte: np.ndarray, ytr: np.ndarray, yte: np.ndarray
) -> Dict[str, float]:
    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                LinearSVC(
                    C=1.0,
                    max_iter=10000,
                    dual="auto",
                    random_state=SEEDS["svm"],
                ),
            ),
        ]
    )
    pipe.fit(Xtr, ytr)
    pred = pipe.predict(Xte)
    return {
        "accuracy": float(accuracy_score(yte, pred)),
        "f1": float(f1_score(yte, pred, zero_division=0)),
    }


def eval_sklearn_kernel(
    name: str,
    Xtr: np.ndarray,
    Xte: np.ndarray,
    ytr: np.ndarray,
    yte: np.ndarray,
) -> Dict[str, float]:
    if name == "rbf":
        # median heuristic on train pairwise distances
        from sklearn.metrics.pairwise import euclidean_distances

        D = euclidean_distances(Xtr)
        tri = D[np.triu_indices_from(D, k=1)]
        gamma = 1.0 / (np.median(tri) ** 2 + 1e-12)
        Ktr = rbf_kernel(Xtr, Xtr, gamma=gamma)
        Kte = rbf_kernel(Xte, Xtr, gamma=gamma)
    elif name == "laplacian":
        from sklearn.metrics.pairwise import euclidean_distances

        D = euclidean_distances(Xtr, squared=False)
        tri = D[np.triu_indices_from(D, k=1)]
        gamma = 1.0 / (np.median(tri) + 1e-12)
        Ktr = laplacian_kernel(Xtr, Xtr, gamma=gamma)
        Kte = laplacian_kernel(Xte, Xtr, gamma=gamma)
    elif name == "poly":
        Ktr = polynomial_kernel(Xtr, Xtr, degree=3, gamma=1.0, coef0=1.0)
        Kte = polynomial_kernel(Xte, Xtr, degree=3, gamma=1.0, coef0=1.0)
    elif name == "linear":
        Ktr = Xtr @ Xtr.T
        Kte = Xte @ Xtr.T
    else:
        raise ValueError(name)
    return eval_kernel_svm(Ktr, Kte, ytr, yte)


def find_zero_cross(xs: List[float], ys: List[float]) -> Dict:
    """First place gap crosses or touches ≤0. If never, 本扫范围内未消失."""
    for i in range(len(ys)):
        if ys[i] <= 0:
            return {
                "vanished_in_sweep": True,
                "cross_x": float(xs[i]),
                "cross_index": i,
                "note": f"gap≤0 first at x={xs[i]}",
            }
        if i > 0 and ys[i - 1] > 0 and ys[i] < 0:
            # linear interpolate
            t = ys[i - 1] / (ys[i - 1] - ys[i])
            xc = xs[i - 1] + t * (xs[i] - xs[i - 1])
            return {
                "vanished_in_sweep": True,
                "cross_x": float(xc),
                "cross_index": i,
                "note": f"gap crossed 0 between {xs[i-1]} and {xs[i]}",
            }
    return {
        "vanished_in_sweep": False,
        "cross_x": None,
        "cross_index": None,
        "note": "本扫范围内未消失",
    }


# ---------------------------------------------------------------------------
# One dataset suite
# ---------------------------------------------------------------------------
def run_suite(
    tag: str,
    order: int,
    n_blocks: int,
    balanced: bool,
    data_seed: int,
) -> Dict:
    X, y, true_blocks, meta = synthesize_thin_slab(
        N_TOTAL, order, n_blocks, data_seed, balanced
    )
    nn_stats = nn_distance_stats(X, y)

    Xtr, Xte, ytr, yte = train_test_split(
        X,
        y,
        train_size=N_TRAIN,
        test_size=N_TEST,
        random_state=SEEDS["split"],
        stratify=y,
    )

    # --- Aligned evaluation ---
    aligned = {}
    Ktr_bf = block_fidelity_kernel(Xtr, Xtr, true_blocks)
    Kte_bf = block_fidelity_kernel(Xte, Xtr, true_blocks)
    aligned["block_fidelity"] = eval_kernel_svm(Ktr_bf, Kte_bf, ytr, yte)

    for name in ["linear", "rbf", "laplacian", "poly"]:
        aligned[name] = eval_sklearn_kernel(name, Xtr, Xte, ytr, yte)

    phi_tr = true_product_features(Xtr, true_blocks)
    phi_te = true_product_features(Xte, true_blocks)
    aligned["true_product_linear"] = eval_linear_on_features(phi_tr, phi_te, ytr, yte)

    # Gaps at alignment
    gaps_aligned = {
        "bf_minus_rbf_acc": aligned["block_fidelity"]["accuracy"]
        - aligned["rbf"]["accuracy"],
        "bf_minus_rbf_f1": aligned["block_fidelity"]["f1"] - aligned["rbf"]["f1"],
        "bf_minus_tpl_acc": aligned["block_fidelity"]["accuracy"]
        - aligned["true_product_linear"]["accuracy"],
        "bf_minus_tpl_f1": aligned["block_fidelity"]["f1"]
        - aligned["true_product_linear"]["f1"],
    }

    # --- Mismatch sweep (wrong partition via column roll) ---
    mismatch_rows = []
    for shift in MISMATCH_SHIFTS:
        blocks_m = make_blocks(order * n_blocks, order)  # same sizes
        # Wrong partition = consecutive blocks after rolling features
        Xtr_m = apply_shift_permute(Xtr, shift)
        Xte_m = apply_shift_permute(Xte, shift)
        # When shift=0, identical to true; when shift≠0, blocks cut wrong boundaries
        Ktr = block_fidelity_kernel(Xtr_m, Xtr_m, blocks_m)
        Kte = block_fidelity_kernel(Xte_m, Xtr_m, blocks_m)
        m_bf = eval_kernel_svm(Ktr, Kte, ytr, yte)
        # Baselines unchanged (feature geometry same; roll is isometric for metric kernels
        # but we re-eval RBF on rolled for fairness — actually roll is permutation of coords,
        # Euclidean invariant. Use aligned RBF/TPL numbers for gap vs those baselines.
        mismatch_rows.append(
            {
                "shift": shift,
                "block_fidelity": m_bf,
                "gap_vs_rbf_acc": m_bf["accuracy"] - aligned["rbf"]["accuracy"],
                "gap_vs_rbf_f1": m_bf["f1"] - aligned["rbf"]["f1"],
                "gap_vs_tpl_acc": m_bf["accuracy"]
                - aligned["true_product_linear"]["accuracy"],
                "gap_vs_tpl_f1": m_bf["f1"]
                - aligned["true_product_linear"]["f1"],
            }
        )

    vanish_mismatch_rbf = find_zero_cross(
        [r["shift"] for r in mismatch_rows],
        [r["gap_vs_rbf_acc"] for r in mismatch_rows],
    )
    vanish_mismatch_tpl = find_zero_cross(
        [r["shift"] for r in mismatch_rows],
        [r["gap_vs_tpl_acc"] for r in mismatch_rows],
    )

    # --- Label flip sweep (aligned blocks, flip train labels only) ---
    flip_rows = []
    for rate in FLIP_RATES:
        ytr_f = flip_labels(ytr, rate, seed=SEEDS["master"] + int(1000 * rate))
        Ktr = block_fidelity_kernel(Xtr, Xtr, true_blocks)
        Kte = block_fidelity_kernel(Xte, Xtr, true_blocks)
        m_bf = eval_kernel_svm(Ktr, Kte, ytr_f, yte)
        m_rbf = eval_sklearn_kernel("rbf", Xtr, Xte, ytr_f, yte)
        m_tpl = eval_linear_on_features(phi_tr, phi_te, ytr_f, yte)
        flip_rows.append(
            {
                "flip_rate": rate,
                "block_fidelity": m_bf,
                "rbf": m_rbf,
                "true_product_linear": m_tpl,
                "gap_vs_rbf_acc": m_bf["accuracy"] - m_rbf["accuracy"],
                "gap_vs_rbf_f1": m_bf["f1"] - m_rbf["f1"],
                "gap_vs_tpl_acc": m_bf["accuracy"] - m_tpl["accuracy"],
                "gap_vs_tpl_f1": m_bf["f1"] - m_tpl["f1"],
            }
        )

    vanish_flip_rbf = find_zero_cross(
        [r["flip_rate"] for r in flip_rows],
        [r["gap_vs_rbf_acc"] for r in flip_rows],
    )
    vanish_flip_tpl = find_zero_cross(
        [r["flip_rate"] for r in flip_rows],
        [r["gap_vs_tpl_acc"] for r in flip_rows],
    )

    return {
        "tag": tag,
        "meta": meta,
        "nn_stats": nn_stats,
        "n_train": N_TRAIN,
        "n_test": N_TEST,
        "aligned": aligned,
        "gaps_aligned": gaps_aligned,
        "mismatch_sweep": mismatch_rows,
        "vanish_mismatch_vs_rbf": vanish_mismatch_rbf,
        "vanish_mismatch_vs_tpl": vanish_mismatch_tpl,
        "flip_sweep": flip_rows,
        "vanish_flip_vs_rbf": vanish_flip_rbf,
        "vanish_flip_vs_tpl": vanish_flip_tpl,
    }


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    suites_spec = [
        ("order3_balanced", 3, 4, True, SEEDS["data_order3_bal"]),
        ("order3_unbalanced", 3, 4, False, SEEDS["data_order3_unbal"]),
        ("order4_balanced", 4, 3, True, SEEDS["data_order4_bal"]),
        ("order4_unbalanced", 4, 3, False, SEEDS["data_order4_unbal"]),
    ]

    suites = []
    for tag, order, n_blocks, bal, seed in suites_spec:
        print(f"[run] {tag} ...", flush=True)
        suites.append(run_suite(tag, order, n_blocks, bal, seed))

    # Aggregate headline numbers for easy citation
    headline = {}
    for s in suites:
        t = s["tag"]
        headline[t] = {
            "aligned_bf_accuracy": s["aligned"]["block_fidelity"]["accuracy"],
            "aligned_bf_f1": s["aligned"]["block_fidelity"]["f1"],
            "aligned_rbf_accuracy": s["aligned"]["rbf"]["accuracy"],
            "aligned_rbf_f1": s["aligned"]["rbf"]["f1"],
            "aligned_linear_accuracy": s["aligned"]["linear"]["accuracy"],
            "aligned_laplacian_accuracy": s["aligned"]["laplacian"]["accuracy"],
            "aligned_poly_accuracy": s["aligned"]["poly"]["accuracy"],
            "aligned_tpl_accuracy": s["aligned"]["true_product_linear"]["accuracy"],
            "aligned_tpl_f1": s["aligned"]["true_product_linear"]["f1"],
            "gap_bf_rbf_acc_aligned": s["gaps_aligned"]["bf_minus_rbf_acc"],
            "gap_bf_tpl_acc_aligned": s["gaps_aligned"]["bf_minus_tpl_acc"],
            "vanish_mismatch_vs_rbf": s["vanish_mismatch_vs_rbf"],
            "vanish_mismatch_vs_tpl": s["vanish_mismatch_vs_tpl"],
            "vanish_flip_vs_rbf": s["vanish_flip_vs_rbf"],
            "vanish_flip_vs_tpl": s["vanish_flip_vs_tpl"],
            "pos_frac": s["meta"]["pos_frac"],
            "nn_same_class_frac": s["nn_stats"]["nn_same_class_frac"],
            "mean_nn_dist": s["nn_stats"]["mean_nn_dist"],
        }

    summary = {
        "track": "qkernel_budget",
        "title_frame": "方法·噪声预算",
        "prior_cite": "Peng, Lu, Chen, arXiv:2608.24631",
        "disclaimer": (
            "本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，"
            "Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；"
            "verify/ 第三方 PDF 禁止入库。"
        ),
        "seeds": SEEDS,
        "protocol": {
            "n_train": N_TRAIN,
            "n_test": N_TEST,
            "flip_rates": FLIP_RATES,
            "mismatch_shifts": MISMATCH_SHIFTS,
            "svm_C": 1.0,
            "block_fidelity_formula": "K=∏_b (1+φ_b(x)φ_b(y))/2, φ_b=∏_{j∈b} tanh(x_j)",
            "no_statevector": True,
            "no_ibm": True,
            "no_fraud_benchmark": True,
        },
        "suites": suites,
        "headline": headline,
    }

    out = DATA_DIR / "summary.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"[write] {out}", flush=True)

    # checksum for STATUS
    h = hashlib.sha256(out.read_bytes()).hexdigest()[:16]
    print(f"[sha256_16] {h}", flush=True)
    return summary


if __name__ == "__main__":
    main()
