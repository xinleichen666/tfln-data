import re, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 9

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
LAM = 1.55e-6
PAT = re.compile(r"^F7 f_GHz=([\d.]+) .*abs_tot=([-\d.e+]+) ReY_Spm=([-\d.e+]+)")


def sweep(log):
    rows = []
    for ln in open(os.path.join(SRC, log), encoding="utf-8", errors="replace"):
        m = PAT.match(ln)
        if m:
            f, a, y = map(float, m.groups())
            rows.append((f, a, y * (LAM / (2 * a)) ** 2 / 2))
    rows.sort()
    return [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows]


sets = [("step7_U2.log", "无汇流条（三维，验证）", "k", "-"),
        ("step7_B25W.log", "段长 25 µm（含汇流条）", "C0", "-"),
        ("step7_B50M200Z900W.log", "段长 50 µm（含汇流条）", "C3", "-")]

fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.6, 4.6), sharex=True)
for log, lab, c, ls in sets:
    f, a, pl = sweep(log)
    a1.plot(f, [x * 1e3 for x in a], color=c, ls=ls, lw=1.2, label=lab)
    a2.semilogy(f, pl, color=c, ls=ls, lw=1.2)
a2.axhline(2.43e-6, color="gray", ls="--", lw=0.8)
a2.text(3.1965, 2.6e-6, "二维有限长 2.43e-6", color="gray", fontsize=8)
a1.set_ylabel(r"|tot|（$10^{-3}$/V）")
a2.set_ylabel(r"$P_\pi L$（W·m）")
a2.set_xlabel("频率（GHz）")
a2.set_ylim(1.5e-6, 3e-5)
a1.legend(fontsize=8, frameon=False)
for ax in (a1, a2):
    ax.grid(alpha=0.3)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(HERE, "fig_3d." + ext), dpi=200)
print("ok")
