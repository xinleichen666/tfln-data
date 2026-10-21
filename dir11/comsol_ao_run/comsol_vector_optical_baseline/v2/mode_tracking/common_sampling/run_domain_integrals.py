"""Reference domain integrals from a saved mode (read-only, no re-solve).

Usage:
  python run_domain_integrals.py <model.mph> <solnum> <tag>
"""
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
TPL = HERE / "domain_integrals.tpl"
ERR = ("错误", "Error", "ERROR", "无法编译", "运行 Java 类时出错")


def main():
    if len(sys.argv) < 4:
        raise SystemExit("usage: run_domain_integrals.py <model.mph> "
                         "<solnum> <tag>")
    model = Path(sys.argv[1]).resolve()
    solnum = int(sys.argv[2])
    tag = sys.argv[3]
    if not model.exists():
        raise SystemExit(f"model not found: {model}")

    run = HERE / "runs" / f"integrals_{tag}"
    run.mkdir(parents=True, exist_ok=True)
    src = run / "gen_int.java"
    text = (TPL.read_text(encoding="utf-8")
               .replace("__CLASS__", src.stem)
               .replace("__MODEL__", str(model).replace("\\", "/"))
               .replace("__SOLNUM__", str(solnum)))
    if "__" in text:
        raise SystemExit("unsubstituted placeholder")
    src.write_text(text, encoding="utf-8")
    cls = run / "gen_int.class"
    if cls.exists():
        cls.unlink()

    r = subprocess.run([str(BIN / "comsolcompile.exe"), src.name],
                       cwd=run, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if any(k in out for k in ERR) or not cls.exists():
        print("FAIL compile")
        print(out.strip()[:2500])
        return 1

    log = run / "integrals.log"
    with log.open("w", encoding="utf-8", errors="replace") as fh:
        subprocess.run([str(BIN / "comsolbatch.exe"), "-inputfile", cls.name],
                       cwd=run, stdout=fh, stderr=subprocess.STDOUT)
    txt = log.read_text(encoding="utf-8", errors="replace")
    if "INTEGRALS_DONE" not in txt:
        print("FAIL run (see %s)" % log)
        for line in txt.splitlines()[-20:]:
            print("  " + line)
        return 1

    doms = []
    for m2 in re.finditer(r"^ORD (\d+) (\S+) applied=(\S+) readback=(\S+) (.*)$",
                          txt, re.M):
        vals = [float(x) for x in m2.group(5).split()]
        doms.append((int(m2.group(1)), m2.group(2), m2.group(3),
                     m2.group(4), vals))
    if not doms:
        print("FAIL no ORD lines")
        return 1
    orders = sorted({d[0] for d in doms})
    names = [d[1] for d in doms if d[0] == orders[0]]
    table = {}
    for o, nm, ap, rb, vals in doms:
        table.setdefault(o, {})[nm] = vals
    problems = []
    if len(orders) < 2:
        problems.append("fewer than two integration orders evaluated")
    applied = {d[2] for d in doms}
    readback = {d[3] for d in doms}
    if "true" not in applied:
        problems.append("integration order could not be set (intorder rejected)")
    print(f"  orders {orders}  readback {sorted(readback)}")

    def totals(o):
        return {nm: v for nm, v in table[o].items()}

    # stability between the two highest orders
    hi, lo = orders[-1], orders[-2]

    def agg(o):
        t = np.array([table[o][nm] for nm in names], dtype=float)
        return t

    A_hi, A_lo = agg(hi), agg(lo)
    # convert SI -> um^2 based units
    A_hi, A_lo = A_hi * 1e12, A_lo * 1e12
    tot_hi = A_hi[:, 0].sum()
    tot_lo = A_lo[:, 0].sum()
    d_tot = abs(tot_hi - tot_lo) / max(abs(tot_hi), 1e-30)
    print(f"  total norm order {lo} -> {hi}: {tot_lo:.9e} -> {tot_hi:.9e} "
          f"(rel change {d_tot:.2e})")
    if d_tot > 1e-3:
        problems.append(f"total norm unstable with order: {d_tot:.2e} > 1e-3")
    for nm, a_lo, a_hi in zip(names, A_lo, A_hi):
        for c, cname in enumerate(("normE2", "Ex2", "Ey2", "Ez2", "area")):
            rel = abs(a_hi[c] - a_lo[c]) / max(abs(a_hi[c]), 1e-30)
            if rel > 1e-3:
                problems.append(f"{nm}.{cname} unstable: {rel:.2e}")
        sr = a_lo[0] / tot_lo
        sh = a_hi[0] / tot_hi
        if abs(sr - sh) > 1e-3:
            problems.append(f"{nm} share unstable: {abs(sr-sh):.2e}")

    arr = A_hi
    if not np.isfinite(arr).all():
        problems.append("non-finite integral values")
    if (arr[:, 4] <= 0).any():
        problems.append("non-positive domain area")
    # the magnitude integral must equal the sum of the component integrals
    d = np.abs(arr[:, 0] - arr[:, 1:4].sum(axis=1)) / np.maximum(arr[:, 0], 1e-30)
    if d.max() > 1e-8:
        problems.append(f"normE^2 != sum of components, max rel {d.max():.2e}")

    area = float(arr[:, 4].sum())
    # every solid region is a rectangle with a known area; air must be what is
    # left, so a wrong selection cannot pass as a valid reference
    EXPECT = {"selSlabL": 0.241875, "selRidge": 0.3225, "selSlabR": 0.241875,
              "selAlL": 0.0645, "selAlR": 0.0645}
    solids = 0.0
    for nm, row in zip(names, arr):
        want = EXPECT.get(nm)
        if want is not None:
            solids += want
            if abs(row[4] - want) > 1e-9:
                problems.append(f"{nm} area {row[4]:.9f} != {want:.9f}")
    if "selAir" in names:
        i = names.index("selAir")
        want_air = 15.028 - solids
        if abs(arr[i, 4] - want_air) > 1e-9:
            problems.append(f"selAir area {arr[i,4]:.9f} != {want_air:.9f}")
    if abs(area - 15.028) > 1e-9:
        problems.append(f"total area {area:.9f} != 15.028")
    neff = re.search(r"MODENEFF sol=\d+ re=(\S+) im=(\S+)", txt)
    with (run / "integrals.csv").open("w", encoding="utf-8") as fh:
        fh.write("region,normE2,Ex2,Ey2,Ez2,area\n")
        for nm, row in zip(names, arr):
            fh.write(nm + "," + ",".join(f"{v:.17g}" for v in row) + "\n")
    (run / "identity.txt").write_text(
        f"model={model}\nsolnum={solnum}\n"
        f"neff_re={neff.group(1) if neff else '?'}\n"
        f"neff_im={neff.group(2) if neff else '?'}\n"
        f"area_total={area:.12f}\n", encoding="utf-8")
    for nm, row in zip(names, arr):
        print(f"  {nm:9s} area {row[4]:9.6f}  normE2 {row[0]:.9e}  "
              f"Ez2 share {row[3]/max(row[0],1e-30):.4f}")
    print(f"  total area {area:.6f} um2   neff "
          f"{neff.group(1) if neff else '?'}")
    for p in problems:
        print("  PROBLEM: " + p)
    print(f"\nRESULT {'PASS' if not problems else 'FAIL'}  run={run}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
