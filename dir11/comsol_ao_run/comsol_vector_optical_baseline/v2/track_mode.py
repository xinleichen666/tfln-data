"""Track optical modes between two runs using complex field overlap.

COMSOL Data exports carry X, Y, normE, then real/imag of Ex, Ey, Ez; the
header also carries the mode's neff.  This script:

  * reads the header to locate columns and units (never by position),
  * resamples the complex E field of each mode onto a common grid,
  * computes the normalised complex overlap, both unconjugated (biorthogonal,
    appropriate for lossy modes) and conjugated (for reference),
  * reports the ridge power fraction and the transverse centroid.

A branch match requires a high overlap AND agreement of the ridge fraction and
centroid; neff alone is never used as the criterion.

Usage:
  python track_mode.py <reference.csv> <candidate1.csv> [candidate2.csv ...]
"""
import re
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import LinearNDInterpolator

RIDGE_X = (0.9675, 1.6125)
RIDGE_Y = (0.0, 0.5)
NX, NY = 360, 200
XMIN, XMAX = -1.6, 4.18
YMIN, YMAX = -1.0, 1.6


def read_mode(path):
    with path.open(encoding="utf-8", errors="replace") as fh:
        header = None
        for line in fh:
            if line.startswith("% X,"):
                header = line.lstrip("% ").strip()
                break
        if header is None:
            raise SystemExit(f"{path.name}: missing '% X,' header")
        names = [h.strip() for h in header.split(",")]
        idx = {}
        for i, n in enumerate(names):
            m = re.match(r"(real|imag)\(ewfd\.E([xyz])\)", n)
            if m:
                idx[(m.group(2), m.group(1))] = i
        if len(idx) != 6:
            raise SystemExit(f"{path.name}: expected 6 E columns, got {list(idx)}")
        unit = re.search(r"\(([^)]*)\)", names[3])
        unit = unit.group(1) if unit else "?"
        tag = re.search(r"@\s*([0-9.eE+-]+(?:[+-][0-9.eE+-]+i)?)", names[3])
        neff = tag.group(1) if tag else "?"
    with path.open(encoding="utf-8", errors="replace") as fh:
        a = np.loadtxt(fh, delimiter=",", comments="%")
    x, y = a[:, 0], a[:, 1]
    if np.abs(x).max() < 1e-3:      # exported in metres
        x, y = x * 1e6, y * 1e6
    E = np.stack([a[:, idx[(c, "real")]] + 1j * a[:, idx[(c, "imag")]]
                  for c in "xyz"], axis=1)
    return dict(path=path, x=x, y=y, E=E, neff=neff, unit=unit)


def resample(mode):
    gx = np.linspace(XMIN, XMAX, NX)
    gy = np.linspace(YMIN, YMAX, NY)
    GX, GY = np.meshgrid(gx, gy)
    pts = np.c_[mode["x"], mode["y"]]
    out = []
    for c in range(3):
        comp = mode["E"][:, c]
        out.append(LinearNDInterpolator(pts, comp.real, fill_value=0.0)(GX, GY)
                   + 1j * LinearNDInterpolator(pts, comp.imag,
                                               fill_value=0.0)(GX, GY))
    return GX, GY, np.stack(out, axis=-1)


def metrics(E, GX, GY):
    w = np.sum(np.abs(E) ** 2, axis=-1)
    tot = w.sum()
    ridge = ((GX >= RIDGE_X[0]) & (GX <= RIDGE_X[1])
             & (GY >= RIDGE_Y[0]) & (GY <= RIDGE_Y[1]))
    cx = float((GX * w).sum() / tot)
    cy = float((GY * w).sum() / tot)
    return float(w[ridge].sum() / tot), cx, cy


def overlap(A, B, conjugate=False):
    """Normalised overlap of two vector fields, optionally conjugated."""
    a = A.ravel()
    b = B.ravel()
    if conjugate:
        num = np.vdot(a, b)
        na = np.sqrt(np.vdot(a, a).real)
        nb = np.sqrt(np.vdot(b, b).real)
    else:
        num = np.sum(a * b)
        na = np.sqrt(abs(np.sum(a * a)))
        nb = np.sqrt(abs(np.sum(b * b)))
    if na == 0 or nb == 0:
        return 0.0
    return float(abs(num) / (na * nb))


def main():
    files = [Path(p) for p in sys.argv[1:]]
    if len(files) < 2:
        raise SystemExit("give a reference and at least one candidate")
    ref = read_mode(files[0])
    GX, GY, Er = resample(ref)
    r_ridge, r_cx, r_cy = metrics(Er, GX, GY)
    print(f"reference {files[0].name}  neff={ref['neff']}  "
          f"ridge={r_ridge:.4f}  centroid=({r_cx:.3f},{r_cy:.3f})")
    print(f"\n{'candidate':24s} {'neff':>10s} {'ridge':>7s} {'cx':>6s} "
          f"{'|ovl_unc|':>10s} {'|ovl_con|':>10s}  same branch?")
    best = None
    for f in files[1:]:
        cand = read_mode(f)
        _, _, Ec = resample(cand)
        c_ridge, c_cx, c_cy = metrics(Ec, GX, GY)
        unc = overlap(Er, Ec, conjugate=False)
        con = overlap(Er, Ec, conjugate=True)
        score = max(unc, con)
        same = (score > 0.8 and abs(c_ridge - r_ridge) < 0.15
                and abs(c_cx - r_cx) < 0.15)
        print(f"{f.name:24s} {cand['neff']:>10s} {c_ridge:7.4f} {c_cx:6.3f} "
              f"{unc:10.4f} {con:10.4f}  {'YES' if same else 'no'}")
        if best is None or score > best[0]:
            best = (score, f.name)
    print(f"\nbest overlap: {best[1]}  ({best[0]:.4f})")
    print("note: a match needs overlap > 0.8 AND ridge/centroid agreement; "
          "neff is not used as the criterion.")


if __name__ == "__main__":
    main()
