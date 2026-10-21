# -*- coding: utf-8 -*-
"""Publication figures for the revised design-study preprint. Data unchanged."""
import json
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle, Polygon, Arc
from matplotlib.lines import Line2D

DATA = Path(r"D:\tfln\tfln-data\dir11\paperB\data")
OUT = Path(r"D:\comsol_ao_run\paper_v2\figures")
OUT.mkdir(parents=True, exist_ok=True)

AO = "#0072B2"
EO = "#D55E00"
MATCH = "#E69F00"
GREEN = "#009E73"
INK = "#222222"
GRID = "#E6E6E6"

mpl.rcParams.update({
    "font.family": "Times New Roman",
    "mathtext.fontset": "stix",
    "font.size": 9,
    "axes.labelsize": 10,
    "axes.titlesize": 10,
    "axes.linewidth": 0.7,
    "axes.edgecolor": INK,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 3.2,
    "ytick.major.size": 3.2,
    "xtick.color": INK,
    "ytick.color": INK,
    "text.color": INK,
    "axes.labelcolor": INK,
    "legend.frameon": False,
    "legend.fontsize": 7.6,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.04,
})


def panel(ax, letter):
    ax.text(-0.12, 1.06, letter, transform=ax.transAxes, fontsize=12, fontweight="bold", va="bottom")


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=220)
    plt.close(fig)


def load_eff():
    rows = []
    for line in (DATA / "eff_vs_power.csv").read_text(encoding="utf-8").splitlines()[1:]:
        a = line.split(",")
        rows.append((a[0], a[1], float(a[3]) * 1e3, float(a[4])))  # P in mW, eta
    return rows


def fig_device():
    fig, ax = plt.subplots(figsize=(7.4, 3.35))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 46)
    ax.set_aspect("equal")
    ax.axis("off")
    chip = FancyBboxPatch((1.5, 2.2), 66, 36, boxstyle="round,pad=0.4,rounding_size=1.0",
                          facecolor="#F4F6F8", edgecolor="#8A93A0", linewidth=0.8, zorder=0)
    ax.add_patch(chip)
    ax.text(64.5, 4.0, "TFLN", ha="right", va="bottom", fontsize=8, color="#5C6770")

    ax.plot([4, 65.5], [8.2, 8.2], color="#C47A8A", lw=3.4, solid_capstyle="round", zorder=2)
    ax.annotate("", xy=(15.5, 8.2), xytext=(8.2, 8.2),
                arrowprops=dict(arrowstyle="-|>", color="#E67E22", lw=1.5))
    ax.annotate("", xy=(62.5, 8.2), xytext=(54.5, 8.2),
                arrowprops=dict(arrowstyle="-|>", color="#0072B2", lw=1.5))
    ax.text(8.0, 10.6, r"input  $\omega$", color="#E67E22", fontsize=8.5, ha="center")
    ax.text(58.5, 10.6, r"output  $\omega+\Omega$", color="#0072B2", fontsize=8.5, ha="center")
    ax.text(34, 5.4, "bus waveguide", ha="center", fontsize=8, color="#8A5A64")

    ax.add_patch(Rectangle((12.5, 16.5), 16, 12, facecolor="#E7F0E4", edgecolor="#4C7A45", lw=0.7, zorder=1))
    for i, x in enumerate(np.linspace(13.8, 27.2, 10)):
        ax.plot([x, x], [17.6, 27.2], color="#C5922A" if i % 2 == 0 else "#7A5A12", lw=1.2, zorder=3)
    ax.add_patch(Rectangle((10.6, 28.4), 4.4, 2.2, facecolor="#E1B84A", edgecolor="#8A6A12", lw=0.4, zorder=4))
    ax.add_patch(Rectangle((25.8, 28.4), 4.4, 2.2, facecolor="#E1B84A", edgecolor="#8A6A12", lw=0.4, zorder=4))
    ax.plot([6.5, 12.6], [33.2, 29.5], color="#555", lw=0.8)
    ax.plot([30.4, 36.2], [33.2, 29.5], color="#555", lw=0.8)
    ax.text(20.5, 35.6, r"RF   $\Omega/2\pi = 3.33$ GHz", ha="center", fontsize=8)
    ax.text(20.5, 33.6, "IDT", ha="center", fontsize=8)
    ax.text(20.5, 15.2, "suspended acoustic section", ha="center", va="top", fontsize=7.5, color="#3E5C38")

    ax.add_patch(Circle((40.5, 20.5), 6.6, fill=False, ec="#C47A8A", lw=2.4, zorder=4))
    ax.add_patch(Circle((53.2, 30.2), 6.6, fill=False, ec="#C47A8A", lw=2.4, zorder=4))
    ax.add_patch(Arc((40.5, 20.5), 13.2, 13.2, theta1=155, theta2=215, color="#2E7D32", lw=2.2, zorder=5))
    ax.text(40.5, 20.5, "ring 1", ha="center", va="center", fontsize=8)
    ax.text(53.2, 30.2, "ring 2", ha="center", va="center", fontsize=8)
    ax.text(46.7, 25.6, r"$\mu$", fontsize=10, ha="center", va="center",
            bbox=dict(boxstyle="circle,pad=0.05", fc="#F4F6F8", ec="none"))

    ia = fig.add_axes([0.72, 0.22, 0.26, 0.62])
    ia.set_xlim(0, 10)
    ia.set_ylim(0, 10)
    ia.set_xticks([])
    ia.set_yticks([])
    for s in ia.spines.values():
        s.set_linewidth(0.6)
        s.set_color("#C5CAD1")
    ia.plot([0.7, 2.7], [2.4, 2.4], color=INK, lw=1.2)
    ia.plot([7.3, 9.3], [2.4, 2.4], color=INK, lw=1.2)
    ia.plot([3.7, 6.3], [7.2, 7.2], color="#0072B2", lw=1.5)
    ia.plot([3.7, 6.3], [4.6, 4.6], color="#D55E00", lw=1.5)
    ia.plot([1.7, 4.2], [2.4, 7.2], color="#C5CAD1", lw=0.7, ls="--")
    ia.plot([1.7, 4.2], [2.4, 4.6], color="#C5CAD1", lw=0.7, ls="--")
    ia.plot([8.3, 5.8], [2.4, 7.2], color="#C5CAD1", lw=0.7, ls="--")
    ia.plot([8.3, 5.8], [2.4, 4.6], color="#C5CAD1", lw=0.7, ls="--")
    ia.annotate("", xy=(6.7, 7.05), xytext=(6.7, 4.75),
                arrowprops=dict(arrowstyle="<->", color="#009E73", lw=1.0))
    ia.text(6.85, 5.9, r"$2\mu=\Omega$", color="#009E73", fontsize=8, va="center")
    ia.text(5.0, 9.2, "supermodes", ha="center", fontsize=9, fontweight="bold")
    ia.text(1.7, 1.15, r"$\omega_0$", ha="center", fontsize=8)
    ia.text(8.3, 1.15, r"$\omega_0$", ha="center", fontsize=8)
    ia.text(3.55, 7.45, r"$\omega_+$", fontsize=8, color="#0072B2", ha="right")
    ia.text(3.55, 4.15, r"$\omega_-$", fontsize=8, color="#D55E00", ha="right")
    ia.text(1.7, 3.05, "ring 1", fontsize=6.5, color="#666", ha="center")
    ia.text(8.3, 3.05, "ring 2", fontsize=6.5, color="#666", ha="center")
    save(fig, "fig1_device")


def fig_power():
    rows = load_eff()
    spec = json.loads((DATA / "results_B.json").read_text(encoding="utf-8"))["spectrum_dB"]
    styles = {
        "AO_Shao_IDT(50%)": (AO, "-", "AO, Shao IDT (50%)"),
        "AO_IDT_100%": (AO, "--", "AO, ideal IDT"),
        "AO_IDT_10%": (AO, ":", "AO, 10% IDT"),
        "EO_unmatched(Vc=V0)": (EO, "-", r"EO unmatched ($V_c=V_0$)"),
        "EO_open(Vc=2V0)": (EO, "-.", r"EO open ($V_c=2V_0$)"),
        "EO_LC_Q30": (MATCH, "--", r"EO LC, $Q_L=30$"),
        "EO_LC_Q100": (MATCH, "-", r"EO LC, $Q_L=100$"),
        "EO_LC_ideal": (MATCH, ":", r"EO LC, ideal $L$"),
    }
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.85), gridspec_kw={"width_ratios": [1.28, 1], "wspace": 0.30})
    ax = axes[0]
    handles = []
    for case, (c, ls, lab) in styles.items():
        pts = sorted((p, e) for d, k, p, e in rows if k == case)
        h, = ax.semilogx([p for p, e in pts], [e for p, e in pts], color=c, ls=ls, lw=1.4, label=lab)
        handles.append(h)
    hstar, = ax.plot(96, 0.987, marker="*", color="k", ms=10, ls="none", label="Hu 2021, measured")
    handles.append(hstar)
    ax.set_xlim(1e-6, 2e3)
    ax.set_ylim(-0.02, 1.12)
    ax.set_xlabel("source RF power (mW)")
    ax.set_ylabel(r"$\eta_{\mathrm{shift}}$")
    panel(ax, "a")

    ax = axes[1]
    qs = np.arange(-3, 4)
    w = 0.36
    ao = np.array([spec["ao"][str(q)] for q in qs]) - spec["ao"]["1"]
    eo = np.array([spec["eo"][str(q)] for q in qs]) - spec["eo"]["1"]
    ax.bar(qs - w / 2, ao, w, color=AO, label="AO", zorder=2)
    ax.bar(qs + w / 2, eo, w, color=MATCH, label="EO", zorder=2)
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_ylim(-70, 8)
    ax.set_xticks(qs)
    ax.set_xlabel(r"order $q$")
    ax.set_ylabel("dB relative to $q=+1$")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, lw=0.5)
    panel(ax, "b")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.96, bottom=0.30, wspace=0.32)
    fig.legend(handles, [h.get_label() for h in handles], loc="lower center", ncol=3,
               bbox_to_anchor=(0.52, 0.01), fontsize=7.3, handlelength=2.6, columnspacing=1.05)
    fig.savefig(OUT / "fig2_power_spectrum.pdf")
    fig.savefig(OUT / "fig2_power_spectrum.png", dpi=220)
    plt.close(fig)


def fig_tol():
    Q = np.loadtxt(DATA / "Q_tolerance.csv", delimiter=",", skiprows=1)
    D = np.loadtxt(DATA / "RF_detuning.csv", delimiter=",", skiprows=1)
    IDT = np.loadtxt(DATA / "IDT_sensitivity.csv", delimiter=",", skiprows=1)
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.7))
    ax = axes[0]
    ax.semilogx(Q[:, 1], Q[:, 2], "o-", color=AO, ms=4.5, lw=1.3, label=r"$\eta_{\mathrm{shift}}$")
    ax.semilogx(Q[:, 1], Q[:, 3], "s--", color="#56B4E9", ms=4.2, lw=1.2, label=r"$\eta_{\mathrm{abs}}$")
    ax.axvline(193.4e12 / 0.08075e9, color="#888", ls=":", lw=0.8)
    ax.text(2.55e6, 0.22, "Shao 2019", color="#666", fontsize=7, rotation=90, va="bottom")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel(r"intrinsic $Q_i$")
    ax.set_ylabel("efficiency")
    ax.legend(loc="center right", fontsize=7.4)
    panel(ax, "a")

    ax = axes[1]
    ax.plot(D[:, 0], D[:, 1], "o-", color=AO, ms=4.2, lw=1.3, label="AO")
    ax.plot(D[:, 0], D[:, 2], "s-", color=MATCH, ms=3.6, lw=1.2, label=r"EO, $Q_L=30$")
    ax.set_ylim(0, 1.08)
    ax.set_xlabel("RF detuning (MHz)")
    ax.set_ylabel(r"$\eta_{\mathrm{shift}}$")
    ax.legend(loc="center right", fontsize=7.4)
    panel(ax, "b")

    ax = axes[2]
    ax.loglog(IDT[:, 0] * 100, IDT[:, 1] * 1e6, color=AO, lw=1.5, label="AO")
    ax.axhline(13.07, color=MATCH, ls="--", lw=1.0, label=r"EO, $Q_L=30$")
    ax.axhline(4.78, color=MATCH, ls="-", lw=1.0, label=r"EO, $Q_L=100$")
    ax.axhline(1.23, color=MATCH, ls=":", lw=1.1, label=r"EO, ideal $L$")
    ax.axvline(10, color="#BBB", ls=":", lw=0.7)
    ax.axvline(50, color="#BBB", ls=":", lw=0.7)
    ax.text(10, 1.6, "10%", ha="center", fontsize=6.5, color="#777")
    ax.text(50, 1.6, "50%", ha="center", fontsize=6.5, color="#777")
    ax.set_xlabel("IDT efficiency (%)")
    ax.set_ylabel(r"source power ($\mu$W)")
    ax.legend(loc="upper right", fontsize=6.6)
    panel(ax, "c")
    fig.tight_layout()
    save(fig, "fig3_tolerance")


def fig_thermal():
    rows = []
    for line in (DATA / "tol_scan.csv").read_text(encoding="utf-8").splitlines()[1:]:
        a = line.split(",")
        rows.append(a)
    cuts = {}
    twod = []
    for a in rows:
        if a[0] in ("Delta", "dr", "eps"):
            cuts.setdefault(a[0], []).append((float(a[1]), float(a[5]), float(a[6])))
        elif a[0] == "2D":
            twod.append((float(a[3]), float(a[2]), float(a[5])))  # dr, Delta, eta
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.75))
    ax = axes[0]
    colors = {"Delta": AO, "dr": EO, "eps": GREEN}
    labels = {"Delta": r"$\Delta$, common", "dr": r"$\delta_r$, mismatch", "eps": r"$2\mu-\Omega$"}
    for k in ("Delta", "dr", "eps"):
        x, e, il = np.array(cuts[k]).T
        ax.plot(x, e, color=colors[k], lw=1.4, label=labels[k])
    ax.axhline(0.95, color="#888", ls="--", lw=0.6)
    ax.axhline(0.90, color="#888", ls=":", lw=0.6)
    ax.set_xlim(-300, 300)
    ax.set_ylim(0.5, 1.02)
    ax.set_xlabel("offset (MHz)")
    ax.set_ylabel(r"$\eta_{\mathrm{shift}}$")
    ax.text(-155, 0.58, r"$\Delta$", color=AO, fontsize=8)
    ax.text(145, 0.72, r"$\delta_r$", color=EO, fontsize=8)
    ax.text(55, 0.60, r"$2\mu-\Omega$", color=GREEN, fontsize=8)
    sec = ax.secondary_xaxis("top", functions=(lambda v: v / 2.809, lambda t: t * 2.809))
    sec.set_xlabel(r"$\Delta T$ (mK), thermo-optic only", fontsize=7.5)
    sec.tick_params(labelsize=7)
    panel(ax, "a")

    ax = axes[1]
    for k in ("Delta", "dr", "eps"):
        x, e, il = np.array(cuts[k]).T
        ax.plot(x, il, color=colors[k], lw=1.4)
    ax.set_xlim(-300, 300)
    ax.set_xlabel("offset (MHz)")
    ax.set_ylabel("insertion loss (dB)")
    panel(ax, "b")

    ax = axes[2]
    dr = np.array([t[0] for t in twod])
    De = np.array([t[1] for t in twod])
    et = np.array([t[2] for t in twod])
    n = int(round(np.sqrt(len(et))))
    # file order is meshgrid ravel of XX=dr, YY=Delta with default xy indexing: x varies fastest? 
    # tol_scan: for d,r_,e in zip(YY.ravel(), XX.ravel(), E2.ravel()) so Delta (d) then dr (r)
    # I stored (dr, Delta, eta) = (a[3], a[2], a[5])
    DR = dr.reshape(n, n)
    DD = De.reshape(n, n)
    EE = et.reshape(n, n)
    cs = ax.contourf(DR, DD, EE, levels=[0.5, 0.7, 0.8, 0.9, 0.95, 0.97, 1.0],
                     colors=["#313695", "#4575b4", "#74add1", "#abd9e9", "#fee090", "#fdae61"])
    ax.contour(DR, DD, EE, levels=[0.90, 0.95], colors="white", linewidths=0.7)
    ax.plot([-200, 200], [-100, 100], color="k", lw=0.6, ls="--")
    ax.set_xlabel(r"$\delta_r$ (MHz)")
    ax.set_ylabel(r"$\Delta$ (MHz)")
    cb = fig.colorbar(cs, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label(r"$\eta_{\mathrm{shift}}$", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    panel(ax, "c")
    fig.tight_layout()
    save(fig, "fig4_thermal")


def fig_mc():
    raw = (DATA / "mc_samples.csv").read_text(encoding="utf-8").splitlines()
    hdr = raw[0].split(",")
    mc = np.array([[float(x) for x in line.split(",")] for line in raw[1:]])
    col = {h: i for i, h in enumerate(hdr)}
    eta = mc[:, col["eta_shift"]]
    il = mc[:, col["IL_dB"]]
    S = json.loads((DATA / "realistic_summary.json").read_text(encoding="utf-8"))
    fig, axes = plt.subplots(2, 3, figsize=(7.4, 4.7))
    ax = axes[0, 0]
    ax.hist(eta, bins=36, color=AO, alpha=0.9, edgecolor="white", lw=0.3)
    ax.axvline(0.9835, color=INK, ls="--", lw=0.9, label="ideal 98.3%")
    ax.axvline(np.median(eta), color=EO, lw=1.1, label="median 94.3%")
    ax.set_xlabel(r"$\eta_{\mathrm{shift}}$")
    ax.set_ylabel("count")
    ax.legend(fontsize=7)
    panel(ax, "a")

    ax = axes[0, 1]
    ax.hist(il, bins=36, color=GREEN, alpha=0.9, edgecolor="white", lw=0.3)
    ax.axvline(2.49, color=INK, ls="--", lw=0.9, label="ideal 2.5 dB")
    ax.axvline(np.median(il), color=EO, lw=1.1, label="median 5.0 dB")
    ax.set_xlabel("on-chip insertion loss (dB)")
    ax.set_ylabel("count")
    ax.legend(fontsize=7)
    panel(ax, "b")

    ax = axes[0, 2]
    labels = ["ideal\nchip", "MC\nchip", "MC\nfiber", "Shao\n2020"]
    med = S["MC"]
    vals = [S["ideal"]["eta_abs"], med["eta_abs_onchip_p10_50_90"][1],
            med["eta_abs_fiber_to_fiber_p10_50_90"][1], 0.035]
    yerr = np.zeros((2, 4))
    yerr[0, 1] = vals[1] - med["eta_abs_onchip_p10_50_90"][0]
    yerr[1, 1] = med["eta_abs_onchip_p10_50_90"][2] - vals[1]
    yerr[0, 2] = vals[2] - med["eta_abs_fiber_to_fiber_p10_50_90"][0]
    yerr[1, 2] = med["eta_abs_fiber_to_fiber_p10_50_90"][2] - vals[2]
    ax.bar(np.arange(4), vals, color=["#B0B6BE", AO, MATCH, EO], yerr=yerr, capsize=3,
           error_kw=dict(lw=0.8, capthick=0.8), zorder=2)
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylabel("absolute shifted fraction")
    ax.set_ylim(0, 0.72)
    panel(ax, "c")

    def band(ax, key, xlabel):
        rows = S["sensitivity"][key]
        x = np.array([r[0] for r in rows], float)
        p10 = np.array([r[1] for r in rows])
        p50 = np.array([r[2] for r in rows])
        p90 = np.array([r[3] for r in rows])
        ax.fill_between(x, p10, p90, color=AO, alpha=0.18, lw=0)
        ax.plot(x, p50, "o-", color=AO, ms=4, lw=1.3)
        ax.set_ylim(0.45, 1.02)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(r"median $\eta_{\mathrm{shift}}$")

    band(axes[1, 0], "sig_gap_nm", "gap error $\\sigma$ (nm)")
    panel(axes[1, 0], "d")
    band(axes[1, 1], "sigT_lock_mK", "lock jitter (mK)")
    panel(axes[1, 1], "e")
    band(axes[1, 2], "ki_extra_frac", r"extra loss, $\kappa_i$ multiplier $-1$")
    # ki_extra_frac values are 0,0.5,1,2,4 meaning +0% to +400%, the column is the fraction added
    axes[1, 2].set_xlabel(r"extra $\kappa_i$ fraction")
    panel(axes[1, 2], "f")
    for ax in axes[1]:
        ax.axhline(0.90, color="#BBB", ls=":", lw=0.7)
    fig.tight_layout()
    save(fig, "fig5_montecarlo")


def fig_hom():
    H = np.loadtxt(DATA / "HOM.csv", delimiter=",", skiprows=1)
    fig, ax = plt.subplots(figsize=(3.7, 2.85))
    x = H[:, 0] / 1e6
    ax.semilogx(x, 1 - H[:, 2], "o-", color=GREEN, ms=5.5, lw=1.4, label="filtered, delay-matched")
    ax.semilogx(x, 1 - H[:, 3], "s--", color=EO, ms=5, lw=1.3, label="unfiltered")
    ax.axhline(1 - 0.98346, color="#888", ls=":", lw=0.7)
    ax.text(5.2, 4.2e-2, r"$1-\eta_{\mathrm{shift}}$", color="#666", fontsize=7.4, ha="left")
    ax.set_yscale("log")
    ax.set_xlabel("photon rms bandwidth (MHz)")
    ax.set_ylabel(r"$1-V_{\mathrm{HOM}}$")
    ax.set_ylim(3e-8, 3e-1)
    ax.legend(loc="lower right", fontsize=7.5)
    ax.set_axisbelow(True)
    save(fig, "fig6_hom")


if __name__ == "__main__":
    fig_device()
    fig_power()
    fig_tol()
    fig_thermal()
    fig_mc()
    fig_hom()
    print("ok", OUT)
