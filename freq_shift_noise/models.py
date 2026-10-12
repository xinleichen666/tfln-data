"""三类移频器件噪声账本模型（甲行波 Bragg / 乙共振换能 / 丙布里渊强耦合）。

室温台面口径。禁止无损、n_th→0、效率追平 Hu≈99% 作为主结果。
插损只进计数率，不进频率仓纯度 / HOM 可见度上限。
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

HBAR = 1.054571817e-34
KB = 1.380649e-23
ROOT = Path(__file__).resolve().parent


def load_params(path: Path | None = None) -> dict[str, Any]:
    p = path or (ROOT / "params.json")
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    by_id = {row["id"]: row for row in data["params"]}
    return {"meta": data["meta"], "by_id": by_id, "rows": data["params"]}


def n_th(f_Hz: float, T_K: float = 300.0) -> float:
    """热声子占据数 n_th = 1/(e^{h f/kT}-1)，f 为普通频率 (Hz)。

    室温 GHz 声频 → ~10^2–10^3。等价于 1/(e^{ħΩ/kT}-1)，Ω=2πf。
    """
    return n_th_ordinary_f(f_Hz, T_K)


def n_th_ordinary_f(f_Hz: float, T_K: float = 300.0) -> float:
    """n_th with ordinary frequency f (Hz): 1/(e^{hf/kT}-1)."""
    if f_Hz <= 0:
        return float("inf")
    x = (HBAR * 2 * math.pi * f_Hz) / (KB * T_K)
    if x < 1e-12:
        return float("inf")
    return 1.0 / (math.exp(x) - 1.0)


# ---------------------------------------------------------------------------
# 甲：行波 Bragg（Shao 2020 参数作器件模型；台面主图叠点规则见 plot）
# ---------------------------------------------------------------------------

def typeA_bin_weights(
    CSR_dB: float,
    SSR_dB: float = 40.0,
    n_extra_sb: int = 0,
    extra_sb_dB: float | None = None,
) -> dict[str, float]:
    """偏转口收集模内各频率仓功率占比（相对移频线归一前）。

    CSR_dB = R_c = 10 log10(P_{+1} / P_0) = 10 log10(P_shift / P_carrier)
      （与台面清单 / 商用 AOM 自测定义一致）
    SSR_dB = 10 log10(P_shift / P_opposite_sb)

    归一后 p_s = 1 / (1 + 10^{-R_c/10} + 10^{-SSR/10})；
    无滤波且时间重叠=1 时 V_upper = p_s。
    插损 / 片上 η_onchip **不进入** 此处。
    """
    r_c = 10.0 ** (-CSR_dB / 10.0)  # η_carrier / η_shift
    r_sb = 10.0 ** (-SSR_dB / 10.0)
    w_s = 1.0
    w_c = r_c
    w_sb = r_sb
    if n_extra_sb > 0:
        db = SSR_dB if extra_sb_dB is None else extra_sb_dB
        w_sb += n_extra_sb * (10.0 ** (-db / 10.0))
    tot = w_s + w_c + w_sb
    return {
        "w_s": w_s,
        "w_carrier": w_c,
        "w_sb": w_sb,
        "p_s": w_s / tot,
        "p_carrier": w_c / tot,
        "p_sb": w_sb / tot,
        "CSR_dB": float(CSR_dB),
        "SSR_dB": float(SSR_dB),
    }


def typeA_count_rate_factor(
    eta_onchip: float,
    IL_fiber_dB: float,
) -> float:
    """相对符合/计数率因子：η_onchip × 10^(IL_dB/10)。只进计数率，不进 V。"""
    return float(eta_onchip) * (10.0 ** (IL_fiber_dB / 10.0))


def typeA_demo(params: dict | None = None) -> dict[str, Any]:
    P = params or load_params()
    b = P["by_id"]
    CSR = float(b["shao2020_CSR_dB"]["value"])
    SSR = float(b["shao2020_SSR_dB"]["value"])
    eta = float(b["shao2020_eta_onchip"]["value"])
    IL = float(b["shao2020_IL_fiber_dB"]["value"])
    bins = typeA_bin_weights(CSR, SSR)
    rate = typeA_count_rate_factor(eta, IL)
    return {
        "device": "typeA_traveling_Bragg",
        "bins": bins,
        "V_upper_no_filter": bins["p_s"],
        "count_rate_factor": rate,
        "eta_onchip": eta,
        "IL_fiber_dB": IL,
        "note": "IL and eta_onchip affect rates only; V_upper = p_s from CSR/SSR",
    }


# ---------------------------------------------------------------------------
# 乙：共振换能（Shao 2019）— 只锁定参数；不写单光子频率仓 HOM 主结果
# ---------------------------------------------------------------------------

def typeB_locked_params(params: dict | None = None) -> dict[str, Any]:
    """锁定 Shao 2019 Table S2 参数；算 C0、室温 n_th、N_add。

    非主结果：不把 η→单光子频率仓 HOM 写成主曲线。
    Ω/2π 用 Table S2 的 2.007 GHz（与 κ、γ、g0 同表），不用共用表 2.17 GHz 行。
    """
    P = params or load_params()
    b = P["by_id"]
    # params store g0/2π, κ/2π, γ/2π, Ω/2π as ordinary-frequency Hz values
    g0_2pi = float(b["shao2019_g0_Hz"]["value"])
    kappa_2pi = float(b["shao2019_kappa_Hz"]["value"])
    gamma_2pi = float(b["shao2019_gamma_Hz"]["value"])
    Omega_2pi = float(b["shao2019_Omega_Hz"]["value"])
    ke_frac = float(b["shao2019_2ke_over_k"]["value"])  # 2κe/κ
    ge_frac = float(b["shao2019_2ge_over_g"]["value"])  # 2γe/γ
    C0_lit = float(b["shao2019_C0"]["value"])
    Vpi = float(b["shao2019_Vpi_V"]["value"])
    Qac = float(b["shao2019_Q_ac_typical"]["value"])

    # C0 = 4 g0^2 / (κ γ) with angular rates: g0=2π*(g0/2π), etc. → same as 4 (g0_2pi)^2 / (κ_2pi * γ_2pi)
    C0 = 4.0 * (g0_2pi ** 2) / (kappa_2pi * gamma_2pi)
    kappa_e_over_kappa = ke_frac / 2.0
    gamma_e_over_gamma = ge_frac / 2.0
    kappa_i_over_kappa = 1.0 - kappa_e_over_kappa
    gamma_i_over_gamma = 1.0 - gamma_e_over_gamma

    f_Hz = Omega_2pi  # params store Ω/2π value in Hz field named Omega_Hz meaning Ω/2π
    nth = n_th_ordinary_f(f_Hz, T_K=float(P["meta"]["T_K"]))
    # N_add = n_th * γ_i / γ_e  (input-referred additive noise, red-detuned)
    N_add = nth * (gamma_i_over_gamma / gamma_e_over_gamma) if gamma_e_over_gamma > 0 else float("inf")

    return {
        "device": "typeB_resonant_transduction",
        "Vpi_V": Vpi,
        "g0_over_2pi_Hz": g0_2pi,
        "kappa_over_2pi_Hz": kappa_2pi,
        "gamma_over_2pi_Hz": gamma_2pi,
        "Omega_over_2pi_Hz": Omega_2pi,
        "Q_ac": Qac,
        "C0_computed": C0,
        "C0_literature": C0_lit,
        "kappa_e_over_kappa": kappa_e_over_kappa,
        "gamma_e_over_gamma": gamma_e_over_gamma,
        "n_th_300K": nth,
        "N_add_roomT": N_add,
        "main_result": False,
        "note": "乙类只锁定 g0/Vπ/Q；不把 η→单光子频率仓 HOM 写成主结果。N_add 为非主结果上界。",
    }


def typeB_noise_bound_if_driven(C: float, n_th_val: float, gamma_i_over_gamma_e: float) -> dict[str, float]:
    """若强驱动到换能，附加噪声上界（非主结果）。N_add ≈ n_th * γ_i/γ_e；η_max=4C/(1+C)^2 * κe/κ * γe/γ。"""
    return {
        "C": float(C),
        "n_th": float(n_th_val),
        "N_add_upper": float(n_th_val) * float(gamma_i_over_gamma_e),
        "eta_bs_factor": 4.0 * C / (1.0 + C) ** 2,
        "label": "非主结果",
    }


# ---------------------------------------------------------------------------
# 丙：布里渊 / 强耦合反射（Zhu/Xu）— 模型假设，图注必写
# ---------------------------------------------------------------------------

def typeC_visibility_vs_R(
    R: np.ndarray | float,
    C: float,
    n_th_val: float,
    spont_model: str = "n_th/(n_th+4C)",
) -> dict[str, Any]:
    """反射率 R → 频率仓可见度/保真度上界（模型假设）。

    账本：
      相干反射进信号仓权重 ∝ R
      残余载波权重 ∝ (1-R)
      自发散射进信号仓相对权重 δ_sp = n_th/(n_th+4C)   （假设）
    无滤波：
      V_upper = [R*(1-δ_sp)] / [R*(1-δ_sp) + (1-R) + R*δ_sp]
              = R*(1-δ_sp) / [1]   wait: denom = R(1-δ)+ (1-R) + Rδ = 1
      → V_upper = R * (1 - δ_sp)   if spontaneous counted as same-bin incoherent dilution
        OR if spontaneous is same frequency but distinguishes by photon-number noise,
        frequency-bin purity vs carrier is still R/(R+(1-R))=R, and Fidelity separately
        degraded by δ_sp.

    采用保守分账（频率可区分极限 + 自发进信号仓稀释）：
      p_s_coh = R * (1 - δ_sp)
      p_carrier = 1 - R
      p_spont = R * δ_sp
      V_upper = p_s_coh / (p_s_coh + p_carrier + p_spont) = R(1-δ_sp) / 1 = R(1-δ_sp)

    图注必须写「模型假设」。
    """
    R = np.asarray(R, dtype=float)
    if spont_model == "n_th/(n_th+4C)":
        delta_sp = n_th_val / (n_th_val + 4.0 * C) if (n_th_val + 4.0 * C) > 0 else 1.0
    elif spont_model == "n_th/(4C)":
        delta_sp = min(1.0, n_th_val / (4.0 * C)) if C > 0 else 1.0
    else:
        raise ValueError(spont_model)
    V = R * (1.0 - delta_sp)
    return {
        "R": R,
        "C": float(C),
        "n_th": float(n_th_val),
        "delta_sp": float(delta_sp),
        "V_upper": V,
        "model": "V_upper = R*(1-δ_sp), δ_sp=n_th/(n_th+4C)",
        "assumption": True,
        "note": "模型假设；非实测器件公式",
    }


def typeC_demo(params: dict | None = None) -> dict[str, Any]:
    P = params or load_params()
    b = P["by_id"]
    f_Hz = float(b["zhu2025_Omega_GHz"]["value"]) * 1e9
    nth = n_th_ordinary_f(f_Hz, T_K=float(P["meta"]["T_K"]))
    C_per_mW = float(b["zhu2025_C_per_mW"]["value"])
    R_meas = float(b["zhu2025_R_max_measured"]["value"])
    # at measured R point: C = 2.46 * 6.3 ≈ 15.5
    P_a = 6.3  # mW acoustic at R=24%
    C = C_per_mW * P_a
    out = typeC_visibility_vs_R(R_meas, C, nth)
    # sensitivity: C scale 0.5× / 1× / 2×
    sens = []
    for s in (0.5, 1.0, 2.0):
        sens.append(typeC_visibility_vs_R(R_meas, C * s, nth))
    return {
        "device": "typeC_brillouin_DBM",
        "n_th_300K": nth,
        "C_at_Rmeas": C,
        "R_meas": R_meas,
        "at_Rmeas": out,
        "sensitivity_C_scale": [
            {"scale": s, "delta_sp": sens[i]["delta_sp"], "V_upper": float(np.asarray(sens[i]["V_upper"]))}
            for i, s in enumerate((0.5, 1.0, 2.0))
        ],
        "note": "模型假设；图注必写",
    }


def demo_all() -> dict[str, Any]:
    P = load_params()
    return {
        "typeA": typeA_demo(P),
        "typeB": typeB_locked_params(P),
        "typeC": typeC_demo(P),
    }


if __name__ == "__main__":
    import pprint

    pprint.pp(demo_all())
