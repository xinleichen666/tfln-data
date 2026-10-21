"""Domain-aware comparison of two exported modes, with geometric guards.

Why this exists
---------------
A plain point-cloud triangulation of the air domain spans the holes left by the
solids: interpolating "air" inside the ridge or the slabs returns a finite but
entirely spurious field.  That was measured on the real exports -- air
interpolation returned 21 V/m at a point inside the ridge.

Fix: one global grid, and every grid point is first assigned to a geometric
region (regions.classify).  A region's field is then interpolated ONLY from
that region's own samples and ONLY at grid points that belong to it.

Similarity
----------
    S = | sum_d I_d | / sqrt( sum_d N1_d * sum_d N2_d )
    I_d = sum over region d of E1* . E2 * dA

Bounded by 1; a value above 1 + 1e-9 raises.  Regions absent from one model are
excluded from S.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import LinearNDInterpolator

import regions as R

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GRIDS = ((240, 150), (360, 225))
S_TOL = 1e-9


def read_dom_csv(path):
    p = Path(path)
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    hdr = next((l for l in lines if l.startswith("% X,")), None)
    if hdr is None:
        raise SystemExit(f"{p.name}: no header")
    names = [h.strip() for h in hdr[2:].split(",")]
    if len(names) < 10 or not names[2].startswith("dom"):
        raise SystemExit(f"{p.name}: third expression is not dom")
    a = np.loadtxt(lines, delimiter=",", comments="%", ndmin=2)
    if a.shape[1] != len(names):
        raise SystemExit(f"{p.name}: {a.shape[1]} columns vs {len(names)}")
    if not np.isfinite(a).all():
        raise SystemExit(f"{p.name}: non-finite values")
    E = np.stack([a[:, 4] + 1j * a[:, 5], a[:, 6] + 1j * a[:, 7],
                  a[:, 8] + 1j * a[:, 9]], axis=1)
    return dict(path=p, x=a[:, 0], y=a[:, 1], dom=a[:, 2].astype(int),
                normE=a[:, 3], E=E)


def grid_points(nx, ny):
    gx = np.linspace(R.XMIN, R.XMAX, nx)
    gy = np.linspace(R.YMIN, R.YMAX, ny)
    GX, GY = np.meshgrid(gx, gy)
    return GX, GY, (gx[1] - gx[0]) * (gy[1] - gy[0])


def field_on(rec, dom, GX, GY, mask):
    """Interpolate one domain's field, evaluated only where mask is true."""
    src = rec["dom"] == dom
    if src.sum() < 30 or mask.sum() == 0:
        return None
    pts = np.c_[rec["x"][src], rec["y"][src]]
    out = np.full((GX.shape[0], GX.shape[1], 3), np.nan + 0j)
    for c in range(3):
        fr = LinearNDInterpolator(pts, rec["E"][src, c].real, fill_value=np.nan)
        fi = LinearNDInterpolator(pts, rec["E"][src, c].imag, fill_value=np.nan)
        out[..., c] = fr(GX, GY) + 1j * fi(GX, GY)
    valid = ~np.isnan(out[..., 0]) & mask
    return out, valid


def label_geometry_check(rec, mapping, metal):
    """Per-sample agreement between the dom label and the geometry."""
    inv = {v: k for k, v in mapping.items()}
    expect = np.array([inv.get(int(d), "?") for d in rec["dom"]], dtype=object)
    geo = R.classify(rec["x"], rec["y"], metal)
    bad = expect != geo
    at_iface = bad & (np.abs(rec["y"]) < 1e-9)
    return dict(total=int(rec["x"].size), mismatch=int(bad.sum()),
                at_interface=int(at_iface.sum()))


def compare(path_a, path_b, map_a, map_b, metal_b, grids=GRIDS):
    a = read_dom_csv(path_a)
    b = read_dom_csv(path_b)
    doms_a, doms_b = set(a["dom"].tolist()), set(b["dom"].tolist())
    shared = [n for n in map_a if n in map_b
              and map_a[n] in doms_a and map_b[n] in doms_b]
    skipped = [n for n in map_a if n in map_b and n not in shared]
    out = {}
    for nx, ny in grids:
        GX, GY, dA = grid_points(nx, ny)
        geo = R.classify(GX.ravel(), GY.ravel(), metal_b).reshape(GX.shape)
        Itot, N1, N2 = 0j, 0.0, 0.0
        per = {}
        for name in shared:
            mask = geo == name
            if mask.sum() < 20:
                per[name] = dict(S=None, cover=0.0, area=0.0, points=int(mask.sum()))
                continue
            fa = field_on(a, map_a[name], GX, GY, mask)
            fb = field_on(b, map_b[name], GX, GY, mask)
            if fa is None or fb is None:
                per[name] = dict(S=None, cover=0.0, area=0.0,
                                 points=int(mask.sum()))
                continue
            EA, vA = fa
            EB, vB = fb
            ok = vA & vB
            cover = float(ok.sum() / mask.sum())
            if ok.sum() < 20:
                per[name] = dict(S=None, cover=cover, area=0.0,
                                 points=int(mask.sum()))
                continue
            ea, eb = EA[ok], EB[ok]
            I = np.sum(ea * np.conj(eb)) * dA
            n1 = float(np.sum(np.abs(ea) ** 2) * dA)
            n2 = float(np.sum(np.abs(eb) ** 2) * dA)
            if n1 <= 0 or n2 <= 0:
                per[name] = dict(S=None, cover=cover, area=0.0,
                                 points=int(mask.sum()))
                continue
            s = float(abs(I) / np.sqrt(n1 * n2))
            if s > 1 + S_TOL:
                raise RuntimeError(f"{name}: S={s:.12f} exceeds 1")
            per[name] = dict(S=s, cover=cover, area=float(ok.sum() * dA),
                             points=int(mask.sum()))
            Itot += I
            N1 += n1
            N2 += n2
        S = float(abs(Itot) / np.sqrt(N1 * N2)) if N1 > 0 and N2 > 0 else 0.0
        if S > 1 + S_TOL:
            raise RuntimeError(f"global S={S:.12f} exceeds 1")
        out[(nx, ny)] = dict(S=S, per=per, dA=dA)
    return dict(a=a, b=b, per_grid=out, shared=shared, skipped=skipped)


MAP_NOMETAL = {"air": 1, "slabL": 2, "ridge": 3, "slabR": 4}
MAP_METAL = {"air": 1, "slabL": 2, "metalL": 3, "ridge": 4, "slabR": 5,
             "metalR": 6}


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: compare_by_domain.py <no_metal.csv> "
                         "<with_metal.csv>")
    a = read_dom_csv(sys.argv[1])
    chk = label_geometry_check(a, MAP_NOMETAL, False)
    print(f"A {a['path'].name}: label/geometry mismatches "
          f"{chk['mismatch']}/{chk['total']} "
          f"(at the y=0 interface: {chk['at_interface']})")
    b = read_dom_csv(sys.argv[2])
    chk2 = label_geometry_check(b, MAP_METAL, True)
    print(f"B {b['path'].name}: label/geometry mismatches "
          f"{chk2['mismatch']}/{chk2['total']} "
          f"(at the y=0 interface: {chk2['at_interface']})")

    res = compare(sys.argv[1], sys.argv[2], MAP_NOMETAL, MAP_METAL, True)
    print(f"\n  shared regions: {res['shared']}")
    for (nx, ny), v in res["per_grid"].items():
        print(f"\n  grid {nx}x{ny}:  global S = {v['S']:.4f}")
        for name, d in v["per"].items():
            s = "n/a" if d["S"] is None else f"{d['S']:.4f}"
            print(f"    {name:7s} S={s:6s} cover={d['cover']:.2f} "
                  f"area={d['area']:.3f} um2")
    ss = [v["S"] for v in res["per_grid"].values()]
    print(f"\n  grid sensitivity of global S: {abs(ss[-1] - ss[0]):.4f}")


if __name__ == "__main__":
    sys.exit(main())

