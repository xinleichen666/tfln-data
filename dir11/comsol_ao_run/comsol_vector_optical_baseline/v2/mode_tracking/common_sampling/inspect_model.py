"""Load a saved model and print its ACTUAL configuration (read-only).

Nothing is solved and nothing is saved.  The point is that material tensors,
selections, physics formulation, mesh and study settings are read from the
file rather than assumed from its name.

Usage:
  python inspect_model.py <model.mph> [tag]
"""
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TPL = HERE / "inspect_model.tpl"
ERR = ("错误", "Error", "ERROR", "无法编译", "运行 Java 类时出错")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: inspect_model.py <model.mph> [tag]")
    model = Path(sys.argv[1]).resolve()
    if not model.exists():
        raise SystemExit(f"model not found: {model}")
    tag = sys.argv[2] if len(sys.argv) > 2 else model.stem

    run = HERE / "runs" / f"inspect_{tag}"
    run.mkdir(parents=True, exist_ok=True)
    src = run / "gen_inspect.java"
    text = (TPL.read_text(encoding="utf-8")
               .replace("__CLASS__", src.stem)
               .replace("__MODEL__", str(model).replace("\\", "/")))
    if "__" in text:
        raise SystemExit("unsubstituted placeholder")
    src.write_text(text, encoding="utf-8")
    cls = run / "gen_inspect.class"
    if cls.exists():
        cls.unlink()

    r = subprocess.run([str(BIN / "comsolcompile.exe"), src.name],
                       cwd=run, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if any(k in out for k in ERR) or not cls.exists():
        print("FAIL compile")
        print(out.strip()[:2500])
        return 1

    log = run / "inspect.log"
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        subprocess.run([str(BIN / "comsolbatch.exe"), "-inputfile", cls.name],
                       cwd=run, stdout=fh, stderr=subprocess.STDOUT)
    txt = log.read_text(encoding="utf-8", errors="replace")
    if "INSPECT_DONE" not in txt:
        print("FAIL inspect (see %s)" % log)
        for line in txt.splitlines()[-20:]:
            print("  " + line)
        return 1
    for line in txt.splitlines():
        if line.startswith("CHK "):
            print(line[4:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
