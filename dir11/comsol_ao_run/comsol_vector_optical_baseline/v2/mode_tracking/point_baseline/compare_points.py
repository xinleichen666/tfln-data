"""Recompute the mode similarity from the validated point evaluations.

Unlike the earlier nodal-export based numbers, these points come from
`Interp` at full precision, the magnitudes were checked to machine precision,
and every point's domain id was verified against the geometry.

Points live on a uniform grid inside each region, so within a region every
point carries the same area weight; the global value combines the regions with
their own grid areas.

Regions that exist in only one model (the electrodes) are reported separately
and excluded from S, because they have no counterpart.

Usage:
  python compare_points.py <no_metal points.csv> <metal points.csv>
"""
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import regions as R  # noqa: E402

NAME = {1: "air", 2: "slabL", 3: "ridge", 4: "slabR", 5: "slabR", 6: "metalR"}
NAME_NOMETAL = {1: "air", 2: "slabL", 3: "ridge", 4: "slabR"}
NAME_METAL = {1: "air", 2: "slabL", 3: "metalL", 4: "ridge", 5: "slabR",
              6: "metalR"}


def load(path, table):
    a = np.loadtxt(path, delimiter=",", skiprows=1)
    E = np.stack([a[:, 4] + 1j * a[:, 5], a[:, 6] + 1j * a[:, 7],
                  a[:, 8] + 1j * a[:, 9]], axis=1)
    names = np.array([table[int(d)] for d in a[:, 2]], dtype=object)
    return dict(x=a[:, 0], y=a[:, 1], E=E, name=names)


def cell_area(x, y):
    ux = np.unique(np.round(x, 12))
    uy = np.unique(np.round(y, 12))
    dx = np.diff(ux).min() if ux.size > 1 else 0.0
    dy = np.diff(uy).min() if uy.size > 1 else 0.0
    return dx * dy


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: compare_points.py <nom.csv> <met.csv>")
    a = load(sys.argv[1], NAME_NOMETAL)
    b = load(sys.argv[2], NAME_METAL)

    key_a = {(round(x, 9), round(y, 9)): i
             for i, (x, y) in enumerate(zip(a["x"], a["y"]))}
    per, Itot, N1, N2 = {}, 0j, 0.0, 0.0
    for name in ("air", "slabL", "ridge", "slabR"):
        idx_a = [i for i, n in enumerate(a["name"]) if n == name]
        idx_b = [i for i, n in enumerate(b["name"]) if n == name]
        kb = {(round(b["x"][i], 9), round(b["y"][i], 9)): i for i in idx_b}
        pairs = [(i, kb[(round(a["x"][i], 9), round(a["y"][i], 9))])
                 for i in idx_a
                 if (round(a["x"][i], 9), round(a["y"][i], 9)) in kb]
        if len(pairs) < 4:
            per[name] = dict(S=None, n=len(pairs))
            continue
        ia, ib = zip(*pairs)
        ea, eb = a["E"][list(ia)], b["E"][list(ib)]
        dA = cell_area(a["x"][list(ia)], a["y"][list(ia)])
        I = np.sum(ea * np.conj(eb)) * dA
        n1 = float(np.sum(np.abs(ea) ** 2) * dA)
        n2 = float(np.sum(np.abs(eb) ** 2) * dA)
        s = float(abs(I) / np.sqrt(n1 * n2))
        if s > 1 + 1e-9:
            raise RuntimeError(f"{name}: S={s} exceeds 1")
        per[name] = dict(S=s, n=len(pairs), area=len(pairs) * dA)
        Itot += I
        N1 += n1
        N2 += n2

    print(f"A {Path(sys.argv[1]).name}  B {Path(sys.argv[2]).name}")
    for name, d in per.items():
        s = "n/a" if d["S"] is None else f"{d['S']:.4f}"
        print(f"  {name:7s} S={s:6s}  points={d['n']}")
    S = float(abs(Itot) / np.sqrt(N1 * N2)) if N1 > 0 else 0.0
    print(f"\n  global S (common regions) = {S:.4f}")
    print("  electrode regions excluded: they exist only in the metal model")
    print("\nnote: points are interior samples; interface behaviour is checked "
          "separately with the same-point magnitude test.")


if __name__ == "__main__":
    sys.exit(main())
