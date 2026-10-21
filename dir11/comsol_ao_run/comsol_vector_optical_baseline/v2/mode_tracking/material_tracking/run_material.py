"""Run one material-continuation step on a saved model (one new solve).

    eps_elec(t) = 1 + t * [ (1.44 - 15.6i)^2 - 1 ]

t is a numerical continuation parameter, NOT a physical mixture fraction.

Usage:
  python run_material.py --t 0 --tag t0
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
BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TPL = HERE / "track_material.tpl"
SRC_MODEL = HERE.parents[1] / "out" / "final_eqairFix.mph"
OUTDIR = HERE / "out"
ERR = ("错误", "Error", "ERROR", "无法编译", "运行 Java 类时出错")


def eps_expr(t):
    if t == 0.0:
        return "1"
    return f"(1+{t!r}*((1.44-15.6*i)^2-1))"


def check_mode_list(modes, expected):
    """Reject a spectrum that is incomplete, duplicated or not finite."""
    problems = []
    if len(modes) != expected:
        problems.append(f"{len(modes)} modes returned, expected {expected}")
    ids = [int(m[0]) for m in modes]
    if len(set(ids)) != len(ids):
        problems.append("duplicate mode numbers")
    if set(ids) != set(range(1, expected + 1)):
        missing = sorted(set(range(1, expected + 1)) - set(ids))
        problems.append(f"mode numbers are not 1..{expected}; missing {missing[:5]}")
    for m in modes:
        vals = [float(m[1]), float(m[2]), float(m[3])]
        if not all(np.isfinite(vals)):
            problems.append(f"non-finite neff for mode {m[0]}")
            break
        if not (0.0 < vals[0] < 5.0):
            problems.append(f"implausible Re(neff) {vals[0]} for mode {m[0]}")
            break
    return problems


def norm_expr(s):
    """Normalise an echoed COMSOL expression for comparison."""
    return "".join(s.split()).replace("[", "").replace("]", "")


def check_readback(lines, expected):
    """The model must hold the requested permittivity, not merely some value."""
    problems = []
    want = norm_expr(expected)
    if len(lines) < 2:
        return ["material readback incomplete"]
    for ln in lines:
        got = norm_expr(ln.split(" ", 2)[-1])
        if got != want:
            problems.append(f"readback mismatch: {got!r} != {want!r}")
            break
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t", required=True, type=float)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--source", default=None,
                    help="explicit source model; defaults to final_eqairFix.mph")
    ap.add_argument("--nmode", type=int, default=40)
    a = ap.parse_args()

    src_model = Path(a.source).resolve() if a.source else SRC_MODEL
    if not src_model.exists():
        raise SystemExit(f"source model not found: {src_model}")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    run = HERE / "runs" / a.tag
    if run.exists():
        raise SystemExit(f"run directory exists: {run}")
    run.mkdir(parents=True)

    out_model = OUTDIR / f"track_{a.tag}.mph"
    src = run / "track.java"
    text = (TPL.read_text(encoding="utf-8")
               .replace("__CLASS__", src.stem)
               .replace("__MODEL__", str(src_model).replace("\\", "/"))
               .replace("__ALEPS__", eps_expr(a.t))
               .replace("__NMODE__", str(a.nmode))
               .replace("__OUT__", str(out_model).replace("\\", "/")))
    if "__" in text:
        raise SystemExit("unsubstituted placeholder")
    src.write_text(text, encoding="utf-8")
    (run / "config.txt").write_text(
        f"source={src_model}\nt={a.t!r}\neps={eps_expr(a.t)}\n"
        f"output={out_model}\nnmode={a.nmode}\n", encoding="utf-8")

    cls = run / "track.class"
    if cls.exists():
        cls.unlink()
    r = subprocess.run([str(BIN / "comsolcompile.exe"), src.name],
                       cwd=run, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if any(k in out for k in ERR) or not cls.exists():
        print("FAIL compile")
        print(out.strip()[:1500])
        return 1
    print("compile: ok")

    log = run / "solve.log"
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        proc = subprocess.run([str(BIN / "comsolbatch.exe"),
                               "-inputfile", cls.name],
                              cwd=run, stdout=fh, stderr=subprocess.STDOUT)
    txt = log.read_text(encoding="utf-8", errors="replace")
    problems = []
    if proc.returncode != 0:
        problems.append(f"batch exit code {proc.returncode}")
    if "SOLVE_DONE" not in txt:
        problems.append("solve did not finish")
    if "SAVED" not in txt:
        problems.append("model not saved")
    rb = [ln for ln in txt.splitlines() if ln.startswith("READBACK ")]
    if not rb:
        problems.append("material readback missing")
    else:
        problems += check_readback(rb, eps_expr(a.t))
    if f"NEIGS_SET {a.nmode}" not in txt:
        problems.append(f"study did not accept neigs={a.nmode}")
    if not out_model.exists() or out_model.stat().st_size < 1_000_000:
        problems.append("output model missing or too small")

    modes = re.findall(r"^NEFF mode=(\d+) re=(\S+) im=(\S+) ridge=(\S+)$",
                       txt, re.M)
    problems += check_mode_list(modes, a.nmode)
    if "POSTPROC_FAILED" in txt:
        problems.append("post-processing failed: " + txt.split("POSTPROC_FAILED")[1].splitlines()[0][:120])
    print(f"  t={a.t}  modes {len(modes)}  eps={eps_expr(a.t)}")
    print(f"  source {src_model}")
    for ln in rb:
        print("  " + ln)
    if modes:
        best = min(modes, key=lambda m: abs(float(m[1]) - 1.7818934544))
        print(f"  closest to 1.7818934544: mode {best[0]} re={best[1]} "
              f"im={best[2]} ridge={best[3]}")
        (run / "modes.csv").write_text(
            "mode,re,im,ridge\n" + "\n".join(
                f"{m[0]},{m[1]},{m[2]},{m[3]}" for m in modes) + "\n",
            encoding="utf-8")
    for p in problems:
        print("  PROBLEM: " + p)
    print(f"\nRESULT {'PASS' if not problems else 'FAIL'}  model={out_model}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
