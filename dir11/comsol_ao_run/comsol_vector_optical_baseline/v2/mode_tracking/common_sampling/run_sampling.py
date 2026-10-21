"""Evaluate the common sampling on a saved model, with domain validation.

The same cell centres are used for every model.  A cell whose geometry is an
electrode must return the electrode domain in the metal model and the air
domain in the no-metal model -- that is checked, not assumed.

Usage:
  python run_sampling.py <model.mph> <solnum> <metal 0|1> <tag> [n]
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

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sampling as S                 # noqa: E402

HERE = Path(__file__).resolve().parent
BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TPL = HERE / "eval_points.tpl"
TPL_CHUNK = HERE / "eval_points_chunk.tpl"
ERR = ("错误", "Error", "ERROR", "无法编译", "运行 Java 类时出错")
NEXPR = 11

EXPECT = {
    False: {"air": 1, "slabL": 2, "ridge": 3, "slabR": 4,
            "metalL": 1, "metalR": 1},
    True: {"air": 1, "slabL": 2, "metalL": 3, "ridge": 4, "slabR": 5,
           "metalR": 6},
}


def java_array(x, y):
    xs = ", ".join(f"{v:.12f}" for v in x)
    ys = ", ".join(f"{v:.12f}" for v in y)
    return "new double[][]{\n        {" + xs + "},\n        {" + ys + "}}"


def chunked(vals, prefix, per=400):
    """Emit several small static methods; one huge initialiser would exceed
    the per-method bytecode limit."""
    meths, names = [], []
    for i in range(0, len(vals), per):
        seg = vals[i:i + per]
        name = f"{prefix}{i // per}"
        names.append(name + "()")
        body = ", ".join(f"{v:.12f}" for v in seg)
        meths.append(f"  static double[] {name}() {{\n"
                     f"    return new double[]{{{body}}};\n  }}")
    return "\n\n".join(meths), ", ".join(names)


def main():
    if len(sys.argv) < 5:
        raise SystemExit("usage: run_sampling.py <model.mph> <solnum> "
                         "<metal> <tag> [n]")
    model = Path(sys.argv[1]).resolve()
    solnum = int(sys.argv[2])
    metal = sys.argv[3] == "1"
    tag = sys.argv[4]
    n = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    if not model.exists():
        raise SystemExit(f"model not found: {model}")

    s = S.cells(n)
    window = (4.18 + 1.6) * (1.6 + 1.0)
    chk = S.check(s, window)
    if chk["problems"]:
        raise SystemExit("sampling check failed: " + "; ".join(chk["problems"]))

    run = HERE / "runs" / f"{time.strftime('%Y%m%d-%H%M%S')}_{tag}"
    if run.exists():
        raise SystemExit(f"run directory exists: {run}")
    run.mkdir(parents=True)

    src = run / "gen_eval.java"
    # a coordinate file is rejected by COMSOL batch security, and one giant
    # array initialiser exceeds the per-method bytecode limit, so large point
    # sets are emitted as several small static methods
    if n >= 8:
        xs, xj = chunked(s["x"], "cx")
        ys, yj = chunked(s["y"], "cy")
        text = (TPL_CHUNK.read_text(encoding="utf-8")
                    .replace("__CLASS__", src.stem)
                    .replace("__MODEL__", str(model).replace("\\", "/"))
                    .replace("__SOLNUM__", str(solnum))
                    .replace("__XCHUNKS__", xs)
                    .replace("__YCHUNKS__", ys)
                    .replace("__XJOIN__", xj)
                    .replace("__YJOIN__", yj))
    else:
        text = (TPL.read_text(encoding="utf-8")
                   .replace("__CLASS__", src.stem)
                   .replace("__MODEL__", str(model).replace("\\", "/"))
                   .replace("__SOLNUM__", str(solnum))
                   .replace("__COORDS__", java_array(s["x"], s["y"])))
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
    if "DONE" not in text:
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
    if (nexpr, nsol, npts) != (NEXPR, 1, s["x"].size):
        problems.append(f"shape {nexpr}/{nsol}/{npts} != {NEXPR}/1/"
                        f"{s['x'].size}")
    if arr.shape != (s["x"].size, NEXPR):
        problems.append(f"parsed {arr.shape}")
    if arr.size and not np.isfinite(arr).all():
        problems.append("non-finite values")

    if not problems:
        derr = float(np.max(np.abs(arr[:, :2] - np.c_[s["x"], s["y"]])))
        if derr > 1e-9:
            problems.append(f"coordinates differ by {derr:.2e} um")
        want = np.array([EXPECT[metal][r] for r in s["region"]])
        bad = np.where(arr[:, 2].astype(int) != want)[0]
        if bad.size:
            detail = ", ".join(
                f"{s['region'][i]}->{int(arr[i, 2])}(exp {want[i]})"
                for i in bad[:5])
            problems.append(f"dom mismatch at {bad.size} cells: {detail}")
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
            problems.append(f"COMSOL magnitude rel {d2.max():.2e}")

    out = np.column_stack([arr, s["w"]])
    np.savetxt(run / "points.csv", out, delimiter=",",
               header="x,y,dom,normE,Exre,Exim,Eyre,Eyim,Ezre,Ezim,Emag_co,w",
               comments="")
    (run / "regions.txt").write_text(
        "\n".join(f"{r},{int((s['region'] == r).sum())}"
                  for r in sorted(set(s["region"]))), encoding="utf-8")
    neff = re.search(r"MODENEFF sol=\d+ re=(\S+) im=(\S+)", text)
    print(f"  points {arr.shape[0]}  neff_re {neff.group(1) if neff else '?'}")
    if not problems:
        print(f"  magnitude rel max {d1.max():.2e}; weight sum "
              f"{chk['area']:.6f} um2")
    for p in problems:
        print("  PROBLEM: " + p)
    print(f"\nRESULT {'PASS' if not problems else 'FAIL'}   run={run}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())

