"""Adaptive refinement driven by already computed densities.

No new indicator function is invented: the local error of a cell is estimated
from how much its integral changed between the n=6 and n=12 grids, which nest
exactly (each n=6 cell is the union of four n=12 cells).  Those two levels are
already on disk, so locating the error costs nothing; only the refined grid is
newly evaluated.

The flagged set is the union over all three models, so every model is compared
on the same cells.

Usage:
  python adapt.py [--budget 20000] [--round 1]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cellspec as C                      # noqa: E402
import compare_integrals as CI            # noqa: E402
import compare_weighted as CW             # noqa: E402
import evalpoints as EP                   # noqa: E402

MODELS = [("nom", "final_nomA6.mph", "0", "nomA6"),
          ("met", "final_metA6.mph", "1", "metA6"),
          ("eqfix", "final_eqairFix.mph", "1", "eqairFix")]
SOLNUM = 40
OUT = HERE.parents[1] / "out"


def find_run(suffix):
    hits = sorted((HERE / "runs").glob(f"*_{suffix}"))
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one run for {suffix}, got {hits}")
    return hits[0]


def load(suffix, n):
    a = np.loadtxt(find_run(suffix) / "points.csv", delimiter=",", skiprows=1)
    sp = C.arrays(C.base_cells(n))
    if a.shape[0] != sp["x"].size:
        raise SystemExit(f"{suffix}: {a.shape[0]} rows vs {sp['x'].size} cells")
    if np.max(np.abs(a[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
        raise SystemExit(f"{suffix}: coordinates differ from cellspec")
    E = np.stack([a[:, 4] + 1j * a[:, 5], a[:, 6] + 1j * a[:, 7],
                  a[:, 8] + 1j * a[:, 9]], axis=1)
    return dict(E=E, w=sp["w"], region=sp["region"], cells=sp["cells"])




def local_error(coarse, fine, ref_tot):
    """Estimated integral error of each coarse cell, from the level change."""
    kids = C.nest(6, 12, len(C.X_EDGES) - 1, len(C.Y_EDGES) - 1)
    v_c = np.sum(np.abs(coarse["E"]) ** 2, axis=1)
    v_f = np.sum(np.abs(fine["E"]) ** 2, axis=1)
    I_c = v_c * coarse["w"]
    I_f = np.sum((v_f * fine["w"])[kids], axis=1)
    return np.abs(I_f - I_c) / ref_tot, I_c, I_f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=20000)
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--share", type=float, default=5e-4)
    a = ap.parse_args()

    ref = {}
    for name, _f, _m, itag in MODELS:
        p = HERE / "runs" / f"integrals_{itag}" / "integrals.csv"
        if not p.exists():
            raise SystemExit(f"missing reference {p}")
        with p.open(encoding="utf-8") as fh:
            next(fh)
            for line in fh:
                q = line.strip().split(",")
                ref.setdefault(name, {})[CI.MAP[q[0]]] = [float(v) for v in q[1:]]
    tot_ref = {k: sum(v[0] for v in d.values()) for k, d in ref.items()}

    coarse = {m[0]: load(f"{m[0]}1260", 6) for m in MODELS}
    fine = {m[0]: load(f"{m[0]}5040", 12) for m in MODELS}
    print("loaded nested grids: n=6 and n=12")

    err = {}
    for name, _f, _m, _i in MODELS:
        e, I_c, I_f = local_error(coarse[name], fine[name], tot_ref[name])
        err[name] = e
        print(f"  {name}: sum |dI| / total = {e.sum():.4f}, "
              f"max cell {e.max():.3e}")

    combined = np.max(np.stack([err[m[0]] for m in MODELS]), axis=0)
    order = np.argsort(-combined)
    cells12 = fine["nom"]["cells"]
    kids = C.nest(6, 12, len(C.X_EDGES) - 1, len(C.Y_EDGES) - 1)

    flag12 = np.zeros(len(cells12), dtype=bool)
    for k in order:
        if combined[k] < a.share:
            break
        if flag12[kids[k]].any():
            continue
        growth = sum(len(C.split4(cells12[j])) - 1 for j in kids[k])
        if len(cells12) + flag12.sum() + growth > a.budget:
            continue
        flag12[kids[k]] = True

    print(f"  flagged n=12 cells {int(flag12.sum())} "
          f"({100*flag12.mean():.1f} % of n=12 cells)")

    refined = C.refine(cells12, flag12)
    chk = C.check(refined)
    print(f"  refined grid: {len(refined)} cells, area {chk['area']:.9f}, "
          f"min side {chk['info']['min_side']*1000:.1f} nm")
    if chk["problems"]:
        raise SystemExit("refined grid failed: " + "; ".join(chk["problems"]))
    print(f"  region counts {chk['counts']}")

    tag = f"adapt{a.round}"
    np.savetxt(HERE / "runs" / f"cells_{tag}.csv", np.array(refined),
               delimiter=",", header="x0,x1,y0,y1", comments="", fmt="%.9f")

    want = {False: {"air": 1, "slabL": 2, "ridge": 3, "slabR": 4,
                    "metalL": 1, "metalR": 1},
            True: {"air": 1, "slabL": 2, "metalL": 3, "ridge": 4,
                   "slabR": 5, "metalR": 6}}
    res = {}
    for name, fname, metal, _i in MODELS:
        sp = C.arrays(refined)
        arr, neff, run = EP.eval_points(OUT / fname, SOLNUM, sp["x"], sp["y"],
                                        f"{tag}_{name}")
        exp = np.array([want[metal == "1"][r] for r in sp["region"]])
        bad = np.where(arr[:, 2].astype(int) != exp)[0]
        if bad.size:
            raise SystemExit(f"{name}: {bad.size} domain mismatches")
        E = np.stack([arr[:, 4] + 1j * arr[:, 5], arr[:, 6] + 1j * arr[:, 7],
                      arr[:, 8] + 1j * arr[:, 9]], axis=1)
        res[name] = dict(E=E, w=sp["w"], region=sp["region"], neff=neff)
        print(f"  {name}: {arr.shape[0]} points, neff {neff[0]:.12f}")

    print("\nagainst the domain-integral reference")
    ok = True
    for name, _f, _m, _i in MODELS:
        rows, tr, ts, bad, contrib = CI.run_compare(
            ref[name], res[name]["E"], res[name]["w"], res[name]["region"])
        ratio = ts / tr
        print(f"  {name:6s} total ratio {ratio:.5f} ({100*(ratio-1):+.2f} %)  "
              f"{'PASS' if not bad else 'FAIL'}")
        for b in bad:
            print("     " + b)
        ok = ok and not bad

    print("\nfield similarity (conjugated, area weighted)")
    for p0, p1 in (("nom", "met"), ("nom", "eqfix")):
        S = CW.similarity(res[p0]["E"], res[p1]["E"], res[p0]["w"])
        print(f"  {p0} vs {p1}: S = {S:.6f}")

    (HERE / "runs" / f"adapt_{tag}.json").write_text(json.dumps(
        dict(cells=len(refined), flagged=int(flag12.sum()),
             area=chk["area"], budget=a.budget), indent=2), encoding="utf-8")
    print(f"\nRESULT {'PASS' if ok else 'FAIL'}  (criterion: total 1 %, "
          f"shares 0.005)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

