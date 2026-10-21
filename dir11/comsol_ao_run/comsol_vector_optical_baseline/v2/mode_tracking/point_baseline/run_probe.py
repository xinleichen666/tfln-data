"""Compile and run the Interp API probe, in an isolated run directory.

Usage: python run_probe.py <model.mph> <tag>
"""
import subprocess
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).parent
BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TPL = HERE / "probe_interp.tpl"
ERR = ("错误", "Error", "ERROR", "无法编译", "运行 Java 类时出错")


def main():
    if len(sys.argv) < 4:
        raise SystemExit("usage: run_probe.py <model.mph> <mode_index> <tag>")
    model = Path(sys.argv[1]).resolve()
    mode = int(sys.argv[2])
    tag = sys.argv[3]
    if not model.exists():
        raise SystemExit(f"model not found: {model}")

    run = HERE / "runs" / f"{time.strftime('%Y%m%d-%H%M%S')}_{tag}"
    if run.exists():
        raise SystemExit(f"run directory exists: {run}")
    run.mkdir(parents=True)

    src = run / "gen_probe.java"
    src.write_text(TPL.read_text(encoding="utf-8")
                      .replace("__CLASS__", src.stem)
                      .replace("__MODEL__", str(model).replace("\\", "/"))
                      .replace("__MODE__", str(mode)),
                   encoding="utf-8")
    if "__" in src.read_text(encoding="utf-8"):
        raise SystemExit("unsubstituted placeholder")

    r = subprocess.run([str(BIN / "comsolcompile.exe"), src.name],
                       cwd=run, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if any(k in out for k in ERR) or not (run / "gen_probe.class").exists():
        print("FAIL compile")
        print(out.strip()[:800])
        return 1
    print("compile: ok")

    log = run / "probe.log"
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        r = subprocess.run([str(BIN / "comsolbatch.exe"),
                            "-inputfile", "gen_probe.class"],
                           cwd=run, stdout=fh, stderr=subprocess.STDOUT)
    text = log.read_text(encoding="utf-8", errors="replace")
    ok = "INTERP_OK" in text
    for line in text.splitlines():
        if line.startswith(("INTERP_OK", "INTERP_FAIL", "LOADED", "SOLS",
                            "DATASETS", "DSET_SOL", "  expr[")):
            print("  " + line)
    print(f"\nRESULT {'PASS' if ok else 'FAIL'}   run={run}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
