"""Generate, compile and run one COMSOL optical baseline case.

COMSOL batch mode blocks both getenv() and file reads (security preferences),
so the parameters are substituted into the Java source and compiled per case.

Usage:  python run_case.py <metal 0|1> <hmax_nm> <xw_um> <tag>
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TEMPLATE = HERE / "optical_baseline.java"
SRC = HERE / "optical_gen.java"


def main():
    metal = sys.argv[1] if len(sys.argv) > 1 else "0"
    hmax = sys.argv[2] if len(sys.argv) > 2 else "25"
    xw = sys.argv[3] if len(sys.argv) > 3 else "1.6"
    tag = sys.argv[4] if len(sys.argv) > 4 else "run"
    shift = sys.argv[5] if len(sys.argv) > 5 else "1.95"
    sigma = sys.argv[6] if len(sys.argv) > 6 else "0"
    lnk = sys.argv[7] if len(sys.argv) > 7 else "0"
    alsign = sys.argv[8] if len(sys.argv) > 8 else "-"

    text = TEMPLATE.read_text(encoding="utf-8")
    text = (text.replace("__METAL__", "true" if metal == "1" else "false")
                .replace("__HMAX__", str(float(hmax)))
                .replace("__XW__", str(float(xw)))
                .replace("__TAG__", tag)
                .replace("__SHIFT__", shift)
                .replace("__SIGMA__", sigma)
                .replace("__LNK__", lnk)
                .replace("__ALSIGN__", alsign))
    SRC.write_text(text, encoding="utf-8")

    r = subprocess.run([str(BIN / "comsolcompile.exe"), SRC.name],
                       cwd=HERE, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if "ERROR" in out or "错误" in out or "无法编译" in out:
        print("COMPILE FAILED")
        print(out.strip())
        return 2
    print("compile: ok")

    log = HERE / "out" / f"run_{tag}.log"
    log.parent.mkdir(exist_ok=True)
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        r = subprocess.run([str(BIN / "comsolbatch.exe"),
                            "-inputfile", SRC.with_suffix(".class").name],
                           cwd=HERE, stdout=fh, stderr=subprocess.STDOUT)
    print(f"batch exit {r.returncode}, log {log}")
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(("CONFIG", "GEOM", "MESH", "NEFF", "SAVED", "SOLVE")):
            print("  " + line)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
