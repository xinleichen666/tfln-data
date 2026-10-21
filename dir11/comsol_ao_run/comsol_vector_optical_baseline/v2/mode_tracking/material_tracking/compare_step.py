"""Compare one continuation step's candidate field with the previous step.

Both are evaluated on the SAME base12 cells, so the comparison is like for
like.  The reference field comes from the accepted eqairFix run.

Usage:
  python compare_step.py --model out/track_t1e-4.mph --solnum 40 --tag t1e-4
"""
import argparse
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
CS = HERE.parent / "common_sampling"
sys.path.insert(0, str(CS))

import cellspec as C                      # noqa: E402
import compare_weighted as CW             # noqa: E402
import evalpoints as EP                   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--solnum", required=True, type=int)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()

    cells = C.base_cells(12)
    sp = C.arrays(cells)
    hits = sorted((CS / "runs").glob("*_eqfix5040"))
    if len(hits) != 1:
        raise SystemExit(f"expected one eqfix5040 run, got {hits}")
    ref = np.loadtxt(hits[0] / "points.csv", delimiter=",", skiprows=1)
    if ref.shape[0] != len(cells):
        raise SystemExit("reference grid size mismatch")
    if np.max(np.abs(ref[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
        raise SystemExit("reference coordinates differ")
    Eref = np.stack([ref[:, 4] + 1j * ref[:, 5], ref[:, 6] + 1j * ref[:, 7],
                     ref[:, 8] + 1j * ref[:, 9]], axis=1)

    arr, neff, run = EP.eval_points(Path(a.model), a.solnum,
                                    sp["x"], sp["y"], f"cmp_{a.tag}")
    E = np.stack([arr[:, 4] + 1j * arr[:, 5], arr[:, 6] + 1j * arr[:, 7],
                  arr[:, 8] + 1j * arr[:, 9]], axis=1)
    w = sp["w"]
    S = CW.similarity(Eref, E, w)
    I = np.sum(w * np.sum(np.conj(Eref) * E, axis=1))
    n0 = np.sum(w * np.sum(np.abs(Eref) ** 2, axis=1))
    n1 = np.sum(w * np.sum(np.abs(E) ** 2, axis=1))
    z = I / np.sqrt(n0 * n1)

    def shares(EE):
        tot = np.sum(w * np.sum(np.abs(EE) ** 2, axis=1))
        return [float(np.sum(w * np.abs(EE[:, c]) ** 2) / tot) for c in range(3)]

    pr, pn = shares(Eref), shares(E)
    print(f"{a.tag}: solnum {a.solnum}  neff {neff[0]:.12f} {neff[1]:+.3e}i")
    print(f"  S = {S:.6f}   overlap {z.real:.6f}{z.imag:+.6f}i")
    print(f"  polarisation ref  Ex {pr[0]:.3f} Ey {pr[1]:.3f} Ez {pr[2]:.3f}")
    print(f"  polarisation step Ex {pn[0]:.3f} Ey {pn[1]:.3f} Ez {pn[2]:.3f}")
    print(f"  region shares (ref -> step):")
    for nm in ("ridge", "slabL", "slabR", "metalL", "metalR", "air"):
        m = sp["region"] == nm
        if not m.any():
            continue
        a0 = np.sum((w * np.sum(np.abs(Eref) ** 2, axis=1))[m])
        a1 = np.sum((w * np.sum(np.abs(E) ** 2, axis=1))[m])
        print(f"    {nm:7s} {a0/n0:.4f} -> {a1/n1:.4f} "
              f"({a1/n1 - a0/n0:+.5f})")
    print(f"\nRESULT {'PASS' if S >= 0.99 else 'FAIL'} (criterion S >= 0.99)")
    return 0 if S >= 0.99 else 1


if __name__ == "__main__":
    sys.exit(main())
