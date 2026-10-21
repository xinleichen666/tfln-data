"""Analyse COMSOL field exports by column NAME, not by position.

COMSOL writes four leading columns for a 2D Data export (X, Y, then the
exported x and y), so the physical quantity is not at a fixed index.  This
script parses the header line to find the field column and its unit, and
refuses to run if it cannot.

Usage: python analyze_modes.py out/f_tag_m12.csv [more files]
"""
import re
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import LinearNDInterpolator

RIDGE = (0.9675, 1.6125, 0.0, 0.5)      # x0, x1, y0, y1 (um)
FILM_X = (0.0, 2.58)
SLAB_H = 0.25


def read_field(path):
    """Return (x, y, E, unit, neff_tag) with the field column found by header."""
    with path.open(encoding="utf-8", errors="replace") as fh:
        header = None
        for line in fh:
            if line.startswith("% X,"):
                header = line.lstrip("% ").strip()
                break
        if header is None:
            raise SystemExit(f"{path.name}: no '% X,' header line")
        names = [h.strip() for h in header.split(",")]
        idx = [i for i, n in enumerate(names) if "normE" in n]
        if len(idx) != 1:
            raise SystemExit(f"{path.name}: cannot locate normE column in {names}")
        unit = re.search(r"\(([^)]*)\)", names[idx[0]])
        unit = unit.group(1) if unit else "?"
        tag = re.search(r"@\s*([0-9.Ee+-]+)", names[idx[0]])
        tag = tag.group(1) if tag else "?"
    with path.open(encoding="utf-8", errors="replace") as fh:
        a = np.loadtxt(fh, delimiter=",", comments="%")
    x, y = a[:, 0], a[:, 1]
    if np.abs(x).max() > 1:      # export is in um already if max is small
        pass
    elif np.abs(x).max() < 1e-3:
        x, y = x * 1e6, y * 1e6
    return x, y, a[:, idx[0]], unit, tag


def analyse(path):
    x, y, E, unit, tag = read_field(path)
    if unit != "V/m":
        raise SystemExit(f"{path.name}: unexpected field unit '{unit}'")
    grid_x = np.linspace(-1.6, 4.18, 500)
    grid_y = np.linspace(-1.0, 1.6, 260)
    gx, gy = np.meshgrid(grid_x, grid_y)
    field = LinearNDInterpolator(np.c_[x, y], E, fill_value=0.0)(gx, gy)
    w = np.abs(field) ** 2

    ridge = ((gx >= RIDGE[0]) & (gx <= RIDGE[1])
             & (gy >= RIDGE[2]) & (gy <= RIDGE[3]))
    ln = (((gx >= FILM_X[0]) & (gx <= FILM_X[1])
           & (gy >= 0) & (gy <= SLAB_H)) | ridge)
    tot = w.sum()
    cx = float((gx * w).sum() / tot)
    cy = float((gy * w).sum() / tot)
    return dict(file=path.name, neff_tag=tag, unit=unit,
                ridge=float(w[ridge].sum() / tot),
                ln=float(w[ln].sum() / tot), cx=cx, cy=cy)


def main():
    files = [Path(p) for p in sys.argv[1:]]
    if not files:
        files = sorted(Path("out").glob("f_*.csv"))
    print(f"{'file':28s} {'neff(hdr)':>9s} {'ridge':>7s} {'LN':>7s} "
          f"{'cx':>6s} {'cy':>6s}  centre?")
    for p in files:
        r = analyse(p)
        centred = "YES" if abs(r["cx"] - 1.289) < 0.15 else "no"
        print(f"{r['file']:28s} {r['neff_tag']:>9s} {r['ridge']:7.3f} "
              f"{r['ln']:7.3f} {r['cx']:6.3f} {r['cy']:6.3f}  {centred}")


if __name__ == "__main__":
    main()
