import re, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 9

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
MATCH = os.path.join(SRC, "step6j_match.log")
SHAO_PL = 2.36e-6  # step6i W104 m62，同流程 Shao 型

pk, mt = {}, {}
for ln in open(MATCH, encoding="utf-8"):
    m = re.match(r"PKM case=(\S+) f_GHz=(\S+) abs_tot=\S+ Y_Spm=\S+ P\*L_ideal_Wm=(\S+)", ln)
    if m:
        pk.setdefault(m.group(1), []).append((float(m.group(2)), float(m.group(3))))
        continue
    m = re.match(r"MATCHM case=(\S+) f_pk=(\S+) L_mm=(\S+) best:.*P_source_avail_mW=(\S+)", ln)
    if m:
        mt.setdefault((m.group(1), float(m.group(2))), []).append((float(m.group(3)), float(m.group(4))))


def main_pk(case):
    return min(pk[case], key=lambda t: t[1]) if case in pk else None


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, name + ".pdf"))
    fig.savefig(os.path.join(HERE, name + ".png"), dpi=150)
    plt.close(fig)


# 图 1：截面示意（比例近似，单位 µm）
p, NP = 1.9277, 7
fig, ax = plt.subplots(figsize=(6.4, 1.4))
L = NP * p
ax.add_patch(Rectangle((0, 0), L, 0.4, fc="#9ecae1", ec="k", lw=0.6))
xc = (NP // 2 + 0.5) * p
ax.add_patch(Rectangle((xc - 0.5, 0.4), 1.0, 0.4, fc="#9ecae1", ec="k", lw=0.6))
for c in range(NP):
    if abs(c - NP // 2) <= 1:
        continue
    for off, col in ((0.125, "#d62728"), (0.625, "#555555")):
        ax.add_patch(Rectangle((c * p + off * p, 0.4), 0.25 * p, 0.1, fc=col, ec="none"))
ax.text(xc, 0.9, "TE0 光波导（脊宽 1.0 µm，脊高 0.4 µm）", ha="center", va="bottom")
ax.text(0.0, -0.15, "悬空 X 切 LN 400 nm；x = 晶体 Z（声传播），y = 晶体 X，光沿晶体 Y（垂直纸面）", va="top")
ax.text(L, 0.6, "Al 叉指 100 nm（红：信号，灰：地）", ha="right", va="bottom")
ax.set_xlim(-0.3, L + 0.3); ax.set_ylim(-0.45, 1.15); ax.set_aspect("equal"); ax.axis("off")
save(fig, "fig_xsec")

# 图 2：脊深
H = [(100, "N7P1938900"), (200, "N7H200P1938900"), (300, "N7H300P1938900"), (400, "N7H400P1938900")]
xs = [h for h, c in H if c in pk]; ys = [main_pk(c)[1] for h, c in H if c in pk]
fig, ax = plt.subplots(figsize=(3.2, 2.4))
ax.semilogy(xs, ys, "o-", label="本设计（周期超胞 NP=7）")
ax.axhline(SHAO_PL, ls="--", c="gray", label="Shao 型（同流程）")
ax.set_xlabel("脊高 (nm)"); ax.set_ylabel(r"$P_\pi L$ (W·m)"); ax.legend(frameon=False, fontsize=7)
ax.grid(alpha=0.3, which="both")
save(fig, "fig_ridge")

# 图 3：配 50 Ω 后的信号源功率 vs 长度
fig, ax = plt.subplots(figsize=(3.4, 2.5))
series = [("N7H400P1927700", "周期 NP=7", "C0", "o-"), ("N9H400P1927700", "周期 NP=9", "C1", "o-"),
          ("N11H400P1927700", "周期 NP=11", "C2", "o-"),
          ("FN7H400P1927700", "有限长 NP=7", "C0", "s--"), ("FN9H400P1927700", "有限长 NP=9", "C1", "s--"),
          ("FN11H400P1927700", "有限长 NP=11", "C2", "s--")]
for case, lab, col, sty in series:
    q = main_pk(case)
    if q is None:
        continue
    d = sorted(mt[(case, q[0])])
    ax.loglog([a for a, b in d], [b for a, b in d], sty, c=col, ms=3, label=lab)
ax.set_xlabel("孔径长度 L (mm)"); ax.set_ylabel(r"信号源功率 $P_\pi$ (mW)")
from matplotlib.ticker import FuncFormatter
fmt = FuncFormatter(lambda v, _: f"{v:g}")
for a in (ax.xaxis, ax.yaxis):
    a.set_major_formatter(fmt); a.set_minor_formatter(FuncFormatter(lambda v, _: ""))
ax.set_yticks([1, 2, 5, 10, 20, 50])
ax.legend(frameon=False, fontsize=7); ax.grid(alpha=0.3, which="both")
save(fig, "fig_power")
print("figs done", sorted(pk))
