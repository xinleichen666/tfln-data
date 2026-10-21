#!/usr/bin/env python3
"""
qcnn_protocol: noiseless QCNN vs param-matched classical CNN.
Prior cue only: Elhag et al. arXiv:2408.08701 (see prior_bib.md).
No literature accuracy numbers enter summary.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (  # noqa: E402
    BATCH_SIZES,
    ENCODINGS,
    EPOCHS,
    IMG_SIZE,
    LOSSES,
    LR_C,
    LR_Q,
    N_QUBITS,
    N_TEST,
    N_TRAIN,
    PRIOR_ARXIV,
    SEED_DATA,
    SEED_INIT,
    SEED_SPLIT,
    SEED_TRAIN,
    SIMULATOR_NAME,
)

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
N_PARAMS_FULL = 15


# ---------- dataset ----------
def make_dataset(n_train: int, n_test: int, seed: int):
    rng = np.random.default_rng(seed)
    n = n_train + n_test
    X = np.zeros((n, IMG_SIZE, IMG_SIZE), dtype=np.float64)
    y = np.zeros(n, dtype=np.int64)
    for i in range(n):
        label = int(i % 2)
        y[i] = label
        img = rng.normal(0.0, 0.15, size=(IMG_SIZE, IMG_SIZE))
        if label == 0:
            row = int(rng.integers(0, IMG_SIZE))
            img[row, :] += 1.0
            if rng.random() < 0.5:
                img[(row + 1) % IMG_SIZE, :] += 0.5
        else:
            for k in range(IMG_SIZE):
                img[k, k] += 1.0
            if rng.random() < 0.5:
                for k in range(IMG_SIZE - 1):
                    img[k, k + 1] += 0.5
        X[i] = img
    rng_s = np.random.default_rng(SEED_SPLIT)
    perm = rng_s.permutation(n)
    X, y = X[perm], y[perm]
    return X[:n_train], y[:n_train], X[n_train:], y[n_train:]


def encode_angle4(img: np.ndarray) -> np.ndarray:
    blocks = img.reshape(2, 2, 2, 2).mean(axis=(1, 3)).ravel()
    blocks = blocks - blocks.min()
    if blocks.max() > 1e-12:
        blocks = blocks / blocks.max()
    return blocks * np.pi


def encode_amplitude(img: np.ndarray) -> np.ndarray:
    v = np.abs(img.ravel().astype(np.float64))
    nrm = np.linalg.norm(v)
    if nrm < 1e-12:
        v = np.ones_like(v) / np.sqrt(v.size)
    else:
        v = v / nrm
    return v


# ---------- fast statevector (bit ops) ----------
def ry_mat(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=np.complex128)


def rz_mat(theta: float) -> np.ndarray:
    e = np.exp(-1j * theta / 2)
    return np.array([[e, 0], [0, np.conj(e)]], dtype=np.complex128)


def apply_1q(state: np.ndarray, U: np.ndarray, q: int, n: int) -> np.ndarray:
    # reshape so qubit q is axis -1 via stride trick
    dim = 1 << n
    state = state.reshape([2] * n)
    axes = [i for i in range(n) if i != q] + [q]
    s = np.transpose(state, axes).reshape(-1, 2)
    s = s @ U.T
    out = s.reshape([2] * n)
    inv = np.empty(n, dtype=int)
    inv[axes] = np.arange(n)
    return np.transpose(out, inv).reshape(dim)


def apply_cnot(state: np.ndarray, c: int, t: int, n: int) -> np.ndarray:
    """CNOT with little-endian qubit 0 = LSB."""
    dim = 1 << n
    cbit, tbit = 1 << c, 1 << t
    out = np.zeros_like(state)
    for i in range(dim):
        if i & cbit:
            out[i ^ tbit] = state[i]
        else:
            out[i] = state[i]
    return out


def z_exp(state: np.ndarray, q: int, n: int) -> float:
    probs = np.abs(state) ** 2
    bit = 1 << q
    e = 0.0
    for i, p in enumerate(probs):
        e += p if (i & bit) == 0 else -p
    return float(e)


def prepare_state(encoding: str, img: np.ndarray) -> np.ndarray:
    n, dim = N_QUBITS, 1 << N_QUBITS
    if encoding == "angle4":
        angles = encode_angle4(img)
        state = np.zeros(dim, dtype=np.complex128)
        state[0] = 1.0
        for q, a in enumerate(angles):
            state = apply_1q(state, ry_mat(a), q, n)
        return state
    if encoding == "amplitude":
        amp = encode_amplitude(img)
        state = np.zeros(dim, dtype=np.complex128)
        state[: amp.size] = amp.astype(np.complex128)
        return state
    raise ValueError(encoding)


def qcnn_forward_from_state(state0: np.ndarray, theta: np.ndarray, mask: np.ndarray) -> float:
    n = N_QUBITS
    th = theta * mask
    s = state0.copy()
    s = apply_1q(s, ry_mat(th[0]), 0, n)
    s = apply_1q(s, rz_mat(th[1]), 0, n)
    s = apply_1q(s, ry_mat(th[2]), 1, n)
    s = apply_1q(s, rz_mat(th[3]), 1, n)
    s = apply_cnot(s, 0, 1, n)
    s = apply_1q(s, ry_mat(th[4]), 2, n)
    s = apply_1q(s, rz_mat(th[5]), 2, n)
    s = apply_1q(s, ry_mat(th[6]), 3, n)
    s = apply_1q(s, rz_mat(th[7]), 3, n)
    s = apply_cnot(s, 2, 3, n)
    s = apply_1q(s, ry_mat(th[8]), 0, n)
    s = apply_1q(s, ry_mat(th[9]), 2, n)
    s = apply_1q(s, ry_mat(th[10]), 0, n)
    s = apply_1q(s, rz_mat(th[11]), 0, n)
    s = apply_1q(s, ry_mat(th[12]), 2, n)
    s = apply_1q(s, rz_mat(th[13]), 2, n)
    s = apply_cnot(s, 0, 2, n)
    s = apply_1q(s, ry_mat(th[14]), 0, n)
    return z_exp(s, 0, n)


def predict_states(states, theta, mask):
    return np.array([qcnn_forward_from_state(st, theta, mask) for st in states])


def loss_value(pred, y_pm1, loss_name):
    if loss_name == "mse":
        return float(np.mean((pred - y_pm1) ** 2))
    p = np.clip((pred + 1.0) / 2.0, 1e-6, 1 - 1e-6)
    y01 = (y_pm1 + 1.0) / 2.0
    return float(-np.mean(y01 * np.log(p) + (1 - y01) * np.log(1 - p)))


def accuracy_from_z(pred, y_pm1):
    return float(np.mean(np.where(pred >= 0.0, 1.0, -1.0) == y_pm1))


def precompute_states(X, encoding):
    return [prepare_state(encoding, img) for img in X]


# ---------- SPSA train ----------
def train_qcnn_spsa(states_tr, ytr_pm, states_te, yte_pm, loss_name, batch_size, mask, seed_init):
    rng = np.random.default_rng(seed_init)
    theta = rng.normal(0, 0.3, size=N_PARAMS_FULL)
    rng_t = np.random.default_rng(SEED_TRAIN)
    hist = []
    n = len(states_tr)
    # SPSA hyperparameters
    a0, c0 = LR_Q, 0.1
    for ep in range(EPOCHS):
        idx = rng_t.permutation(n)
        losses = []
        step = 0
        for start in range(0, n, batch_size):
            bi = idx[start : start + batch_size]
            batch = [states_tr[i] for i in bi]
            yb = ytr_pm[bi]
            # SPSA perturbation on active params
            delta = rng_t.choice([-1.0, 1.0], size=N_PARAMS_FULL)
            delta = delta * mask
            ck = c0 / ((ep + 1) ** 0.101)
            ak = a0 / ((ep + 10) ** 0.602)
            pred_p = predict_states(batch, theta + ck * delta, mask)
            pred_m = predict_states(batch, theta - ck * delta, mask)
            lp = loss_value(pred_p, yb, loss_name)
            lm = loss_value(pred_m, yb, loss_name)
            ghat = (lp - lm) / (2.0 * ck) * delta
            # inactive grads zero
            ghat = ghat * mask
            theta = theta - ak * ghat
            losses.append(0.5 * (lp + lm))
            step += 1
        tr_pred = predict_states(states_tr, theta, mask)
        te_pred = predict_states(states_te, theta, mask)
        hist.append(
            {
                "epoch": ep,
                "train_loss": float(np.mean(losses)),
                "train_acc": accuracy_from_z(tr_pred, ytr_pm),
                "test_acc": accuracy_from_z(te_pred, yte_pm),
            }
        )
    return theta, hist


# ---------- classical matched MLP ----------
def cnn_param_count(h: int) -> int:
    return 17 * h + 1


def choose_h(target: int) -> int:
    best_h, best_diff = 1, abs(cnn_param_count(1) - target)
    for h in range(1, 8):
        d = abs(cnn_param_count(h) - target)
        if d < best_diff:
            best_h, best_diff = h, d
    return best_h


def cnn_init(h, rng):
    return {
        "W1": rng.normal(0, 1 / np.sqrt(16), size=(16, h)),
        "b1": np.zeros(h),
        "W2": rng.normal(0, 1 / np.sqrt(h), size=(h, 1)),
        "b2": np.zeros(1),
        "h": h,
    }


def cnn_forward(X_flat, params):
    h1 = np.tanh(X_flat @ params["W1"] + params["b1"])
    return np.tanh((h1 @ params["W2"] + params["b2"]).ravel())


def loss_dpred(pred, y_pm1, loss_name):
    if loss_name == "mse":
        return 2.0 * (pred - y_pm1)
    p = np.clip((pred + 1.0) / 2.0, 1e-6, 1 - 1e-6)
    y01 = (y_pm1 + 1.0) / 2.0
    return (-y01 / p + (1 - y01) / (1 - p)) * 0.5


def cnn_train_epoch(X_flat, y_pm1, params, lr, batch_size, loss_name, rng):
    n = len(X_flat)
    idx = rng.permutation(n)
    total, nb = 0.0, 0
    for start in range(0, n, batch_size):
        bi = idx[start : start + batch_size]
        xb, yb = X_flat[bi], y_pm1[bi]
        z1 = xb @ params["W1"] + params["b1"]
        h1 = np.tanh(z1)
        z2 = (h1 @ params["W2"] + params["b2"]).ravel()
        pred = np.tanh(z2)
        total += loss_value(pred, yb, loss_name)
        nb += 1
        dL = loss_dpred(pred, yb, loss_name) / len(bi)
        d_z2 = dL * (1 - pred**2)
        dW2 = h1.T @ d_z2.reshape(-1, 1)
        db2 = d_z2.sum(keepdims=True)
        dh1 = d_z2.reshape(-1, 1) @ params["W2"].T
        dz1 = dh1 * (1 - h1**2)
        params["W2"] -= lr * dW2
        params["b2"] -= lr * db2.ravel()
        params["W1"] -= lr * (xb.T @ dz1)
        params["b1"] -= lr * dz1.sum(axis=0)
    return total / max(nb, 1)


def train_cnn(Xtr, ytr_pm, Xte, yte_pm, loss_name, batch_size, n_params_target, seed_init):
    h = choose_h(n_params_target)
    rng = np.random.default_rng(seed_init)
    params = cnn_init(h, rng)
    Xtr_f = Xtr.reshape(len(Xtr), -1)
    Xte_f = Xte.reshape(len(Xte), -1)
    rng_t = np.random.default_rng(SEED_TRAIN + 7)
    hist = []
    for ep in range(EPOCHS):
        tr_loss = cnn_train_epoch(Xtr_f, ytr_pm, params, LR_C, batch_size, loss_name, rng_t)
        hist.append(
            {
                "epoch": ep,
                "train_loss": float(tr_loss),
                "train_acc": accuracy_from_z(cnn_forward(Xtr_f, params), ytr_pm),
                "test_acc": accuracy_from_z(cnn_forward(Xte_f, params), yte_pm),
            }
        )
    return params, hist, cnn_param_count(h), h


# ---------- expressivity prune ----------
def sensitivity_scores(states_probe, theta, mask, max_probe=20):
    probe = states_probe[:max_probe]
    scores = np.zeros(len(theta))
    shift = np.pi / 2
    for j in range(len(theta)):
        if mask[j] < 0.5:
            continue
        tp, tm = theta.copy(), theta.copy()
        tp[j] += shift
        tm[j] -= shift
        dpred = (predict_states(probe, tp, mask) - predict_states(probe, tm, mask)) / 2.0
        scores[j] = float(np.var(dpred))
    return scores


def prune_mask(scores, keep_fraction=0.6):
    active = np.where(scores > 0)[0]
    if len(active) == 0:
        return np.ones_like(scores)
    k = max(1, int(np.ceil(len(active) * keep_fraction)))
    order = active[np.argsort(scores[active])[::-1]]
    mask = np.zeros_like(scores)
    mask[order[:k]] = 1.0
    return mask


def main():
    print("dataset...")
    Xtr, ytr, Xte, yte = make_dataset(N_TRAIN, N_TEST, SEED_DATA)
    ytr_pm = np.where(ytr == 1, 1.0, -1.0)
    yte_pm = np.where(yte == 1, 1.0, -1.0)

    # cache states per encoding
    state_cache = {enc: (precompute_states(Xtr, enc), precompute_states(Xte, enc)) for enc in ENCODINGS}

    comparison_rows, prune_rows, low_param_rows, runs = [], [], [], []

    for encoding in ENCODINGS:
        str_tr, str_te = state_cache[encoding]
        for loss_name in LOSSES:
            for bs in BATCH_SIZES:
                run_id = f"{encoding}_{loss_name}_bs{bs}"
                print(f"== {run_id} ==")
                mask_full = np.ones(N_PARAMS_FULL)
                theta, hist_q = train_qcnn_spsa(
                    str_tr, ytr_pm, str_te, yte_pm, loss_name, bs, mask_full, SEED_INIT
                )
                q_test, q_train = hist_q[-1]["test_acc"], hist_q[-1]["train_acc"]
                n_q = int(mask_full.sum())

                _, hist_c, n_c, h = train_cnn(
                    Xtr, ytr_pm, Xte, yte_pm, loss_name, bs, n_q, SEED_INIT + 1
                )
                c_test, c_train = hist_c[-1]["test_acc"], hist_c[-1]["train_acc"]

                scores = sensitivity_scores(str_tr, theta, mask_full)
                mask_pr = prune_mask(scores, 0.6)
                n_pr = int(mask_pr.sum())
                print(f"  prune keep {n_pr}/{N_PARAMS_FULL}")
                _, hist_pr = train_qcnn_spsa(
                    str_tr, ytr_pm, str_te, yte_pm, loss_name, bs, mask_pr, SEED_INIT + 2
                )
                _, hist_c2, n_c2, h2 = train_cnn(
                    Xtr, ytr_pm, Xte, yte_pm, loss_name, bs, n_pr, SEED_INIT + 3
                )

                row = {
                    "run_id": run_id,
                    "encoding": encoding,
                    "loss": loss_name,
                    "batch_size": bs,
                    "optimizer": "SPSA",
                    "qcnn_n_params_full": n_q,
                    "qcnn_test_acc_full": q_test,
                    "qcnn_train_acc_full": q_train,
                    "cnn_n_params_full": n_c,
                    "cnn_hidden": h,
                    "cnn_test_acc_full": c_test,
                    "cnn_train_acc_full": c_train,
                    "delta_test_qcnn_minus_cnn_full": q_test - c_test,
                    "qcnn_n_params_pruned": n_pr,
                    "qcnn_test_acc_pruned": hist_pr[-1]["test_acc"],
                    "qcnn_train_acc_pruned": hist_pr[-1]["train_acc"],
                    "cnn_n_params_pruned_match": n_c2,
                    "cnn_hidden_pruned_match": h2,
                    "cnn_test_acc_pruned_match": hist_c2[-1]["test_acc"],
                    "delta_test_qcnn_minus_cnn_pruned": hist_pr[-1]["test_acc"]
                    - hist_c2[-1]["test_acc"],
                    "pruned_param_indices": [int(i) for i in np.where(mask_pr < 0.5)[0]],
                    "kept_param_indices": [int(i) for i in np.where(mask_pr > 0.5)[0]],
                    "sensitivity_scores": [float(s) for s in scores],
                }
                comparison_rows.append(row)
                prune_rows.append(
                    {
                        "run_id": run_id,
                        "n_before": n_q,
                        "n_after": n_pr,
                        "test_acc_before": q_test,
                        "test_acc_after": hist_pr[-1]["test_acc"],
                        "test_acc_change": hist_pr[-1]["test_acc"] - q_test,
                    }
                )
                low_param_rows.append(
                    {
                        "run_id": run_id,
                        "regime": "pruned",
                        "n_params": n_pr,
                        "qcnn_test_acc": hist_pr[-1]["test_acc"],
                        "cnn_test_acc": hist_c2[-1]["test_acc"],
                        "winner": (
                            "qcnn"
                            if hist_pr[-1]["test_acc"] > hist_c2[-1]["test_acc"] + 1e-12
                            else (
                                "cnn"
                                if hist_c2[-1]["test_acc"] > hist_pr[-1]["test_acc"] + 1e-12
                                else "tie"
                            )
                        ),
                    }
                )
                runs.append(
                    {
                        "run_id": run_id,
                        "hist_qcnn_full": hist_q,
                        "hist_cnn_full": hist_c,
                        "hist_qcnn_pruned": hist_pr,
                        "hist_cnn_pruned_match": hist_c2,
                    }
                )

    deltas = [r["delta_test_qcnn_minus_cnn_full"] for r in comparison_rows]
    mean_delta = float(np.mean(deltas))
    if mean_delta > 0.02:
        verdict = "qcnn_better_on_average"
    elif mean_delta < -0.02:
        verdict = "cnn_better_on_average"
    else:
        verdict = "tie_on_average"
    n_q_wins = sum(1 for d in deltas if d > 1e-12)
    n_c_wins = sum(1 for d in deltas if d < -1e-12)
    n_ties = len(deltas) - n_q_wins - n_c_wins

    summary = {
        "meta": {
            "track": "qcnn_protocol",
            "prior_arxiv": PRIOR_ARXIV,
            "prior_bib_path": "prior_bib.md",
            "prior_note": (
                "Cite Elhag et al. arXiv:2408.08701 for protocol frame only; "
                "no literature accuracy/coverage numbers copied into this file."
            ),
            "simulator": SIMULATOR_NAME,
            "optimizer": "SPSA",
            "n_qubits": N_QUBITS,
            "img_size": IMG_SIZE,
            "n_train": N_TRAIN,
            "n_test": N_TEST,
            "epochs": EPOCHS,
            "seeds": {
                "data": SEED_DATA,
                "init": SEED_INIT,
                "train": SEED_TRAIN,
                "split": SEED_SPLIT,
            },
            "encodings_finished": ENCODINGS,
            "losses_finished": LOSSES,
            "batch_sizes_finished": BATCH_SIZES,
            "encodings_not_run": [],
            "losses_not_run": [],
            "batch_sizes_not_run": [],
            "dataset_description": (
                "Locally generated 4x4 images: class0=horizontal-bar, "
                "class1=diagonal; Gaussian noise. NOT HEP/jet/top-quark."
            ),
            "disclaimer": (
                "本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，"
                "Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；"
                "verify/ 第三方 PDF 禁止入库。"
            ),
        },
        "qcnn_architecture": {
            "n_params_full": N_PARAMS_FULL,
            "layout": (
                "conv(0,1) RY/RZ; conv(2,3) RY/RZ; pool-RY on 0,2; "
                "conv(0,2) RY/RZ; final RY on 0; CNOT links"
            ),
        },
        "comparison_table": comparison_rows,
        "prune_table": prune_rows,
        "low_param_regime": low_param_rows,
        "aggregate": {
            "mean_delta_test_qcnn_minus_cnn_full": mean_delta,
            "n_runs": len(comparison_rows),
            "n_qcnn_wins_full": n_q_wins,
            "n_cnn_wins_full": n_c_wins,
            "n_ties_full": n_ties,
            "verdict": verdict,
        },
        "class_balance": {
            "train_pos": int(ytr.sum()),
            "train_neg": int(len(ytr) - ytr.sum()),
            "test_pos": int(yte.sum()),
            "test_neg": int(len(yte) - yte.sum()),
        },
    }

    (DATA_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (DATA_DIR / "histories.json").write_text(json.dumps(runs, indent=2), encoding="utf-8")
    np.savez_compressed(
        DATA_DIR / "examples.npz",
        X_train=Xtr[:8],
        y_train=ytr[:8],
        X_test=Xte[:8],
        y_test=yte[:8],
    )
    print("Wrote data/summary.json verdict=", verdict, "mean_delta=", mean_delta)


if __name__ == "__main__":
    main()
