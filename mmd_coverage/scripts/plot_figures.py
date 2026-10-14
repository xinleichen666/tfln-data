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


def plot_loss_vs_unseen(summary: dict):
    """Main figure: x=training MMD² loss, y=unseen valid coverage."""
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    colors = {"ProductValid": "#1f77b4", "PairIsingValid": "#d62728"}
    markers = {"ProductValid": "o", "PairIsingValid": "s"}
    for m in summary["models"]:
        name = m["name"]
        hist = m["history"]
        # skip step 0 (huge loss) for readability; keep in json
        pts = [h for h in hist if h["step"] > 0]
        xs = [h["loss_mmd2"] for h in pts]
        ys = [h["unseen_valid_coverage"] for h in pts]
        ax.plot(
            xs,
            ys,
            "-" + markers[name],
            color=colors[name],
            label=name,
            markersize=5,
            linewidth=1.6,
            alpha=0.9,
        )
    # mark matched-loss snapshots
    for snap in summary["separation"]["matched_snapshots"]:
        ax.scatter(
            [snap["loss_mmd2"]],
            [snap["unseen_valid_coverage"]],
            s=90,
            facecolors="none",
            edgecolors="black",
            linewidths=1.5,
            zorder=5,
        )
    Lstar = summary["separation"]["L_star"]
    ax.axvline(Lstar, color="gray", ls="--", lw=1, alpha=0.7, label=f"L*={Lstar:.3f}")
    ax.set_xlabel("训练损失 MMD²（Pauli-Z 矩，相对训练集经验矩）")
    ax.set_ylabel("未见有效串覆盖率（直接采样）")
    ax.set_title("损失–未见覆盖：同级 MMD 下覆盖可分叉")
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)
    # annotation
    verdict = summary["headline"]["verdict_zh"]
    ax.text(
        0.98,
        0.02,
        verdict,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85),
    )
    save(fig, "fig_loss_unseen_coverage")


def plot_loss_curves(summary: dict):
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    colors = {"ProductValid": "#1f77b4", "PairIsingValid": "#d62728"}
    for m in summary["models"]:
        hist = m["history"]
        ax.plot(
            [h["step"] for h in hist],
            [h["loss_mmd2"] for h in hist],
            "-o",
            color=colors[m["name"]],
            label=m["name"],
            markersize=3.5,
            linewidth=1.5,
        )
    ax.set_yscale("log")
    ax.set_xlabel("训练步")
    ax.set_ylabel("MMD²（log）")
    ax.set_title("两模型同损失类：MMD² 随步数")
    ax.grid(True, alpha=0.3, which="both")
    ax.legend()
    save(fig, "fig_loss_vs_step")


def plot_coverage_bars(summary: dict):
    """Matched-loss train / unseen coverage + final KL."""
    snaps = summary["separation"]["matched_snapshots"]
    names = [s["model"] for s in snaps]
    train_c = [s["train_coverage"] for s in snaps]
    unseen_c = [s["unseen_valid_coverage"] for s in snaps]
    x = np.arange(len(names))
    w = 0.35
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.bar(x - w / 2, train_c, w, label="训练串覆盖", color="#7f7f7f")
    ax.bar(x + w / 2, unseen_c, w, label="未见有效覆盖", color="#ff7f0e")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("覆盖率（n_sample_eval 直接采样）")
    ax.set_title(f"匹配损失 L*={summary['separation']['L_star']:.4f} 处覆盖对照")
    for i, s in enumerate(snaps):
        ax.text(i, max(train_c[i], unseen_c[i]) + 0.03, f"loss={s['loss_mmd2']:.3f}", ha="center", fontsize=8)
    ax.legend(loc="upper right")
    ax.grid(True, axis="y", alpha=0.3)
    save(fig, "fig_matched_coverage_bars")


def plot_kl_bars(summary: dict):
    snaps = summary["separation"]["matched_snapshots"]
    names = [s["model"] for s in snaps]
    kls = [s["forward_kl_pstar_q"] for s in snaps]
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    colors = ["#1f77b4", "#d62728"]
    ax.bar(names, kls, color=colors)
    ax.set_ylabel("前向 KL(p* ∥ q)")
    ax.set_title("匹配损失处：对自构目标的前向 KL")
    ax.grid(True, axis="y", alpha=0.3)
    for i, v in enumerate(kls):
        ax.text(i, v + 0.002, f"{v:.4f}", ha="center", fontsize=9)
    save(fig, "fig_matched_forward_kl")


def main():
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    plot_loss_vs_unseen(summary)
    plot_loss_curves(summary)
    plot_coverage_bars(summary)
    plot_kl_bars(summary)
    print("[plot] OK")


if __name__ == "__main__":
    main()
