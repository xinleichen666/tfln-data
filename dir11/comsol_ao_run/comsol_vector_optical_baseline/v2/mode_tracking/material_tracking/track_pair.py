"""Rank all modes of a target model against one mode of a reference model.

Usage:
  python track_pair.py --ref out/track_t1e-4.mph --refsol 40 \
                       --tgt out/track_t2e-4.mph --tag step2
"""
import argparse
import re
import subprocess
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

BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TPL = HERE / "track_pair.tpl"
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


def check_ranking(rows, nmode, min_s=0.99, min_margin=0.02):
    """Reject an incomplete, duplicated or ambiguous pairing."""
    problems = []
    ids = [int(r[0]) for r in rows]
    if len(ids) != nmode:
        problems.append(f"{len(ids)} modes ranked, expected {nmode}")
    if len(set(ids)) != len(ids):
        problems.append("duplicate mode numbers in the ranking")
    if set(ids) != set(range(1, nmode + 1)):
        problems.append(f"ranking does not cover modes 1..{nmode}")
    for r in rows:
        if not all(np.isfinite([float(r[1]), float(r[2]), float(r[3])])):
            problems.append(f"non-finite overlap for mode {r[0]}")
            break
    if len(rows) >= 2:
        best = max(rows, key=lambda t: float(t[1]))
        second = sorted(rows, key=lambda t: -float(t[1]))[1]
        if float(best[1]) < min_s:
            problems.append(f"best S {float(best[1]):.6f} < {min_s}")
        if float(best[1]) - float(second[1]) < min_margin:
            problems.append(f"margin {float(best[1])-float(second[1]):.4f} "
                            f"< {min_margin}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--refsol", required=True, type=int)
    ap.add_argument("--tgt", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--nmode", type=int, default=40)
    a = ap.parse_args()

    cells = C.base_cells(12)
    sp = C.arrays(cells)
    run = HERE / "runs" / f"pair_{a.tag}"
    if run.exists():
        raise SystemExit(f"run directory exists: {run}")
    run.mkdir(parents=True)

    parts, joins = [], []
    for name, vals in (("x", sp["x"]), ("y", sp["y"]), ("w", sp["w"])):
        m, j = chunked(vals, name)
        parts.append(m)
        joins.append((name.upper() + "JOIN", j))
    text = (TPL.read_text(encoding="utf-8")
               .replace("__CLASS__", "trackpair")
               .replace("__CHUNKS__", "\n\n".join(parts))
               .replace("__REFMODEL__", str(Path(a.ref).resolve()).replace("\\", "/"))
               .replace("__TGTMODEL__", str(Path(a.tgt).resolve()).replace("\\", "/"))
               .replace("__REFSOL__", str(a.refsol))
               .replace("__NMODE__", str(a.nmode)))
    for key, j in joins:
        text = text.replace(f"__{key}__", j)
    if "__" in text:
        raise SystemExit("unsubstituted placeholder")
    src = run / "trackpair.java"
    src.write_text(text, encoding="utf-8")
    cls = run / "trackpair.class"
    if cls.exists():
        cls.unlink()

    r = subprocess.run([str(BIN / "comsolcompile.exe"), src.name],
                       cwd=run, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if any(k in out for k in ERR) or not cls.exists():
        print("FAIL compile")
        print(out.strip()[:1200])
        return 1
    print("compile ok")

    log = run / "pair.log"
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        subprocess.run([str(BIN / "comsolbatch.exe"), "-inputfile", cls.name],
                       cwd=run, stdout=fh, stderr=subprocess.STDOUT)
    txt = log.read_text(encoding="utf-8", errors="replace")
    if "PAIR_DONE" not in txt:
        print("FAIL run (see log)")
        for ln in txt.splitlines()[-12:]:
            print("  " + ln)
        return 1

    rows = re.findall(r"^MODE (\d+) S=(\S+) zre=(\S+) zim=(\S+) nrm=(\S+)$",
                      txt, re.M)
    data = sorted([(int(m), float(s), float(zr), float(zi), float(nn))
                   for m, s, zr, zi, nn in rows], key=lambda t: -t[1])
    if not data:
        print("FAIL no modes parsed")
        return 1
    (run / "ranking.csv").write_text(
        "mode,S,zre,zim,norm\n" + "\n".join(
            f"{m},{s:.9f},{zr:.9f},{zi:.9f},{nn:.12g}"
            for m, s, zr, zi, nn in data) + "\n", encoding="utf-8")
    print(f"  {a.tag}: {len(data)} modes")
    for m, s, zr, zi, nn in data[:4]:
        print(f"    mode {m:2d}  S {s:.6f}  z {zr:.6f}{zi:+.6f}i")
    best, second = data[0][1], data[1][1] if len(data) > 1 else 0.0
    print(f"  margin best-second = {best - second:.4f}")
    problems = check_ranking([(str(m), str(s), str(zr), str(zi))
                              for m, s, zr, zi, nn in data], a.nmode)
    for p in problems:
        print("  PROBLEM: " + p)
    ok = not problems
    print(f"\nRESULT {'PASS' if ok else 'AMBIGUOUS/FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
