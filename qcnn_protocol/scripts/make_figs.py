#!/usr/bin/env python3
"""Make paper figures from data/summary.json and data/histories.json."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIG = ROOT / "paper" / "fig"
FIG.mkdir(parents=True, exist_ok=True)


def save(fig, name: str):
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.png", dpi=150)
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)
    print("wrote", name)


def main():
    summary = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    histories = json.loads((DATA / "histories.json").read_text(encoding="utf-8"))
    rows = summary["comparison_table"]

    # Fig 1: example images
    ex = np.load(DATA / "examples.npz")
    fig, axes = plt.subplots(2, 4, figsize=(8, 4))
    for i in range(4):
        axes[0, i].imshow(ex["X_train"][i], cmap="gray")
        axes[0, i].set_title(f"train y={int(ex['y_train'][i])}")
        axes[0, i].axis("off")
        axes[1, i].imshow(ex["X_test"][i], cmap="gray")
        axes[1, i].set_title(f"test y={int(ex['y_test'][i])}")
        axes[1, i].axis("off")
    fig.suptitle("Local 4×4 bar/diag samples (not HEP)")
    save(fig, "fig1_examples")

    # Fig 2: test acc QCNN vs CNN (full)
    labels = [r["run_id"] for r in rows]
    q = [r["qcnn_test_acc_full"] for r in rows]
    c = [r["cnn_test_acc_full"] for r in rows]
    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(x - w / 2, q, w, label="QCNN full")
    ax.bar(x + w / 2, c, w, label="CNN matched")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("test accuracy")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.set_title("Protocol comparison (full-parameter)")
    ax.axhline(0.5, color="gray", ls="--", lw=0.8)
    save(fig, "fig2_acc_full")

    # Fig 3: delta QCNN - CNN
    deltas = [r["delta_test_qcnn_minus_cnn_full"] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 3.5))
    colors = ["#2ca02c" if d > 0 else "#d62728" if d < 0 else "#7f7f7f" for d in deltas]
    ax.bar(x, deltas, color=colors)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("Δ test acc (QCNN − CNN)")
    ax.set_title("Sign of advantage (positive ⇒ QCNN higher this run)")
    save(fig, "fig3_delta")

    # Fig 4: prune before/after
    pr = summary["prune_table"]
    fig, ax = plt.subplots(figsize=(10, 3.5))
    before = [r["test_acc_before"] for r in pr]
    after = [r["test_acc_after"] for r in pr]
    ax.plot(x, before, "o-", label="before prune")
    ax.plot(x, after, "s-", label="after prune")
    ax.set_xticks(x)
    ax.set_xticklabels([r["run_id"] for r in pr], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("QCNN test accuracy")
    ax.set_title("Dimensional-expressivity prune (sensitivity keep≈60%)")
    ax.legend()
    save(fig, "fig4_prune")

    # Fig 5: low-param regime
    low = summary["low_param_regime"]
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, r in enumerate(low):
        ax.scatter(r["n_params"], r["qcnn_test_acc"], c="C0", marker="o")
        ax.scatter(r["n_params"], r["cnn_test_acc"], c="C1", marker="x")
    ax.scatter([], [], c="C0", marker="o", label="QCNN pruned")
    ax.scatter([], [], c="C1", marker="x", label="CNN matched-to-pruned")
    ax.set_xlabel("parameter count (pruned regime)")
    ax.set_ylabel("test accuracy")
    ax.set_title("Low-parameter regime")
    ax.legend()
    save(fig, "fig5_low_param")

    # Fig 6: one training curve example (first run)
    h0 = histories[0]
    fig, ax = plt.subplots(figsize=(7, 4))
    ep = [e["epoch"] for e in h0["hist_qcnn_full"]]
    ax.plot(ep, [e["test_acc"] for e in h0["hist_qcnn_full"]], label="QCNN test")
    ax.plot(ep, [e["test_acc"] for e in h0["hist_cnn_full"]], label="CNN test")
    ax.set_xlabel("epoch")
    ax.set_ylabel("test accuracy")
    ax.set_title(f"Training curve: {h0['run_id']}")
    ax.legend()
    save(fig, "fig6_train_curve")

    print("all figs done")


if __name__ == "__main__":
    main()
