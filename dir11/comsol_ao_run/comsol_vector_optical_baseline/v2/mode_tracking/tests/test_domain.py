"""Regression tests for the geometric guards in the domain comparison.

The bug these guard against: an air point cloud triangulates across the holes
left by the solids, so "air" was returned inside the ridge.  The test below
builds a dataset with NO ridge samples and requires the comparison to report
the ridge as unavailable rather than silently filling it from air.

Run:  python tests\test_domain.py
"""
import sys
import tempfile
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import compare_by_domain as C      # noqa: E402
import regions as R                # noqa: E402

HDR = ("% Model,test.mph\n% Version,COMSOL 6.3.0.290\n% Date,\"x\"\n"
       "% Dimension,2\n% Nodes,{n}\n% Expressions,8\n% Description,\"f\"\n"
       "% Length unit,µm\n% X,Y,dom @ 1.8 1,ewfd.normE (V/m) @ 1.8 1,"
       "real(ewfd.Ex) (V/m) @ 1.8 1,imag(ewfd.Ex) (V/m) @ 1.8 1,"
       "real(ewfd.Ey) (V/m) @ 1.8 1,imag(ewfd.Ey) (V/m) @ 1.8 1,"
       "real(ewfd.Ez) (V/m) @ 1.8 1,imag(ewfd.Ez) (V/m) @ 1.8 1\n")


def write_dom(path, x, y, dom, E):
    norm = np.sqrt(np.sum(np.abs(E) ** 2, axis=1))
    cols = [x, y, dom.astype(float), norm]
    for c in range(3):
        cols += [E[:, c].real, E[:, c].imag]
    data = np.column_stack(cols)
    lines = [HDR.replace("{n}", str(x.size))]
    lines += [",".join(f"{v:.12e}" for v in row) for row in data]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def field_at(x, y):
    core = np.exp(-((x - 1.29) ** 2 / 0.05 + (y - 0.22) ** 2 / 0.02))
    return np.stack([core + 0j, 0.2j * core, 0.05 * core], axis=1)


def sample_grid(step=0.03):
    gx = np.arange(-1.5, 4.1, step)
    gy = np.arange(-0.9, 1.5, step)
    GX, GY = np.meshgrid(gx, gy)
    return GX.ravel(), GY.ravel()


def main():
    res = []

    def check(name, cond, detail=""):
        res.append(bool(cond))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name:52s} {detail}")

    # ---- classifier
    x = np.array([1.29, 0.6, 0.6, 1.29, -1.0, 5.0])
    y = np.array([0.25, 0.12, 0.30, 0.60, 0.00, 0.00])
    geo = R.classify(x, y, metal=True)
    check("ridge classified as ridge", geo[0] == "ridge", geo[0])
    check("slab classified as slabL", geo[1] == "slabL", geo[1])
    check("electrode classified as metalL", geo[2] == "metalL", geo[2])
    check("space above film classified as air", geo[3] == "air", geo[3])
    check("outside the window rejected", geo[5] == "outside", geo[5])

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        x, y = sample_grid()
        geo = R.classify(x, y, metal=False)
        E = field_at(x, y)

        # full dataset: every region present
        dom = np.where(geo == "ridge", 3,
                       np.where(geo == "air", 1,
                                np.where(geo == "slabL", 2, 4)))
        full = td / "full.csv"
        write_dom(full, x, y, dom, E)

        r = C.compare(full, full, C.MAP_NOMETAL, C.MAP_NOMETAL, False)
        v = r["per_grid"][C.GRIDS[-1]]
        check("self comparison gives S=1 everywhere",
              all(d["S"] is not None and abs(d["S"] - 1) < 1e-9
                  for d in v["per"].values()),
              ", ".join(f"{k}={d['S']:.4f}" for k, d in v["per"].items()))

        # dataset WITHOUT ridge samples: the ridge must not be filled from air
        keep = geo != "ridge"
        no_ridge = td / "no_ridge.csv"
        write_dom(no_ridge, x[keep], y[keep], dom[keep], E[keep])
        r2 = C.compare(no_ridge, no_ridge, C.MAP_NOMETAL, C.MAP_NOMETAL, False)
        v2 = r2["per_grid"][C.GRIDS[-1]]
        check("ridge not filled when it has no samples",
              "ridge" in r2["skipped"] and "ridge" not in v2["per"],
              f"skipped={r2['skipped']}")
        check("other regions still evaluated",
              v2["per"]["air"]["S"] is not None,
              f"air={v2['per']['air']['S']:.4f}")

        # label/geometry conflict: a sample placed on the film's bottom face
        # but labelled as the air domain must be reported as a mismatch
        xi = np.array([0.50, 0.60, 1.20, 1.30, 2.00])
        yi = np.zeros_like(xi)
        Ei = field_at(xi, yi)
        xc = np.r_[x, xi]
        yc = np.r_[y, yi]
        domc = np.r_[dom, np.ones(xi.size, dtype=int)]      # labelled air
        Ec = np.r_[E, Ei]
        conf = td / "conflict.csv"
        write_dom(conf, xc, yc, domc, Ec)
        rec = C.read_dom_csv(conf)
        chk = C.label_geometry_check(rec, C.MAP_NOMETAL, False)
        check("interface sample with the wrong domain label is flagged",
              chk["mismatch"] >= xi.size, f"mismatch={chk['mismatch']}")

    ok = all(res)
    print(f"\n{sum(res)}/{len(res)} checks passed")
    print("TESTS " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
