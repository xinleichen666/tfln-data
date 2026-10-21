"""Sampling-stability check on the accepted 40k grid.

Evaluates ONE mode of a model on the accepted cell list and compares it with
the stored reference field there.  The 40-mode scan is done on the coarse grid;
here only the candidate that survived the scan is re-checked, so the Java
source stays small (embedding 40k points for 9 arrays exceeds the constant
pool).

Usage:
  python check_40k.py --model out/track_t1e-4.mph --solnum 40 --tag t1e-4
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
    ap.add_argument("--ref-points", default=None,
                    help="compare against another 12-column points.csv instead "
                         "of the stored eqfix reference")
    a = ap.parse_args()

    cells = [tuple(float(v) for v in ln.split(","))
             for ln in (CS / "runs" / "cells_rec3low.csv")
             .read_text(encoding="utf-8").splitlines()[1:] if ln.strip()]
    sp = C.arrays(cells)
    chk = C.check(cells)
    if chk["problems"]:
        raise SystemExit("cell list failed: " + "; ".join(chk["problems"]))
    if a.ref_points:
        ref = np.loadtxt(a.ref_points, delimiter=",", skiprows=1)
        if ref.shape[0] != len(cells):
            raise SystemExit("reference rows do not match the cell list")
        if np.max(np.abs(ref[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
            raise SystemExit("reference coordinates differ from the cell list")
        Eref = np.stack([ref[:, 4] + 1j * ref[:, 5], ref[:, 6] + 1j * ref[:, 7],
                         ref[:, 8] + 1j * ref[:, 9]], axis=1)
    else:
        ref = np.loadtxt(CS / "runs" / "rec_rec3low" / "eqfix.csv",
                         delimiter=",", skiprows=1)
        if ref.shape[0] != len(cells):
            raise SystemExit("reference rows do not match the cell list")
        if np.max(np.abs(ref[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
            raise SystemExit("reference coordinates differ")
        Eref = np.stack([ref[:, 2] + 1j * ref[:, 3], ref[:, 4] + 1j * ref[:, 5],
                         ref[:, 6] + 1j * ref[:, 7]], axis=1)

    arr, neff, run = EP.eval_points(Path(a.model), a.solnum,
                                    sp["x"], sp["y"], f"k40_{a.tag}")
    E = np.stack([arr[:, 4] + 1j * arr[:, 5], arr[:, 6] + 1j * arr[:, 7],
                  arr[:, 8] + 1j * arr[:, 9]], axis=1)
    w = sp["w"]
    S = CW.similarity(Eref, E, w)
    I = np.sum(w * np.sum(np.conj(Eref) * E, axis=1))
    n0 = np.sum(w * np.sum(np.abs(Eref) ** 2, axis=1))
    n1 = np.sum(w * np.sum(np.abs(E) ** 2, axis=1))
    z = I / np.sqrt(n0 * n1)
    print(f"{a.tag} @ {len(cells)} cells, solnum {a.solnum}")
    print(f"  neff {neff[0]:.12f} {neff[1]:+.4e}i")
    print(f"  S = {S:.9f}   z = {z.real:.9f}{z.imag:+.9f}i")
    print(f"  |z| = {abs(z):.9f}")
    print(f"\nRESULT {'PASS' if S >= 0.99 else 'FAIL'}")
    return 0 if S >= 0.99 else 1


if __name__ == "__main__":
    sys.exit(main())
