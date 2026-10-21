"""Evaluate an explicit point list on one saved model (read-only).

Coordinates are embedded as several small static methods: a single array
initialiser exceeds the per-method bytecode limit, and COMSOL batch refuses to
read a coordinate file (its security preference denies "read").

Usage (library):  r = eval_points(model, solnum, x, y, tag)
"""
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TPL = HERE / "eval_points_chunk.tpl"
ERR = ("错误", "Error", "ERROR", "无法编译", "运行 Java 类时出错")
NEXPR = 11


def chunked(vals, prefix, per=400):
    meths, names = [], []
    for i in range(0, len(vals), per):
        seg = vals[i:i + per]
        name = f"{prefix}{i // per}"
        names.append(name + "()")
        body = ", ".join(f"{v:.12f}" for v in seg)
        meths.append(f"  static double[] {name}() {{\n"
                     f"    return new double[]{{{body}}};\n  }}")
    return "\n\n".join(meths), ", ".join(names)


def eval_points(model, solnum, x, y, tag):
    """Return (arr, neff, run_dir).  arr columns as in run_sampling.points.csv."""
    model = Path(model).resolve()
    if not model.exists():
        raise RuntimeError(f"model not found: {model}")
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.size == 0:
        raise RuntimeError("bad point list")
    if not (np.isfinite(x).all() and np.isfinite(y).all()):
        raise RuntimeError("non-finite coordinates")

    run = HERE / "runs" / f"{time.strftime('%Y%m%d-%H%M%S')}_{tag}"
    if run.exists():
        raise RuntimeError(f"run directory exists: {run}")
    run.mkdir(parents=True)
    src = run / "gen_eval.java"
    xs, xj = chunked(x, "cx")
    ys, yj = chunked(y, "cy")
    text = (TPL.read_text(encoding="utf-8")
               .replace("__CLASS__", src.stem)
               .replace("__MODEL__", str(model).replace("\\", "/"))
               .replace("__SOLNUM__", str(solnum))
               .replace("__XCHUNKS__", xs)
               .replace("__YCHUNKS__", ys)
               .replace("__XJOIN__", xj)
               .replace("__YJOIN__", yj))
    if "__" in text:
        raise RuntimeError("unsubstituted placeholder")
    src.write_text(text, encoding="utf-8")

    cls = run / "gen_eval.class"
    if cls.exists():
        cls.unlink()
    r = subprocess.run([str(BIN / "comsolcompile.exe"), src.name],
                       cwd=run, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if any(k in out for k in ERR) or not cls.exists():
        raise RuntimeError("compile failed: " + out.strip()[:600])

    log = run / "eval.log"
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        subprocess.run([str(BIN / "comsolbatch.exe"), "-inputfile", cls.name],
                       cwd=run, stdout=fh, stderr=subprocess.STDOUT)
    txt = log.read_text(encoding="utf-8", errors="replace")
    if "DONE" not in txt:
        # keep every artefact: a failed run is evidence, and deleting the
        # source or the partial log would make the failure unreproducible
        raise RuntimeError("run failed, see " + str(log))

    shape = re.search(r"SHAPE expr=(\d+) sol=(\d+) pts=(\d+)", txt)
    if not shape:
        raise RuntimeError("no SHAPE line")
    nexpr, nsol, npts = map(int, shape.groups())
    rows = [[float(v) for v in m.group(2).split()]
            for m in re.finditer(r"^PT (\d+) (.*)$", txt, re.M)]
    arr = np.array(rows)
    if (nexpr, nsol, npts) != (NEXPR, 1, x.size):
        raise RuntimeError(f"shape {nexpr}/{nsol}/{npts} != {NEXPR}/1/{x.size}")
    if arr.shape != (x.size, NEXPR) or not np.isfinite(arr).all():
        raise RuntimeError(f"parsed {arr.shape} or non-finite values")
    if np.max(np.abs(arr[:, :2] - np.c_[x, y])) > 1e-9:
        raise RuntimeError("coordinates echoed back do not match the request")

    neff = re.search(r"MODENEFF sol=\d+ re=(\S+) im=(\S+)", txt)
    if neff is None:
        raise RuntimeError("no MODENEFF line")
    np.savetxt(run / "points.csv", arr, delimiter=",",
               header="x,y,dom,normE,Exre,Exim,Eyre,Eyim,Ezre,Ezim,Emag_co",
               comments="")
    return arr, (float(neff.group(1)), float(neff.group(2))), run


if __name__ == "__main__":
    sys.exit("import this module; use run_sampling.py for grid runs")
