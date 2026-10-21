#!/usr/bin/env python3
"""Bot C · mmd_coverage — Pauli-Z moment MMD, loss vs unseen-valid coverage.

Classical numerical only. Fixed seeds. Writes data/summary.json.
Prior narrative: Raj, Mathur, Perdomo-Ortiz, arXiv:2608.31117 (cite only; no copy of their numbers).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.special import comb

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "summary.json"

SEEDS = {
    "master": 20261013,
    "target": 301,
    "train_sample": 302,
    "product_init": 303,
    "ising_init": 304,
    "eval_sample": 305,
}

N = 10
K_WEIGHT = 5
N_TRAIN = 48
N_SAMPLE_EVAL = 2000
BETA_TARGET = 1.8
N_STEPS = 120
LR_PRODUCT = 0.35
LR_ISING = 0.08
CHECKPOINT_EVERY = 5
MOMENT_ORDER = 2
# Matched-loss band: relative |L_a-L_b|/mean <= this ⇒ "损失接近"
LOSS_TOL_RATIO = 0.25
# Absolute unseen-coverage gap to call "分开"
COV_GAP_THR = 0.05

DISCLAIMER = (
    "本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，"
    "Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；"
    "verify/ 第三方 PDF 禁止入库。"
)


def all_bitstrings(n: int) -> np.ndarray:
    idx = np.arange(2**n, dtype=np.uint32)
    return ((idx[:, None] >> np.arange(n, dtype=np.uint32)) & 1).astype(np.float64)


def valid_mask(bits: np.ndarray, k: int) -> np.ndarray:
    return bits.sum(axis=1) == k


def pauli_z_features(bits: np.ndarray) -> np.ndarray:
    z = 1.0 - 2.0 * bits
    cols = [z]
    n = bits.shape[1]
    for i in range(n):
        for j in range(i + 1, n):
            cols.append((z[:, i] * z[:, j])[:, None])
    return np.concatenate(cols, axis=1)


def softmax_neg_energy(energy: np.ndarray) -> np.ndarray:
    e = -energy
    e = e - e.max()
    p = np.exp(e)
    return p / p.sum()


def mmd2(mu_a: np.ndarray, mu_b: np.ndarray) -> float:
    d = mu_a - mu_b
    return float(d @ d)


def forward_kl(p: np.ndarray, q: np.ndarray, eps: float = 1e-15) -> float:
    mask = p > eps
    return float(np.sum(p[mask] * (np.log(p[mask] + eps) - np.log(q[mask] + eps))))


def sample_from_probs(probs: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.choice(len(probs), size=n, replace=True, p=probs)


def coverage_from_samples(
    sample_idx: np.ndarray, train_idx_set: set[int], unseen_idx_set: set[int]
) -> dict:
    hit = set(int(i) for i in sample_idx)
    train_hit = hit & train_idx_set
    unseen_hit = hit & unseen_idx_set
    return {
        "train_coverage": len(train_hit) / max(len(train_idx_set), 1),
        "unseen_valid_coverage": len(unseen_hit) / max(len(unseen_idx_set), 1),
        "n_unique_samples": len(hit),
        "n_train_hit": len(train_hit),
        "n_unseen_hit": len(unseen_hit),
    }


def build_target(bits_v: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    w = rng.normal(0.0, 1.0, size=N)
    w[: N // 2] *= 1.4
    score = bits_v @ w
    logits = BETA_TARGET * score
    logits = logits - logits.max()
    p_star = np.exp(logits)
    p_star = p_star / p_star.sum()
    return p_star, w


def product_energy(bits_v: np.ndarray, theta: np.ndarray) -> np.ndarray:
    return -(bits_v @ theta)


def ising_energy(bits_v: np.ndarray, h: np.ndarray, J: np.ndarray) -> np.ndarray:
    linear = bits_v @ h
    quad = np.einsum("mi,ij,mj->m", bits_v, J, bits_v)
    return -(linear + 0.5 * quad)


def pack_J_from_vec(vec: np.ndarray, n: int) -> np.ndarray:
    J = np.zeros((n, n), dtype=np.float64)
    k = 0
    for i in range(n):
        for j in range(i + 1, n):
            J[i, j] = J[j, i] = vec[k]
            k += 1
    return J


def train_model(
    name: str,
    bits_v: np.ndarray,
    feat_v: np.ndarray,
    mu_train: np.ndarray,
    p_star: np.ndarray,
    train_idx_set: set[int],
    unseen_idx_set: set[int],
    init_rng: np.random.Generator,
    eval_rng: np.random.Generator,
    kind: str,
) -> dict:
    n_pair = N * (N - 1) // 2
    if kind == "product":
        theta = init_rng.normal(0.0, 0.15, size=N)
        params_dim = N
        h = jvec = None
    elif kind == "ising":
        h = init_rng.normal(0.0, 0.1, size=N)
        jvec = init_rng.normal(0.0, 0.05, size=n_pair)
        theta = None
        params_dim = N + n_pair
    else:
        raise ValueError(kind)

    history = []
    lr = LR_PRODUCT if kind == "product" else LR_ISING

    def current_q():
        if kind == "product":
            E = product_energy(bits_v, theta)
        else:
            J = pack_J_from_vec(jvec, N)
            E = ising_energy(bits_v, h, J)
        return softmax_neg_energy(E)

    for step in range(N_STEPS + 1):
        q = current_q()
        mu_q = feat_v.T @ q
        loss = mmd2(mu_q, mu_train)

        if step % CHECKPOINT_EVERY == 0 or step == N_STEPS:
            sidx = sample_from_probs(q, N_SAMPLE_EVAL, eval_rng)
            cov = coverage_from_samples(sidx, train_idx_set, unseen_idx_set)
            kl = forward_kl(p_star, q)
            t_list = list(train_idx_set)
            u_list = list(unseen_idx_set)
            history.append(
                {
                    "step": step,
                    "loss_mmd2": loss,
                    "train_coverage": cov["train_coverage"],
                    "unseen_valid_coverage": cov["unseen_valid_coverage"],
                    "n_unique_samples": cov["n_unique_samples"],
                    "n_train_hit": cov["n_train_hit"],
                    "n_unseen_hit": cov["n_unseen_hit"],
                    "train_mass": float(q[t_list].sum()) if t_list else 0.0,
                    "unseen_mass": float(q[u_list].sum()) if u_list else 0.0,
                    "forward_kl_pstar_q": kl,
                }
            )

        if step == N_STEPS:
            break

        diff = mu_q - mu_train
        mean_x = bits_v.T @ q
        x_c = bits_v - mean_x
        feat_c = feat_v - mu_q

        if kind == "product":
            cov_phi_x = feat_c.T @ (q[:, None] * x_c)
            grad = 2.0 * (cov_phi_x.T @ diff)
            theta = theta - lr * grad
        else:
            cov_phi_x = feat_c.T @ (q[:, None] * x_c)
            grad_h = 2.0 * (cov_phi_x.T @ diff)
            pair_feats = []
            for i in range(N):
                for j in range(i + 1, N):
                    pair_feats.append(bits_v[:, i] * bits_v[:, j])
            pair = np.stack(pair_feats, axis=1)
            mean_pair = pair.T @ q
            pair_c = pair - mean_pair
            cov_phi_pair = feat_c.T @ (q[:, None] * pair_c)
            grad_j = 2.0 * (cov_phi_pair.T @ diff)
            h = h - lr * grad_h
            jvec = jvec - lr * grad_j
            jvec *= 0.999

    q_final = current_q()
    final = history[-1]
    return {
        "name": name,
        "kind": kind,
        "params_dim": int(params_dim),
        "history": history,
        "final": {
            "loss_mmd2": final["loss_mmd2"],
            "train_coverage": final["train_coverage"],
            "unseen_valid_coverage": final["unseen_valid_coverage"],
            "forward_kl_pstar_q": final["forward_kl_pstar_q"],
            "train_mass": final["train_mass"],
            "unseen_mass": final["unseen_mass"],
            "n_unique_samples": final["n_unique_samples"],
            "step": final["step"],
        },
        "q_entropy": float(-(q_final * np.log(q_final + 1e-300)).sum()),
    }


def snapshot_at_loss(history: list[dict], L_star: float) -> dict:
    """Earliest checkpoint with loss <= L_star; else checkpoint closest to L_star."""
    below = [h for h in history if h["loss_mmd2"] <= L_star]
    if below:
        h = below[0]
        return {**h, "match_rule": "first_loss_le_Lstar", "L_star": L_star}
    h = min(history, key=lambda z: abs(z["loss_mmd2"] - L_star))
    return {**h, "match_rule": "closest_to_Lstar", "L_star": L_star}


def decide_separation(models: list[dict]) -> dict:
    """Stop-at-similar-loss: L_star = max(final losses); compare coverage at matched snaps."""
    finals = [m["final"] for m in models]
    L_star = max(f["loss_mmd2"] for f in finals)
    snaps = [snapshot_at_loss(m["history"], L_star) for m in models]
    la, lb = snaps[0]["loss_mmd2"], snaps[1]["loss_mmd2"]
    mean_l = 0.5 * (la + lb)
    rel = abs(la - lb) / max(mean_l, 1e-12)
    ca, cb = snaps[0]["unseen_valid_coverage"], snaps[1]["unseen_valid_coverage"]
    gap = abs(ca - cb)
    similar = rel <= LOSS_TOL_RATIO
    split = bool(similar and gap >= COV_GAP_THR)
    if not similar:
        note = (
            f"匹配损失水平 L*={L_star:.6f} 上两模型相对差 {rel:.3f}>{LOSS_TOL_RATIO}，"
            f"未达「损失接近」；未见覆盖 |Δ|={gap:.4f}。"
            f"记：**本设置未分开**（n_sample_eval={N_SAMPLE_EVAL}；种子见 seeds）。"
        )
        verdict = "本设置未分开"
        separated = False
    elif split:
        note = (
            f"在相近损失水平 L*={L_star:.6f}（相对差 {rel:.3f}≤{LOSS_TOL_RATIO}）下，"
            f"未见有效覆盖 |Δ|={gap:.4f}≥{COV_GAP_THR} → 损失接近但覆盖分开。"
        )
        verdict = "损失接近但覆盖分开"
        separated = True
    else:
        note = (
            f"在相近损失水平 L*={L_star:.6f}（相对差 {rel:.3f}）下，"
            f"未见有效覆盖 |Δ|={gap:.4f}<{COV_GAP_THR} → **本设置未分开**"
            f"（n_sample_eval={N_SAMPLE_EVAL}；种子见 seeds）。"
        )
        verdict = "本设置未分开"
        separated = False
    return {
        "L_star": L_star,
        "loss_similar": similar,
        "coverage_split": split,
        "separated": separated,
        "rel_loss_diff": rel,
        "abs_unseen_coverage_gap": gap,
        "loss_tol_ratio": LOSS_TOL_RATIO,
        "coverage_gap_threshold": COV_GAP_THR,
        "matched_snapshots": [
            {
                "model": models[i]["name"],
                "step": snaps[i]["step"],
                "loss_mmd2": snaps[i]["loss_mmd2"],
                "unseen_valid_coverage": snaps[i]["unseen_valid_coverage"],
                "train_coverage": snaps[i]["train_coverage"],
                "forward_kl_pstar_q": snaps[i]["forward_kl_pstar_q"],
                "match_rule": snaps[i]["match_rule"],
            }
            for i in range(2)
        ],
        "note": note,
        "verdict_zh": verdict,
    }


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    rng_target = np.random.default_rng(SEEDS["target"])
    rng_train = np.random.default_rng(SEEDS["train_sample"])
    rng_prod = np.random.default_rng(SEEDS["product_init"])
    rng_ising = np.random.default_rng(SEEDS["ising_init"])
    rng_eval = np.random.default_rng(SEEDS["eval_sample"])

    bits_all = all_bitstrings(N)
    vmask = valid_mask(bits_all, K_WEIGHT)
    bits_v = bits_all[vmask]
    n_valid = int(bits_v.shape[0])
    assert n_valid == int(comb(N, K_WEIGHT))

    feat_v = pauli_z_features(bits_v)
    p_star, w_target = build_target(bits_v, rng_target)

    train_draws = sample_from_probs(p_star, N_TRAIN, rng_train)
    train_unique = sorted(set(int(i) for i in train_draws))
    train_idx_set = set(train_unique)
    unseen_idx = [i for i in range(n_valid) if i not in train_idx_set]
    unseen_idx_set = set(unseen_idx)

    emp = np.zeros(n_valid, dtype=np.float64)
    for i in train_draws:
        emp[i] += 1.0
    emp /= emp.sum()
    mu_train = feat_v.T @ emp
    mu_star = feat_v.T @ p_star

    model_a = train_model(
        name="ProductValid",
        bits_v=bits_v,
        feat_v=feat_v,
        mu_train=mu_train,
        p_star=p_star,
        train_idx_set=train_idx_set,
        unseen_idx_set=unseen_idx_set,
        init_rng=rng_prod,
        eval_rng=rng_eval,
        kind="product",
    )
    rng_eval_b = np.random.default_rng(SEEDS["eval_sample"] + 1)
    model_b = train_model(
        name="PairIsingValid",
        bits_v=bits_v,
        feat_v=feat_v,
        mu_train=mu_train,
        p_star=p_star,
        train_idx_set=train_idx_set,
        unseen_idx_set=unseen_idx_set,
        init_rng=rng_ising,
        eval_rng=rng_eval_b,
        kind="ising",
    )

    models = [model_a, model_b]
    sep = decide_separation(models)

    curves = {
        m["name"]: [
            {
                "step": h["step"],
                "loss_mmd2": h["loss_mmd2"],
                "unseen_valid_coverage": h["unseen_valid_coverage"],
                "train_coverage": h["train_coverage"],
                "forward_kl_pstar_q": h["forward_kl_pstar_q"],
            }
            for h in m["history"]
        ]
        for m in models
    }

    snap_a, snap_b = sep["matched_snapshots"]

    headline = {
        "N": N,
        "k_weight": K_WEIGHT,
        "n_valid": n_valid,
        "valid_definition": f"Hamming_weight=={K_WEIGHT}",
        "n_train_draws": N_TRAIN,
        "n_train_unique": len(train_unique),
        "n_unseen_valid": len(unseen_idx),
        "n_sample_eval": N_SAMPLE_EVAL,
        "model_a": model_a["name"],
        "model_b": model_b["name"],
        "L_star_matched_loss": sep["L_star"],
        "model_a_matched_loss_mmd2": snap_a["loss_mmd2"],
        "model_b_matched_loss_mmd2": snap_b["loss_mmd2"],
        "model_a_matched_unseen_valid_coverage": snap_a["unseen_valid_coverage"],
        "model_b_matched_unseen_valid_coverage": snap_b["unseen_valid_coverage"],
        "model_a_matched_train_coverage": snap_a["train_coverage"],
        "model_b_matched_train_coverage": snap_b["train_coverage"],
        "model_a_matched_forward_kl": snap_a["forward_kl_pstar_q"],
        "model_b_matched_forward_kl": snap_b["forward_kl_pstar_q"],
        "model_a_matched_step": snap_a["step"],
        "model_b_matched_step": snap_b["step"],
        "model_a_final_loss_mmd2": model_a["final"]["loss_mmd2"],
        "model_b_final_loss_mmd2": model_b["final"]["loss_mmd2"],
        "model_a_final_unseen_valid_coverage": model_a["final"]["unseen_valid_coverage"],
        "model_b_final_unseen_valid_coverage": model_b["final"]["unseen_valid_coverage"],
        "model_a_final_train_coverage": model_a["final"]["train_coverage"],
        "model_b_final_train_coverage": model_b["final"]["train_coverage"],
        "model_a_final_forward_kl": model_a["final"]["forward_kl_pstar_q"],
        "model_b_final_forward_kl": model_b["final"]["forward_kl_pstar_q"],
        "abs_unseen_coverage_gap_matched": sep["abs_unseen_coverage_gap"],
        "rel_loss_diff_matched": sep["rel_loss_diff"],
        "loss_coverage_separated": sep["separated"],
        "verdict_zh": sep["verdict_zh"],
        "separation_note": sep["note"],
    }

    summary = {
        "track": "mmd_coverage",
        "title_frame": "方法·噪声预算",
        "prior_cite": "Raj, Mathur, Perdomo-Ortiz, arXiv:2608.31117",
        "disclaimer": DISCLAIMER,
        "seeds": SEEDS,
        "protocol": {
            "N": N,
            "k_weight": K_WEIGHT,
            "valid_definition": f"x in {{0,1}}^N with Hamming_weight(x)=={K_WEIGHT}",
            "n_valid": n_valid,
            "n_train_draws": N_TRAIN,
            "n_sample_eval": N_SAMPLE_EVAL,
            "beta_target": BETA_TARGET,
            "n_steps": N_STEPS,
            "lr_product": LR_PRODUCT,
            "lr_ising": LR_ISING,
            "checkpoint_every": CHECKPOINT_EVERY,
            "moment_order": MOMENT_ORDER,
            "feature_map": "Pauli-Z monomials order<=2: Z_i and Z_i Z_j (Z=1-2x)",
            "loss": "MMD2 = ||mu_model - mu_train_empirical||^2 on Pauli-Z features",
            "matched_loss_rule": (
                "L_star = max(final_loss_a, final_loss_b); "
                "each model uses earliest checkpoint with loss<=L_star"
            ),
            "models": [
                {
                    "name": "ProductValid",
                    "description": "Independent-bit logits; q=softmax(-E) on valid set V",
                },
                {
                    "name": "PairIsingValid",
                    "description": "Pairwise Ising energy on V; same MMD2 loss",
                },
            ],
            "no_30_qubit": True,
            "no_genomic": True,
            "no_quantum_hardware": True,
            "no_copied_raj_coverage_numbers": True,
        },
        "target": {
            "weight_vector": w_target.tolist(),
            "beta": BETA_TARGET,
            "entropy": float(-(p_star * np.log(p_star + 1e-300)).sum()),
            "max_prob": float(p_star.max()),
        },
        "train_set": {
            "n_draws": N_TRAIN,
            "n_unique": len(train_unique),
            "n_unseen_valid": len(unseen_idx),
            "unique_indices": train_unique,
        },
        "moments": {
            "mu_train_norm": float(np.linalg.norm(mu_train)),
            "mu_star_norm": float(np.linalg.norm(mu_star)),
            "mmd2_train_vs_star": mmd2(mu_train, mu_star),
        },
        "models": [
            {
                "name": m["name"],
                "kind": m["kind"],
                "params_dim": m["params_dim"],
                "q_entropy": m["q_entropy"],
                "final": m["final"],
                "history": m["history"],
            }
            for m in models
        ],
        "curves": curves,
        "separation": sep,
        "headline": headline,
        "empty_cells": [],
    }

    body = json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2)
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    summary["rerun_sha256"] = sha
    summary["rerun_sha16"] = sha[:16]
    headline["rerun_sha16"] = sha[:16]
    summary["headline"] = headline

    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[mmd_coverage] wrote {OUT}")
    print(f"[mmd_coverage] sha16={sha[:16]}")
    print(f"[mmd_coverage] verdict={sep['verdict_zh']}")
    print(
        f"[mmd_coverage] matched L*={sep['L_star']:.6f} "
        f"losses={snap_a['loss_mmd2']:.6f}/{snap_b['loss_mmd2']:.6f} "
        f"unseen={snap_a['unseen_valid_coverage']:.4f}/{snap_b['unseen_valid_coverage']:.4f}"
    )


if __name__ == "__main__":
    main()
