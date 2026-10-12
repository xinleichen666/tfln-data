#!/workspace/dir13/venv/bin/python
"""Direction-2 Step 2: LN / LNoS thermo-acoustic α + single optical WG photoelastic AO.

Structure (NO coupled double rings / Zhu photon-molecule):
  acoustic MZI bus  +  thermal phase arm  +  ONE optical waveguide overlap region

Gate-1 wording: materials α vs Xu is "same order of magnitude; band covers Xu",
NOT "reproduced 4.03".

Does NOT claim to beat:
  - Shao Optica 2019 suspended MZI VπL ≈ 0.045 V·cm
  - Ni/Bhave/Xu arXiv:2606.05337 non-suspended ~1.004 V·cm (brief: full text not re-read)
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
DATA, FIG = ROOT / "data", ROOT / "fig"
DATA.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

# ─── Physical constants ───────────────────────────────────────────────
C0 = 299792458.0
R_LOAD = 50.0  # ohm

# ─── LN material tables (literature) ─────────────────────────────────
# Elastic c^E [GPa] — Ogi et al., J. Appl. Phys. 92, 2451 (2002) Table I
C11, C12, C13, C14 = 199.56, 55.27, 67.67, 8.7
C33, C44 = 235.2, 59.48
C66 = (C11 - C12) / 2.0  # 72.145
# Piezoelectric e [C/m²] — same Ogi 2002 table
E15, E22, E31, E33 = 3.65, 2.39, 0.31, 1.72
# Photoelastic p (dimensionless) — Andrushchak et al., J. Appl. Phys. 106, 073510 (2009) Table
P11, P12, P13, P14 = -0.021, 0.060, 0.172, -0.052
P31, P33, P41, P44 = 0.141, 0.118, -0.109, 0.121
# Density
RHO_LN = 4700.0  # kg/m³, standard congruent LN
# Thermo-optic / expansion (already used in paperB)
DN_DT = 3.34e-5  # 1/K, Moretti et al., JAP 98, 036101 (2005) — table pin not re-verified here
ALPHA_EXPAND = 1.54e-5  # 1/K a-axis bulk; film on sapphire constrained — ASSUMED bulk value
# Thermal conductivity
K_LN = 4.2  # W/(m·K) ~Slack/literature mid for congruent LN; ASSUMED mid of ~3.5–5.5
K_LN_LO, K_LN_HI = 3.5, 5.5
K_SAP = 35.0  # W/(m·K) sapphire @300 K
# LN SAW TCF (Ward-like / thermoacoustic elasticity)
TCF_LN = -80e-6  # 1/K nominal ASSUMED mid of ~−70…−95 ppm/K for common LN SAW cuts
TCF_LN_LO, TCF_LN_HI = -70e-6, -95e-6

# Optical
LAM_M = 1550e-9
N_TE = 2.14  # TFLN TE neff ASSUMED (paperB-like)
P_EFF = abs(P31)  # Shao Optica 2019: TE couples mainly via p31 to s_xx

# ─── Geometry: Shao-like LNoS + single optical WG (ASSUMED where noted) ─
H_LN = 620e-9  # Shao 2022 LNoS film
W_AC = 7.0e-6  # Shao acoustic rib top width
W_OPT = 1.5e-6  # ASSUMED single optical rib (telecom TE)
L_HEATER = 200e-6  # mid of Shao 100–250 µm heater length
L_AO = 200e-6  # ASSUMED AO overlap = heater/phase-arm length class
W_HEATER = 10e-6
GAP = 6e-6  # Shao min clearance
T_SAP = 430e-6
# Acoustic mode
F_LNOS = 2.45e9  # Shao LNoS phase-modulator band center-ish
F_BULK = 1.385e9  # Shao bulk
V_LNOS = 4165.0  # m/s ≈ f*λ with λ_IDT=1.7 µm (Shao); ASSUMED phase~group for order
V_BULK = 3800.0  # ASSUMED Rayleigh-like on 128Y LN
# Crystal / mode family (stated for report)
CUT_LNOS = "X-cut LN on sapphire; acoustic along crystal Y; quasi-Rayleigh / shear (Shao 2022)"
CUT_BULK = "128° Y-cut LN; acoustic along crystal X; Rayleigh (Shao 2022)"
MODE_OPT = "TE0 @ 1550 nm in single LN rib (no double-ring)"

# IDT / AO
ETA_IDT = 0.10  # conservative ASSUMED (paperB); 0.50 Shao-like sensitivity
ETA_IDT_SHAO = 0.50
# Effective acoustic area for traveling-wave strain energy.
# Unsuspended: mode spreads into sapphire → A_eff = Γ_area * W_AC * H_LN
# Γ_area > 1. ASSUMED; scanned.
GAMMA_AREA = 8.0  # ASSUMED unsuspended spreading
GAMMA_AREA_LO, GAMMA_AREA_HI = 3.0, 20.0
# Optical–acoustic overlap Γ_ov ∈ (0,1)
GAMMA_OV = 0.45  # ASSUMED co-located ribs on same film
GAMMA_OV_LO, GAMMA_OV_HI = 0.25, 0.70
# Stiffness for s_xx energy density ~ 1/2 c S² — use C11
C_EFF = C11 * 1e9  # Pa
# RF heat fraction deposited near AO region (crosstalk) — ASSUMED
XI_RF_HEAT = 0.05  # 5% of P_RF becomes local heat near WG/heater zone
# Heater→optical thermo-optic path: fraction of acoustic-arm ΔT seen by optical WG
XI_H_TO_OPT = 0.35  # ASSUMED (same film, few µm away)
# Acoustic loss
LOSS_DB_MM = 2.4  # keep Xu-scale as order; LNoS may differ — mark ASSUMED transfer from gate1

# Anchors
ALPHA_XU = 4.03  # GaN gate1 anchor (order-of-magnitude only)
SHAO_BULK_DPMW = 2.6
SHAO_LNOS_DPMW = 0.52
VPIL_SHAO = 0.045  # V·cm suspended Optica 2019
VPIL_NI = 1.004  # V·cm non-suspended; arXiv:2606.05337 — full text NOT re-read this turn


def deg_per_mw_to_rad_per_w(x):
    return x * (math.pi / 180.0) * 1000.0


def alpha_materials(tcf, r_th, omega, L, v):
    return -(omega * L / v) * tcf * r_th


def solve_r_th_2d(
    k_film,
    h_film,
    w_wg,
    w_heater=W_HEATER,
    gap=GAP,
    t_sap=T_SAP,
    k_sap=K_SAP,
    L=L_HEATER,
    half_w=80e-6,
    nx=81,
    ny=65,
    power=1.0,
    suspended=False,
):
    """2D thermal R_th. suspended=True → air under film (high R_th); else sapphire sink."""
    x_wg_c = 0.5 * w_heater + gap + 0.5 * w_wg
    xs = np.linspace(-half_w, max(half_w, x_wg_c + 30e-6), nx)
    ys = np.linspace(0.0, h_film + t_sap, ny)
    dx, dy = float(xs[1] - xs[0]), float(ys[1] - ys[0])
    kappa = np.full((ny, nx), k_sap if not suspended else 0.026, dtype=float)
    film = np.broadcast_to(ys[:, None] < h_film, (ny, nx)).copy()
    # film layer: LN everywhere on top for LNoS slab+rib simplification
    # (rib etch residual slab ASSUMED continuous LN sheet for heat)
    kappa[film] = k_film
    if suspended:
        # air below film except we still need a path — use thin tether: keep small κ column
        below = ~film
        kappa[below] = 0.026
        # artificial weak conduction to bottom so Dirichlet is reachable
        kappa[below] = 0.05  # ASSUMED poor suspension thermal path
    N = nx * ny

    def idx(j, i):
        return j * nx + i

    rows, cols, data, b = [], [], [], np.zeros(N)
    q_flux = (power / L) / w_heater

    def add(r, c, v):
        rows.append(r); cols.append(c); data.append(v)

    for j in range(ny):
        for i in range(nx):
            p = idx(j, i)
            if j == ny - 1:
                add(p, p, 1.0)
                continue
            kc = kappa[j, i]
            gL = gR = gU = 0.0
            if i > 0:
                gL = (2 / (1 / kc + 1 / kappa[j, i - 1])) * dy / dx
            if i < nx - 1:
                gR = (2 / (1 / kc + 1 / kappa[j, i + 1])) * dy / dx
            if j > 0:
                gU = (2 / (1 / kc + 1 / kappa[j - 1, i])) * dx / dy
            gD = (2 / (1 / kc + 1 / kappa[j + 1, i])) * dx / dy
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
    # average over film near waveguide x
    i0 = int(np.argmin(np.abs(xs - x_wg_c)))
    i1 = int(np.argmin(np.abs(xs - (x_wg_c + 0.5 * w_wg))))
    lo, hi = min(i0, i1), max(i0, i1) + 1
    dT = float(np.mean(T[film[:, 0], lo:hi])) if False else float(np.mean(T[ys < h_film][:, lo:hi]))
    return dT / power


def strain_from_acoustic_power(P_a, A_eff, v=V_LNOS, c_eff=C_EFF):
    """P_a = (1/2) c S² v A_eff  →  S = sqrt(2 P_a / (c v A))."""
    if P_a <= 0:
        return 0.0
    return math.sqrt(2.0 * P_a / (c_eff * v * A_eff))


def ao_phase(S, L=L_AO, n=N_TE, p_eff=P_EFF, gamma_ov=GAMMA_OV, lam=LAM_M):
    """φ_opt = (2π/λ)(n³/2) p_eff S Γ_ov L  (traveling-wave photoelastic)."""
    dn = 0.5 * (n ** 3) * p_eff * S * gamma_ov
    return (2 * math.pi / lam) * dn * L


def vpi_from_phase_curve(eta_idt, A_eff, L=L_AO, gamma_ov=GAMMA_OV, push_pull=True):
    """Find RF voltage for π differential (push-pull) or π single-arm phase."""
    # φ_arm(P_RF) = ao_phase(S(η P_RF))
    # push-pull: φ_diff = 2 φ_arm; need φ_arm = π/2 for Vπ
    target = 0.5 * math.pi if push_pull else math.pi
    # binary search on P_RF
    lo, hi = 1e-6, 50.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        S = strain_from_acoustic_power(eta_idt * mid, A_eff)
        ph = ao_phase(S, L=L, gamma_ov=gamma_ov)
        if ph < target:
            lo = mid
        else:
            hi = mid
    P_pi = 0.5 * (lo + hi)
    V_pi = math.sqrt(2.0 * R_LOAD * P_pi)
    VpiL = V_pi * (L * 100.0)  # V·cm  (L in m → *100 for cm)
    return {"Vpi_V": V_pi, "VpiL_Vcm": VpiL, "P_RF_pi_W": P_pi,
            "eta_idt": eta_idt, "A_eff_m2": A_eff, "L_m": L, "push_pull": push_pull}


def acoustic_phase(P_H, alpha, phi0=0.0):
    return alpha * P_H + phi0


def group_delay(L, v_g):
    return L / v_g


def joint_transfer(P_RF, P_H, alpha_ac, r_th_opt, eta_idt, A_eff):
    """Acoustic phase, AO optical phase, thermo-optic crosstalk, fidelity proxies."""
    P_RF = np.atleast_1d(P_RF).astype(float)
    P_H = np.atleast_1d(P_H).astype(float)
    # broadcast on mesh
    PR, PH = np.meshgrid(P_RF, P_H, indexing="xy")
    phi_ac = alpha_ac * PH  # heater → acoustic phase
    # RF heating also shifts acoustic phase
    phi_ac = phi_ac + alpha_ac * (XI_RF_HEAT * PR)
    # AO optical phase from acoustic strain (desired)
    Pa = eta_idt * PR
    S = np.sqrt(np.maximum(2.0 * Pa / (C_EFF * V_LNOS * A_eff), 0.0))
    phi_ao = ao_phase(S, L=L_AO, gamma_ov=GAMMA_OV)
    # Thermo-optic on optical WG from heater + RF heat
    dT_opt = r_th_opt * (XI_H_TO_OPT * PH + XI_RF_HEAT * PR)
    phi_to = (2 * math.pi / LAM_M) * DN_DT * dT_opt * L_AO
    # Interferometric phase error (undesired TO + RF-heat acoustic) relative to pure AO intent
    phi_err = phi_to + alpha_ac * XI_RF_HEAT * PR  # rad error budget
    # Carrier-suppression / shift-fidelity proxy for MZI null:
    # ideal null T=0 at φ=π; with error δ → T ≈ (δ/2)² for small δ
    # Extinction degradation: residual power fraction ≈ sin²(φ_err/2)
    residual = np.sin(0.5 * phi_err) ** 2
    csr_db = -10.0 * np.log10(np.clip(residual, 1e-16, 1.0))  # higher = better suppression
    # Sensing: min resolvable phase — take heater-limited 1 mW step on α, and TO floor
    dphi_sense = abs(alpha_ac) * 1e-3  # rad per mW heater (resolution proxy)
    return {
        "P_RF": P_RF, "P_H": P_H, "PR": PR, "PH": PH,
        "phi_ac": phi_ac, "phi_ao": phi_ao, "phi_to": phi_to,
        "phi_err": phi_err, "residual": residual, "csr_db": csr_db,
        "dphi_sense_rad_per_mW": dphi_sense,
    }


def main():
    print("=== Step 2: LN/LNoS thermo-acoustic + single-WG photoelastic ===")

    # --- Thermal R_th ---
    # LNoS: LN film on sapphire
    r_th_lnos = solve_r_th_2d(K_LN, H_LN, W_AC, L=L_HEATER)
    # Bulk LN: treat "substrate" as LN (thick), k_sap → K_LN, thick
    r_th_bulk = solve_r_th_2d(
        K_LN, H_LN, W_AC, L=L_HEATER, t_sap=500e-6, k_sap=K_LN, half_w=100e-6
    )
    # Optical WG thermal (same film; use same R_th scale)
    r_th_opt = r_th_lnos

    omega_lnos = 2 * math.pi * F_LNOS
    omega_bulk = 2 * math.pi * F_BULK
    alpha_lnos = alpha_materials(TCF_LN, r_th_lnos, omega_lnos, L_HEATER, V_LNOS)
    alpha_bulk = alpha_materials(TCF_LN, r_th_bulk, omega_bulk, L_HEATER, V_BULK)

    shao_lnos = deg_per_mw_to_rad_per_w(SHAO_LNOS_DPMW)
    shao_bulk = deg_per_mw_to_rad_per_w(SHAO_BULK_DPMW)
    print(f"R_th LNoS={r_th_lnos:.1f} K/W  bulk={r_th_bulk:.1f} K/W")
    print(f"α_LNoS={alpha_lnos:.3f} rad/W (Shao meas {shao_lnos:.2f})  ratio={alpha_lnos/shao_lnos:.2f}")
    print(f"α_bulk={alpha_bulk:.3f} rad/W (Shao meas {shao_bulk:.2f})  ratio={alpha_bulk/shao_bulk:.2f}")

    # TCF / κ band for LNoS
    band = []
    for tcf in (TCF_LN_LO, TCF_LN, TCF_LN_HI):
        for kln in (K_LN_LO, K_LN, K_LN_HI):
            rt = solve_r_th_2d(kln, H_LN, W_AC, L=L_HEATER, nx=65, ny=55)
            band.append(alpha_materials(tcf, rt, omega_lnos, L_HEATER, V_LNOS))
    band.append(alpha_lnos)
    a_lo, a_hi = float(min(band)), float(max(band))

    # Gate vs Shao: same-order check
    def oom(a, ref):
        r = a / ref
        return bool(a > 0 and 0.1 <= r <= 10), r

    pass_lnos, ratio_lnos = oom(alpha_lnos, shao_lnos)
    pass_bulk, ratio_bulk = oom(alpha_bulk, shao_bulk)

    # --- AO / VπL ---
    A_eff = GAMMA_AREA * W_AC * H_LN
    vp = vpi_from_phase_curve(ETA_IDT, A_eff, L=L_AO, gamma_ov=GAMMA_OV, push_pull=True)
    vp50 = vpi_from_phase_curve(ETA_IDT_SHAO, A_eff, L=L_AO, gamma_ov=GAMMA_OV, push_pull=True)
    # sensitivity band on Γ_area, Γ_ov, η
    vpil_band = []
    for ga in (GAMMA_AREA_LO, GAMMA_AREA, GAMMA_AREA_HI):
        for go in (GAMMA_OV_LO, GAMMA_OV, GAMMA_OV_HI):
            for et in (ETA_IDT, ETA_IDT_SHAO):
                vpil_band.append(
                    vpi_from_phase_curve(et, ga * W_AC * H_LN, L=L_AO, gamma_ov=go)["VpiL_Vcm"]
                )
    vpil_lo, vpil_hi = float(min(vpil_band)), float(max(vpil_band))

    print(f"VπL_calc (η=10%) = {vp['VpiL_Vcm']:.3f} V·cm")
    print(f"VπL_calc (η=50%) = {vp50['VpiL_Vcm']:.3f} V·cm")
    print(f"VπL band = [{vpil_lo:.3f}, {vpil_hi:.3f}] V·cm")
    print(f"Anchors: Shao suspended {VPIL_SHAO} | Ni non-susp {VPIL_NI} (full text not re-read)")
    # Non-claim checks
    beats_shao = vpil_hi < VPIL_SHAO  # would need whole band below — we forbid claiming
    beats_ni = vp["VpiL_Vcm"] < VPIL_NI and vpil_hi < VPIL_NI
    claim_beat_shao = False
    claim_beat_ni = False
    print(f"Claim beat Shao 0.045? {claim_beat_shao} (forbidden). Band below? {beats_shao}")
    print(f"Claim beat Ni 1.004? {claim_beat_ni} (forbidden unless authorized).")

    # --- Joint transfer ---
    P_RF = np.linspace(0, 0.5, 51)
    P_H = np.linspace(0, 0.5, 51)
    jt = joint_transfer(P_RF, P_H, alpha_lnos, r_th_opt, ETA_IDT, A_eff)
    # slopes at origin
    # dφ_ac/dP_H, dφ_ao/dP_RF, dφ_err/dP_H, dφ_err/dP_RF
    dphi_ac_dPH = alpha_lnos
    # finite diff AO
    S1 = strain_from_acoustic_power(ETA_IDT * 0.01, A_eff)
    dphi_ao_dPRF = ao_phase(S1) / 0.01
    dphi_err_dPH = (2 * math.pi / LAM_M) * DN_DT * (r_th_opt * XI_H_TO_OPT) * L_AO
    dphi_err_dPRF = (2 * math.pi / LAM_M) * DN_DT * (r_th_opt * XI_RF_HEAT) * L_AO + alpha_lnos * XI_RF_HEAT

    tau_g = group_delay(L_AO, V_LNOS)

    # --- Figures ---
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))

    ax = axes[0, 0]
    labs = ["Xu GaN\n(meas.)", "Gate1 GaN\n(calc band)", "Shao LNoS\n(meas.)", "LNoS calc", "Shao bulk\n(meas.)", "bulk calc"]
    # gate1 band mid
    g1 = json.load(open(DATA / "gate1_alpha.json"))
    vals = [ALPHA_XU, g1["alpha_calc_rad_per_W"], shao_lnos, alpha_lnos, shao_bulk, alpha_bulk]
    cols = ["#F58518", "#4C78A8", "#54A24B", "#72B7B2", "#E45756", "#B279A2"]
    ax.bar(range(6), vals, color=cols)
    ax.errorbar([1], [g1["alpha_calc_median_rad_per_W"]],
                yerr=[[g1["alpha_calc_median_rad_per_W"] - g1["alpha_calc_band_rad_per_W"][0]],
                      [g1["alpha_calc_band_rad_per_W"][1] - g1["alpha_calc_median_rad_per_W"]]],
                fmt="none", ecolor="k", capsize=3)
    y0 = max(alpha_lnos - a_lo, 0.0); y1 = max(a_hi - alpha_lnos, 0.0)
    ax.errorbar([3], [alpha_lnos], yerr=[[y0], [y1]], fmt="none", ecolor="k", capsize=3)
    ax.set_xticks(range(6)); ax.set_xticklabels(labs, fontsize=7)
    ax.set_ylabel(r"$\alpha$ [rad/W]")
    ax.set_title("Thermo-acoustic α (same-order wording for Xu)")
    ax.axhspan(0.1 * ALPHA_XU, 10 * ALPHA_XU, color="orange", alpha=0.06)

    ax = axes[0, 1]
    ax.bar([0, 1, 2], [vp["VpiL_Vcm"], VPIL_NI, VPIL_SHAO],
           color=["#4C78A8", "#F58518", "#54A24B"],
           tick_label=["calc TW LNoS\n(η=10%)", "Ni non-susp\n1.004\n(not re-read)", "Shao susp.\n0.045"])
    ax.errorbar([0], [vp["VpiL_Vcm"]],
                yerr=[[vp["VpiL_Vcm"] - vpil_lo], [vpil_hi - vp["VpiL_Vcm"]]],
                fmt="none", ecolor="k", capsize=4)
    ax.set_ylabel(r"$V_\pi L$ [V·cm]")
    ax.set_title("AO strength vs anchors (NO beat-claim)")
    ax.set_yscale("log")

    ax = axes[1, 0]
    # φ_ao vs P_RF at P_H=0; φ_ac vs P_H at P_RF=0
    ax.plot(P_RF, jt["phi_ao"][0, :], color="#4C78A8", lw=2, label=r"$\phi_{AO}(P_{RF})$")
    ax.plot(P_H, alpha_lnos * P_H, color="#E45756", lw=2, label=r"$\phi_{ac}(P_H)=\alpha P_H$")
    ax.plot(P_H, dphi_err_dPH * P_H, color="#F58518", ls="--", label=r"$\phi_{err}$ from heater TO")
    ax.set_xlabel("Power [W]")
    ax.set_ylabel("Phase [rad]")
    ax.set_title("Joint knobs (LNoS, single WG)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    im = ax.pcolormesh(jt["PR"], jt["PH"], jt["csr_db"], shading="auto", cmap="viridis")
    ax.set_xlabel(r"$P_{RF}$ [W]"); ax.set_ylabel(r"$P_H$ [W]")
    ax.set_title("MZI null CSR proxy [dB] (thermal crosstalk)")
    fig.colorbar(im, ax=ax, fraction=0.046, label="CSR proxy dB")

    fig.suptitle("Step 2: LN/LNoS thermo-acoustic + photoelastic (no double-ring)", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "step2_joint_transfer.png", dpi=160)
    fig.savefig(FIG / "step2_joint_transfer.pdf")
    plt.close(fig)

    # --- JSON ---
    out = {
        "step": 2,
        "structure": "acoustic MZI bus + thermal phase arm + single optical WG (NO double-ring)",
        "gate1_wording": "same order of magnitude as Xu 4.03; uncertainty band covers Xu — NOT 'reproduced 4.03'",
        "thermoacoustic": {
            "alpha_LNoS_rad_per_W": alpha_lnos,
            "alpha_LNoS_band": [a_lo, a_hi],
            "alpha_bulk_rad_per_W": alpha_bulk,
            "Shao_LNoS_rad_per_W": shao_lnos,
            "Shao_bulk_rad_per_W": shao_bulk,
            "ratio_LNoS_calc_over_Shao": ratio_lnos,
            "ratio_bulk_calc_over_Shao": ratio_bulk,
            "LNoS_same_order_as_Shao": pass_lnos,
            "bulk_same_order_as_Shao": pass_bulk,
            "R_th_LNoS": r_th_lnos,
            "R_th_bulk": r_th_bulk,
            "L_heater_m": L_HEATER,
            "f_LNoS_Hz": F_LNOS,
            "f_bulk_Hz": F_BULK,
            "v_LNoS": V_LNOS,
            "v_bulk": V_BULK,
            "cut_mode_LNoS": CUT_LNOS,
            "cut_mode_bulk": CUT_BULK,
            "group_delay_s": tau_g,
        },
        "acousto_optic": {
            "VpiL_calc_Vcm_eta10": vp["VpiL_Vcm"],
            "VpiL_calc_Vcm_eta50": vp50["VpiL_Vcm"],
            "VpiL_band_Vcm": [vpil_lo, vpil_hi],
            "Vpi_V_eta10": vp["Vpi_V"],
            "P_RF_pi_W_eta10": vp["P_RF_pi_W"],
            "L_ao_m": L_AO,
            "p_eff": P_EFF,
            "p_eff_source": "Andrushchak JAP 106, 073510 (2009) p31=0.141; Shao Optica 2019 uses p31 for TE",
            "n_TE": N_TE,
            "lambda_m": LAM_M,
            "Gamma_area_ASSUMED": GAMMA_AREA,
            "Gamma_ov_ASSUMED": GAMMA_OV,
            "A_eff_m2": A_eff,
            "eta_idt_main": ETA_IDT,
            "optical_mode": MODE_OPT,
            "anchor_Shao_suspended_VpiL_Vcm": VPIL_SHAO,
            "anchor_Ni_nonsuspended_VpiL_Vcm": VPIL_NI,
            "Ni_flag": "arXiv:2606.05337 — brief says full text not re-read; keep as flagged anchor only",
            "claim_beats_Shao_0p045": claim_beat_shao,
            "claim_beats_Ni_1p004": claim_beat_ni,
            "note": "Traveling-wave unsuspended estimate; Shao 0.045 is suspended RESONANT MZI — not a fair beat target",
        },
        "joint_crosstalk": {
            "dphi_ac_dP_H_rad_per_W": dphi_ac_dPH,
            "dphi_ao_dP_RF_rad_per_W_at_10mW_scale": dphi_ao_dPRF,
            "dphi_err_dP_H_rad_per_W": dphi_err_dPH,
            "dphi_err_dP_RF_rad_per_W": dphi_err_dPRF,
            "xi_RF_heat_ASSUMED": XI_RF_HEAT,
            "xi_H_to_opt_ASSUMED": XI_H_TO_OPT,
            "sense_rad_per_mW_heater": jt["dphi_sense_rad_per_mW"],
            "sensing_definition": "heater-limited Δφ = |α|×1 mW; NOT a gas-sensing card",
        },
        "materials": {
            "elastic_GPa": {"c11": C11, "c12": C12, "c13": C13, "c14": C14, "c33": C33, "c44": C44,
                            "source": "Ogi et al., J. Appl. Phys. 92, 2451 (2002) Table I"},
            "piezoelectric_C_per_m2": {"e15": E15, "e22": E22, "e31": E31, "e33": E33,
                                       "source": "Ogi et al., JAP 92, 2451 (2002) Table I"},
            "photoelastic": {"p11": P11, "p12": P12, "p13": P13, "p14": P14,
                             "p31": P31, "p33": P33, "p41": P41, "p44": P44,
                             "source": "Andrushchak et al., J. Appl. Phys. 106, 073510 (2009)"},
            "k_LN_W_per_mK": K_LN,
            "k_sapphire": K_SAP,
            "TCF_LN_1_per_K": TCF_LN,
            "rho_kg_per_m3": RHO_LN,
        },
        "non_claims": [
            "Do not claim α reproduced Xu 4.03 — only same order; band covers Xu (gate1).",
            "Do not claim VπL beats Shao suspended 0.045 V·cm.",
            "Do not claim VπL beats Ni/Bhave 1.004 V·cm without full-text re-read + fair geometry.",
            "Simulation only; no fabrication; no 'on-chip already integrates shift+delay'.",
            "No Zhu coupled-double-ring / photon-molecule geometry.",
            "No unverified gas-sensing application card.",
        ],
    }
    with open(DATA / "step2_summary.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("Wrote data/step2_summary.json and fig/step2_joint_transfer.*")
    print(f"PASS-quality: LNoS α same-order Shao? {pass_lnos}; bulk? {pass_bulk}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
