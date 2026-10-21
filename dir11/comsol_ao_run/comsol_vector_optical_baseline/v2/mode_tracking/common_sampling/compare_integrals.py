"""Compare sampling aggregates against the COMSOL domain integrals.

The reference integrals come from R.run_domain_integrals (IntSurface on the
model's own named selections, in um^2 after unit conversion).  The sampling
comes from run_sampling.py at the same density.

Regions are matched by name.  In the no-metal model the electrode footprints
belong to the single air domain, so metalL/metalR have no separate reference
and are folded into air instead of being compared against nothing.

Usage:
  python compare_integrals.py <integrals.csv> <points.csv> <n>
"""
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sampling as S                 # noqa: E402

MAP = {"selRidge": "ridge", "selSlabL": "slabL", "selSlabR": "slabR",
       "selAlL": "metalL", "selAlR": "metalR", "selAir": "air"}


def run_compare(ref, E, w, region, total_tol=0.01, share_tol=0.005):
    """Core comparison, separated from file handling so it can be tested.

    ref: {region: [normE2, Ex2, Ey2, Ez2, area]}
    Returns (rows, tot_ref, tot_samp, problems, contrib).

    The total check is essential: a sampling that is uniformly low by 5 %
    keeps every regional share identical, so a share-only test would pass it.
    """
    region = np.array(region, dtype=object)
    if region.shape[0] != E.shape[0] or E.shape[0] != w.shape[0]:
        raise ValueError("shape mismatch between field, weights and regions")
    if not np.isfinite(E).all() or not np.isfinite(w).all():
        raise ValueError("non-finite input")
    if (w <= 0).any():
        raise ValueError("weights must be positive")

    fold = ("metalL" not in ref and "metalR" not in ref)
    if fold:
        region = np.where(np.isin(region, ["metalL", "metalR"]), "air", region)

    rows = []
    for name in ("ridge", "slabL", "slabR", "metalL", "metalR", "air"):
        m = region == name
        if not m.any() and name not in ref:
            continue
        samp = dict(normE2=float(np.sum(w[m] * np.sum(np.abs(E[m]) ** 2, 1))),
                    Ex2=float(np.sum(w[m] * np.abs(E[m, 0]) ** 2)),
                    Ey2=float(np.sum(w[m] * np.abs(E[m, 1]) ** 2)),
                    Ez2=float(np.sum(w[m] * np.abs(E[m, 2]) ** 2)),
                    area=float(w[m].sum()), cells=int(m.sum()))
        r = ref.get(name)
        rows.append((name, samp,
                     None if r is None else
                     dict(normE2=r[0], Ex2=r[1], Ey2=r[2], Ez2=r[3], area=r[4])))

    tot_s = sum(x[1]["normE2"] for x in rows)
    tot_r = sum(x[2]["normE2"] for x in rows if x[2])
    comp_r = [sum(x[2]["Ex2" if c == 0 else "Ey2" if c == 1 else "Ez2"]
                  for x in rows if x[2]) for c in range(3)]
    comp_s = [sum(x[1]["Ex2" if c == 0 else "Ey2" if c == 1 else "Ez2"]
                  for x in rows) for c in range(3)]

    problems = []
    if tot_r <= 0 or tot_s <= 0:
        problems.append("zero total norm")
        return rows, tot_r, tot_s, problems, []
    ratio = tot_s / tot_r
    if abs(ratio - 1) > total_tol:
        problems.append(f"total norm off by {100*(ratio-1):+.2f} % "
                        f"(tolerance {100*total_tol:.0f} %)")

    for c, cname in enumerate(("Ex", "Ey", "Ez")):
        if comp_s[c] <= 0 or comp_r[c] <= 0:
            continue
        d = comp_s[c] / tot_s - comp_r[c] / tot_r
        if abs(d) > share_tol:
            problems.append(f"global {cname} share off by {d:+.4f}")

    contrib = []
    for name, samp, r in rows:
        if r is None:
            continue
        sr = r["normE2"] / tot_r
        ss = samp["normE2"] / tot_s
        if abs(ss - sr) > share_tol:
            problems.append(f"{name} share off by {ss - sr:+.4f}")
        if abs(samp["area"] - r["area"]) > 1e-9:
            problems.append(f"{name} area mismatch")
        # share of the global error, so a large relative error on a small
        # region cannot be mistaken for the main problem
        d_abs = samp["normE2"] - r["normE2"]
        contrib.append((name, d_abs, d_abs / tot_r,
                        d_abs / max(abs(tot_s - tot_r), 1e-30)))
    return rows, tot_r, tot_s, problems, contrib


def main():
    if len(sys.argv) < 4:
        raise SystemExit("usage: compare_integrals.py <integrals.csv> "
                         "<points.csv> <n>")
    n = int(sys.argv[3])
    ref = {}
    with open(sys.argv[1], encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.strip().split(",")
            if len(p) != 6:
                raise SystemExit(f"bad row in reference: {line!r}")
            ref[MAP[p[0]]] = [float(v) for v in p[1:]]

    a = np.loadtxt(sys.argv[2], delimiter=",", skiprows=1)
    s = S.cells(n)
    if a.shape[0] != s["x"].size:
        raise SystemExit("point count does not match the sampling density")
    if np.max(np.abs(a[:, :2] - np.c_[s["x"], s["y"]])) > 1e-9:
        raise SystemExit("coordinates differ from the sampling")
    E = np.stack([a[:, 4] + 1j * a[:, 5], a[:, 6] + 1j * a[:, 7],
                  a[:, 8] + 1j * a[:, 9]], axis=1)
    w = a[:, 11]
    rows, tot_r, tot_s, bad, contrib = run_compare(ref, E, w, s["region"])

    print(f"{'region':8s} {'cells':>6s} {'ref E2':>12s} {'samp E2':>12s} "
          f"{'ratio':>7s} {'share_ref':>10s} {'share_samp':>10s} {'d_share':>8s}")
    for name, samp, r in rows:
        if r is None:
            print(f"{name:8s} {samp['cells']:6d} {'no reference':>12s}")
            continue
        ratio = samp["normE2"] / r["normE2"] if r["normE2"] > 0 else float("nan")
        sr, ss = r["normE2"] / tot_r, samp["normE2"] / tot_s
        print(f"{name:8s} {samp['cells']:6d} {r['normE2']:12.5e} "
              f"{samp['normE2']:12.5e} {ratio:7.4f} {sr:10.4f} {ss:10.4f} "
              f"{ss - sr:+8.4f}")

    print("\n  component shares (ref -> samp)")
    for c, cname in enumerate(("Ex", "Ey", "Ez")):
        cr = sum(x[2]["Ex2" if c == 0 else "Ey2" if c == 1 else "Ez2"]
                 for x in rows if x[2])
        cs = sum(x[1]["Ex2" if c == 0 else "Ey2" if c == 1 else "Ez2"]
                 for x in rows)
        print(f"    {cname}: {cr/tot_r:.4f} -> {cs/tot_s:.4f}  "
              f"({cs/tot_s - cr/tot_r:+.4f})")

    print("\n  error contribution by region")
    print(f"    {'region':8s} {'dE2':>12s} {'dE2/tot_ref':>12s} "
          f"{'pct_of_error':>13s}")
    for name, d_abs, d_rel, d_frac in sorted(contrib, key=lambda x: -abs(x[1])):
        print(f"    {name:8s} {d_abs:+12.4e} {d_rel:+12.4f} "
              f"{100*d_frac:+12.1f} %")

    print(f"\n  total E2  ref {tot_r:.6e}  samp {tot_s:.6e}  "
          f"ratio {tot_s/tot_r:.5f}  ({100*(tot_s/tot_r-1):+.2f} %)")
    for b in bad:
        print("  PROBLEM: " + b)
    print(f"\nRESULT {'PASS' if not bad else 'FAIL'}  "
          f"(tolerance: total 1 %, shares 0.005)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
