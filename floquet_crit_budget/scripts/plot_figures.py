#!/usr/bin/env python3
"""Plot Bot D budget figures from data/summary.json → paper/fig/ (png+pdf)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "summary.json"
FIG = ROOT / "paper" / "fig"


def save(fig, name: str):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=160, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    clean = s["clean_limit"]
    drows = s["disorder_sweep"]
    lrows = s["loss_sweep"]
    h = s["headline"]

    # --- clean quasienergy spectrum ---
    eps = np.array(clean["quasienergies"])
    ew = np.array(clean["end_weights"])
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    idx = np.arange(len(eps))
    colors = np.where(ew >= 0.45, "C3", "C0")
    ax.scatter(idx, eps, c=colors, s=18, zorder=3)
    ax.axhline(0.0, color="k", ls="--", lw=0.8, alpha=0.5)
    ax.axhline(np.pi, color="k", ls=":", lw=0.8, alpha=0.5)
    ax.axhline(-np.pi, color="k", ls=":", lw=0.8, alpha=0.5)
    ax.set_xlabel("mode index (sorted by ε)")
    ax.set_ylabel("quasienergy ε")
    ax.set_title(
        f"Clean Floquet SSH (textbook)  γ1/π={clean['gamma1_over_pi']:.2f}, "
        f"γ2/π={clean['gamma2_over_pi']:.2f}, N={clean['n_sites']}"
    )
    ax.text(
        0.02,
        0.98,
        "red: end-weight≥0.45\ntextbook model (not Nature replay)",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
    )
    save(fig, "fig_clean_spectrum")

    # --- disorder vs gaps ---
    W = np.array([r["W"] for r in drows])
    g0 = np.array([r["gap_0_bulk_mean"] for r in drows])
    g0s = np.array([r["gap_0_bulk_std"] for r in drows])
    gp = np.array([r["gap_pi_bulk_mean"] for r in drows])
    gps = np.array([r["gap_pi_bulk_std"] for r in drows])
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.errorbar(W, g0, yerr=g0s, fmt="-o", ms=4, label="bulk gap → 0", color="C0")
    ax.errorbar(W, gp, yerr=gps, fmt="-s", ms=4, label="bulk gap → π", color="C1")
    for key, color, label in [
        ("vanish_disorder_0", "C0", "0-sig vanish"),
        ("vanish_disorder_pi", "C1", "π-sig vanish"),
    ]:
        v = h[key]
        if v.get("vanished_in_sweep") and v.get("cross_x") is not None:
            ax.axvline(v["cross_x"], color=color, ls="--", alpha=0.7, label=f"{label} W={v['cross_x']:.2f}")
        elif v.get("note"):
            note_en = "no vanish in sweep range" if "未消失" in (v.get("note") or "") else (v.get("note") or "")
            ax.text(0.98, 0.05 if "pi" in key else 0.12, f"{key}: {note_en}", transform=ax.transAxes,
                    ha="right", fontsize=7, color=color)
    ax.set_xlabel("bond disorder W")
    ax.set_ylabel("bulk quasienergy gap")
    ax.set_title("Disorder budget: edge-mode bulk gaps (mean±std over 8 seeds)")
    ax.legend(fontsize=8, loc="best")
    ax.set_ylim(bottom=0)
    save(fig, "fig_disorder_gap")

    # --- disorder vs EE ---
    ee = np.array([r["half_chain_ee_mean"] for r in drows])
    ees = np.array([r["half_chain_ee_std"] for r in drows])
    ee0 = clean["half_chain_ee"]
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.errorbar(W, ee, yerr=ees, fmt="-o", ms=4, color="C2", label="half-chain EE")
    ax.axhline(ee0, color="k", ls="--", lw=0.9, label=f"clean EE={ee0:.3f}")
    ax.set_xlabel("bond disorder W")
    ax.set_ylabel("half-chain entanglement entropy")
    ax.set_title("Disorder budget: half-chain EE vs clean")
    ax.legend(fontsize=8)
    save(fig, "fig_disorder_ee")

    # --- loss vs gaps ---
    K = np.array([r["kappa"] for r in lrows])
    lg0 = np.array([r["gap_0_bulk"] for r in lrows])
    lgp = np.array([r["gap_pi_bulk"] for r in lrows])
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.plot(K, lg0, "-o", ms=4, label="bulk gap → 0", color="C0")
    ax.plot(K, lgp, "-s", ms=4, label="bulk gap → π", color="C1")
    for key, color, label in [
        ("vanish_loss_0", "C0", "0-sig vanish"),
        ("vanish_loss_pi", "C1", "π-sig vanish"),
    ]:
        v = h[key]
        if v.get("vanished_in_sweep") and v.get("cross_x") is not None:
            ax.axvline(v["cross_x"], color=color, ls="--", alpha=0.7, label=f"{label} κ={v['cross_x']:.2f}")
        elif v.get("note"):
            note_en = "no vanish in sweep range" if "未消失" in (v.get("note") or "") else (v.get("note") or "")
            ax.text(0.98, 0.05 if "pi" in key else 0.12, f"{key}: {note_en}", transform=ax.transAxes,
                    ha="right", fontsize=7, color=color)
    ax.set_xlabel("staggered loss κ (even sites)")
    ax.set_ylabel("bulk quasienergy gap")
    ax.set_title("Loss budget: edge-mode bulk gaps")
    ax.legend(fontsize=8, loc="best")
    ax.set_ylim(bottom=0)
    save(fig, "fig_loss_gap")

    # --- loss vs EE ---
    lee = np.array([r["half_chain_ee"] for r in lrows])
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(K, lee, "-o", ms=4, color="C2", label="half-chain EE")
    ax.axhline(ee0, color="k", ls="--", lw=0.9, label=f"clean EE={ee0:.3f}")
    ax.set_xlabel("staggered loss κ (even sites)")
    ax.set_ylabel("half-chain entanglement entropy")
    ax.set_title("Loss budget: half-chain EE vs clean")
    ax.legend(fontsize=8)
    save(fig, "fig_loss_ee")

    print(f"[plot_figures] wrote png+pdf under {FIG}")


if __name__ == "__main__":
    main()
