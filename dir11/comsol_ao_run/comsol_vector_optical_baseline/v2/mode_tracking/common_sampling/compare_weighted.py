"""Weighted, full-window comparison of two modes sampled on the same cells.

Both files must come from run_sampling.py with the SAME n, so that cell i has
the same coordinates and the same area weight in both.  The comparison

    S = | sum_i w_i E_a* . E_b | / sqrt( sum_i w_i|E_a|^2 * sum_i w_i|E_b|^2 )

includes every cell of the window, electrodes included (they are air in one
model and metal in the other -- that difference is part of what is compared).
Per-region contributions are reported as well, together with the polarisation
split, so a single number cannot hide a regional disagreement.

Usage:
  python compare_weighted.py <A.csv> <B.csv>
"""
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sampling as S                 # noqa: E402

REGIONS = ("ridge", "slabL", "slabR", "metalL", "metalR", "air")


def load(path, n):
    a = np.loadtxt(path, delimiter=",", skiprows=1)
    if a.shape[1] != 12:
        raise SystemExit(f"{Path(path).name}: expected 12 columns, got "
                         f"{a.shape[1]}")
    s = S.cells(n)
    if a.shape[0] != s["x"].size:
        raise SystemExit(f"{Path(path).name}: {a.shape[0]} rows, sampling has "
                         f"{s['x'].size} - n mismatch")
    if np.max(np.abs(a[:, :2] - np.c_[s["x"], s["y"]])) > 1e-9:
        raise SystemExit(f"{Path(path).name}: coordinates differ from sampling")
    if np.max(np.abs(a[:, 11] - s["w"])) > 1e-15:
        raise SystemExit(f"{Path(path).name}: weights differ from sampling")
    E = np.stack([a[:, 4] + 1j * a[:, 5], a[:, 6] + 1j * a[:, 7],
                  a[:, 8] + 1j * a[:, 9]], axis=1)
    return dict(E=E, w=a[:, 11], region=s["region"], dom=a[:, 2].astype(int),
                neff=None, path=Path(path))


def similarity(Ea, Eb, w):
    """Area-weighted conjugated overlap, summed over cells.

    Ea, Eb: (N, 3) complex fields; w: (N,) positive area weights.
    Returns S in [0, 1].  Computed from the summed complex inner product and
    the summed norms, never from a per-region maximum.
    """
    Ea = np.asarray(Ea, dtype=complex)
    Eb = np.asarray(Eb, dtype=complex)
    w = np.asarray(w, dtype=float)
    if Ea.shape != Eb.shape or Ea.shape[0] != w.shape[0]:
        raise ValueError("shape mismatch between fields and weights")
    if not (np.isfinite(Ea).all() and np.isfinite(Eb).all()):
        raise ValueError("non-finite field values")
    if not (np.isfinite(w).all() and (w > 0).all()):
        raise ValueError("weights must be finite and positive")
    I = np.sum(w * np.sum(Ea * np.conj(Eb), axis=1))
    n1 = float(np.sum(w * np.sum(np.abs(Ea) ** 2, axis=1)))
    n2 = float(np.sum(w * np.sum(np.abs(Eb) ** 2, axis=1)))
    if n1 <= 0 or n2 <= 0:
        return 0.0
    S = float(abs(I) / np.sqrt(n1 * n2))
    if S > 1 + 1e-9:
        raise ValueError(f"similarity {S} exceeds 1")
    return min(S, 1.0)


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: compare_weighted.py <A.csv> <B.csv>")
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    a = load(sys.argv[1], n)
    b = load(sys.argv[2], n)

    Itot, N1, N2 = 0j, 0.0, 0.0
    per = {}
    for name in REGIONS:
        m = a["region"] == name
        if not m.any():
            per[name] = None
            continue
        ea, eb, w = a["E"][m], b["E"][m], a["w"][m]
        I = np.sum(w * np.sum(ea * np.conj(eb), axis=1))
        n1 = float(np.sum(w * np.sum(np.abs(ea) ** 2, axis=1)))
        n2 = float(np.sum(w * np.sum(np.abs(eb) ** 2, axis=1)))
        s = similarity(ea, eb, w) if (n1 > 0 and n2 > 0) else None
        if s is not None and s > 1 + 1e-9:
            raise RuntimeError(f"{name}: S={s:.12f} exceeds 1")
        per[name] = dict(S=s, n=int(m.sum()), area=float(w.sum()),
                         share_a=float(n1), share_b=float(n2))
        Itot += I
        N1 += n1
        N2 += n2

    S_glob = similarity(a["E"], b["E"], a["w"]) if (N1 > 0 and N2 > 0) else 0.0
    if S_glob > 1 + 1e-9:
        raise RuntimeError(f"global S={S_glob:.12f} exceeds 1")

    print(f"A {a['path'].name}")
    print(f"B {b['path'].name}")
    print(f"\n{'region':8s} {'S':>7s} {'cells':>6s} {'area':>8s} "
          f"{'E2_A':>11s} {'E2_B':>11s}")
    for name, d in per.items():
        if d is None:
            print(f"{name:8s} {'n/a':>7s}")
            continue
        s = "n/a" if d["S"] is None else f"{d['S']:.4f}"
        print(f"{name:8s} {s:>7s} {d['n']:6d} {d['area']:8.3f} "
              f"{d['share_a']:11.3e} {d['share_b']:11.3e}")
    print(f"\n  weighted global S = {S_glob:.4f}")
    print(f"  total weight = {a['w'].sum():.6f} um2 "
          f"(window 15.028000)")

    for tag, r in (("A", a), ("B", b)):
        tot = float(np.sum(r["w"] * np.sum(np.abs(r["E"]) ** 2, axis=1)))
        parts = [float(np.sum(r["w"] * np.abs(r["E"][:, c]) ** 2)) / tot
                 for c in range(3)]
        print(f"  polarisation {tag}: Ex {parts[0]:.3f} Ey {parts[1]:.3f} "
              f"Ez {parts[2]:.3f}")

    print("\nnote: this is a field-shape similarity over one mode pair; it is "
          "not a branch claim.")


if __name__ == "__main__":
    sys.exit(main())
