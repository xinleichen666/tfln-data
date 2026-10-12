#!/workspace/dir13/venv/bin/python
"""Direction-2 HARD GATE 1: materials → thermo-acoustic phase efficiency α.

Platform: GaN-on-sapphire, matching Xu et al. arXiv:2510.26596 Fig. 2h
  α_Xu = 4.03 rad/W  for L = 100 μm.

Physics (NO optical waveguide in this gate):
  φ = ω L / v(T)
  α = dφ/dP = −(ω L / v) · TCF · R_th
  TCF ≡ (1/v)(dv/dT) ≈ SAW temperature coefficient of frequency
  R_th ≡ dT_wg/dP from 2D cross-section thermal model (heater → sapphire sink)

Run:
  /workspace/dir13/venv/bin/python /workspace/dir2/gate1_thermal_acoustic.py
  # or:  python gate1_thermal_acoustic.py   (if that python has scipy)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FIG = ROOT / "fig"
DATA.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

# ---- Xu anchors (arXiv:2510.26596) ----
F_HZ = 1.5e9
OMEGA = 2.0 * math.pi * F_HZ
L_M = 100e-6
V_PHASE = 4879.0
V_GROUP = 3904.0
W_WG = 2.8e-6
H_GAN = 700e-9
ALPHA_XU = 4.03

# GaN/sapphire SAW TCF (literature). Negative: velocity falls with T.
TCF_NOM = -55e-6
TCF_LO = -30e-6
TCF_HI = -96.5e-6

K_SAPPHIRE = 35.0
K_SAP_LO, K_SAP_HI = 23.0, 46.0
K_GAN = 130.0

# Heater geometry ASSUMED (Xu unpublished; Shao PRA 2022 class)
W_HEATER = 10e-6
GAP_EDGE = 6e-6
T_SAP = 430e-6
DOMAIN_HALF_W = 60e-6

SHAO_BULK_DEG_PER_MW = 2.6
SHAO_LNOS_DEG_PER_MW = 0.52
SHAO_L_ASSUMED = 200e-6


def deg_per_mw_to_rad_per_w(x: float) -> float:
    return x * (math.pi / 180.0) * 1000.0


def alpha_from_materials(tcf: float, r_th: float, omega=OMEGA, L=L_M, v=V_PHASE) -> float:
    return -(omega * L / v) * tcf * r_th


def r_th_analytic_strip(kappa: float, L: float, t: float, w: float) -> float:
    return math.log(4.0 * t / max(w, 1e-9)) / (math.pi * kappa * L)


def solve_r_th_2d(
    w_heater: float = W_HEATER,
    gap: float = GAP_EDGE,
    t_sap: float = T_SAP,
    k_sap: float = K_SAPPHIRE,
    k_gan: float = K_GAN,
    h_gan: float = H_GAN,
    w_wg: float = W_WG,
    L: float = L_M,
    half_w: float = DOMAIN_HALF_W,
    nx: int = 97,
    ny: int = 81,
    power: float = 1.0,
) -> dict:
    """2D steady heat conduction; heater on sapphire; GaN ridge only."""
    x_wg_c = 0.5 * w_heater + gap + 0.5 * w_wg
    x_right = max(half_w, x_wg_c + 30e-6)
    xs = np.linspace(-half_w, x_right, nx)
    ys = np.linspace(0.0, h_gan + t_sap, ny)
    dx = float(xs[1] - xs[0])
    dy = float(ys[1] - ys[0])

    kappa = np.full((ny, nx), k_sap, dtype=float)
    film = np.broadcast_to((ys[:, None] < h_gan), (ny, nx)).copy()
    x_wg_lo, x_wg_hi = x_wg_c - 0.5 * w_wg, x_wg_c + 0.5 * w_wg
    in_ridge = np.broadcast_to(
        (xs[None, :] >= x_wg_lo) & (xs[None, :] <= x_wg_hi), (ny, nx)
    ).copy()
    kappa[film & in_ridge] = k_gan

    N = nx * ny

    def idx(j, i):
        return j * nx + i

    rows, cols, data = [], [], []
    b = np.zeros(N, dtype=float)
    q_flux = (power / L) / w_heater

    def add(r, c, v):
        rows.append(r); cols.append(c); data.append(v)

    for j in range(ny):
        for i in range(nx):
            p = idx(j, i)
            if j == ny - 1:
                add(p, p, 1.0)
                continue
            k_c = kappa[j, i]
            gL = gR = gU = 0.0
            if i > 0:
                gL = (2.0 / (1.0 / k_c + 1.0 / kappa[j, i - 1])) * dy / dx
            if i < nx - 1:
                gR = (2.0 / (1.0 / k_c + 1.0 / kappa[j, i + 1])) * dy / dx
            if j > 0:
                gU = (2.0 / (1.0 / k_c + 1.0 / kappa[j - 1, i])) * dx / dy
            gD = (2.0 / (1.0 / k_c + 1.0 / kappa[j + 1, i])) * dx / dy
            add(p, p, gL + gR + gU + gD)
            if i > 0:
                add(p, idx(j, i - 1), -gL)
            if i < nx - 1:
                add(p, idx(j, i + 1), -gR)
            if j > 0:
                add(p, idx(j - 1, i), -gU)
            add(p, idx(j + 1, i), -gD)
            if j == 0 and abs(xs[i]) <= 0.5 * w_heater:
                b[p] += q_flux * dx

    T = spsolve(sparse.coo_matrix((data, (rows, cols)), shape=(N, N)).tocsr(), b).reshape(ny, nx)
    ridge = film & in_ridge
    dT_wg = float(np.mean(T[ridge])) if np.any(ridge) else float(
        np.mean(T[ys < h_gan, int(np.argmin(np.abs(xs - x_wg_c)))])
    )
    dT_h = float(np.mean(T[0, np.abs(xs) <= 0.5 * w_heater]))
    return {
        "R_th_K_per_W": dT_wg / power,
        "dT_wg_per_W": dT_wg / power,
        "dT_heater_per_W": dT_h / power,
        "xs": xs, "ys": ys, "T_per_W": T / power, "x_wg_c": x_wg_c,
    }


def main():
    print("=== Gate 1: materials → α (GaN-on-sapphire) ===")
    th = solve_r_th_2d()
    r_th_nom = th["R_th_K_per_W"]
    r_th_an = r_th_analytic_strip(K_SAPPHIRE, L_M, T_SAP, W_HEATER)
    alpha_nom = alpha_from_materials(TCF_NOM, r_th_nom)
    print(f"R_th 2D FD (WG) = {r_th_nom:.1f} K/W | analytic heater = {r_th_an:.1f} K/W")
    print(f"dT_h/dT_wg = {th['dT_heater_per_W']/max(th['dT_wg_per_W'],1e-30):.2f}")
    print(f"α_nom = {alpha_nom:.3f} rad/W  (Xu = {ALPHA_XU})")

    samples = []
    configs = [
        (TCF_LO, K_SAP_HI, 25e-6, 10e-6),
        (TCF_NOM, K_SAPPHIRE, W_HEATER, GAP_EDGE),
        (TCF_HI, K_SAP_LO, 5e-6, 3e-6),
        (TCF_NOM, K_SAP_LO, W_HEATER, GAP_EDGE),
        (TCF_NOM, K_SAP_HI, W_HEATER, GAP_EDGE),
        (TCF_LO, K_SAPPHIRE, W_HEATER, GAP_EDGE),
        (TCF_HI, K_SAPPHIRE, W_HEATER, GAP_EDGE),
        (TCF_NOM, K_SAPPHIRE, 5e-6, 3e-6),
        (TCF_NOM, K_SAPPHIRE, 25e-6, 10e-6),
    ]
    for tcf, k_sap, w_h, gap in configs:
        sol = solve_r_th_2d(w_heater=w_h, gap=gap, k_sap=k_sap, nx=81, ny=65)
        a = alpha_from_materials(tcf, sol["R_th_K_per_W"])
        samples.append({
            "tcf_1_per_K": tcf, "k_sapphire": k_sap,
            "w_heater_m": w_h, "gap_m": gap,
            "R_th": sol["R_th_K_per_W"], "alpha": a,
        })
        print(f"  α={a:.3f} R_th={sol['R_th_K_per_W']:.1f} "
              f"TCF={tcf*1e6:.1f}ppm κ={k_sap} w={w_h*1e6:.0f}µm gap={gap*1e6:.0f}µm")

    alphas = np.array([s["alpha"] for s in samples])
    alpha_lo, alpha_hi = float(alphas.min()), float(alphas.max())
    alpha_med = float(np.median(alphas))
    ratio = alpha_nom / ALPHA_XU
    final_pass = (alpha_nom > 0) and (0.1 <= ratio <= 10.0) and (
        alpha_hi >= 0.1 * ALPHA_XU and alpha_lo <= 10.0 * ALPHA_XU
    )

    shao_bulk = deg_per_mw_to_rad_per_w(SHAO_BULK_DEG_PER_MW)
    shao_lnos = deg_per_mw_to_rad_per_w(SHAO_LNOS_DEG_PER_MW)

    # Figures
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    ax = axes[0]
    ax.bar([0, 1], [alpha_nom, ALPHA_XU], color=["#4C78A8", "#F58518"], width=0.55)
    ax.errorbar([0], [alpha_med],
                yerr=[[alpha_med - alpha_lo], [alpha_hi - alpha_med]],
                fmt="o", color="k", capsize=4, label="calc band")
    ax.axhspan(0.1 * ALPHA_XU, 10 * ALPHA_XU, color="green", alpha=0.08, label="±1 order of Xu")
    ax.set_xticks([0, 1])
    ax.set_xticklabels([r"$\alpha_{\mathrm{calc}}$ (materials)", r"$\alpha_{\mathrm{Xu}}$ (meas.)"])
    ax.set_ylabel(r"$\alpha$ [rad/W]")
    ax.set_title(f"Gate 1: {'PASS' if final_pass else 'FAIL'} (L=100 µm, GaN/sapphire)")
    ax.legend(fontsize=8)
    ax.set_ylim(0, max(ALPHA_XU * 3, alpha_hi * 1.15, 1.0))

    ax = axes[1]
    vals = [ALPHA_XU / L_M / 1e4, alpha_nom / L_M / 1e4,
            shao_bulk / SHAO_L_ASSUMED / 1e4, shao_lnos / SHAO_L_ASSUMED / 1e4]
    ax.bar(range(4), vals, color=["#F58518", "#4C78A8", "#54A24B", "#B279A2"])
    ax.set_xticks(range(4))
    ax.set_xticklabels(["Xu\nGaN/sap", "calc\nGaN/sap", "Shao bulk\n(norm.)", "Shao LNoS\n(norm.)"], fontsize=8)
    ax.set_ylabel(r"$\alpha/L$ [$10^4$ rad/(W·m)]")
    ax.set_title("Length-normalized (Shao L assumed 200 µm)")
    fig.tight_layout()
    fig.savefig(FIG / "gate1_alpha.png", dpi=160)
    fig.savefig(FIG / "gate1_alpha.pdf")
    plt.close(fig)

    P = np.linspace(0, 1.2, 241)
    phi0 = 0.3
    fig2, axes2 = plt.subplots(1, 2, figsize=(10.5, 4.2))
    axes2[0].plot(P, 0.5 * (1 + np.cos(ALPHA_XU * P + phi0)), "k--", lw=2, label=rf"Xu α={ALPHA_XU}")
    axes2[0].plot(P, 0.5 * (1 + np.cos(alpha_nom * P + phi0)), color="#4C78A8", lw=2,
                  label=rf"calc α={alpha_nom:.2f}")
    axes2[0].set_xlabel(r"$P_H$ [W]")
    axes2[0].set_ylabel(r"$[1+\cos(\alpha P+\phi_0)]/2$")
    axes2[0].set_title("Qualitative vs Xu Fig. 2h")
    axes2[0].legend(fontsize=8)
    axes2[0].set_ylim(-0.05, 1.05)

    y_cut = th["ys"] <= 40e-6
    im = axes2[1].pcolormesh(th["xs"] * 1e6, th["ys"][y_cut] * 1e6, th["T_per_W"][y_cut],
                             shading="auto", cmap="inferno")
    axes2[1].invert_yaxis()
    axes2[1].axvline(th["x_wg_c"] * 1e6, color="cyan", ls="--", lw=1, label="WG")
    axes2[1].set_xlabel("x [µm]"); axes2[1].set_ylabel("y [µm]")
    axes2[1].set_title(r"$\Delta T/P$ top 40 µm [K/W]")
    axes2[1].legend(fontsize=7)
    fig2.colorbar(im, ax=axes2[1], fraction=0.046)
    fig2.tight_layout()
    fig2.savefig(FIG / "gate1_mzi_thermal.png", dpi=160)
    fig2.savefig(FIG / "gate1_mzi_thermal.pdf")
    plt.close(fig2)

    out = {
        "gate": "direction2_hard_gate1_thermoacoustic_alpha",
        "platform": "GaN-on-sapphire (Xu PnIC)",
        "result": "PASS" if final_pass else "FAIL",
        "alpha_calc_rad_per_W": alpha_nom,
        "alpha_calc_median_rad_per_W": alpha_med,
        "alpha_calc_band_rad_per_W": [alpha_lo, alpha_hi],
        "alpha_Xu_rad_per_W": ALPHA_XU,
        "ratio_calc_over_Xu": ratio,
        "ratio_median_over_Xu": alpha_med / ALPHA_XU,
        "pass_criterion": "0.1 ≤ α_calc/α_Xu ≤ 10 (same order of magnitude)",
        "optical_waveguide_added": False,
        "device_metrics_written": False,
        "inputs": {
            "f_Hz": F_HZ, "L_m": L_M, "v_phase_m_per_s": V_PHASE,
            "v_group_m_per_s": V_GROUP, "w_wg_m": W_WG, "h_GaN_m": H_GAN,
            "TCF_nom_1_per_K": TCF_NOM, "TCF_range_1_per_K": [TCF_LO, TCF_HI],
            "R_th_2D_K_per_W": r_th_nom, "R_th_analytic_heater_K_per_W": r_th_an,
            "dT_heater_per_W": th["dT_heater_per_W"], "dT_wg_per_W": th["dT_wg_per_W"],
            "k_sapphire_W_per_mK": K_SAPPHIRE, "k_GaN_W_per_mK": K_GAN,
            "heater_width_m_ASSUMED": W_HEATER, "heater_gap_m_ASSUMED": GAP_EDGE,
            "sapphire_thickness_m_ASSUMED": T_SAP,
            "formula": "alpha = -(omega*L/v)*TCF*R_th",
        },
        "uncertainty_samples": samples,
        "shao_crosscheck": {
            "bulk_LN_rad_per_W": shao_bulk, "LNoS_rad_per_W": shao_lnos,
            "L_assumed_m": SHAO_L_ASSUMED,
            "alpha_over_L_Xu": ALPHA_XU / L_M,
            "alpha_over_L_calc": alpha_nom / L_M,
            "alpha_over_L_shao_bulk": shao_bulk / SHAO_L_ASSUMED,
            "alpha_over_L_shao_lnos": shao_lnos / SHAO_L_ASSUMED,
            "note": "Shao heater length not unique for quoted deg/mW; 200 µm mid-range ASSUMED for /L",
        },
        "sources": {
            "Xu": "arXiv:2510.26596 Fig.2h / text",
            "Shao": "Phys. Rev. Applied 18, 054078 (2022); arXiv:2203.16003",
            "TCF_GaN_sapphire": "Lee et al. SAW filters; Nicoloiu IEEE Access 2022; Oota JJAP 44 L564 (2005)",
            "k_sapphire": "~35 W/mK @300K (tables; anisotropy 23–46)",
            "k_GaN_epi": "Kyma/NCSU ~130 W/mK thin templates on sapphire",
        },
    }
    with open(DATA / "gate1_alpha.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"RESULT: {'PASS' if final_pass else 'FAIL'}")
    print(f"α_calc = {alpha_nom:.3f} rad/W ; band [{alpha_lo:.3f}, {alpha_hi:.3f}] ; ratio={ratio:.3f}")
    return 0 if final_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
