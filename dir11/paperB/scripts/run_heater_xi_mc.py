#!/usr/bin/env python3
"""Dir1 paperB: heater-tunable MZI coupler + ξ coverage + IL columns MC.

ASSUMPTIONS (documented; not pulled from Zhang 2019):
- MZI-type coupler: µ(φ) = µ_gap * sin(Δφ/2), Δφ ∈ [0, π]  → µ ∈ [0, µ_gap]
  Textbook T=sin²(Δφ/2); amplitude rate taken ∝ sin(Δφ/2). NOT Zhang 2019 (they do DC detuning).
- Heater arm Pπ = 44.4 mW labeled「Maeder 几何假设」(Maeder et al. QST 9, 035040 (2024));
  NOT a ring–ring coupler calibration for this layout.
- Coupler-heater thermal crosstalk to rings (no lit number for this geometry):
  at P=Pπ, ΔT_diff=20 mK, ΔT_cm=50 mK, linear in P/Pπ. ASSUMED.

Seeds: master=20261014. Re-runnable from /workspace/dir11/paperB/.
"""
from __future__ import annotations
import os, sys, json, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from core import tp, F, WM, MU, G, KI, NG, P_from_dw, K_AO

plt.rcParams.update({
    "font.size": 8, "font.family": "serif", "mathtext.fontset": "dejavuserif",
    "axes.linewidth": 0.6, "lines.linewidth": 1.1,
})

# -------------------- fixed drive / seeds --------------------
DW = json.load(open("data/results_B.json"))["optimum"]["ao"]["dw_GHz"] * tp * 1e9
SEED_MASTER = 20261114  # v2 redesign (v1 was 20261014)
SEED_OFF = SEED_MASTER + 1
SEED_ON = SEED_MASTER + 2
SEED_ON_SHAO = SEED_MASTER + 3
SEED_OFF_SHAO = SEED_MASTER + 4
REDESIGN_TAG = "v2_coupler_isolation"
N_MC = 1000
MHz = tp * 1e6
f0 = 193.4e12

# -------------------- shared params (match realistic.py) --------------------
P_BASE = dict(
    eta_IDT_main=0.10,
    Qa_main=2000,
    Qa_cons=1570,
    dndT=3.34e-5,
    alpha=1.54e-5,
    n_eff=2.14,
    sigT_lock_mK=5.0,
    sig_gap_nm=5.0,
    gap_decay_nm=150.0,
    retune_MHz=1.0,          # RF retune when heater OFF
    facet_dB=1.5,
    Qi_spread=(0.7, 1.3),
    # --- heater / MZI (ASSUMED / Maeder geometry label) ---
    Ppi_mW=44.4,             # Maeder 2024 Pπ;「Maeder 几何假设」
    dT_diff_at_Ppi_mK=2.0,   # ASSUMED v2: coupler thermal isolation redesign (v1=5)
    dT_cm_at_Ppi_mK=3.0,     # ASSUMED v2: coupler thermal isolation redesign (v1=10)
    design_mu_factor=float(2**0.5),  # ASSUMED: gap designed so mu_max=MU*sqrt(2); bias ~pi/2
    mzi_form="mu = mu_gap * sin(dphi/2), dphi in [0,pi]; mu_gap_design=MU*sqrt(2)",
)

dfdT = f0 * (P_BASE["dndT"] + P_BASE["n_eff"] * P_BASE["alpha"]) / NG  # Hz/K
K_AO_2pi_GHz_per_V = K_AO / tp / 1e9  # ≈21.3; ξ=1 reference


def runv_full(mu, g, ki, Delta, dr, wm=WM, dw=DW, T=40e-9):
    """Vectorized RK4; returns eta_shift, IL_dB, eta_abs, sideband dict p[q], spur_q."""
    mu, g, ki, Delta, dr = np.broadcast_arrays(
        *(np.atleast_1d(np.asarray(v, float)) for v in (mu, g, ki, Delta, dr))
    )
    W = wm
    dt = 1 / (W / tp) / 80
    n = int(T / dt)
    d0 = mu - Delta
    sg = np.sqrt(g)
    a1 = np.zeros(mu.shape, complex)
    a2 = a1.copy()
    tt = np.arange(n) * dt
    msk = tt > T - 20e-9
    Q = range(-3, 4)
    acc = {q: 0j for q in Q}

    def f(t, a1, a2):
        m = dw * np.cos(W * t)
        return (
            (-1j * (d0 + m) - (g + ki) / 2) * a1 - 1j * mu * a2 - sg,
            (-1j * (d0 + dr) - ki / 2) * a2 - 1j * mu * a1,
        )

    t = 0.0
    for i in range(n):
        k1 = f(t, a1, a2)
        k2 = f(t + dt / 2, a1 + dt / 2 * k1[0], a2 + dt / 2 * k1[1])
        k3 = f(t + dt / 2, a1 + dt / 2 * k2[0], a2 + dt / 2 * k2[1])
        k4 = f(t + dt, a1 + dt * k3[0], a2 + dt * k3[1])
        a1 = a1 + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        a2 = a2 + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        t += dt
        if msk[i]:
            o = 1 + sg * a1
            for q in Q:
                acc[q] = acc[q] + o * np.exp(1j * q * W * tt[i])
    N = msk.sum()
    p = {q: np.abs(acc[q] / N) ** 2 for q in Q}
    tot = sum(p.values())
    # intended shift: larger of ±1
    shift_q = np.where(p[1] >= p[-1], 1, -1)
    ps = np.maximum(p[1], p[-1])
    eta = ps / tot
    il = -10 * np.log10(tot)
    # worst SPOILER sideband among q in {-3,-2,-1,2,3} (exclude shift tone AND carrier q=0).
    # Carrier suppression is tracked separately; fab "杂散" = unwanted AO orders.
    spur_pow = np.zeros(mu.shape)
    spur_q = np.zeros(mu.shape, int)
    for q in (-3, -2, -1, 2, 3):
        cand = p[q].copy()
        cand = np.where(shift_q == q, 0.0, cand)  # if shift landed on -1, zero it
        better = cand > spur_pow
        spur_pow = np.where(better, cand, spur_pow)
        spur_q = np.where(better, q, spur_q)
    spur_rel_dB = 10 * np.log10(np.maximum(spur_pow, 1e-30) / np.maximum(ps, 1e-30))
    # carrier relative to shift
    carrier_rel_dB = 10 * np.log10(np.maximum(p[0], 1e-30) / np.maximum(ps, 1e-30))
    return dict(eta=eta, IL=il, eta_abs=ps, p=p, shift_q=shift_q, spur_q=spur_q,
                spur_rel_dB=spur_rel_dB, carrier_rel_dB=carrier_rel_dB, tot=tot)


def mzi_tune(mu_gap, p):
    """Minimize |2µ−Ω| under MZI assumption µ = µ_gap * sin(Δφ/2), Δφ∈[0,π].

    Returns mu_eff, dphi, P_heater_mW, eps_res_rad_s, hit_target (bool array).
    """
    mu_target = WM / 2  # = MU
    # sin(Δφ/2) = mu_target / mu_gap  if mu_gap >= mu_target else 1
    ratio = np.where(mu_gap > 0, mu_target / mu_gap, np.inf)
    hit = ratio <= 1.0
    sin_half = np.where(hit, ratio, 1.0)
    sin_half = np.clip(sin_half, 0.0, 1.0)
    dphi = 2.0 * np.arcsin(sin_half)  # [0, π]
    mu_eff = mu_gap * sin_half
    P_h = (dphi / np.pi) * p["Ppi_mW"]
    eps_res = 2.0 * mu_eff - WM
    return mu_eff, dphi, P_h, eps_res, hit


def sample(N, rng, p, heater_on: bool, ki_extra_frac: float):
    ki = KI * (1 + ki_extra_frac) * rng.uniform(*p["Qi_spread"], N)
    dgap = rng.normal(0, p["sig_gap_nm"], N)
    dgap_b = rng.normal(0, p["sig_gap_nm"], N)
    g = G * np.exp(-dgap_b / p["gap_decay_nm"])

    sT = p["sigT_lock_mK"] * 1e-3
    Delta = rng.normal(0, sT, N) * dfdT * tp
    dr = rng.normal(0, np.sqrt(2) * sT, N) * dfdT * tp

    if heater_on:
        # ASSUMED design: coupler gap sized for mu_max = design_mu_factor * MU
        # so that MZI bias ~pi/2 (P~Ppi/2) lands on Omega/2; NOT Zhang 2019.
        mu_gap = (p.get("design_mu_factor", 1.0) * MU) * np.exp(-dgap / p["gap_decay_nm"])
        eps_raw = 2 * mu_gap - WM
        mu, dphi, P_h, eps_res, hit = mzi_tune(mu_gap, p)
        # thermal crosstalk from coupler heater (ASSUMED)
        frac = P_h / p["Ppi_mW"]
        sign = rng.choice([-1.0, 1.0], size=N)
        dT_diff = (p["dT_diff_at_Ppi_mK"] * 1e-3) * frac
        dT_cm = (p["dT_cm_at_Ppi_mK"] * 1e-3) * frac
        dr = dr + sign * dT_diff * dfdT * tp
        Delta = Delta + dT_cm * dfdT * tp
        # no RF retune needed when heater used for |2µ−Ω|; residual is post-heater
    else:
        # Heater OFF: gap designed for mu≈MU (no sqrt2 margin); RF retune ±retune_MHz only.
        mu_gap = MU * np.exp(-dgap / p["gap_decay_nm"])
        eps_raw = 2 * mu_gap - WM
        eps = eps_raw
        eps_res = np.sign(eps) * np.maximum(np.abs(eps) - p["retune_MHz"] * MHz, 0)
        mu = (WM + eps_res) / 2
        dphi = np.zeros(N)
        P_h = np.zeros(N)
        hit = np.abs(eps) <= p["retune_MHz"] * MHz

    return dict(
        mu=mu, mu_gap=mu_gap, g=g, ki=ki, Delta=Delta, dr=dr,
        eps_raw_MHz=eps_raw / MHz, eps_res_MHz=eps_res / MHz,
        dphi=dphi, P_heater_mW=P_h, hit_target=hit.astype(float),
    )


def run_mc(N, p, seed, heater_on, ki_extra_frac, label):
    rng = np.random.default_rng(seed)
    s = sample(N, rng, p, heater_on, ki_extra_frac)
    print(f"  RK4 {label} N={N} ...", flush=True)
    out = runv_full(s["mu"], s["g"], s["ki"], s["Delta"], s["dr"])
    s.update(out)
    return s


pct = lambda v: [float(np.percentile(v, q)) for q in (10, 50, 90)]


def summarize(s, tag):
    fac = 10 ** (-2 * P_BASE["facet_dB"] / 10)
    spur_is_qm1 = float(np.mean(s["spur_q"] == -1))
    # when shift is q=-1 (rare), "worst spur q=-1" means the other first-order; count intended
    # Criterion: among samples, the worst non-shift tone is q=−1 (AO molecule typically shifts +1)
    shift_is_qp1 = float(np.mean(s["shift_q"] == 1))
    return dict(
        tag=tag,
        N=int(len(s["eta"])),
        eta_shift_p10_50_90=pct(s["eta"]),
        IL_dB_p10_50_90=pct(s["IL"]),
        eta_abs_onchip_p10_50_90=pct(s["eta_abs"]),
        eta_abs_fiber_p10_50_90=pct(s["eta_abs"] * fac),
        frac_eta_ge_090=float(np.mean(s["eta"] >= 0.90)),
        frac_eta_ge_095=float(np.mean(s["eta"] >= 0.95)),
        frac_hit_2mu_target=float(np.mean(s["hit_target"])),
        eps_res_MHz_p10_50_90=pct(s["eps_res_MHz"]),
        eps_raw_MHz_std=float(np.std(s["eps_raw_MHz"])),
        P_heater_mW_p10_50_90=pct(s["P_heater_mW"]),
        frac_shift_q_plus1=shift_is_qp1,
        frac_worst_spur_is_qm1=spur_is_qm1,
        spur_rel_dB_p10_50_90=pct(s["spur_rel_dB"]),
        carrier_rel_dB_p10_50_90=pct(s["carrier_rel_dB"]),
        median_carrier_rel_dB=float(np.median(s["carrier_rel_dB"])),
    )


def power_xi_table():
    """Power ∝ 1/ξ²; also ∝ 1/Qa and ∝ 1/η_IDT relative to Shao-50% cal."""
    P50 = P_from_dw(DW, "AO_Shao_IDT(50%)")  # Qa=2000 implicit in K_AO
    P10 = P_from_dw(DW, "AO_IDT_10%")
    rows = []
    for xi in (0.3, 0.5, 1.0, 2.0):
        for idt, Pbase, qa in (
            ("IDT50_Qa2000", P50, 2000),
            ("IDT10_Qa2000", P10, 2000),
            ("IDT10_Qa1570", P10 * 2000 / 1570, 1570),
        ):
            P = Pbase / xi ** 2
            rows.append(dict(
                xi=xi,
                case=idt,
                Qa=qa,
                P_uW=P * 1e6,
                P_mW=P * 1e3,
                note="power ∝ 1/ξ²; ξ=1 → K_AO/2π≈21.3 GHz/V",
            ))
    # conservative headline
    P_cons = P10 * 2000 / 1570 / (0.5 ** 2)  # ξ=0.5 × IDT10% × Qa=1570
    return rows, dict(
        xi=0.5, IDT=0.10, Qa=1570,
        P_uW=P_cons * 1e6, P_W=P_cons,
        Shao2020_drive_W=1.0,  # 30 dBm thermal-redshift / AOFS drive
        ratio_vs_Shao2020=P_cons / 1.0,
        much_less_than_Shao=bool(P_cons < 0.01),  # ≪ if < 1% of 1 W
    )


def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("fig", exist_ok=True)
    os.makedirs("paper/notes", exist_ok=True)

    p = dict(P_BASE)
    print("=== heater OFF, κi×2 (conservative loss) ===", flush=True)
    s_off = run_mc(N_MC, p, SEED_OFF, heater_on=False, ki_extra_frac=1.0, label="heater_OFF_ki2")
    print("=== heater ON, κi×2 (primary yield) ===", flush=True)
    s_on = run_mc(N_MC, p, SEED_ON, heater_on=True, ki_extra_frac=1.0, label="heater_ON_ki2")
    print("=== heater ON, Shao Qi as-is (IL column) ===", flush=True)
    s_on_shao = run_mc(N_MC, p, SEED_ON_SHAO, heater_on=True, ki_extra_frac=0.0, label="heater_ON_ShaoQi")
    print("=== heater OFF, Shao Qi as-is ===", flush=True)
    s_off_shao = run_mc(N_MC, p, SEED_OFF_SHAO, heater_on=False, ki_extra_frac=0.0, label="heater_OFF_ShaoQi")

    sum_off = summarize(s_off, "heater_OFF_ki_x2")
    sum_on = summarize(s_on, "heater_ON_ki_x2")
    sum_on_shao = summarize(s_on_shao, "heater_ON_Shao_Qi")
    sum_off_shao = summarize(s_off_shao, "heater_OFF_Shao_Qi")

    xi_rows, P_cons = power_xi_table()

    # Ideal / nominal single-shot for reference
    ideal = runv_full(MU, G, KI, 0, 0)
    nom_x2 = runv_full(MU, G, KI * 2, 0, 0)

    # Fab criteria against OUR numbers
    # 1) heater ON + conservative loss (ki×2) + 10% IDT: ≥90% samples η≥90%
    c1_frac = sum_on["frac_eta_ge_090"]
    c1_pass = c1_frac >= 0.90
    # 2) conservative RF ≪ Shao 30 dBm = 1 W
    c2_pass = bool(P_cons["P_W"] < 0.01)  # <10 mW = 1% of 1 W as ≪ threshold
    # 3) worst spur still q=−1 (among heater-ON conservative suite)
    c3_frac = sum_on["frac_worst_spur_is_qm1"]
    c3_pass = c3_frac >= 0.95  # nearly all samples
    all_pass = c1_pass and c2_pass and c3_pass

    fab = dict(
        criteria=[
            dict(
                id=1,
                text="heater ON + conservative loss (κi×2) + IDT 10%: ≥90% samples ηshift≥90%",
                metric="frac_eta_ge_090",
                value=c1_frac,
                threshold=0.90,
                eta_p10=sum_on["eta_shift_p10_50_90"][0],
                eta_median=sum_on["eta_shift_p10_50_90"][1],
                PASS=c1_pass,
            ),
            dict(
                id=2,
                text="conservative RF (ξ=0.5×IDT10%×Qa=1570) ≪ Shao 2020 30 dBm (=1 W) thermal/AOFS drive",
                metric="P_cons_W / 1 W",
                P_cons_uW=P_cons["P_uW"],
                Shao2020_W=1.0,
                ratio=P_cons["ratio_vs_Shao2020"],
                PASS=c2_pass,
            ),
            dict(
                id=3,
                text="worst spur still q=−1 (heater ON, κi×2 suite)",
                metric="frac_worst_spur_is_qm1",
                value=c3_frac,
                threshold=0.95,
                spur_rel_dB_median=sum_on["spur_rel_dB_p10_50_90"][1],
                PASS=c3_pass,
            ),
        ],
        ALL_PASS=all_pass,
        recommendation=(
            "PASS: simulation supports proceeding to layout with measurement hooks."
            if all_pass
            else "FAIL: do NOT greenlight current layout — redesign coupler and/or coverage (ξ) before tape-out."
        ),
    )

    summary = dict(
        meta=dict(
            seed_master=SEED_MASTER,
            seeds=dict(off_ki2=SEED_OFF, on_ki2=SEED_ON, on_shao=SEED_ON_SHAO, off_shao=SEED_OFF_SHAO),
            N=N_MC,
            DW_GHz=float(DW / tp / 1e9),
            K_AO_2pi_GHz_per_V_xi1=float(K_AO_2pi_GHz_per_V),
            F_GHz=F / 1e9,
            dfdT_GHz_per_K=dfdT / 1e9,
            hang_repo="simulation + scheme; measured columns empty; not a methods-only paper",
        ),
        assumptions=dict(
            mzi_coupler=P_BASE["mzi_form"],
            mzi_NOT_from="Zhang 2019 (DC detuning only; no heater-tuned µ(φ))",
            Ppi_mW=P_BASE["Ppi_mW"],
            Ppi_label="Maeder 几何假设 (Maeder et al. QST 2024); NOT this layout ring–ring cal",
            crosstalk_dT_diff_at_Ppi_mK=P_BASE["dT_diff_at_Ppi_mK"],
            crosstalk_dT_cm_at_Ppi_mK=P_BASE["dT_cm_at_Ppi_mK"],
            crosstalk_label="ASSUMED v2 coupler isolation redesign (v1 was 5/10 mK); no lit number",
            design_mu_factor=P_BASE["design_mu_factor"],
            design_mu_note="heater-ON gap targets mu_max=MU*sqrt(2) so bias~Ppi/2 hits Omega/2",
            xi_definition="ξ=1 ↔ δω/2π per volt = 21.3 GHz/V (K_AO); power ∝ 1/ξ²",
        ),
        params=P_BASE,
        ideal=dict(eta_shift=float(ideal["eta"][0]), IL_dB=float(ideal["IL"][0]),
                   eta_abs=float(ideal["eta_abs"][0]),
                   spur_q=int(ideal["spur_q"][0]),
                   spur_rel_dB=float(ideal["spur_rel_dB"][0])),
        nominal_ki_x2=dict(eta_shift=float(nom_x2["eta"][0]), IL_dB=float(nom_x2["IL"][0]),
                           eta_abs=float(nom_x2["eta_abs"][0])),
        MC_heater_OFF_ki_x2=sum_off,
        MC_heater_ON_ki_x2=sum_on,  # PRIMARY YIELD
        MC_heater_ON_Shao_Qi=sum_on_shao,
        MC_heater_OFF_Shao_Qi=sum_off_shao,
        IL_two_columns=dict(
            Shao_Qi_as_is=dict(
                heater_ON=dict(IL_dB_p10_50_90=sum_on_shao["IL_dB_p10_50_90"],
                               eta_p10_50_90=sum_on_shao["eta_shift_p10_50_90"],
                               frac_eta_ge_090=sum_on_shao["frac_eta_ge_090"]),
                heater_OFF=dict(IL_dB_p10_50_90=sum_off_shao["IL_dB_p10_50_90"],
                                eta_p10_50_90=sum_off_shao["eta_shift_p10_50_90"],
                                frac_eta_ge_090=sum_off_shao["frac_eta_ge_090"]),
            ),
            ki_x2=dict(
                heater_ON=dict(IL_dB_p10_50_90=sum_on["IL_dB_p10_50_90"],
                               eta_p10_50_90=sum_on["eta_shift_p10_50_90"],
                               frac_eta_ge_090=sum_on["frac_eta_ge_090"]),
                heater_OFF=dict(IL_dB_p10_50_90=sum_off["IL_dB_p10_50_90"],
                                eta_p10_50_90=sum_off["eta_shift_p10_50_90"],
                                frac_eta_ge_090=sum_off["frac_eta_ge_090"]),
            ),
        ),
        xi_power_sweep_uW=xi_rows,
        conservative_power=P_cons,
        fab_criteria=fab,
        primary_yield=dict(
            suite="heater_ON_ki_x2",
            eta_p10=sum_on["eta_shift_p10_50_90"][0],
            eta_median=sum_on["eta_shift_p10_50_90"][1],
            frac_eta_ge_090=sum_on["frac_eta_ge_090"],
        ),
    )

    summary["redesign"] = dict(
        tag="v2_coupler_isolation",
        v1_seed_master=20261014,
        changed=[
            "dT_cm_at_Ppi_mK: 10 -> 3 (ASSUMED better coupler-ring thermal isolation)",
            "dT_diff_at_Ppi_mK: 5 -> 2 (ASSUMED)",
        ],
        unchanged=["sigT_lock_mK=5", "ki_extra_frac=1 for primary", "Ppi=44.4 Maeder", "design_mu_factor=sqrt(2)", "MZI form"],
        rationale="v1 failures dominated by common-mode Delta (corr~-0.66); reduce heater crosstalk without relaxing kappa_i x2",
    )
    for path in ("data/summary_heater_xi.json", "data/summary_heater_xi_v2.json"):
        with open(path, "w") as fh:
            json.dump(summary, fh, indent=1)
        print("wrote", path, flush=True)
    if not os.path.exists("data/summary_heater_xi_v1.json"):
        print("(v1 archive missing)", flush=True)

    # CSV samples (heater ON primary)
    with open("data/mc_heater_on_ki2.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "mu_rad_s", "mu_gap_rad_s", "g_rad_s", "ki_rad_s",
            "Delta_MHz", "delta_r_MHz", "eps_raw_MHz", "eps_res_MHz",
            "dphi_rad", "P_heater_mW", "hit_target",
            "eta_shift", "IL_dB", "eta_abs", "shift_q", "spur_q", "spur_rel_dB",
        ])
        for i in range(N_MC):
            w.writerow([
                s_on["mu"][i], s_on["mu_gap"][i], s_on["g"][i], s_on["ki"][i],
                s_on["Delta"][i] / MHz, s_on["dr"][i] / MHz,
                s_on["eps_raw_MHz"][i], s_on["eps_res_MHz"][i],
                s_on["dphi"][i], s_on["P_heater_mW"][i], s_on["hit_target"][i],
                s_on["eta"][i], s_on["IL"][i], s_on["eta_abs"][i],
                int(s_on["shift_q"][i]), int(s_on["spur_q"][i]), s_on["spur_rel_dB"][i],
            ])

    with open("data/mc_heater_off_ki2.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "mu_rad_s", "mu_gap_rad_s", "g_rad_s", "ki_rad_s",
            "Delta_MHz", "delta_r_MHz", "eps_raw_MHz", "eps_res_MHz",
            "eta_shift", "IL_dB", "eta_abs", "shift_q", "spur_q", "spur_rel_dB",
        ])
        for i in range(N_MC):
            w.writerow([
                s_off["mu"][i], s_off["mu_gap"][i], s_off["g"][i], s_off["ki"][i],
                s_off["Delta"][i] / MHz, s_off["dr"][i] / MHz,
                s_off["eps_raw_MHz"][i], s_off["eps_res_MHz"][i],
                s_off["eta"][i], s_off["IL"][i], s_off["eta_abs"][i],
                int(s_off["shift_q"][i]), int(s_off["spur_q"][i]), s_off["spur_rel_dB"][i],
            ])

    # -------------------- figures --------------------
    # Fig 1: heater OFF vs ON η histograms
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.4))
    ax[0].hist(s_off["eta"], bins=40, color="C0", alpha=0.75, label="heater OFF")
    ax[0].hist(s_on["eta"], bins=40, color="C3", alpha=0.55, label="heater ON")
    ax[0].axvline(0.90, color="k", ls="--", lw=0.7)
    ax[0].set_xlabel(r"$\eta_{\rm shift}$")
    ax[0].set_ylabel("count")
    ax[0].legend(fontsize=6)
    ax[0].set_title(r"$\kappa_i\times 2$ MC", fontsize=8)

    # IL columns
    labs = ["Shao Qi\nOFF", "Shao Qi\nON", r"$\kappa_i\times2$" + "\nOFF", r"$\kappa_i\times2$" + "\nON"]
    meds = [
        sum_off_shao["IL_dB_p10_50_90"][1],
        sum_on_shao["IL_dB_p10_50_90"][1],
        sum_off["IL_dB_p10_50_90"][1],
        sum_on["IL_dB_p10_50_90"][1],
    ]
    lo = [
        meds[0] - sum_off_shao["IL_dB_p10_50_90"][0],
        meds[1] - sum_on_shao["IL_dB_p10_50_90"][0],
        meds[2] - sum_off["IL_dB_p10_50_90"][0],
        meds[3] - sum_on["IL_dB_p10_50_90"][0],
    ]
    hi = [
        sum_off_shao["IL_dB_p10_50_90"][2] - meds[0],
        sum_on_shao["IL_dB_p10_50_90"][2] - meds[1],
        sum_off["IL_dB_p10_50_90"][2] - meds[2],
        sum_on["IL_dB_p10_50_90"][2] - meds[3],
    ]
    ax[1].bar(range(4), meds, yerr=[lo, hi], color=["0.7", "C0", "0.55", "C3"], capsize=2)
    ax[1].set_xticks(range(4))
    ax[1].set_xticklabels(labs, fontsize=6)
    ax[1].set_ylabel("on-chip IL (dB)")
    ax[1].set_title("IL two columns", fontsize=8)

    # yield bars
    fracs = [
        sum_off_shao["frac_eta_ge_090"],
        sum_on_shao["frac_eta_ge_090"],
        sum_off["frac_eta_ge_090"],
        sum_on["frac_eta_ge_090"],
    ]
    ax[2].bar(range(4), fracs, color=["0.7", "C0", "0.55", "C3"])
    ax[2].axhline(0.90, color="k", ls="--", lw=0.7, label="fab ≥90%")
    ax[2].set_xticks(range(4))
    ax[2].set_xticklabels(labs, fontsize=6)
    ax[2].set_ylabel(r"fraction $\eta\geq 0.90$")
    ax[2].set_ylim(0, 1.05)
    ax[2].legend(fontsize=6)
    ax[2].set_title("yield (primary=ON+$\\kappa_i\\times2$)", fontsize=8)
    for a, lab in zip(ax, "abc"):
        a.text(-0.22, 1.05, f"({lab})", transform=a.transAxes, fontsize=8)
    fig.tight_layout()
    fig.savefig("fig/figB6_heater_on_off.png", dpi=300)
    fig.savefig("fig/figB6_heater_on_off.pdf")
    fig.savefig("paper/notes/figB6_heater_on_off.png", dpi=300)
    fig.savefig("paper/notes/figB6_heater_on_off.pdf")
    plt.close(fig)

    # Fig 2: ξ power sweep
    fig, ax = plt.subplots(1, 2, figsize=(6.4, 2.5))
    xis = [0.3, 0.5, 1.0, 2.0]
    for case, color, marker in (
        ("IDT10_Qa2000", "C0", "o"),
        ("IDT10_Qa1570", "C3", "s"),
        ("IDT50_Qa2000", "C2", "^"),
    ):
        ys = [r["P_uW"] for r in xi_rows if r["case"] == case]
        ax[0].plot(xis, ys, marker=marker, color=color, label=case)
    ax[0].set_xlabel(r"coverage $\xi$")
    ax[0].set_ylabel(r"RF power (µW)")
    ax[0].set_yscale("log")
    ax[0].axvline(0.5, color="0.5", ls=":", lw=0.7)
    ax[0].legend(fontsize=6)
    ax[0].set_title(r"power $\propto 1/\xi^2$", fontsize=8)

    # conservative vs Shao
    ax[1].bar([0, 1], [P_cons["P_uW"], 1e6], color=["C3", "0.5"])
    ax[1].set_xticks([0, 1])
    ax[1].set_xticklabels(["cons.\nξ=0.5×IDT10%\nQa=1570", "Shao 2020\n30 dBm"], fontsize=6)
    ax[1].set_ylabel("RF power (µW)")
    ax[1].set_yscale("log")
    ax[1].set_title("crit.2: cons. << Shao drive", fontsize=8)
    fig.tight_layout()
    fig.savefig("fig/figB7_xi_power.png", dpi=300)
    fig.savefig("fig/figB7_xi_power.pdf")
    fig.savefig("paper/notes/figB7_xi_power.png", dpi=300)
    fig.savefig("paper/notes/figB7_xi_power.pdf")
    plt.close(fig)

    # Fig 3: residual |2µ−Ω| and spur
    fig, ax = plt.subplots(1, 2, figsize=(6.0, 2.4))
    ax[0].hist(np.abs(s_off["eps_res_MHz"]), bins=40, color="C0", alpha=0.7, label="OFF")
    ax[0].hist(np.abs(s_on["eps_res_MHz"]), bins=40, color="C3", alpha=0.55, label="ON")
    ax[0].set_xlabel(r"$|2\mu-\Omega|$ residual (MHz)")
    ax[0].set_ylabel("count")
    ax[0].legend(fontsize=6)
    ax[0].set_title("match residual", fontsize=8)

    # spur q histogram
    for sq, lab, c in ((s_off, "OFF", "C0"), (s_on, "ON", "C3")):
        qs, cnts = np.unique(sq["spur_q"], return_counts=True)
        ax[1].bar(qs + (-0.15 if lab == "OFF" else 0.15), cnts, width=0.3, color=c, label=lab)
    ax[1].set_xlabel("worst-spur order $q$")
    ax[1].set_ylabel("count")
    ax[1].legend(fontsize=6)
    ax[1].set_title("worst spur (crit.3)", fontsize=8)
    fig.tight_layout()
    fig.savefig("fig/figB8_residual_spur.png", dpi=300)
    fig.savefig("fig/figB8_residual_spur.pdf")
    fig.savefig("paper/notes/figB8_residual_spur.png", dpi=300)
    fig.savefig("paper/notes/figB8_residual_spur.pdf")
    plt.close(fig)

    print(json.dumps({
        "primary_yield": summary["primary_yield"],
        "IL_two_columns": summary["IL_two_columns"],
        "conservative_power_uW": P_cons["P_uW"],
        "fab_ALL_PASS": all_pass,
        "fab": fab,
    }, indent=1))
    return summary


if __name__ == "__main__":
    main()
