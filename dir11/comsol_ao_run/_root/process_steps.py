# -*- coding: utf-8 -*-
"""Post-process the GitHub paper-B data files. Does not re-integrate Eq. (1)."""
import json
import numpy as np
from pathlib import Path

ROOT = Path(r"D:\tfln\tfln-data\dir11\paperB\data")
OUT = Path(r"D:\comsol_ao_run\processed_steps.json")

def load_csv(name):
    text = (ROOT / name).read_text(encoding="utf-8").splitlines()
    header = text[0].lstrip("#").split(",")
    rows = []
    for line in text[1:]:
        if not line.strip():
            continue
        parts = line.split(",")
        rows.append([float(x) if x not in ("", "nan") else np.nan for x in parts])
    return header, np.array(rows, float)

# ----- 1. operating point from the power sweep -----
raw = (ROOT / "eff_vs_power.csv").read_text(encoding="utf-8").splitlines()[1:]
recs = []
for line in raw:
    a = line.split(",")
    recs.append(dict(drive=a[0], case=a[1], dw=float(a[2]), P=float(a[3]),
                     eta=float(a[4]), eta_abs=float(a[5]), IL=float(a[6]), car=float(a[7])))
ao = [r for r in recs if r["case"] == "AO_Shao_IDT(50%)"]
eo = [r for r in recs if r["case"] == "EO_unmatched(Vc=V0)"]
iao = int(np.argmax([r["eta"] for r in ao]))
ieo = int(np.argmax([r["eta"] for r in eo]))
dw_ao, dw_eo = ao[iao]["dw"], eo[ieo]["dw"]

def at_dw(dw, case):
    hit = [r for r in recs if r["case"] == case and abs(r["dw"] - dw) / dw < 1e-9]
    return hit[0]

ao_cases = ["AO_Shao_IDT(50%)", "AO_IDT_100%", "AO_IDT_10%"]
eo_cases = ["EO_unmatched(Vc=V0)", "EO_open(Vc=2V0)", "EO_LC_Q30", "EO_LC_Q100", "EO_LC_ideal"]
step1 = {
    "ao": {**{k: ao[iao][k] for k in ("dw", "eta", "eta_abs", "IL", "car")},
           "dw_GHz": dw_ao / (2 * np.pi) / 1e9,
           "P_uW": {c: at_dw(dw_ao, c)["P"] * 1e6 for c in ao_cases}},
    "eo": {**{k: eo[ieo][k] for k in ("dw", "eta", "eta_abs", "IL", "car")},
           "dw_GHz": dw_eo / (2 * np.pi) / 1e9,
           "P_uW": {c: at_dw(dw_eo, c)["P"] * 1e6 for c in eo_cases}},
}

# ----- 2. spectrum relative to the shifted line -----
R = json.loads((ROOT / "results_B.json").read_text(encoding="utf-8"))
def rel_spectrum(block):
    p = {int(q): 10 ** (db / 10) for q, db in block.items()}
    p1 = p[1]
    tot = sum(p.values())
    return {
        "dB_rel_input": {int(q): float(db) for q, db in block.items()},
        "dB_rel_shift": {q: float(10 * np.log10(p[q] / p1)) for q in p},
        "eta_shift": float(p1 / tot),
        "eta_abs": float(p1),
        "IL_dB": float(-10 * np.log10(tot)),
    }
step2 = {"ao": rel_spectrum(R["spectrum_dB"]["ao"]), "eo": rel_spectrum(R["spectrum_dB"]["eo"])}

# ----- 3. intrinsic Q -----
_, Q = load_csv("Q_tolerance.csv")
step3 = [{"ki_MHz": r[0] / 1e6, "Qi": r[1], "eta": r[2], "eta_abs": r[3], "IL": r[4], "P_uW": r[5] * 1e6} for r in Q]

# ----- 4. RF detuning -----
_, D = load_csv("RF_detuning.csv")
step4 = [{"df_MHz": r[0], "eta_ao": r[1], "eta_eo": r[2]} for r in D]

# ----- 5. IDT efficiency and xi -----
_, IDT = load_csv("IDT_sensitivity.csv")
P50 = step1["ao"]["P_uW"]["AO_Shao_IDT(50%)"]
P10 = step1["ao"]["P_uW"]["AO_IDT_10%"]
P1570 = P10 * 2000 / 1570
step5 = {
    "curve_uW": [{"eff_percent": float(e * 100), "P_uW": float(p * 1e6)} for e, p in IDT],
    "at": {f"{e:.0%}": float(P50 * 0.5 / e) for e in (0.10, 0.25, 0.50, 1.0)},
    "Qm_scale_uW": {
        "IDT10_Qm2000": P10,
        "IDT10_Qm1570": P1570,
        "IDT10_Qm3600": P10 * 2000 / 3600,
        "IDT50_Qm1570": P50 * 2000 / 1570,
        "IDT50_Qm3600": P50 * 2000 / 3600,
    },
    "xi_IDT10_Qm1570_uW": {str(xi): P1570 / xi ** 2 for xi in (0.3, 0.5, 1.0, 2.0)},
}

# ----- 6. tolerance windows -----
tol_lines = (ROOT / "tol_scan.csv").read_text(encoding="utf-8").splitlines()[1:]
scans = {"Delta": [], "dr": [], "eps": []}
for line in tol_lines:
    a = line.split(",")
    if a[0] not in scans:
        continue
    scans[a[0]].append((float(a[1]), float(a[5]), float(a[6])))

def window(pairs, thr):
    x = np.array([p[0] for p in pairs])
    e = np.array([p[1] for p in pairs])
    il = np.array([p[2] for p in pairs])
    ok = e >= thr
    i0 = int(np.argmin(np.abs(x)))
    if not ok[i0]:
        return None
    l = i0
    while l > 0 and ok[l - 1]:
        l -= 1
    r = i0
    while r < len(x) - 1 and ok[r + 1]:
        r += 1
    def cross(j, k):
        return float(x[j] + (thr - e[j]) * (x[k] - x[j]) / (e[k] - e[j]))
    lo = cross(l, l - 1) if l > 0 else float(x[0])
    hi = cross(r, r + 1) if r < len(x) - 1 else float(x[-1])
    return lo, hi

f0 = 193.4e12
ng = 2.3
dndT = 3.34e-5
alpha = 1.54e-5
neff = 2.14
dfdT_to = f0 * dndT / ng                 # Hz/K
dfdT_ex = f0 * (dndT + neff * alpha) / ng
step6 = {"dfdT_GHz_per_K": {"thermo_optic": dfdT_to / 1e9, "with_expansion": dfdT_ex / 1e9}}
for name in ("Delta", "dr", "eps"):
    step6[name] = {}
    for thr in (0.95, 0.90):
        lo, hi = window(scans[name], thr)
        half = min(-lo, hi)  # MHz
        step6[name][str(thr)] = {
            "lo_MHz": lo, "hi_MHz": hi, "narrow_half_MHz": half,
            "mK_thermo_optic": half * 1e6 / dfdT_to * 1e3,
            "mK_with_expansion": half * 1e6 / dfdT_ex * 1e3,
        }

# ----- 7. Monte Carlo percentiles from the sample table -----
mc_raw = (ROOT / "mc_samples.csv").read_text(encoding="utf-8").splitlines()
mc_hdr = mc_raw[0].split(",")
mc = np.array([[float(x) for x in line.split(",")] for line in mc_raw[1:]], float)
col = {h: i for i, h in enumerate(mc_hdr)}
eta = mc[:, col["eta_shift"]]
il = mc[:, col["IL_dB"]]
ea = mc[:, col["eta_abs_onchip"]]
ef = mc[:, col["eta_abs_fiber"]]
eps = mc[:, col["eps_raw_MHz"]]
resid = mc[:, col["eps_resid_MHz"]]
step7 = {
    "N": int(len(eta)),
    "what": "realistic.py seed 1: ki x 2, gap sigma 5 nm, lock 5 mK, RF retune +/-1 MHz, Qm fixed at 2000",
    "eta_p10_50_90": [float(np.percentile(eta, q)) for q in (10, 50, 90)],
    "IL_p10_50_90": [float(np.percentile(il, q)) for q in (10, 50, 90)],
    "eta_abs_p10_50_90": [float(np.percentile(ea, q)) for q in (10, 50, 90)],
    "fiber_p10_50_90": [float(np.percentile(ef, q)) for q in (10, 50, 90)],
    "frac_ge_090": float(np.mean(eta >= 0.90)),
    "frac_ge_095": float(np.mean(eta >= 0.95)),
    "eps_raw_std_MHz": float(np.std(eps)),
    "frac_beyond_1MHz": float(np.mean(np.abs(resid) > 1e-9)),
}

# ----- 8. HOM from H(Delta), delay-matched -----
_, Hraw = load_csv("H_shift.csv")
hom = []
for sig in np.unique(Hraw[:, 0]):
    m = Hraw[:, 0] == sig
    D = Hraw[m, 1]
    H = Hraw[m, 2] + 1j * Hraw[m, 3]
    psi = np.exp(-(D ** 2) / (4 * sig ** 2))
    best, tb = 0.0, 0.0
    for tau in np.linspace(-20e-9, 20e-9, 4001):
        A = H * psi * np.exp(-2j * np.pi * D * tau)
        ov = abs(np.sum(psi * A)) ** 2 / (np.sum(psi ** 2) * np.sum(np.abs(A) ** 2))
        if ov > best:
            best, tb = float(ov), float(tau)
    eta_shift = step1["ao"]["eta"]
    hom.append({
        "sigma_MHz": float(sig / 1e6),
        "delay_ns": tb * 1e9,
        "V_filtered": best,
        "one_minus_V_filtered": 1 - best,
        "V_unfiltered": best * eta_shift,
        "one_minus_V_unfiltered": 1 - best * eta_shift,
    })
step8 = hom

# ----- 9. thermal phonons from the step-1 power -----
hb = 1.0546e-34
kB = 1.380649e-23
WM = 2 * np.pi * 3.33e9
Qm = 2000
gamma = WM / Qm
ge = 0.15 * gamma
Pac = step1["ao"]["P_uW"]["AO_Shao_IDT(50%)"] * 1e-6
Ncoh = 4 * ge / gamma ** 2 * Pac / (hb * WM)
g0 = 2 * np.pi * 1.1e3
kappa = 2 * np.pi * 680.75e6
gm = WM / Qm
C0 = 4 * g0 ** 2 / (kappa * gm)
thermal = {"Ncoh": float(Ncoh), "C0": float(C0)}
for T in (300, 4, 0.01):
    nth = 1 / np.expm1(hb * WM / (kB * T))
    thermal[str(T)] = {"nth": float(nth), "nth_over_Ncoh": float(nth / Ncoh), "nth_C0": float(nth * C0)}
step9 = thermal

blob = {"step1": step1, "step2": step2, "step3": step3, "step4": step4,
        "step5": {k: v for k, v in step5.items() if k != "curve_uW"},
        "step6": step6, "step7": step7, "step8": step8, "step9": step9}
OUT.write_text(json.dumps(blob, indent=1), encoding="utf-8")
print(OUT)
