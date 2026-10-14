#!/usr/bin/env python3
"""Plot figures from data/summary.json → paper/fig/ (png+pdf)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

for _fp in (
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/arphic/uming.ttc",
):
    if Path(_fp).exists():
        font_manager.fontManager.addfont(_fp)
        _name = font_manager.FontProperties(fname=_fp).get_name()
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = [_name, "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
        break

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "summary.json"
FIG = ROOT / "paper" / "fig"


def save(fig, name: str):
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        p = FIG / f"{name}.{ext}"
        fig.savefig(p, dpi=200, bbox_inches="tight")
        print(f"[fig] {p}")
    plt.close(fig)


def plot_aligned(summary: dict):
    tags = [s["tag"] for s in summary["suites"]]
    models = [
        ("block_fidelity", "Block-Fid"),
        ("true_product_linear", "TrueProd-Lin"),
        ("rbf", "RBF"),
        ("laplacian", "Laplacian"),
        ("poly", "Poly-3"),
        ("linear", "Linear"),
    ]
    acc = {m: [] for m, _ in models}
    f1 = {m: [] for m, _ in models}
    for s in summary["suites"]:
        for m, _ in models:
            acc[m].append(s["aligned"][m]["accuracy"])
            f1[m].append(s["aligned"][m]["f1"])

    x = np.arange(len(tags))
    width = 0.13
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=False)
    for ax, metric, store in zip(axes, ["Accuracy", "F1"], [acc, f1]):
        for i, (m, label) in enumerate(models):
            ax.bar(x + (i - 2.5) * width, store[m], width, label=label)
        ax.set_xticks(x)
        ax.set_xticklabels(tags, rotation=20, ha="right", fontsize=8)
        ax.set_ylim(0.4, 1.05)
        ax.set_ylabel(metric)
        ax.axhline(0.5, color="gray", ls="--", lw=0.8)
        ax.set_title(f"Aligned blocks · {metric}")
        ax.legend(fontsize=7, ncol=2, loc="lower right")
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle(
        "Fig.aligned · 分块对准时准确率/F1（经典仿真，非量子优势）",
        fontsize=11,
    )
    fig.tight_layout()
    save(fig, "fig_aligned_acc_f1")


def _mark_zero(ax, vanish: dict, xs, color="k"):
    if vanish.get("vanished_in_sweep") and vanish.get("cross_x") is not None:
        ax.axvline(vanish["cross_x"], color=color, ls=":", lw=1.2)
        ax.text(
            vanish["cross_x"],
            ax.get_ylim()[1] * 0.92,
            f"gap≤0 @ {vanish['cross_x']:.2g}",
            fontsize=7,
            rotation=90,
            va="top",
            ha="right",
            color=color,
        )
    else:
        ax.text(
            0.98,
            0.05,
            "本扫范围内未消失",
            transform=ax.transAxes,
            fontsize=8,
            ha="right",
            va="bottom",
            color="darkgreen",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="darkgreen", alpha=0.8),
        )


def plot_mismatch(summary: dict):
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5), sharex=True)
    axes = axes.ravel()
    for ax, s in zip(axes, summary["suites"]):
        rows = s["mismatch_sweep"]
        xs = [r["shift"] for r in rows]
        g_rbf = [r["gap_vs_rbf_acc"] for r in rows]
        g_tpl = [r["gap_vs_tpl_acc"] for r in rows]
        ax.plot(xs, g_rbf, "o-", label="BF − RBF (acc)", color="C0")
        ax.plot(xs, g_tpl, "s--", label="BF − TrueProd-Lin (acc)", color="C1")
        ax.axhline(0, color="gray", lw=1)
        ax.set_title(s["tag"], fontsize=10)
        ax.set_xlabel("partition shift (wrong block boundaries)")
        ax.set_ylabel("accuracy gap")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
        # annotate using RBF vanish as primary
        _mark_zero(ax, s["vanish_mismatch_vs_rbf"], xs)
    fig.suptitle(
        "Fig.mismatch · 分块边界划错时 BF 相对基线的准确率差值",
        fontsize=11,
    )
    fig.tight_layout()
    save(fig, "fig_mismatch_gap")


def plot_flip(summary: dict):
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5), sharex=True)
    axes = axes.ravel()
    for ax, s in zip(axes, summary["suites"]):
        rows = s["flip_sweep"]
        xs = [r["flip_rate"] for r in rows]
        g_rbf = [r["gap_vs_rbf_acc"] for r in rows]
        g_tpl = [r["gap_vs_tpl_acc"] for r in rows]
        ax.plot(xs, g_rbf, "o-", label="BF − RBF (acc)", color="C0")
        ax.plot(xs, g_tpl, "s--", label="BF − TrueProd-Lin (acc)", color="C1")
        ax.axhline(0, color="gray", lw=1)
        ax.set_title(s["tag"], fontsize=10)
        ax.set_xlabel("train label flip rate")
        ax.set_ylabel("accuracy gap")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
        _mark_zero(ax, s["vanish_flip_vs_rbf"], xs)
    fig.suptitle(
        "Fig.flip · 训练集标签翻转比例增大时 BF 相对基线的准确率差值",
        fontsize=11,
    )
    fig.tight_layout()
    save(fig, "fig_flip_gap")


def plot_flip_raw(summary: dict):
    """Absolute accuracy vs flip for BF / RBF / TPL (one panel per suite)."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5), sharex=True)
    axes = axes.ravel()
    for ax, s in zip(axes, summary["suites"]):
        rows = s["flip_sweep"]
        xs = [r["flip_rate"] for r in rows]
        ax.plot(xs, [r["block_fidelity"]["accuracy"] for r in rows], "o-", label="Block-Fid")
        ax.plot(xs, [r["rbf"]["accuracy"] for r in rows], "^-", label="RBF")
        ax.plot(
            xs,
            [r["true_product_linear"]["accuracy"] for r in rows],
            "s-",
            label="TrueProd-Lin",
        )
        ax.set_title(s["tag"], fontsize=10)
        ax.set_xlabel("train label flip rate")
        ax.set_ylabel("test accuracy")
        ax.set_ylim(0.4, 1.05)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    fig.suptitle("Fig.flip_abs · 标签翻转下绝对准确率（对照）", fontsize=11)
    fig.tight_layout()
    save(fig, "fig_flip_abs")


def main():
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    plot_aligned(summary)
    plot_mismatch(summary)
    plot_flip(summary)
    plot_flip_raw(summary)
    print("[done] figures")


if __name__ == "__main__":
    main()
