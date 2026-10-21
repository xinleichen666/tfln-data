"""Batch point evaluation at full precision, with hard validation.

Generates a Java source with the coordinates embedded (COMSOL batch blocks file
reads), evaluates one solution of a saved model, then validates shape,
finiteness, coordinates, domain ids and three independent magnitudes.

Usage:
  python run_eval.py <model.mph> <solnum> <metal 0|1> <tag>
"""
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

HERE = Path(__file__).parent
BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TPL = HERE / "eval_points.tpl"
ERR = ("错误", "Error", "ERROR", "无法编译", "运行 Java 类时出错")

MAPS = {
    False: {"air": 1, "slabL": 2, "ridge": 3, "slabR": 4},
    True: {"air": 1, "slabL": 2, "metalL": 3, "ridge": 4, "slabR": 5,
           "metalR": 6},
}


def points(metal):
    """Interior sample points per region, away from every interface."""
    out = []

    def grid(x0, x1, y0, y1, nx, ny, name):
        for x in np.linspace(x0, x1, nx):
            for y in np.linspace(y0, y1, ny):
                out.append((float(x), float(y), name))

    grid(1.00, 1.58, 0.03, 0.47, 6, 6, "ridge")
    grid(0.05, 0.93, 0.03, 0.22, 5, 5, "slabL")
    grid(1.66, 2.55, 0.03, 0.22, 5, 5, "slabR")
    grid(1.00, 1.58, 0.60, 1.40, 3, 3, "air")
    grid(-1.40, -0.20, 0.10, 0.40, 3, 2, "air")
    if metal:
        grid(0.36, 0.95, 0.27, 0.33, 4, 3, "metalL")
        grid(1.64, 2.24, 0.27, 0.33, 4, 3, "metalR")
    return out


def java_array(pts):
    xs = ", ".join(f"{p[0]:.12f}" for p in pts)
    ys = ", ".join(f"{p[1]:.12f}" for p in pts)
    return "new double[][]{\n        {" + xs + "},\n        {" + ys + "}}"


def main():
    if len(sys.argv) < 5:
        raise SystemExit("usage: run_eval.py <model.mph> <solnum> <metal> <tag>")
    model = Path(sys.argv[1]).resolve()
    solnum = int(sys.argv[2])
    metal = sys.argv[3] == "1"
    tag = sys.argv[4]
    if not model.exists():
        raise SystemExit(f"model not found: {model}")

    pts = points(metal)
    run = HERE / "runs" / f"{time.strftime('%Y%m%d-%H%M%S')}_{tag}"
    if run.exists():
        raise SystemExit(f"run directory exists: {run}")
    run.mkdir(parents=True)

    src = run / "gen_eval.java"
    text = (TPL.read_text(encoding="utf-8")
               .replace("__CLASS__", src.stem)
               .replace("__MODEL__", str(model).replace("\\", "/"))
               .replace("__SOLNUM__", str(solnum))
               .replace("__COORDS__", java_array(pts)))
    if "__" in text:
        raise SystemExit("unsubstituted placeholder")
    src.write_text(text, encoding="utf-8")

    r = subprocess.run([str(BIN / "comsolcompile.exe"), src.name],
                       cwd=run, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if any(k in out for k in ERR) or not (run / "gen_eval.class").exists():
        print("FAIL compile")
        print(out.strip()[:800])
        return 1
    print("compile: ok")

    log = run / "eval.log"
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        r = subprocess.run([str(BIN / "comsolbatch.exe"),
                            "-inputfile", "gen_eval.class"],
                           cwd=run, stdout=fh, stderr=subprocess.STDOUT)
    text = log.read_text(encoding="utf-8", errors="replace")
    if "DONE" not in text or "PT 0 " not in text:
        print("FAIL run (see log)")
        for line in text.splitlines()[-15:]:
            print("  " + line)
        return 1

    shape = re.search(r"SHAPE expr=(\d+) sol=(\d+) pts=(\d+)", text)
    if not shape:
        print("FAIL no SHAPE line")
        return 1
    nexpr, nsol, npts = map(int, shape.groups())
    rows = [[float(v) for v in m.group(2).split()]
            for m in re.finditer(r"^PT (\d+) (.*)$", text, re.M)]
    arr = np.array(rows)
    problems = []
    if (nexpr, nsol, npts) != (11, 1, len(pts)):
        problems.append(f"shape {nexpr}/{nsol}/{npts} != 11/1/{len(pts)}")
    if arr.shape != (len(pts), 11):
        problems.append(f"parsed {arr.shape} rows")
    if arr.size and not np.isfinite(arr).all():
        problems.append("non-finite values")

    if not problems:
        req = np.array([[p[0], p[1]] for p in pts])
        derr = float(np.max(np.abs(arr[:, :2] - req)))
        if derr > 1e-9:
            problems.append(f"coordinates differ by {derr:.2e} um")
        expect = np.array([MAPS[metal][p[2]] for p in pts])
        bad = np.where(arr[:, 2].astype(int) != expect)[0]
        if bad.size:
            problems.append(f"dom mismatch at {bad.size} points, first "
                            f"index {int(bad[0])}")
        Ex = arr[:, 4] + 1j * arr[:, 5]
        Ey = arr[:, 6] + 1j * arr[:, 7]
        Ez = arr[:, 8] + 1j * arr[:, 9]
        reb = np.sqrt(np.abs(Ex) ** 2 + np.abs(Ey) ** 2 + np.abs(Ez) ** 2)
        normE, cosol = arr[:, 3], arr[:, 10]
        d1 = np.abs(reb - normE) / np.maximum(normE, 1e-30)
        d2 = np.abs(cosol - normE) / np.maximum(normE, 1e-30)
        if d1.max() > 1e-10:
            problems.append(f"python rebuild vs normE max rel {d1.max():.2e}")
        if d2.max() > 1e-10:
            problems.append(f"COMSOL magnitude vs normE max rel {d2.max():.2e}")

    np.savetxt(run / "points.csv", arr, delimiter=",",
               header="x,y,dom,normE,Exre,Exim,Eyre,Eyim,Ezre,Ezim,Emag_co",
               comments="")
    neff = re.search(r"MODENEFF sol=\d+ re=(\S+) im=(\S+)", text)
    print(f"  points {arr.shape[0]}  neff_re "
          f"{neff.group(1) if neff else '?'}")
    if not problems:
        print(f"  |rebuild-normE| rel max {d1.max():.2e}; "
              f"COMSOL magnitude rel max {d2.max():.2e}")
    for p in problems:
        print("  PROBLEM: " + p)
    print(f"\nRESULT {'PASS' if not problems else 'FAIL'}   run={run}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())

