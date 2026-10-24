import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

HERE = os.path.dirname(os.path.abspath(__file__))
D = r"D:\comsol_ao_run"
P, ID, WR, HLN, HR = 1.84, 3, 1.0, 0.4, 0.4
XC = (ID + 0.5) * P


def load(case):
    a = np.loadtxt(os.path.join(D, "s9tr_%s.txt" % case), usecols=(0, 1, 2, 3, 4, 5))
    x, y = a[:, 0] * 1e6, a[:, 1] * 1e6
    xs, ys = np.unique(x), np.unique(y)
    a = a[np.lexsort((x, y))]
    ex = (a[:, 2] + 1j * a[:, 3]).reshape(len(ys), len(xs))
    ey = (a[:, 4] + 1j * a[:, 5]).reshape(len(ys), len(xs))
    e2 = abs(ex) ** 2 + abs(ey) ** 2
    return xs, ys, e2 / e2.max()


def outline(ax, susp):
    x0, x1 = XC - 3.5, XC + 3.5
    ax.add_patch(Rectangle((x0, 0), x1 - x0, HLN, fill=False, ec="w", lw=1))
    ax.add_patch(Rectangle((XC - WR / 2, HLN), WR, HR, fill=False, ec="w", lw=1))
    if not susp:
        ax.axhline(0, color="w", lw=0.6, ls="--")


def fig_modes():
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.0), sharey=True)
    for ax, case, ttl, susp in [(axs[0], "S0", "悬空段（脊下为空气），$n_{\\rm eff}$ = 1.92670", True),
                                (axs[1], "O2", "普通段（SiO$_2$ 2 µm 上），$n_{\\rm eff}$ = 1.93743", False)]:
        xs, ys, e2 = load(case)
        im = ax.pcolormesh(xs - XC, ys, e2, shading="auto", cmap="inferno", vmin=0, vmax=1, rasterized=True)
        outline(ax, susp)
        for p in ax.patches:
            p.set_x(p.get_x() - XC)
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-0.8, 1.6)
        ax.set_aspect("equal")
        ax.set_title(ttl, fontsize=10)
        ax.set_xlabel("x (µm)")
    axs[0].set_ylabel("y (µm)")
    cb = fig.colorbar(im, ax=axs, shrink=0.85, pad=0.02)
    cb.set_label("$|E|^2$（归一化）")
    fig.savefig(os.path.join(HERE, "fig_modes.png"), dpi=220, bbox_inches="tight")


def fig_layout():
    RED, GRY, FLT, BEAM = "#c0392b", "#555555", "#d4ac0d", "#2e86c1"
    fig, ax = plt.subplots(figsize=(10.5, 4.2))
    segw, gap, nseg = 10.0, 1.0, 4
    bw, nf, fp, y0 = 0.3, 4, 0.55, 0.75
    gaps = [RED, FLT, GRY, FLT, RED]
    labs = ["信号", "浮空", "地", "浮空", "信号"]
    ytop = y0 + nf * fp
    x = 0.0
    for s in range(nseg + 1):
        gx = s * (segw + gap) - gap / 2
        c = gaps[s]
        for sg in (1, -1):
            yb0, yb1 = sorted((sg * (ytop + 0.1), sg * (ytop + 1.9)))
            ax.add_patch(Rectangle((gx - 0.3, yb0), 0.6, yb1 - yb0, color=BEAM))
            if c != FLT:
                ax.add_patch(Rectangle((gx - 0.1, yb0), 0.2, yb1 - yb0, color=c))
        ax.text(gx, ytop + 2.65, labs[s], ha="center", fontsize=8.5, color=c if c != FLT else "#9a7d0a")
    for s in range(nseg):
        x0, x1 = s * (segw + gap), s * (segw + gap) + segw
        cl, cr = gaps[s], gaps[s + 1]
        for sg in (1, -1):
            yb0, yb1 = sorted((sg * y0 * 0.85, sg * (ytop + 0.1)))
            ax.add_patch(Rectangle((x0, yb0), bw, yb1 - yb0, color=cl))
            ax.add_patch(Rectangle((x1 - bw, yb0), bw, yb1 - yb0, color=cr))
            for k in range(nf):
                yf = sg * (y0 + k * fp + 0.1)
                if k % 2 == 0:
                    ax.add_patch(Rectangle((x0 + bw, yf - 0.07), segw - 2 * bw - 0.5, 0.14, color=cl))
                else:
                    ax.add_patch(Rectangle((x0 + bw + 0.5, yf - 0.07), segw - 2 * bw - 0.5, 0.14, color=cr))
    xe = nseg * (segw + gap)
    ax.add_patch(Rectangle((-1.5, -0.2), xe + 1.5, 0.4, color="#85c1e9"))
    ax.text(xe + 0.2, 0, "TE0 光波导（脊 1 µm × 400 nm）", va="center", fontsize=9)
    for sg, txt in ((1, "引线轨（锚区）"), (-1, "引线轨（锚区）")):
        yr = sg * (ytop + 2.0)
        ax.add_patch(Rectangle((-1.5, yr - 0.3 if sg > 0 else yr - 0.3), xe + 1.5, 0.6, color="#bbbbbb"))
        ax.text(xe + 0.2, yr, txt + "：信号轨 + 地轨", va="center", fontsize=9)
    ax.annotate("", xy=(0, -ytop - 2.75), xytext=(segw, -ytop - 2.75), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(segw / 2, -ytop - 3.2, "一段 100 µm", ha="center", fontsize=9)
    ax.annotate("支撑梁 2 µm（梁上铝走线）", xy=(segw + gap / 2 + 0.3, ytop + 1.0), xytext=(segw + 2.5, ytop + 1.0),
                fontsize=9, va="center", arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.annotate("汇流条 0.5 µm", xy=(2 * (segw + gap) + 0.15, -ytop + 0.4), xytext=(2 * (segw + gap) + 2.0, -ytop - 1.2),
                fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.text(xe + 0.2, ytop - 0.6, "叉指平行于波导\n周期 1.84 µm，铝 100 nm", fontsize=9, va="center")
    ax.text(-1.5, -ytop - 4.1, "示意图，不按比例（只画 4 段、每侧 4 根指）。L = 1 mm = 10 段；段间隙电位依次为 信号 / 浮空 / 地 / 浮空，"
            "相邻两段串联，共 2 串 × 5 并接 50 Ω。", fontsize=8.5, color="#444")
    ax.set_xlim(-2, xe + 12)
    ax.set_ylim(-ytop - 4.5, ytop + 3.0)
    ax.axis("off")
    fig.savefig(os.path.join(HERE, "fig_layout.png"), dpi=220, bbox_inches="tight")


if __name__ == "__main__":
    fig_layout()
    fig_modes()
