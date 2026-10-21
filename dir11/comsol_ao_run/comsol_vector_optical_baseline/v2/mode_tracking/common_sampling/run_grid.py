"""Evaluate a named grid on all three saved models and compare it.

Grids come from cellspec (uniform bands, or an explicit cell list file), so the
same coordinates and the same area weights are used for every model.

Usage:
  python run_grid.py --spec film24 --budget 20000
  python run_grid.py --cells runs/cells_adapt3.csv --tag reuse
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
DOM = {False: {"air": 1, "slabL": 2, "ridge": 3, "slabR": 4,
               "metalL": 1, "metalR": 1},
       True: {"air": 1, "slabL": 2, "metalL": 3, "ridge": 4,
              "slabR": 5, "metalR": 6}}


def load_ref():
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
    return ref


def build(spec):
    if spec == "base12":
        return C.base_cells(12)
    if spec == "base24":
        return C.base_cells(24)
    if spec == "film24":
        return C.uniform_bands(12, 24)
    raise SystemExit(f"unknown spec {spec}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=None)
    ap.add_argument("--cells", default=None)
    ap.add_argument("--budget", type=int, default=20000)
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()

    if a.cells:
        cells = [tuple(float(v) for v in ln.split(","))
                 for ln in Path(a.cells).read_text(encoding="utf-8").splitlines()[1:]
                 if ln.strip()]
        tag = a.tag or Path(a.cells).stem
    else:
        cells = build(a.spec)
        tag = a.tag or a.spec

    chk = C.check(cells)
    print(f"grid {tag}: {len(cells)} cells, area {chk['area']:.9f}, "
          f"min side {chk['info']['min_side']*1000:.1f} nm")
    print(f"  counts {chk['counts']}")
    if chk["problems"]:
        raise SystemExit("grid failed checks: " + "; ".join(chk["problems"]))
    if len(cells) > a.budget:
        raise SystemExit(f"{len(cells)} cells exceeds the budget {a.budget}")

    ref = load_ref()
    res = {}
    for name, fname, metal, _i in MODELS:
        sp = C.arrays(cells)
        arr, neff, run = EP.eval_points(OUT / fname, SOLNUM, sp["x"], sp["y"],
                                        f"grid_{tag}_{name}")
        exp = np.array([DOM[metal == "1"][r] for r in sp["region"]])
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
        print(f"  {name:6s} total ratio {ts/tr:.5f} ({100*(ts/tr-1):+.2f} %)  "
              f"{'PASS' if not bad else 'FAIL'}")
        for b in bad:
            print("     " + b)
        ok = ok and not bad

    print("\nfield similarity")
    out = {}
    for p0, p1 in (("nom", "met"), ("nom", "eqfix")):
        S = CW.similarity(res[p0]["E"], res[p1]["E"], res[p0]["w"])
        out[f"S_{p0}_{p1}"] = S
        print(f"  {p0} vs {p1}: S = {S:.6f}")

    # complex overlap: its real and imaginary parts must also be stable
    for p0, p1 in (("nom", "met"),):
        I = np.sum(res[p0]["w"] * np.sum(np.conj(res[p0]["E"]) * res[p1]["E"],
                                         axis=1))
        n0 = np.sum(res[p0]["w"] * np.sum(np.abs(res[p0]["E"]) ** 2, axis=1))
        n1 = np.sum(res[p1]["w"] * np.sum(np.abs(res[p1]["E"]) ** 2, axis=1))
        z = I / np.sqrt(n0 * n1)
        out["z_re"], out["z_im"] = float(z.real), float(z.imag)
        print(f"  normalized complex overlap {z.real:.6f} {z.imag:+.6f}i")

    (HERE / "runs" / f"grid_{tag}.json").write_text(
        json.dumps(dict(cells=len(cells), area=chk["area"], **out), indent=2),
        encoding="utf-8")
    print(f"\nRESULT {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
