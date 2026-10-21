"""Generate, compile and run a domain-aware export of one mode.

COMSOL batch blocks environment variables and file reads, so the parameters are
substituted into the Java source and compiled per case, as established earlier.

Fails loudly when compilation, the solve-dataset lookup or the export fail.

Usage:
  python export_dom.py <model.mph> <mode_index> <tag>
"""
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).parent
BIN = Path(r"D:\COMSOL63\Multiphysics\bin\win64")
TPL = HERE / "export_dom_fields.tpl"
SRC = HERE / "gen_export.java"
CLS = HERE / "gen_export.class"
ERR = ("错误", "Error", "ERROR", "无法编译", "运行 Java 类时出错")


def main():
    if len(sys.argv) < 4:
        raise SystemExit("usage: export_dom.py <model.mph> <mode_index> <tag>")
    model, mode, tag = sys.argv[1], sys.argv[2], sys.argv[3]
    model_path = Path(model).resolve()
    if not model_path.exists():
        raise SystemExit(f"model not found: {model_path}")
    out_csv = HERE / "out" / f"dom_{tag}.csv"
    out_csv.parent.mkdir(exist_ok=True)
    if out_csv.exists():
        out_csv.unlink()          # never leave a stale export in place

    text = (TPL.read_text(encoding="utf-8")
               .replace("__CLASS__", SRC.stem)
               .replace("__MODEL__", str(model_path).replace("\\", "/"))
               .replace("__MODE__", str(int(mode)))
               .replace("__TAG__", tag)
               .replace("__OUT__", str(out_csv).replace("\\", "/")))
    if "__" in text:
        raise SystemExit("unsubstituted placeholder remains")
    SRC.write_text(text, encoding="utf-8")

    if CLS.exists():
        CLS.unlink()
    r = subprocess.run([str(BIN / "comsolcompile.exe"), SRC.name],
                       cwd=HERE, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if any(k in out for k in ERR) or not CLS.exists():
        print("FAIL: compile")
        print(out.strip()[:800])
        return 1
    if CLS.stat().st_mtime < SRC.stat().st_mtime:
        print("FAIL: class older than source")
        return 1
    print("compile: ok")

    log = HERE / "out" / f"export_{tag}.log"
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        r = subprocess.run([str(BIN / "comsolbatch.exe"),
                            "-inputfile", CLS.name],
                           cwd=HERE, stdout=fh, stderr=subprocess.STDOUT)
    text_log = log.read_text(encoding="utf-8", errors="replace")
    if r.returncode != 0 or "EXPORTED" not in text_log:
        print(f"FAIL: batch (see {log})")
        for line in text_log.splitlines()[-12:]:
            print("  " + line)
        return 1
    if not out_csv.exists() or out_csv.stat().st_size < 1000:
        print(f"FAIL: export missing or empty: {out_csv}")
        return 1

    for line in text_log.splitlines():
        if line.startswith(("LOADED", "MODES_TOTAL", "EXPORTED", "MODENEFF",
                            "SELMAP", "NDOM")):
            print("  " + line)
    with out_csv.open(encoding="utf-8", errors="replace") as fh:
        rows = sum(1 for _ in fh) - 9
    print(f"rows {rows} -> {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
