"""Where does the residual error live?  Region ratios and sign statistics.

If the remaining error were a few badly sampled cells, the per-region ratios
would be scattered.  If it is a distributed quadrature bias, every region is
low by a similar fraction.

Usage: python analyse_residual.py <cells.csv> <points.csv> <integrals.csv> <tag>
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cellspec as C                      # noqa: E402
import compare_integrals as CI            # noqa: E402


def main():
    cells = [tuple(float(v) for v in ln.split(","))
             for ln in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()[1:]
             if ln.strip()]
    a = np.loadtxt(sys.argv[2], delimiter=",", skiprows=1)
    ref = {}
    with open(sys.argv[3], encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.strip().split(",")
            ref[CI.MAP[p[0]]] = [float(v) for v in p[1:]]
    sp = C.arrays(cells)
    if a.shape[0] != len(cells):
        raise SystemExit("point count does not match the cell list")
    if np.max(np.abs(a[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
        raise SystemExit("coordinates differ from the cell list")
    E = np.stack([a[:, 4] + 1j * a[:, 5], a[:, 6] + 1j * a[:, 7],
                  a[:, 8] + 1j * a[:, 9]], axis=1)
    rows, tr, ts, bad, contrib = CI.run_compare(ref, E, sp["w"], sp["region"])
    print(f"{sys.argv[4]}: {len(cells)} cells, total ratio {ts/tr:.5f} "
          f"({100*(ts/tr-1):+.2f} %)")
    print(f"  {'region':8s} {'ratio':>8s} {'share_ref':>10s} {'d_share':>9s}")
    for name, samp, r in rows:
        if r is None:
            continue
        ratio = samp["normE2"] / r["normE2"]
        print(f"  {name:8s} {ratio:8.5f} {r['normE2']/tr:10.4f} "
              f"{samp['normE2']/ts - r['normE2']/tr:+9.4f}")
    rs = [s["normE2"] / r["normE2"] for _, s, r in rows if r]
    print(f"  ratio spread: {max(rs)-min(rs):.5f} "
          f"(small spread means a distributed bias)")
    print(f"  share problems: {len([b for b in bad if 'share' in b])}")


if __name__ == "__main__":
    sys.exit(main())
