#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "paper" / "fig"
FIG.mkdir(parents=True, exist_ok=True)

# 优先中文字体
for fp in (
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/truetype/arphic/uming.ttc",
):
    p = Path(fp)
    if p.exists():
        font_manager.fontManager.addfont(str(p))
        prop = font_manager.FontProperties(fname=str(p))
        plt.rcParams["font.family"] = prop.get_name()
        break
plt.rcParams.update({"axes.unicode_minus": False, "font.size": 11, "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 140})


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.png")
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)


def main() -> None:
    s = json.loads((ROOT / "data" / "summary.json").read_text(encoding="utf-8"))
    wall = s["sweeps"]["domain_wall"]
    thick = s["sweeps"]["thickness"]
    temp = s["sweeps"]["temperature_dk"]
    duty = s["sweeps"]["duty_cycle"]

    x = np.array([r["sigma_over_Lambda"] for r in wall])
    y = np.array([r["eta_rel_p50"] for r in wall])
    y10 = np.array([r["eta_rel_p10"] for r in wall])
    y90 = np.array([r["eta_rel_p90"] for r in wall])
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.fill_between(x, y10, y90, alpha=0.25, label="p10–p90")
    ax.plot(x, y, "o-", ms=3.5, label="p50")
    ax.axhline(0.5, color="C3", ls="--", lw=1, label="η=0.5")
    ax.set_xlabel(r"domain-wall jitter $\sigma/\Lambda$")
    ax.set_ylabel(r"relative efficiency $\eta/\eta_0$")
    ax.set_title("Efficiency vs domain-wall error")
    ax.legend(frameon=False)
    save(fig, "fig_eta_vs_domain")

    xh = np.array([r["dH_um"] for r in thick])
    yh = np.array([r["eta_rel_sinc2"] for r in thick])
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.plot(xh * 1000, yh, "-", lw=2)
    ax.axhline(0.5, color="C3", ls="--", lw=1, label="η=0.5")
    ax.set_xlabel(r"thickness offset $\delta H$ (nm)")
    ax.set_ylabel(r"$\mathrm{sinc}^2(\Delta k L/2)$")
    ax.set_title("Efficiency vs film-thickness offset")
    ax.legend(frameon=False)
    save(fig, "fig_eta_vs_thickness")

    T = np.array([r["dT_K"] for r in temp])
    dq = np.array([r["delta_k_qfc_per_um"] for r in temp])
    ds = np.array([r["delta_k_spdc_per_um"] for r in temp])
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.plot(T, dq, "-", lw=2, label=r"$\Delta k_{\mathrm{QFC}}$")
    ax.plot(T, ds, "-", lw=2, label=r"$\Delta k_{\mathrm{SPDC}}$")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel(r"temperature offset $\Delta T$ (K)")
    ax.set_ylabel(r"$\Delta k$ (1/μm)")
    ax.set_title("Δk vs T · " + s["headline"]["reverse_tuning_temp_note"])
    ax.legend(frameon=False)
    save(fig, "fig_dk_vs_temperature")

    xd = np.array([r["duty"] for r in duty])
    yd = np.array([r["eta_rel_p50"] for r in duty])
    yf = np.array([r["fourier1_amp_sq"] for r in duty])
    # 相对 D=0.5 归一傅里叶
    yf = yf / yf.max() if yf.max() > 0 else yf
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.plot(xd, yd, "o-", ms=3.5, label="domain sum p50")
    ax.plot(xd, yf, "--", label=r"$|\sin(\pi D)|^2$ (norm.)")
    ax.set_xlabel("duty cycle D")
    ax.set_ylabel("relative efficiency")
    ax.set_title("Efficiency vs duty cycle")
    ax.legend(frameon=False)
    save(fig, "fig_eta_vs_duty")

    print(f"[plot] wrote figs under {FIG}")


if __name__ == "__main__":
    main()
