import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 9

HERE = os.path.dirname(os.path.abspath(__file__))

# L = 1 mm 所需信号源功率（mW，仿真，未乘校准系数）；数值取自 summary_step6g/6h/6j/7/8.md
rows = [
    ("6g  主峰，单段馈电（分布 RC）", 123e3, "C7"),
    ("6h  NP 11，8 段并联", 2.9e3, "C7"),
    ("6j  转 Shao 取向（未计匹配损耗）", 24, "C1"),
    ("6j  400 nm 脊 + 串并联配 50 Ω（超胞）", 2.76, "C1"),
    ("6j  有限长校核", 2.46, "C1"),
    ("7   三维 25 µm 段（含汇流条）", 5.6, "C0"),
    ("7   三维 100 µm 段", 3.9, "C0"),
    ("7   汇流条 0.5 µm + 周期 1.84 µm", 2.85, "C0"),
    ("7   + 每段一根支撑梁", 3.15, "C2"),
    ("8   + 引线轨与焊盘", 3.26, "C3"),
]

fig, ax = plt.subplots(figsize=(7.2, 3.6))
y = list(range(len(rows)))[::-1]
for yi, (lab, v, c) in zip(y, rows):
    ax.barh(yi, v, color=c, height=0.62)
    txt = f"{v/1e3:.1f} W" if v >= 1e3 else f"{v:.2f} mW" if v < 10 else f"{v:.0f} mW"
    ax.text(v * 1.15, yi, txt, va="center", fontsize=8)
ax.set_xscale("log")
ax.set_xlim(1, 2e6)
ax.set_yticks(y)
ax.set_yticklabels([r[0] for r in rows], fontsize=8)
ax.axvspan(5.5, 17, color="C3", alpha=0.08)
ax.text(9.5, -0.95, "校准后 5.5–17 mW", fontsize=7, color="C3", ha="center", va="center")
ax.set_ylim(-1.4, len(rows) - 0.5)
ax.set_xlabel("$L=1$ mm 所需信号源功率（mW，对数坐标；仿真，未乘校准系数）")
ax.grid(axis="x", alpha=0.3, which="both")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(HERE, "fig_history." + ext), dpi=200)
