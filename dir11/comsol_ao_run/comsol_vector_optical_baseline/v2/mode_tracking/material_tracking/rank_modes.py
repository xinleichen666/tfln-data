"""Rank all stored modes of a model against a reference field.

The reference is the accepted eqairFix mode on the SAME grid, so every mode is
compared like for like.  One Java run yields all 40 overlaps.

Usage:
  python rank_modes.py --model out/track_t1e-4.mph --nmode 40 --tag t1e-4
  python rank_modes.py --model <ref>.mph --nmode 40 --tag selfcheck --grid 12
"""
import argparse
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

HERE = Path(__file__).resolve().parent
CS = HERE.parent / "common_sampling"
sys.path.insert(0, str(CS))

import cellspec as C                      # noqa: E402

BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TPL = HERE / "rank_modes.tpl"
ERR = ("错误", "Error", "ERROR", "无法编译", "运行 Java 类时出错")


def chunked(vals, prefix, per=400):
    meths, names = [], []
    for i in range(0, len(vals), per):
        seg = vals[i:i + per]
        name = f"{prefix}{i // per}"
        names.append(name + "()")
        body = ", ".join(f"{v:.17g}" for v in seg)
        meths.append(f"  static double[] {name}() {{\n"
                     f"    return new double[]{{{body}}};\n  }}")
    return "\n\n".join(meths), ", ".join(names)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--nmode", type=int, default=40)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--grid", type=int, default=12)
    ap.add_argument("--cells", default=None,
                    help="explicit cell list; overrides --grid")
    ap.add_argument("--ref", default=None,
                    help="reference field csv with x,y,Exre,Exim,...,Ezre,Ezim")
    a = ap.parse_args()

    if a.cells:
        cells = [tuple(float(v) for v in ln.split(","))
                 for ln in Path(a.cells).read_text(encoding="utf-8").splitlines()[1:]
                 if ln.strip()]
        sp = C.arrays(cells)
        rr = np.loadtxt(a.ref, delimiter=",", skiprows=1)
        if rr.shape[0] != len(cells):
            raise SystemExit("reference rows do not match the cell list")
        if np.max(np.abs(rr[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
            raise SystemExit("reference coordinates differ from the cell list")
        ref = np.zeros((len(cells), 12))
        ref[:, 0:2] = rr[:, 0:2]
        ref[:, 4:10] = rr[:, 2:8]     # 8-column layout -> 12-column layout
    else:
        cells = C.base_cells(a.grid)
        sp = C.arrays(cells)
        hits = sorted((CS / "runs").glob("*_eqfix5040"))
        if len(hits) != 1:
            raise SystemExit(f"expected one eqfix5040 run, got {hits}")
        ref = np.loadtxt(hits[0] / "points.csv", delimiter=",", skiprows=1)
        if ref.shape[0] != len(cells):
            raise SystemExit("reference grid size mismatch")
        if np.max(np.abs(ref[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
            raise SystemExit("reference coordinates differ from the grid")

    run = HERE / "runs" / f"rank_{a.tag}"
    if run.exists():
        raise SystemExit(f"run directory exists: {run}")
    run.mkdir(parents=True)

    parts = []
    joins = []
    for name, vals in (("x", sp["x"]), ("y", sp["y"]), ("w", sp["w"]),
                       ("rr", ref[:, 4]), ("ri", ref[:, 5]),
                       ("gr", ref[:, 6]), ("gi", ref[:, 7]),
                       ("br", ref[:, 8]), ("bi", ref[:, 9])):
        m, j = chunked(vals, name)
        parts.append(m)
        joins.append((name.upper() + "JOIN", j))
    text = (TPL.read_text(encoding="utf-8")
               .replace("__CLASS__", "rankmodes")
               .replace("__CHUNKS__", "\n\n".join(parts))
               .replace("__MODEL__", str(Path(a.model).resolve()).replace("\\", "/"))
               .replace("__NMODE__", str(a.nmode)))
    for key, j in joins:
        text = text.replace(f"__{key}__", j)
    if "__" in text:
        raise SystemExit("unsubstituted placeholder")
    src = run / "rankmodes.java"
    src.write_text(text, encoding="utf-8")
    cls = run / "rankmodes.class"
    if cls.exists():
        cls.unlink()

    r = subprocess.run([str(BIN / "comsolcompile.exe"), src.name],
                       cwd=run, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if any(k in out for k in ERR) or not cls.exists():
        print("FAIL compile")
        print(out.strip()[:1500])
        return 1
    print(f"compile ok ({src.stat().st_size/1e6:.1f} MB source)")

    log = run / "rank.log"
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        subprocess.run([str(BIN / "comsolbatch.exe"), "-inputfile", cls.name],
                       cwd=run, stdout=fh, stderr=subprocess.STDOUT)
    txt = log.read_text(encoding="utf-8", errors="replace")
    if "RANK_DONE" not in txt:
        print("FAIL run (see log)")
        for ln in txt.splitlines()[-15:]:
            print("  " + ln)
        return 1

    rows = re.findall(r"^MODE (\d+) S=(\S+) zre=(\S+) zim=(\S+) nrm=(\S+)$",
                      txt, re.M)
    if not rows:
        print("FAIL no MODE lines")
        return 1
    data = [(int(m), float(s), float(zr), float(zi), float(nn))
            for m, s, zr, zi, nn in rows]
    data.sort(key=lambda t: -t[1])
    (run / "ranking.csv").write_text(
        "mode,S,zre,zim,norm\n" + "\n".join(
            f"{m},{s:.9f},{zr:.9f},{zi:.9f},{nn:.12g}" for m, s, zr, zi, nn in data)
        + "\n", encoding="utf-8")
    print(f"  {a.tag}: {len(data)} modes ranked")
    for m, s, zr, zi, nn in data[:4]:
        print(f"    mode {m:2d}  S {s:.6f}  z {zr:.6f}{zi:+.6f}i")
    best, second = data[0][1], data[1][1] if len(data) > 1 else 0.0
    print(f"  margin best-second = {best - second:.4f}")
    ok = best >= 0.99 and (best - second) >= 0.02
    print(f"\nRESULT {'PASS' if ok else 'AMBIGUOUS/FAIL'} "
          f"(S>=0.99 and margin>=0.02)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
