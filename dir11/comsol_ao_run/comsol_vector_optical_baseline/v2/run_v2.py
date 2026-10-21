"""Run one optical_v2 case with hard failure detection.

Fails (non-zero exit) if any of these is true:
  * compilation reports an error, or the .class is missing / older than the source
  * the log contains COMSOL error markers
  * the saved model file is missing or empty
  * a requested field export is missing or empty

Usage:
  python run_v2.py --metal 1 --hmax 25 --xw 1.6 --shift 1.78 --neigs 40
                   --nexport 2 --tag eqairFix --aniso true --aleps "1"
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TPL = HERE / "optical_v2.java"
OUT = HERE / "out"

ERR_MARKERS = ("错误", "Error", "ERROR", "无法编译", "运行 Java 类时出错")
KNOWN = ("metal", "hmax", "xw", "shift", "neigs", "nexport", "tag",
         "aniso", "aleps", "alsign", "kappa")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def parse(argv):
    """Named parameters only.  A stray positional value used to be silently
    consumed as kappa, which produced a wrong model under a plausible name."""
    p = dict(metal="0", hmax="25", xw="1.6", shift="1.78", neigs="40",
             nexport="2", tag="run", aniso="false", aleps=None,
             alsign="-", kappa="15.6")
    i = 0
    while i < len(argv):
        if not argv[i].startswith("--"):
            fail(f"unexpected positional argument {argv[i]!r}; use --name value")
        k = argv[i][2:]
        if k not in KNOWN:
            fail(f"unknown option --{k}")
        if i + 1 >= len(argv):
            fail(f"option --{k} needs a value")
        p[k] = argv[i + 1]
        i += 2
    if p["aleps"] is None:
        p["aleps"] = f"({1.44}{p['alsign']}{p['kappa']}*i)^2"
    return p


def main():
    p = parse(sys.argv[1:])
    metal = p["metal"]
    hmax = p["hmax"]
    xw = p["xw"]
    shift = p["shift"]
    neigs = p["neigs"]
    nexport = p["nexport"]
    tag = p["tag"]
    alsign = p["alsign"]
    aniso = p["aniso"]
    kappa = p["kappa"]
    aleps = p["aleps"]

    # per-run artefacts, so a run never overwrites another run's evidence
    run = OUT / f"case_{tag}"
    if run.exists():
        fail(f"run directory already exists: {run}")
    run.mkdir(parents=True)
    SRC = run / "gen_v2.java"
    CLS = run / "gen_v2.class"

    cfg = dict(metal=metal, hmax_nm=hmax, xw=xw, neff_shift=shift,
               neigs=neigs, nexport=nexport, tag=tag, aniso=aniso,
               al_eps=aleps, ln_no=2.211, ln_ne=2.138,
               created=time.strftime("%Y-%m-%d %H:%M:%S"))
    print("CONFIG " + json.dumps(cfg, ensure_ascii=False))
    (run / "config.json").write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")

    text = (TPL.read_text(encoding="utf-8")
               .replace("__CLASS__", SRC.stem)
               .replace("__METAL__", "true" if metal == "1" else "false")
               .replace("__HMAX__", str(float(hmax)))
               .replace("__XW__", str(float(xw)))
               .replace("__SHIFT__", shift)
               .replace("__NEIGS__", neigs)
               .replace("__NEXPORT__", nexport)
               .replace("__TAG__", tag)
               .replace("__ALSIGN__", alsign)
               .replace("__ANISO__", aniso)
               .replace("__KAPPA__", kappa)
               .replace("__ALEPS__", aleps))
    if "__" in text.replace("__METAL__", ""):
        leftovers = [ln.strip() for ln in text.splitlines() if "__" in ln]
        fail(f"unsubstituted placeholders: {leftovers[:3]}")

    # verify the generated source really carries the requested physics
    must = [f'String al = "{aleps}";',
            f"String nzz = {aniso} ? String.valueOf(NE * NE) : no2;"]
    for s in must:
        if s not in text:
            fail(f"generated source does not contain {s!r}")
    SRC.write_text(text, encoding="utf-8")
    print(f"  electrode eps expression : {aleps}")
    print(f"  LN anisotropic           : {aniso}")

    # force a fresh class file so a stale build cannot be reused
    if CLS.exists():
        CLS.unlink()
    r = subprocess.run([str(BIN / "comsolcompile.exe"), SRC.name],
                       cwd=run, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if any(k in out for k in ERR_MARKERS) or not CLS.exists():
        fail("compile: " + out.strip()[:800])
    if CLS.stat().st_mtime < SRC.stat().st_mtime:
        fail("class file older than source")
    print("compile: ok")

    log = run / "run.log"
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        r = subprocess.run([str(BIN / "comsolbatch.exe"),
                            "-inputfile", CLS.name],
                           cwd=run, stdout=fh, stderr=subprocess.STDOUT)
    text_log = log.read_text(encoding="utf-8", errors="replace")

    model = OUT / f"final_{tag}.mph"
    if r.returncode != 0:
        fail(f"batch exit {r.returncode}, see {log}")
    if "SOLVE_DONE" not in text_log:
        fail(f"solve did not finish, see {log}")
    if "POSTPROC_FAILED" in text_log:
        fail(f"post-processing failed, see {log}")
    if metal == "1" and "ENBAL_FAILED" in text_log:
        fail(f"energy-balance check did not run; loss is unverified, see {log}")
    if not model.exists() or model.stat().st_size < 1_000_000:
        fail(f"model not saved properly: {model}")

    exports = sorted(OUT.glob(f"f_{tag}_m*.csv"))
    if not exports:
        fail("no field exports produced")
    for e in exports:
        if e.stat().st_size < 1000:
            fail(f"empty export {e.name}")

    print(f"batch ok, log {log}, model {model.name} "
          f"({model.stat().st_size/1e6:.0f} MB), {len(exports)} exports")
    if "ENBAL_FAILED" in text_log:
        print("WARNING: energy-balance check failed - see log; "
              "loss values are NOT verified")
    for line in text_log.splitlines():
        if line.startswith(("CONFIG", "GEOM", "SEL", "MESH", "TOP", "NEFF mode=",
                            "ENERGY mode=", "ENBAL_FAILED", "POSTPROC_OK",
                            "SAVED_FINAL")):
            print("  " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
