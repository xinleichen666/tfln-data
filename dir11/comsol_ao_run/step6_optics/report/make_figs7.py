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
    return rows


def peak_pl(log):
    r = sweep(log)
    f, a, pl = max(r, key=lambda t: t[1])
    return pl


fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.35, 1]})
sets = [("step7_U2M250.log", "无汇流条", "k"),
        ("step7_B25M250Z1500W.log", "段长 25 µm", "C0"),
        ("step7_B50M250Z1500W.log", "段长 50 µm", "C2"),
        ("step7_B100M250Z1000W.log", "段长 100 µm", "C3")]
for log, lab, c in sets:
    r = sweep(log)
    a1.plot([t[0] for t in r], [t[1] * 1e3 for t in r], color=c, lw=1.1, label=lab)
a1.set_xlim(3.200, 3.226)
a1.set_xlabel("频率（GHz）")
a1.set_ylabel(r"|tot|（$10^{-3}$/V）")
a1.legend(fontsize=7.5, frameon=False)
a1.grid(alpha=0.3)
a1.set_title("(a) 本设计，含汇流条（2 µm）", fontsize=9)

seg = [25, 50, 100]
ours = [peak_pl(l) for l in ("step7_B25M250Z1500W.log", "step7_B50M250Z1500W.log", "step7_B100M250Z1000W.log")]
shao = [peak_pl("step7_SB25M200Z1500W.log"), None, peak_pl("step7_SB100M200Z1500W.log")]
a2.plot(seg, [x * 1e6 for x in ours], "o-", color="C3", label="本设计")
a2.plot([25, 100], [shao[0] * 1e6, shao[2] * 1e6], "s--", color="C0", label="Shao 型（直壁近似）")
a2.axhline(peak_pl("step7_U2M250.log") * 1e6, color="C3", ls=":", lw=0.9)
a2.axhline(peak_pl("step7_SU2M200.log") * 1e6, color="C0", ls=":", lw=0.9)
a2.text(52, 1.3, "点线：无汇流条", fontsize=7.5, color="gray")
a2.set_xlabel("段长（µm）")
a2.set_ylabel(r"$P_\pi L$ 主峰（$10^{-6}$ W·m）")
a2.set_xticks(seg)
a2.set_ylim(0, 9.5)
a2.legend(fontsize=7.5, frameon=False)
a2.grid(alpha=0.3)
a2.set_title("(b) 段长依赖（沿波导网格 1–1.5 µm）", fontsize=9)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(HERE, "fig_3d." + ext), dpi=200)
print("ours", ours, "shao", shao)
