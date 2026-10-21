#!/usr/bin/env python3
"""
Bot D · floquet_crit_budget
Textbook 1D two-step Floquet SSH: clean limit + bond-disorder / loss budget sweeps.
Classical exact diagonalization of Floquet operator. Fixed seeds. No Nature couplings.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SEEDS = {
    "master": 20261013,
    "disorder_sweep": 301,
    "loss_sweep": 302,
    "phase_diag_probe": 303,
}

N_SITES = 60
# Textbook anomalous Floquet SSH (assumption; NOT Nature couplings).
# Chosen so clean open chain hosts BOTH 0- and π-localized edge modes.
GAMMA1 = 0.25 * np.pi
GAMMA2 = 0.80 * np.pi

EDGE_SITES = 4
EDGE_WEIGHT_THR = 0.45
ZERO_WIN = 0.40
PI_WIN = 0.40
GAP_PRESENT_THR = 0.05
GAP_VANISH_THR = 0.02

DISORDER_WS = np.linspace(0.0, 1.2, 13)
LOSS_KS = np.linspace(0.0, 0.80, 17)
N_DISORDER_REALIZATIONS = 8

DISCLAIMER = (
    "本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，"
    "Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；"
    "verify/ 第三方 PDF 禁止入库。"
)


def floquet_U(
    n: int,
    g1: float,
    g2: float,
    *,
    disorder_odd: np.ndarray | None = None,
    disorder_even: np.ndarray | None = None,
    loss_kappa: float = 0.0,
) -> np.ndarray:
    """
    Two-step Floquet: U = exp(-i H_even) @ exp(-i H_odd).
    Bond disorder: multiplicative on hoppings.
    Loss: staggered on-site -i κ on even-indexed sites only (non-Hermitian).
    Uniform -iκ I would only rescale |λ| and leave eigenvectors/angles unchanged —
    hence staggered loss is the budget channel used here.
    """
    odd_bonds = list(range(0, n - 1, 2))
    even_bonds = list(range(1, n - 1, 2))
    if disorder_odd is None:
        disorder_odd = np.ones(len(odd_bonds))
    if disorder_even is None:
        disorder_even = np.ones(len(even_bonds))

    h_odd = np.zeros((n, n), dtype=complex)
    for k, i in enumerate(odd_bonds):
        amp = g1 * float(disorder_odd[k])
        h_odd[i, i + 1] = amp
        h_odd[i + 1, i] = amp
    h_even = np.zeros((n, n), dtype=complex)
    for k, i in enumerate(even_bonds):
        amp = g2 * float(disorder_even[k])
        h_even[i, i + 1] = amp
        h_even[i + 1, i] = amp

    if loss_kappa != 0.0:
        loss = np.zeros((n, n), dtype=complex)
        for j in range(0, n, 2):
            loss[j, j] = -1j * loss_kappa
        h_odd = h_odd + loss
        h_even = h_even + loss

    return expm(-1j * h_even) @ expm(-1j * h_odd)


def spectrum(U: np.ndarray):
    evals, evecs = np.linalg.eig(U)
    phases = np.angle(evals)
    order = np.argsort(phases)
    return phases[order], evecs[:, order], np.abs(evals[order])


def end_weight(vec: np.ndarray, edge: int = EDGE_SITES) -> float:
    p = np.abs(vec) ** 2
    p = p / (p.sum() + 1e-30)
    return float(p[:edge].sum() + p[-edge:].sum())


def classify_modes(eps: np.ndarray, evecs: np.ndarray):
    records = []
    for i in range(len(eps)):
        e = float(eps[i])
        w = end_weight(evecs[:, i])
        is_edge = w >= EDGE_WEIGHT_THR
        d0 = abs(e)
        dpi = min(abs(e - np.pi), abs(e + np.pi))
        records.append(
            {
                "eps": e,
                "end_weight": w,
                "is_edge": is_edge,
                "near0": d0 <= ZERO_WIN,
                "nearpi": dpi <= PI_WIN,
                "d0": d0,
                "dpi": dpi,
            }
        )
    return records


def gaps_and_edges(records):
    bulk = [r for r in records if not r["is_edge"]]
    edge0 = [r for r in records if r["is_edge"] and r["near0"] and r["d0"] <= r["dpi"]]
    edgepi = [r for r in records if r["is_edge"] and r["nearpi"] and r["dpi"] < r["d0"]]
    if bulk:
        gap0 = float(min(r["d0"] for r in bulk))
        gappi = float(min(r["dpi"] for r in bulk))
    else:
        gap0, gappi = float("nan"), float("nan")
    e0_mean = float(np.mean([r["eps"] for r in edge0])) if edge0 else None
    epi_mean = float(np.mean([r["eps"] for r in edgepi])) if edgepi else None
    return {
        "n_edge_0": len(edge0),
        "n_edge_pi": len(edgepi),
        "gap_0_bulk": gap0,
        "gap_pi_bulk": gappi,
        "edge0_eps_mean": e0_mean,
        "edgepi_eps_mean": epi_mean,
        "sig_0_present": bool(len(edge0) >= 1 and (np.isnan(gap0) or gap0 >= GAP_PRESENT_THR)),
        "sig_pi_present": bool(len(edgepi) >= 1 and (np.isnan(gappi) or gappi >= GAP_PRESENT_THR)),
    }


def half_chain_ee(evecs: np.ndarray, eps: np.ndarray) -> float:
    n = len(eps)
    half = n // 2
    occ_idx = np.where(eps <= 0.0)[0]
    if len(occ_idx) == 0:
        return 0.0
    V = evecs[:, occ_idx]
    Q, _ = np.linalg.qr(V, mode="reduced")
    C = Q @ Q.conj().T
    C_A = 0.5 * (C[:half, :half] + C[:half, :half].conj().T)
    w = np.clip(np.real(np.linalg.eigvalsh(C_A)), 1e-12, 1.0 - 1e-12)
    return float(-np.sum(w * np.log(w) + (1 - w) * np.log(1 - w)))


def bond_disorder_factors(n: int, W: float, rng: np.random.Generator):
    odd_bonds = list(range(0, n - 1, 2))
    even_bonds = list(range(1, n - 1, 2))
    d_odd = 1.0 + W * rng.uniform(-1.0, 1.0, size=len(odd_bonds))
    d_even = 1.0 + W * rng.uniform(-1.0, 1.0, size=len(even_bonds))
    return np.clip(d_odd, 0.05, None), np.clip(d_even, 0.05, None)


def analyze_U(U: np.ndarray) -> dict:
    eps, evecs, absevals = spectrum(U)
    rec = classify_modes(eps, evecs)
    g = gaps_and_edges(rec)
    ee = half_chain_ee(evecs, eps)
    return {
        **g,
        "half_chain_ee": ee,
        "eps": [float(x) for x in eps],
        "abs_evals_min": float(np.min(absevals)),
        "abs_evals_max": float(np.max(absevals)),
        "end_weights": [float(r["end_weight"]) for r in rec],
    }


def find_vanish(xs, present_flags, gaps, edge_counts, kind: str, clean_present: bool):
    """
    First x where a signature that WAS present in clean limit is gone:
    present_flag False, or edge_count==0, or gap < GAP_VANISH_THR.
    If never present in clean: note accordingly (do not invent a threshold).
    If present throughout sweep: 本扫范围内未消失.
    """
    if not clean_present:
        return {
            "vanished_in_sweep": False,
            "cross_x": None,
            "note": "清洁极限无此签名，不报消失阈值",
            "kind": kind,
            "at_vanish_gap": None,
            "at_vanish_n_edge": None,
        }
    for x, present, gap, nec in zip(xs, present_flags, gaps, edge_counts):
        gone = (not present) or (nec == 0) or (not np.isnan(gap) and gap < GAP_VANISH_THR)
        # skip the clean point itself if still present
        if gone and not (x == xs[0] and present and nec > 0 and gap >= GAP_VANISH_THR):
            # if first point already gone despite clean_present, still record
            return {
                "vanished_in_sweep": True,
                "cross_x": float(round(float(x), 10)),
                "note": None,
                "kind": kind,
                "at_vanish_gap": float(gap) if gap is not None and not np.isnan(gap) else None,
                "at_vanish_n_edge": float(nec),
            }
    # re-scan without the awkward first-point guard
    for x, present, gap, nec in zip(xs, present_flags, gaps, edge_counts):
        gone = (not present) or (nec == 0) or (not np.isnan(gap) and gap < GAP_VANISH_THR)
        if gone:
            return {
                "vanished_in_sweep": True,
                "cross_x": float(round(float(x), 10)),
                "note": None,
                "kind": kind,
                "at_vanish_gap": float(gap) if gap is not None and not np.isnan(gap) else None,
                "at_vanish_n_edge": float(nec),
            }
    return {
        "vanished_in_sweep": False,
        "cross_x": None,
        "note": "本扫范围内未消失",
        "kind": kind,
        "at_vanish_gap": None,
        "at_vanish_n_edge": None,
    }


def phase_diag_probe(n_g: int = 11) -> dict:
    g1s = np.linspace(0.05 * np.pi, 0.95 * np.pi, n_g)
    g2s = np.linspace(0.05 * np.pi, 0.95 * np.pi, n_g)
    crit0, critpi = [], []
    for g1 in g1s:
        for g2 in g2s:
            out = analyze_U(floquet_U(N_SITES, float(g1), float(g2)))
            if out["gap_0_bulk"] < 0.08:
                crit0.append((float(g1), float(g2)))
            if out["gap_pi_bulk"] < 0.08:
                critpi.append((float(g1), float(g2)))
    set0 = {(round(a, 5), round(b, 5)) for a, b in crit0}
    setpi = {(round(a, 5), round(b, 5)) for a, b in critpi}
    inter = set0 & setpi
    return {
        "grid_n": n_g,
        "n_near_crit_0": len(crit0),
        "n_near_crit_pi": len(critpi),
        "n_intersection_cells": len(inter),
        "multicritical_located": False,
        "additive_log_reported": False,
        "note": (
            "仅做粗网格近零隙探测，不足以定出两条临界边界的交点；"
            "故不报多临界点、不报可加对数。"
        ),
    }


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    rng_master = np.random.default_rng(SEEDS["master"])

    U0 = floquet_U(N_SITES, GAMMA1, GAMMA2, loss_kappa=0.0)
    clean = analyze_U(U0)
    clean_export = {
        "n_sites": N_SITES,
        "gamma1_over_pi": float(GAMMA1 / np.pi),
        "gamma2_over_pi": float(GAMMA2 / np.pi),
        "gamma1": float(GAMMA1),
        "gamma2": float(GAMMA2),
        "n_edge_0": clean["n_edge_0"],
        "n_edge_pi": clean["n_edge_pi"],
        "gap_0_bulk": clean["gap_0_bulk"],
        "gap_pi_bulk": clean["gap_pi_bulk"],
        "edge0_eps_mean": clean["edge0_eps_mean"],
        "edgepi_eps_mean": clean["edgepi_eps_mean"],
        "sig_0_present": clean["sig_0_present"],
        "sig_pi_present": clean["sig_pi_present"],
        "half_chain_ee": clean["half_chain_ee"],
        "quasienergies": clean["eps"],
        "end_weights": clean["end_weights"],
        "model_note": "标准模型诊断，不是该实验的复现",
    }

    rng_d = np.random.default_rng(SEEDS["disorder_sweep"])
    disorder_rows = []
    for W in DISORDER_WS:
        gaps0, gapspi, ee_list = [], [], []
        n0s, npis, sig0s, sigpis = [], [], [], []
        for _ in range(N_DISORDER_REALIZATIONS):
            d_odd, d_even = bond_disorder_factors(N_SITES, float(W), rng_d)
            out = analyze_U(
                floquet_U(
                    N_SITES, GAMMA1, GAMMA2,
                    disorder_odd=d_odd, disorder_even=d_even, loss_kappa=0.0,
                )
            )
            gaps0.append(out["gap_0_bulk"])
            gapspi.append(out["gap_pi_bulk"])
            ee_list.append(out["half_chain_ee"])
            n0s.append(out["n_edge_0"])
            npis.append(out["n_edge_pi"])
            sig0s.append(out["sig_0_present"])
            sigpis.append(out["sig_pi_present"])
        disorder_rows.append(
            {
                "W": float(round(float(W), 10)),
                "gap_0_bulk_mean": float(np.mean(gaps0)),
                "gap_0_bulk_std": float(np.std(gaps0)),
                "gap_pi_bulk_mean": float(np.mean(gapspi)),
                "gap_pi_bulk_std": float(np.std(gapspi)),
                "half_chain_ee_mean": float(np.mean(ee_list)),
                "half_chain_ee_std": float(np.std(ee_list)),
                "half_chain_ee_delta_vs_clean": float(np.mean(ee_list) - clean["half_chain_ee"]),
                "n_edge_0_mean": float(np.mean(n0s)),
                "n_edge_pi_mean": float(np.mean(npis)),
                "sig_0_frac": float(np.mean(sig0s)),
                "sig_pi_frac": float(np.mean(sigpis)),
                "n_realizations": N_DISORDER_REALIZATIONS,
            }
        )

    vanish_d0 = find_vanish(
        [r["W"] for r in disorder_rows],
        [r["sig_0_frac"] >= 0.5 for r in disorder_rows],
        [r["gap_0_bulk_mean"] for r in disorder_rows],
        [r["n_edge_0_mean"] for r in disorder_rows],
        "disorder_0",
        clean_present=bool(clean["sig_0_present"]),
    )
    vanish_dpi = find_vanish(
        [r["W"] for r in disorder_rows],
        [r["sig_pi_frac"] >= 0.5 for r in disorder_rows],
        [r["gap_pi_bulk_mean"] for r in disorder_rows],
        [r["n_edge_pi_mean"] for r in disorder_rows],
        "disorder_pi",
        clean_present=bool(clean["sig_pi_present"]),
    )

    loss_rows = []
    for kappa in LOSS_KS:
        out = analyze_U(floquet_U(N_SITES, GAMMA1, GAMMA2, loss_kappa=float(kappa)))
        loss_rows.append(
            {
                "kappa": float(round(float(kappa), 10)),
                "gap_0_bulk": out["gap_0_bulk"],
                "gap_pi_bulk": out["gap_pi_bulk"],
                "half_chain_ee": out["half_chain_ee"],
                "half_chain_ee_delta_vs_clean": float(out["half_chain_ee"] - clean["half_chain_ee"]),
                "n_edge_0": out["n_edge_0"],
                "n_edge_pi": out["n_edge_pi"],
                "sig_0_present": out["sig_0_present"],
                "sig_pi_present": out["sig_pi_present"],
                "abs_evals_min": out["abs_evals_min"],
                "abs_evals_max": out["abs_evals_max"],
            }
        )

    vanish_l0 = find_vanish(
        [r["kappa"] for r in loss_rows],
        [r["sig_0_present"] for r in loss_rows],
        [r["gap_0_bulk"] for r in loss_rows],
        [r["n_edge_0"] for r in loss_rows],
        "loss_0",
        clean_present=bool(clean["sig_0_present"]),
    )
    vanish_lpi = find_vanish(
        [r["kappa"] for r in loss_rows],
        [r["sig_pi_present"] for r in loss_rows],
        [r["gap_pi_bulk"] for r in loss_rows],
        [r["n_edge_pi"] for r in loss_rows],
        "loss_pi",
        clean_present=bool(clean["sig_pi_present"]),
    )

    probe = phase_diag_probe()

    headline = {
        "model": "textbook_two_step_floquet_ssh",
        "model_note": "标准模型诊断，不是该实验的复现",
        "n_sites": N_SITES,
        "gamma1_over_pi": float(GAMMA1 / np.pi),
        "gamma2_over_pi": float(GAMMA2 / np.pi),
        "clean_gap_0_bulk": clean["gap_0_bulk"],
        "clean_gap_pi_bulk": clean["gap_pi_bulk"],
        "clean_n_edge_0": clean["n_edge_0"],
        "clean_n_edge_pi": clean["n_edge_pi"],
        "clean_half_chain_ee": clean["half_chain_ee"],
        "clean_sig_0_present": clean["sig_0_present"],
        "clean_sig_pi_present": clean["sig_pi_present"],
        "disorder_W_range": [float(round(float(DISORDER_WS[0]), 10)), float(round(float(DISORDER_WS[-1]), 10))],
        "loss_kappa_range": [float(round(float(LOSS_KS[0]), 10)), float(round(float(LOSS_KS[-1]), 10))],
        "vanish_disorder_0": vanish_d0,
        "vanish_disorder_pi": vanish_dpi,
        "vanish_loss_0": vanish_l0,
        "vanish_loss_pi": vanish_lpi,
        "multicritical_additive_log": {
            "reported": False,
            "reason": probe["note"],
        },
    }

    summary = {
        "track": "floquet_crit_budget",
        "title_frame": "方法·噪声预算",
        "prior_cite": "Cheng et al., Nature 658, 358 (2026), doi:10.1038/s41586-026-11067-5",
        "disclaimer": DISCLAIMER,
        "seeds": SEEDS,
        "protocol": {
            "n_sites": N_SITES,
            "drive": "two_step_floquet_ssh",
            "U_formula": "U=expm(-i H_even) @ expm(-i H_odd)",
            "gamma1": float(GAMMA1),
            "gamma2": float(GAMMA2),
            "gamma1_over_pi": float(GAMMA1 / np.pi),
            "gamma2_over_pi": float(GAMMA2 / np.pi),
            "edge_sites": EDGE_SITES,
            "edge_weight_thr": EDGE_WEIGHT_THR,
            "zero_win": ZERO_WIN,
            "pi_win": PI_WIN,
            "gap_present_thr": GAP_PRESENT_THR,
            "gap_vanish_thr": GAP_VANISH_THR,
            "disorder_W_grid": [float(round(float(x), 10)) for x in DISORDER_WS],
            "loss_kappa_grid": [float(round(float(x), 10)) for x in LOSS_KS],
            "n_disorder_realizations": N_DISORDER_REALIZATIONS,
            "disorder_rule": "J -> J*(1+W*U[-1,1]), clip>=0.05",
            "loss_rule": "staggered on-site -i*kappa on even sites (both half-periods); not uniform -i*kappa*I",
            "ee_occupation": "modes with eps<=0; QR orthonormalization of right evecs",
            "no_nature_couplings_in_results": True,
            "no_observation_claim": True,
            "no_recommended_device_length": True,
            "model_note": "标准模型诊断，不是该实验的复现",
        },
        "clean_limit": clean_export,
        "disorder_sweep": disorder_rows,
        "loss_sweep": loss_rows,
        "phase_diag_probe": probe,
        "headline": headline,
        "rng_master_drawn_u01": float(rng_master.random()),
    }

    out_path = DATA / "summary.json"
    text = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    out_path.write_text(text, encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    (DATA / "summary.sha256").write_text(sha + "\n", encoding="utf-8")
    print(f"[run_floquet_budget] wrote {out_path}")
    print(f"[run_floquet_budget] sha256={sha[:16]}")
    print(
        f"[clean] gap0={clean['gap_0_bulk']:.4f} gappi={clean['gap_pi_bulk']:.4f} "
        f"n0={clean['n_edge_0']} npi={clean['n_edge_pi']} EE={clean['half_chain_ee']:.4f} "
        f"sig0={clean['sig_0_present']} sigpi={clean['sig_pi_present']}"
    )
    print(f"[vanish] d0={vanish_d0}")
    print(f"[vanish] dpi={vanish_dpi}")
    print(f"[vanish] l0={vanish_l0}")
    print(f"[vanish] lpi={vanish_lpi}")


if __name__ == "__main__":
    main()
