"""Tests for the strict reader and the region-wise comparison.

Each test builds a synthetic export in a temporary directory.  The negative
cases matter as much as the positive ones: a reader that silently accepts a
malformed file is worse than one that crashes.

Run:  python tests\test_all.py
"""
import sys
import tempfile
from pathlib import Path

import numpy as np

try:                                   # the console may be GBK on Windows
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import compare_fields as cf          # noqa: E402
import read_fields as rf             # noqa: E402

NORM = "ewfd.normE (V/m)"
HDR_EXPR = ",".join(
    [f"{NORM} @ 1.8 1"] +
    [f"{k}(ewfd.E{c}) (V/m) @ 1.8 1" for c in "xyz" for k in ("real", "imag")])


def write_export(path, x, y, E, unit="µm", neff="1.8", drop=None,
                 nan_at=None):
    norm = np.sqrt(np.sum(np.abs(E) ** 2, axis=1))
    cols = [x, y, norm]
    for c in range(3):
        cols += [E[:, c].real, E[:, c].imag]
    data = np.column_stack(cols)
    if nan_at is not None:
        data[nan_at[0], nan_at[1]] = np.nan
    names = ["X", "Y"] + HDR_EXPR.split(",")
    if drop is not None:
        keep = [i for i in range(len(names)) if i != drop]
        names = [names[i] for i in keep]
        data = data[:, keep]
    lines = ["% Model,test.mph", "% Version,COMSOL 6.3.0.290",
             '% Date,"Oct 21 2026"', "% Dimension,2",
             f"% Nodes,{x.size}", "% Expressions,7",
             '% Description,"field"', f"% Length unit,{unit}",
             "% " + ",".join(names)]
    for row in data:
        lines.append(",".join(f"{v:.12e}" for v in row))
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def grid_field(scale=1.0, phase=0.0, slab_only_change=False):
    gx = np.linspace(-1.4, 4.0, 60)
    gy = np.linspace(-0.9, 1.5, 40)
    GX, GY = np.meshgrid(gx, gy)
    x, y = GX.ravel(), GY.ravel()
    core = np.exp(-((x - 1.29) ** 2 / 0.05 + (y - 0.22) ** 2 / 0.02))
    Ex = core * (1 + 0j)
    Ey = 0.2j * core
    Ez = 0.05 * core
    if slab_only_change:
        # add a field that lives in the slab regions only, so the ridge part is
        # unchanged but the slab overlap must drop
        outside = ~((x > 0.9675) & (x < 1.6125) & (y > 0) & (y < 0.5))
        slab_env = np.exp(-((x - 0.45) ** 2 / 0.06 + (y - 0.12) ** 2 / 0.004))
        Ex = Ex + 1.5 * slab_env * outside
    E = np.stack([Ex, Ey, Ez], axis=1) * scale * np.exp(1j * phase)
    return x, y, E


def main():
    results = []

    def check(name, cond, detail=""):
        results.append((name, bool(cond)))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name:46s} {detail}")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        x, y, E = grid_field()
        good = td / "good.csv"
        write_export(good, x, y, E)

        r = rf.read_export(good)
        check("reader accepts a well-formed file", r.nodes == x.size,
              f"nodes={r.nodes}")
        check("unit parsed from metadata", r.unit == "µm", r.unit)
        check("neff tag parsed", r.neff_tag == "1.8", r.neff_tag)

        def expect_error(fn, label):
            try:
                fn()
                check(label, False, "no error raised")
            except Exception as exc:
                check(label, True, type(exc).__name__)

        bad = td / "nan.csv"
        write_export(bad, x, y, E, nan_at=(3, 4))
        expect_error(lambda: rf.read_export(bad), "reader rejects NaN")

        bad = td / "unit.csv"
        write_export(bad, x, y, E, unit="furlong")
        expect_error(lambda: rf.read_export(bad), "reader rejects unknown unit")

        bad = td / "col.csv"
        write_export(bad, x, y, E, drop=5)
        expect_error(lambda: rf.read_export(bad), "reader rejects missing column")

        bad = td / "empty.csv"
        bad.write_text("% Model,x\n% Length unit,µm\n", encoding="utf-8")
        expect_error(lambda: rf.read_export(bad), "reader rejects empty file")

        rng = np.random.default_rng(3)
        A = rng.standard_normal(400) + 1j * rng.standard_normal(400)
        B = rng.standard_normal(400) + 1j * rng.standard_normal(400)
        check("similarity self = 1", abs(cf.similarity(A, A) - 1) < 1e-12)
        check("phase invariant",
              abs(cf.similarity(A * np.exp(0.7j), A) - 1) < 1e-12)
        check("amplitude invariant", abs(cf.similarity(2.5 * A, A) - 1) < 1e-12)
        proj = np.vdot(A, B) / np.vdot(A, A)
        check("orthogonal -> 0", cf.similarity(A, B - proj * A) < 1e-10)

        same = td / "same.csv"
        write_export(same, x, y, E)
        out = cf.summarise(cf.compare(good, same), verbose=False)
        check("compare(self) gives S=1 everywhere",
              abs(out["max_region_S"] - 1) < 1e-9,
              f"{out['max_region_S']:.6f}")

        ph = td / "phase.csv"
        write_export(ph, x, y, E * np.exp(1.3j))
        out2 = cf.summarise(cf.compare(good, ph), verbose=False)
        check("compare(global phase) unchanged",
              abs(out2["max_region_S"] - 1) < 1e-9)

        xs, ys, Es = grid_field(slab_only_change=True)
        slab = td / "slab.csv"
        write_export(slab, xs, ys, Es)
        s = cf.summarise(cf.compare(good, slab), verbose=False)
        check("ridge unaffected by a slab-only change",
              s["regions"]["ridge"] > 0.99, f"ridge={s['regions']['ridge']:.4f}")
        check("slab similarity drops for a slab-only change",
              s["regions"]["slabL"] < 0.9, f"slabL={s['regions']['slabL']:.4f}")

        order = np.argsort((x - 1.29) ** 2 + (y - 0.22) ** 2)[:5]
        xd = np.r_[x, x[order]]
        yd = np.r_[y, y[order]]
        Ed = np.r_[E, E[order] * 0.5]
        dup = td / "dup.csv"
        write_export(dup, xd, yd, Ed)
        rd = rf.read_export(dup)
        check("duplicates detected", rd.dup_extra >= 5, f"extra={rd.dup_extra}")
        check("duplicate spread reported", rd.dup_max_spread > 0,
              f"{rd.dup_max_spread:.3e}")
        expect_error(lambda: cf.compare(good, dup, dup_policy="reject"),
                     "policy 'reject' refuses duplicates")

    ok = all(r[1] for r in results)
    print(f"\n{sum(r[1] for r in results)}/{len(results)} checks passed")
    print("TESTS " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

