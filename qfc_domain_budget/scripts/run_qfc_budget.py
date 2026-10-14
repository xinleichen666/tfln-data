#!/usr/bin/env python3
"""qfc_domain_budget — 标准准相位匹配噪声预算（非实验复现）。

先验对照（仅 bib，不抄器件数进结果）：
  Phys. Rev. Lett. doi:10.1103/wx56-plcm
  器件数 28.8% / 35/s / 120:1 —— 不得作本轨目标。

口径：标准模型预算，不是该实验的复现。不编造该文畴缺陷公式系数。
不用 dir1_metrology run7 纯度当转换效率。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

SEEDS = {
    "master": 20261014,
    "domain_wall": 401,
    "duty_cycle": 402,
    "thickness": 403,
    "temp_scan": 404,
}

LAM_S_NM = 393.0
LAM_I_NM = 1550.0
LAM_P_NM = 1.0 / (1.0 / LAM_S_NM - 1.0 / LAM_I_NM)

H0_UM = 0.60
L_MM = 5.0

# n(λ,δH,ΔT)=A+B/λ_um^2+α·δH+(dn/dT)·ΔT （自设，非实验拟合）
N_COEFF = {
    "s": (2.25, 0.040, 0.12),
    "i": (2.14, 0.020, 0.05),
    "p": (2.21, 0.030, 0.08),
}
LAM_A_NM = LAM_I_NM
LAM_B_NM = 1.0 / (1.0 / LAM_P_NM - 1.0 / LAM_A_NM)
N_COEFF["a"] = N_COEFF["i"]
N_COEFF["b"] = (2.18, 0.028, 0.07)

DN_DT = {
    "s": 3.5e-5,
    "i": 2.0e-5,
    "p": 2.8e-5,
    "a": 2.0e-5,
    "b": 2.6e-5,
}


def n_eff(band: str, lam_nm: float, dH_um: float = 0.0, dT_K: float = 0.0) -> float:
    A, B, alpha = N_COEFF[band]
    lam_um = lam_nm / 1000.0
    return float(A + B / (lam_um ** 2) + alpha * dH_um + DN_DT[band] * dT_K)


def beta(band: str, lam_nm: float, dH_um: float = 0.0, dT_K: float = 0.0) -> float:
    """传播常数 [1/μm]。"""
    return 2.0 * np.pi * n_eff(band, lam_nm, dH_um, dT_K) / (lam_nm / 1000.0)


def delta_beta_qfc(dH_um: float = 0.0, dT_K: float = 0.0) -> float:
    """材料失配 Δβ = β_s - β_i - β_p（不含光栅）。"""
    return (
        beta("s", LAM_S_NM, dH_um, dT_K)
        - beta("i", LAM_I_NM, dH_um, dT_K)
        - beta("p", LAM_P_NM, dH_um, dT_K)
    )


def delta_beta_spdc(dH_um: float = 0.0, dT_K: float = 0.0) -> float:
    return (
        beta("p", LAM_P_NM, dH_um, dT_K)
        - beta("a", LAM_A_NM, dH_um, dT_K)
        - beta("b", LAM_B_NM, dH_um, dT_K)
    )


def delta_k(db: float, Lambda_um: float) -> float:
    return db - 2.0 * np.pi / Lambda_um


def sinc2(x: float) -> float:
    if abs(x) < 1e-12:
        return 1.0
    s = np.sin(x) / x
    return float(s * s)


def envelope_eta(dk: float, L_um: float) -> float:
    return sinc2(0.5 * dk * L_um)


def domain_chi_integral(
    Lambda_um: float,
    n_periods: int,
    delta_beta: float,
    sigma_wall_um: float,
    duty: float,
    rng: np.random.Generator,
) -> complex:
    """
    ∫ χ(z) exp(i Δβ z) dz，χ=±1 交替。
    一阶 QPM 在 Δβ≈2π/Λ 时取极大；抖动/占空比进入 χ(z)。
    """
    amp = 0.0 + 0.0j
    z = 0.0
    sign = 1.0
    for _ in range(n_periods):
        wall = duty * Lambda_um
        if sigma_wall_um > 0:
            wall = wall + float(rng.normal(0.0, sigma_wall_um))
        wall = float(np.clip(wall, 0.05 * Lambda_um, 0.95 * Lambda_um))
        for seg in (wall, Lambda_um - wall):
            if abs(delta_beta) < 1e-14:
                piece = sign * seg
            else:
                piece = sign * (np.exp(1j * delta_beta * seg) - 1.0) / (1j * delta_beta)
            amp += piece * np.exp(1j * delta_beta * z)
            z += seg
            sign *= -1.0
    return amp


def rel_eff_domain(
    Lambda_um: float,
    n_periods: int,
    delta_beta: float,
    sigma_wall_um: float,
    duty: float,
    seed: int,
    n_real: int,
) -> dict:
    # 参考：理想 QPM（Δβ=2π/Λ）、D=0.5、无抖动
    ref_db = 2.0 * np.pi / Lambda_um
    ref = domain_chi_integral(Lambda_um, n_periods, ref_db, 0.0, 0.5, np.random.default_rng(0))
    ref_pow = abs(ref) ** 2
    if ref_pow < 1e-30:
        raise RuntimeError("reference QPM amplitude vanished; check domain model")

    rng = np.random.default_rng(seed)
    powers = []
    for _ in range(n_real):
        sub = np.random.default_rng(int(rng.integers(0, 2**31 - 1)))
        a = domain_chi_integral(
            Lambda_um, n_periods, delta_beta, sigma_wall_um, duty, sub
        )
        powers.append(abs(a) ** 2 / ref_pow)
    arr = np.asarray(powers, dtype=float)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        "p10": float(np.percentile(arr, 10)),
        "p50": float(np.percentile(arr, 50)),
        "p90": float(np.percentile(arr, 90)),
        "n_real": n_real,
    }


def first_fourier_sq(D: float) -> float:
    return float(np.sin(np.pi * D) ** 2)


def main() -> None:
    db0 = delta_beta_qfc()
    Lambda0 = 2.0 * np.pi / db0
    n_per = int(round((L_MM * 1000.0) / Lambda0))
    L_um = n_per * Lambda0
    L_mm_eff = L_um / 1000.0

    # 畴壁抖动扫：Δβ 固定在 QPM 点
    sigma_fracs = np.linspace(0.0, 0.25, 26)
    wall_sweep = []
    db_qpm = 2.0 * np.pi / Lambda0
    for i, sf in enumerate(sigma_fracs):
        sig = float(sf * Lambda0)
        st = rel_eff_domain(
            Lambda0, n_per, db_qpm, sig, 0.5, SEEDS["domain_wall"] + i, n_real=32
        )
        wall_sweep.append(
            {
                "sigma_over_Lambda": float(sf),
                "sigma_wall_um": sig,
                "eta_rel_mean": st["mean"],
                "eta_rel_p50": st["p50"],
                "eta_rel_p10": st["p10"],
                "eta_rel_p90": st["p90"],
                "eta_rel_std": st["std"],
            }
        )

    duties = np.linspace(0.30, 0.70, 17)
    duty_sweep = []
    for i, D in enumerate(duties):
        st = rel_eff_domain(
            Lambda0, n_per, db_qpm, 0.0, float(D), SEEDS["duty_cycle"] + i, n_real=4
        )
        duty_sweep.append(
            {
                "duty": float(D),
                "eta_rel_mean": st["mean"],
                "eta_rel_p50": st["p50"],
                "fourier1_amp_sq": first_fourier_sq(float(D)),
            }
        )

    dH_list = np.linspace(-0.040, 0.040, 41)
    thick_sweep = []
    for dH in dH_list:
        db = delta_beta_qfc(dH_um=float(dH))
        dk = delta_k(db, Lambda0)
        thick_sweep.append(
            {
                "dH_um": float(dH),
                "delta_beta_qfc_per_um": float(db),
                "delta_k_qfc_per_um": float(dk),
                "eta_rel_sinc2": float(envelope_eta(dk, L_um)),
            }
        )

    # 联合：固定中等抖动 + 膜厚（Δβ 随膜厚变，畴结构带抖动）
    joint = []
    sig_joint = 0.03 * Lambda0
    for j, dH in enumerate(np.linspace(-0.030, 0.030, 13)):
        db = delta_beta_qfc(dH_um=float(dH))
        st = rel_eff_domain(
            Lambda0, n_per, db, sig_joint, 0.5, SEEDS["thickness"] + j, n_real=24
        )
        joint.append(
            {
                "dH_um": float(dH),
                "sigma_over_Lambda": 0.03,
                "delta_k_qfc_per_um": float(delta_k(db, Lambda0)),
                "eta_rel_mean": st["mean"],
                "eta_rel_p50": st["p50"],
            }
        )

    # 温度扫：两条 Δk
    dT_list = np.linspace(-20.0, 20.0, 41)
    temp_rows = []
    for dT in dT_list:
        dk_q = delta_k(delta_beta_qfc(dT_K=float(dT)), Lambda0)
        dk_s = delta_k(delta_beta_spdc(dT_K=float(dT)), Lambda0)
        temp_rows.append(
            {
                "dT_K": float(dT),
                "delta_k_qfc_per_um": float(dk_q),
                "delta_k_spdc_per_um": float(dk_s),
            }
        )
    T = np.array([r["dT_K"] for r in temp_rows])
    dq = np.array([r["delta_k_qfc_per_um"] for r in temp_rows])
    ds = np.array([r["delta_k_spdc_per_um"] for r in temp_rows])
    slope_q = float(np.polyfit(T, dq, 1)[0])
    slope_s = float(np.polyfit(T, ds, 1)[0])
    opposite_T = bool(slope_q * slope_s < 0.0)

    # 周期扫
    dLam_frac = np.linspace(-0.02, 0.02, 41)
    period_rows = []
    db_q0 = delta_beta_qfc()
    db_s0 = delta_beta_spdc()
    for f in dLam_frac:
        Lam = Lambda0 * (1.0 + float(f))
        period_rows.append(
            {
                "dLambda_over_Lambda": float(f),
                "Lambda_um": float(Lam),
                "delta_k_qfc_per_um": float(delta_k(db_q0, Lam)),
                "delta_k_spdc_per_um": float(delta_k(db_s0, Lam)),
            }
        )
    F = np.array([r["dLambda_over_Lambda"] for r in period_rows])
    pq = np.array([r["delta_k_qfc_per_um"] for r in period_rows])
    ps = np.array([r["delta_k_spdc_per_um"] for r in period_rows])
    slope_q_L = float(np.polyfit(F, pq, 1)[0])
    slope_s_L = float(np.polyfit(F, ps, 1)[0])
    opposite_P = bool(slope_q_L * slope_s_L < 0.0)

    # 膜厚扫两条 Δk（额外诊断；主文仍以温度/周期为准）
    thick_dk_rows = []
    for dH in np.linspace(-0.040, 0.040, 41):
        thick_dk_rows.append(
            {
                "dH_um": float(dH),
                "delta_k_qfc_per_um": float(delta_k(delta_beta_qfc(dH_um=float(dH)), Lambda0)),
                "delta_k_spdc_per_um": float(delta_k(delta_beta_spdc(dH_um=float(dH)), Lambda0)),
            }
        )
    H = np.array([r["dH_um"] for r in thick_dk_rows])
    hq = np.array([r["delta_k_qfc_per_um"] for r in thick_dk_rows])
    hs = np.array([r["delta_k_spdc_per_um"] for r in thick_dk_rows])
    slope_q_H = float(np.polyfit(H, hq, 1)[0])
    slope_s_H = float(np.polyfit(H, hs, 1)[0])
    opposite_H = bool(slope_q_H * slope_s_H < 0.0)

    half = None
    for row in wall_sweep:
        if row["eta_rel_p50"] <= 0.5:
            half = row["sigma_over_Lambda"]
            break
    half_note = f"σ/Λ={half:.4f}" if half is not None else "本扫范围内未降到 0.5"

    half_H = None
    for row in thick_sweep:
        if row["dH_um"] >= 0 and row["eta_rel_sinc2"] <= 0.5:
            half_H = row["dH_um"]
            break
    half_H_note = (
        f"δH≈{half_H:.4f} μm（正侧）" if half_H is not None else "本扫范围内未降到 0.5"
    )

    def rt_note(flag: bool) -> str:
        return "本模型里见到反向调谐" if flag else "未见到"

    summary = {
        "track": "qfc_domain_budget",
        "title_frame": "方法·噪声预算",
        "model_frame": "标准模型预算，不是该实验的复现",
        "prior_cite": "Phys. Rev. Lett. doi:10.1103/wx56-plcm（393 nm→1550 nm tPPLN QFC；器件数仅对照）",
        "disclaimer": (
            "本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，"
            "Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；"
            "verify/ 第三方 PDF 禁止入库。仓写完后再改 private。"
        ),
        "seeds": SEEDS,
        "protocol": {
            "process_qfc": "DFG: Δβ=β_s-β_i-β_p；Δk=Δβ-2π/Λ",
            "process_spdc": "泵浦寄生 SPDC: Δβ=β_p-β_a-β_b；同 Λ",
            "lambda_s_nm": LAM_S_NM,
            "lambda_i_nm": LAM_I_NM,
            "lambda_p_nm": float(LAM_P_NM),
            "lambda_spdc_a_nm": float(LAM_A_NM),
            "lambda_spdc_b_nm": float(LAM_B_NM),
            "H0_um": H0_UM,
            "L_mm_nominal": L_MM,
            "L_mm_aligned": float(L_mm_eff),
            "Lambda0_um": float(Lambda0),
            "n_periods": int(n_per),
            "n_eff_model": "n=A+B/λ_um^2+α·δH+(dn/dT)·ΔT（自设系数）",
            "n_coeff": {
                k: {"A": v[0], "B": v[1], "alpha_per_um": v[2]}
                for k, v in N_COEFF.items()
                if k in ("s", "i", "p", "b")
            },
            "dn_dT": DN_DT,
            "domain_model": "∫χ(z)e^{iΔβz}dz，χ=±1；畴壁高斯抖动；非 PRL 畴缺陷公式",
            "note_run7": "未使用 dir1_metrology/run7 纯度；纯度≠转换效率",
        },
        "headline": {
            "Lambda0_um": float(Lambda0),
            "lambda_p_nm": float(LAM_P_NM),
            "L_mm": float(L_mm_eff),
            "n_periods": int(n_per),
            "wall_half_eta": half,
            "wall_half_eta_note": half_note,
            "thickness_half_eta_um": half_H,
            "thickness_half_eta_note": half_H_note,
            "temp_slope_dk_qfc": slope_q,
            "temp_slope_dk_spdc": slope_s,
            "reverse_tuning_temp": opposite_T,
            "reverse_tuning_temp_note": rt_note(opposite_T),
            "period_slope_dk_qfc": slope_q_L,
            "period_slope_dk_spdc": slope_s_L,
            "reverse_tuning_period": opposite_P,
            "reverse_tuning_period_note": rt_note(opposite_P),
            "thickness_slope_dk_qfc": slope_q_H,
            "thickness_slope_dk_spdc": slope_s_H,
            "reverse_tuning_thickness": opposite_H,
            "reverse_tuning_thickness_note": rt_note(opposite_H),
            "literature_device_numbers_not_used": {
                "efficiency_pct": 28.8,
                "pump_noise_per_s": 35,
                "snr": "120:1",
                "role": "仅对照引用，非本轨目标或结果",
            },
        },
        "sweeps": {
            "domain_wall": wall_sweep,
            "duty_cycle": duty_sweep,
            "thickness": thick_sweep,
            "joint_wall_thickness": joint,
            "temperature_dk": temp_rows,
            "period_dk": period_rows,
            "thickness_dk": thick_dk_rows,
        },
    }

    out = DATA / "summary.json"
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    out.write_text(text, encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    (DATA / "summary.sha256").write_text(sha + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote": str(out),
                "sha16": sha[:16],
                "Lambda0_um": Lambda0,
                "lambda_p_nm": LAM_P_NM,
                "wall0": wall_sweep[0]["eta_rel_p50"],
                "wall_last": wall_sweep[-1]["eta_rel_p50"],
                "wall_half": half_note,
                "thick_half": half_H_note,
                "rt_temp": rt_note(opposite_T),
                "rt_period": rt_note(opposite_P),
                "rt_thick": rt_note(opposite_H),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
