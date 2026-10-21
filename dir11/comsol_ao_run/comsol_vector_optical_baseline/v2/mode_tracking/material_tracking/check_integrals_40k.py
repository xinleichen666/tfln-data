"""Integral acceptance for one continuation step on the accepted 40k grid.

Reads the domain-integral reference produced by
common_sampling/run_domain_integrals.py for the new model, and the field
already evaluated on the accepted cell list.  Nothing is re-evaluated and
nothing is solved.

Usage:
  python check_integrals_40k.py --tag t1e-4 --solnum 40
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
import compare_integrals as CI            # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--cells", default="cells_rec3low.csv")
    ap.add_argument("--points", default=None)
    a = ap.parse_args()

    cells = [tuple(float(v) for v in ln.split(","))
             for ln in (CS / "runs" / a.cells)
             .read_text(encoding="utf-8").splitlines()[1:] if ln.strip()]
    chk = C.check(cells)
    sp = C.arrays(cells)
    print(f"{a.tag}: {len(cells)} cells, area {chk['area']:.9f}, "
          f"min side {chk['info']['min_side']*1000:.2f} nm")
    if chk["problems"]:
        raise SystemExit("cell list failed: " + "; ".join(chk["problems"]))

    pts = a.points or None
    if pts is None:
        hits = sorted((CS / "runs").glob(f"*_k40_{a.tag}"))
        if len(hits) != 1:
            raise SystemExit(f"expected one k40_{a.tag} run, got {hits}")
        pts = hits[0] / "points.csv"
    arr = np.loadtxt(pts, delimiter=",", skiprows=1)
    if arr.shape[0] != len(cells):
        raise SystemExit(f"{arr.shape[0]} points vs {len(cells)} cells")
    if not np.isfinite(arr).all():
        raise SystemExit("non-finite field values")
    if np.max(np.abs(arr[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
        raise SystemExit("coordinates do not match the cell list")

    ref_path = CS / "runs" / f"integrals_{a.tag}" / "integrals.csv"
    ref = {}
    with ref_path.open(encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.strip().split(",")
            ref[CI.MAP[p[0]]] = [float(v) for v in p[1:]]

    E = np.stack([arr[:, 4] + 1j * arr[:, 5], arr[:, 6] + 1j * arr[:, 7],
                  arr[:, 8] + 1j * arr[:, 9]], axis=1)
    rows, tr, ts, bad, contrib = CI.run_compare(ref, E, sp["w"],
                                                sp["region"])
    print(f"{'region':8s} {'ref E2':>12s} {'samp E2':>12s} {'ratio':>8s} "
          f"{'d_share':>9s}")
    for name, samp, r in rows:
        if r is None:
            print(f"{name:8s} {'no reference':>12s}")
            continue
        ratio = samp["normE2"] / r["normE2"]
        sr, ss = r["normE2"] / tr, samp["normE2"] / ts
        print(f"{name:8s} {r['normE2']:12.5e} {samp['normE2']:12.5e} "
              f"{ratio:8.4f} {ss - sr:+9.5f}")
    print(f"\n  total  ref {tr:.6e}  samp {ts:.6e}  ratio {ts/tr:.5f} "
          f"({100*(ts/tr-1):+.2f} %)")
    for b in bad:
        print("  PROBLEM: " + b)
    print(f"\nRESULT {'PASS' if not bad else 'FAIL'} "
          f"(total <=1 %, shares <=0.005)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
