#!/usr/bin/env python3
"""主图：理论 V(R_c) + 商用光纤 AOM 计划自测空心点；Shao 仅虚线文献锚。

叠点规则（台面清单）：
- 只叠商用 AOM 实验点占位（空心、「计划自测」）
- 不要把 Shao 3.5% / 片上 3 GHz 画进同一实验系列
- Shao 可作虚线文献锚 / 脚注，明确不是台面点
- 图注强制句：AOM≠片上 3 GHz 声模，nth 不由本次 HOM 测出
- 插损只进计数率注释，不进 V 曲线
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
import numpy as np

# Prefer CJK-capable font for mandatory Chinese caption
for _name in ("Noto Sans CJK SC", "Noto Serif CJK SC", "AR PL UMing CN"):
    try:
        font_manager.findfont(_name, fallback_to_default=False)
        mpl.rcParams["font.sans-serif"] = [_name, "DejaVu Sans"]
        mpl.rcParams["font.family"] = "sans-serif"
        mpl.rcParams["axes.unicode_minus"] = False
        break
    except Exception:
        continue


from hom_visibility import V_vs_Rc, shao2020_literature_anchor_V
from models import load_params, typeC_visibility_vs_R, n_th_ordinary_f

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "fig"
FIG.mkdir(exist_ok=True)


def plot_main_V_vs_Rc() -> Path:
    P = load_params()
    SSR = float(P["by_id"]["shao2020_SSR_dB"]["value"])

    Rc = np.linspace(10.0, 50.0, 401)
    # 主理论曲线：无滤波，完美时间重叠；SSR 取 Shao 对侧边带下界作模型参数（非台面实测）
    V = V_vs_Rc(Rc, SSR_dB=SSR)
    # 敏感性：若边带更差（SSR=30 dB）或更好（50 dB）
    V30 = V_vs_Rc(Rc, SSR_dB=30.0)
    V50 = V_vs_Rc(Rc, SSR_dB=50.0)

    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=150)

    ax.plot(Rc, V, color="C0", lw=2.0, label=rf"理论 $V(R_c)$（SSR={SSR:.0f} dB 模型）")
    ax.plot(Rc, V30, color="C0", lw=1.0, ls=":", alpha=0.7, label="SSR=30 dB（敏感性）")
    ax.plot(Rc, V50, color="C0", lw=1.0, ls="--", alpha=0.5, label="SSR=50 dB（敏感性）")

    # Shao 文献锚：竖虚线 + 标注，不是实验系列点
    lit = shao2020_literature_anchor_V(CSR_dB=31.0, SSR_dB=SSR)
    ax.axvline(lit["CSR_dB"], color="0.45", ls="-.", lw=1.2, alpha=0.9)
    ax.annotate(
        f"文献锚 Shao2020\nCSR≈{lit['CSR_dB']:.0f} dB\n"
        f"偏转口频率仓纯度（残余载波账）\n"
        f"$V_\\mathrm{{bin}}\\approx${lit['V_upper']:.4f}\n"
        f"（片上 ~3 GHz；≠台面 HOM 可见度）",
        xy=(lit["CSR_dB"], lit["V_upper"]),
        xytext=(lit["CSR_dB"] + 3.5, 0.92),
        fontsize=8,
        color="0.35",
        arrowprops=dict(arrowstyle="->", color="0.5", lw=0.8),
    )

    # 商用光纤 AOM：计划自测只标横轴位置，纵轴不贴理论线（尚未实测，避免看起来已吻合）
    planned_Rc = np.array([20.0, 30.0, 35.0, 40.0, 45.0])  # 计划扫区示意，非实测
    y0 = ax.get_ylim()[0]
    # 先设 ylim 后再取底边；下面统一设 ylim 后重画标记
    ax.set_ylim(0.5, 1.02)
    y_mark = 0.505
    ax.plot(
        planned_Rc,
        np.full_like(planned_Rc, y_mark, dtype=float),
        linestyle="none",
        marker="|",
        markersize=14,
        markeredgecolor="C3",
        markeredgewidth=2.0,
        label="商用 AOM 计划自测 $R_c$（仅横轴；V 待测）",
        zorder=5,
    )
    for x in planned_Rc:
        ax.annotate(
            "",
            xy=(x, 0.52),
            xytext=(x, 0.58),
            arrowprops=dict(arrowstyle="-", color="C3", lw=0.8, alpha=0.5),
        )
    # 手册消光 ≥50 dB 旁注（非填入实测 CSR）
    ax.axvline(50.0, color="C3", ls=":", lw=0.9, alpha=0.6)
    ax.text(
        49.2,
        0.55,
        "手册 on/off\n消光 ≥50 dB\n（≠已测 $R_c$）",
        fontsize=7,
        color="C3",
        ha="right",
        va="center",
    )

    ax.set_xlabel(r"载波抑制 $R_c$ (dB)")
    ax.set_ylabel(r"HOM 可见度上限 $V$")
    ax.set_xlim(10, 52)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=8, framealpha=0.92)

    caption = (
        "AOM≠片上 3 GHz 声模，$n_\\mathrm{th}$ 不由本次 HOM 测出\n"
        "插损（手册 ≤2.5 dB；Shao 文献光纤到光纤 ~−15 dB）只进计数率，不进 $V$ 上限。"
        "Shao 3.5%@30 dBm 不入本实验点。"
    )
    fig.text(0.5, 0.01, caption, ha="center", va="bottom", fontsize=8, wrap=True)
    fig.subplots_adjust(bottom=0.22)
    ax.set_title(r"频率仓 HOM：理论 $V(R_c)$ + 商用 AOM 台面计划点")

    out_png = FIG / "vis_vs_carrier.png"
    out_pdf = FIG / "vis_vs_carrier.pdf"
    fig.savefig(out_png, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    return out_png


def plot_typeC_R() -> Path:
    P = load_params()
    b = P["by_id"]
    f_Hz = float(b["zhu2025_Omega_GHz"]["value"]) * 1e9
    nth = n_th_ordinary_f(f_Hz, T_K=float(P["meta"]["T_K"]))
    C_per_mW = float(b["zhu2025_C_per_mW"]["value"])
    R = np.linspace(0.01, 0.99, 200)

    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=150)
    for scale, ls in [(0.5, ":"), (1.0, "-"), (2.0, "--")]:
        # reference C at P_a such that mid-curve; use C = 2.46 * 6.3 * scale
        C = C_per_mW * 6.3 * scale
        out = typeC_visibility_vs_R(R, C, nth)
        ax.plot(R, out["V_upper"], ls=ls, label=rf"$C$ 缩放 ×{scale}（δ_sp={out['delta_sp']:.3f}）")

    R_meas = float(b["zhu2025_R_max_measured"]["value"])
    C0 = C_per_mW * 6.3
    Vm = float(typeC_visibility_vs_R(R_meas, C0, nth)["V_upper"])
    ax.plot([R_meas], [Vm], "s", color="0.3", markersize=7, label=f"Zhu 实测 R={R_meas:.0%} 文献锚")

    ax.set_xlabel(r"反射率 $R$")
    ax.set_ylabel(r"可见度/保真度上界 $V_\mathrm{upper}$")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_title("丙类 DBM：R → F/V（模型假设）")
    fig.text(
        0.5,
        0.02,
        "模型假设：V=R(1−δ_sp)，δ_sp=n_th/(n_th+4C)。室温 n_th；非液氦主结果。",
        ha="center",
        fontsize=8,
    )
    fig.subplots_adjust(bottom=0.18)
    out = FIG / "vis_vs_R.png"
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(FIG / "vis_vs_R.pdf", bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    p1 = plot_main_V_vs_Rc()
    p2 = plot_typeC_R()
    lit = shao2020_literature_anchor_V()
    print("main", p1)
    print("typeC", p2)
    print("Shao lit V_upper", lit)
