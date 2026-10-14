#!/usr/bin/env python3
"""Plot skyrmion / concurrence / discord (+ purity, fidelity) vs noise; mark zero crossings."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "summary.json"
FIG = ROOT / "paper" / "fig"


def mark_zeros(ax, vanish: dict, xlabel_name: str):
    colors = {"skyrmion": "C0", "concurrence": "C1", "discord": "C2"}
    ymin, ymax = ax.get_ylim()
    for name, v in vanish.items():
        if v.get("crossed") and v.get("cross_x") is not None:
            ax.axvline(
                v["cross_x"],
                color=colors.get(name, "k"),
                ls="--",
                lw=1.0,
                alpha=0.7,
                label=f"{name}→0 @ {xlabel_name}={v['cross_x']}",
            )


def plot_channel(rows, xkey, xlabel, vanish, outfile_stem, title):
    xs = np.array([r[xkey] for r in rows])
    nsk = np.array([r["skyrmion_abs"] for r in rows])
    conc = np.array([r["concurrence"] for r in rows])
    disc = np.array([r["discord"] for r in rows])
    pur = np.array([r["purity"] for r in rows])
    fid = np.array([r["fidelity"] for r in rows])

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), constrained_layout=True)

    ax = axes[0]
    ax.plot(xs, nsk, "o-", label="|N_sk|", color="C0", ms=4)
    ax.plot(xs, conc, "s-", label="concurrence", color="C1", ms=4)
    ax.plot(xs, disc, "^-", label="discord", color="C2", ms=4)
    ax.axhline(0.02, color="0.5", ls=":", lw=0.8, label="zero thr=0.02")
    mark_zeros(ax, vanish, xkey)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("metric")
    ax.set_title(title + " · main metrics")
    ax.set_ylim(-0.05, 1.15)
    ax.legend(fontsize=7, loc="best")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(xs, pur, "o-", label="purity", color="C3", ms=4)
    ax.plot(xs, fid, "s-", label="fidelity", color="C4", ms=4)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("purity / fidelity")
    ax.set_title(title + " · purity / fidelity")
    ax.set_ylim(-0.05, 1.15)
    ax.legend(fontsize=8, loc="best")
    ax.grid(True, alpha=0.3)

    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"{outfile_stem}.{ext}", dpi=150)
    plt.close(fig)
    print(f"[plot] {outfile_stem}.png/pdf")


def main():
    summary = json.loads(DATA.read_text(encoding="utf-8"))
    h = summary["headline"]
    sweeps = summary["sweeps"]

    plot_channel(
        sweeps["depolarizing"],
        "xi",
        r"depolarizing $\xi$",
        h["vanish_depolarizing"],
        "fig_depolarizing",
        "Depolarizing channel",
    )
    plot_channel(
        sweeps["phase_flip"],
        "p",
        r"phase-flip mix $p$",
        h["vanish_phase_flip"],
        "fig_phase_flip",
        "Phase-flip mix",
    )
    plot_channel(
        sweeps["bit_phase_flip"],
        "p",
        r"bit-phase-flip mix $p$",
        h["vanish_bit_phase_flip"],
        "fig_bit_phase_flip",
        "Bit-phase-flip mix",
    )

    # Clean Stokes texture snapshot (optional diagnostic fig)
    # Recompute quickly for illustration
    from run_skyrmion_budget import (
        ELL,
        GRID_HALF,
        GRID_N,
        WAIST,
        conditional_pol_rho,
        ket_phi_plus,
        lg_p0,
        pure_dm,
        stokes_field,
    )

    xs = np.linspace(-GRID_HALF * WAIST, GRID_HALF * WAIST, GRID_N)
    ys = np.linspace(-GRID_HALF * WAIST, GRID_HALF * WAIST, GRID_N)
    dx = float(xs[1] - xs[0])
    dy = float(ys[1] - ys[0])
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    u_L = lg_p0(X, Y, 0, WAIST)
    u_R = lg_p0(X, Y, ELL, WAIST)
    u_L = u_L / np.sqrt(np.sum(np.abs(u_L) ** 2) * dx * dy)
    u_R = u_R / np.sqrt(np.sum(np.abs(u_R) ** 2) * dx * dy)
    pol = conditional_pol_rho(pure_dm(ket_phi_plus()))
    s0, s1, s2, s3 = stokes_field(pol, u_L, u_R)
    mag = np.sqrt(s1**2 + s2**2 + s3**2) + 1e-30
    n1, n2, n3 = s1 / mag, s2 / mag, s3 / mag

    fig, ax = plt.subplots(figsize=(5.0, 4.2), constrained_layout=True)
    # quiver subsample
    step = 4
    ax.quiver(
        X[::step, ::step],
        Y[::step, ::step],
        n1[::step, ::step],
        n2[::step, ::step],
        n3[::step, ::step],
        cmap="coolwarm",
        angles="xy",
        scale_units="xy",
        scale=2.2,
        width=0.004,
    )
    ax.set_aspect("equal")
    ax.set_xlabel("x / w")
    ax.set_ylabel("y / w")
    ax.set_title(r"Clean limit: conditional Stokes $n_\perp$ (color=$n_3$)")
    fig.savefig(FIG / "fig_clean_texture.png", dpi=150)
    fig.savefig(FIG / "fig_clean_texture.pdf")
    plt.close(fig)
    print("[plot] fig_clean_texture.png/pdf")


if __name__ == "__main__":
    main()
