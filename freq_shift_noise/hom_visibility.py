"""频率仓 HOM 可见度上限。

双光子 |1>_ideal ⊗ |ψ>_device，完美时间重叠、无滤波：
  V_upper = p_s = |⟨ω_s|ψ⟩|² / Σ_k |⟨ω_k|ψ⟩|²

有滤波时 T_k 取**强度**透过率（不是振幅）：
  p_s' = T_s p_s / Σ_k T_k p_k，再 V_upper = p_s'。

时间重叠本轮取 O=1；以后非完美重叠时 V_upper → V_upper * O
（见 report_formulas_v1.md §0.3）。

插损 / 片上转换效率 **不进入** V_upper（只进计数率，见 models.typeA_count_rate_factor）。
"""
from __future__ import annotations

import numpy as np

from models import typeA_bin_weights


def V_upper_from_bins(p_s: float, p_other: float | None = None) -> float:
    """无滤波、完美时间重叠：V_upper = p_s（错频仓全部稀释）。"""
    if p_other is not None:
        return float(p_s / (p_s + p_other))
    return float(p_s)


def V_upper_filtered(p: dict[str, float], T: dict[str, float]) -> float:
    """滤波后 V_upper。

    p: {'s':..., 'carrier':..., 'sb':...} 频率仓概率（已归一）。
    T: 同键的**强度**透过率（不是振幅；勿再平方）。
    返回 T_s p_s / Σ_k T_k p_k。
    """
    keys = list(p.keys())
    num = T.get("s", 1.0) * p["s"]
    den = sum(T.get(k, 1.0) * p[k] for k in keys)
    return float(num / den) if den > 0 else 0.0


def V_vs_Rc(
    CSR_dB: np.ndarray | float,
    SSR_dB: float = 40.0,
) -> np.ndarray:
    """甲类主曲线：V_upper(R_c)。SSR 固定为文献/假设下界。"""
    CSR_dB = np.atleast_1d(np.asarray(CSR_dB, dtype=float))
    out = np.empty_like(CSR_dB)
    for i, c in enumerate(CSR_dB):
        bins = typeA_bin_weights(float(c), SSR_dB=SSR_dB)
        out[i] = bins["p_s"]
    return out


def shao2020_literature_anchor_V(CSR_dB: float = 31.0, SSR_dB: float = 40.0) -> dict:
    """文献锚（非台面点）：Shao2020 偏转口 CSR/SSR → V_upper。"""
    bins = typeA_bin_weights(CSR_dB, SSR_dB)
    return {
        "CSR_dB": CSR_dB,
        "SSR_dB": SSR_dB,
        "V_upper": bins["p_s"],
        "kind": "literature_anchor",
        "not_bench": True,
    }


if __name__ == "__main__":
    Rc = np.linspace(10, 50, 9)
    print("Rc_dB", Rc)
    print("V", V_vs_Rc(Rc, SSR_dB=40.0))
    print("Shao lit anchor", shao2020_literature_anchor_V())
