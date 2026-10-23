import re, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 9

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)

# ---- (a) L = 1 mm 信号源功率逐步演变（数值取自 summary_step7.md / summary_step8.md 的表）
stages = [
    ("二维有限长 NP7，无汇流条（2 串×16 并）", 2.46, "C7"),
    ("三维 100 µm 段，汇流条 2 µm", 3.90, "C0"),
    ("汇流条改 0.5 µm", 3.05, "C0"),
    ("周期回调 1.84 µm（3.333 GHz）", 2.85, "C0"),
    ("+ 每段一根支撑梁（含梁上铝走线）", 3.15, "C2"),
    ("+ 引线轨与焊盘（500 nm 铝，端部馈电）", 3.26, "C3"),
]
worst = 3.70   # 100 nm 铝窄轨，C 型端部馈电，2 串×5 并

# ---- (b) 段间失谐（post_step7_spread.py，周期 1.84 µm，L = 1 mm）
pat = re.compile(r"^RAND7S L_mm=1\.0 series=(\d+) sigma_MHz=([\d.]+) .* ratio_med=([\d.]+) ratio_p90=([\d.]+)")
data = {}
for ln in open(os.path.join(SRC, "step7_spread_p184.log"), encoding="utf-8", errors="replace"):
    m = pat.match(ln)
    if m:
        s, sg, rm, rp = int(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
        data.setdefault(s, []).append((sg, rm, rp))

fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.1), gridspec_kw={"width_ratios": [1.25, 1]})

y = list(range(len(stages)))[::-1]
for yi, (lab, v, c) in zip(y, stages):
    a1.barh(yi, v, color=c, height=0.62)
    a1.text(v + 0.05, yi, f"{v:.2f}", va="center", fontsize=8)
a1.set_yticks(y)
a1.set_yticklabels([s[0] for s in stages], fontsize=7.5)
a1.axvline(worst, color="gray", ls=":", lw=1)
a1.text(worst + 0.06, y[3], "薄铝窄轨\n最差 3.70", fontsize=7, color="gray", va="center")
a1.set_xlim(0, 4.9)
a1.set_xlabel("$L=1$ mm，信号源功率 $P_\\pi$（mW，仿真）")
a1.set_title("(a) 逐步计入后的功率（校准后 5.5–17 mW）", fontsize=9)
a1.grid(axis="x", alpha=0.3)

cols = {2: ("C3", "2 串×5 并"), 1: ("C0", "10 并"), 5: ("C2", "5 串×2 并")}
for s in (2, 1, 5):
    d = sorted(data[s])
    a2.plot([t[0] for t in d], [t[1] for t in d], "-o", ms=3, color=cols[s][0], label=cols[s][1] + " 中位")
    a2.plot([t[0] for t in d], [t[2] for t in d], "--", color=cols[s][0], lw=0.9)
a2.axhline(1.3, color="gray", ls=":", lw=0.9)
a2.text(0.27, 1.34, "×1.3", fontsize=7, color="gray")
a2.set_xlabel("段间随机失谐 σ（MHz）")
a2.set_ylabel("功率相对无偏差的倍数")
a2.set_ylim(0.95, 3.3)
a2.set_xlim(0, 2.1)
a2.legend(fontsize=7.5, frameon=False, loc="upper left")
a2.grid(alpha=0.3)
a2.set_title("(b) 段间失谐（实线中位，虚线 P90）", fontsize=9)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(HERE, "fig_chain." + ext), dpi=200)
print({k: v for k, v in data.items() if k in (1, 2, 5)})
