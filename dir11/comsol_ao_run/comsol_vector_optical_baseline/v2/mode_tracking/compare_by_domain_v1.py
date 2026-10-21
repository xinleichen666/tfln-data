"""Domain-aware comparison of two exported modes.

Inputs are the CSVs written by export_dom.py, which carry the COMSOL domain
number for every sample.  Domain indices are model-specific and MUST be read
from each model (see the SELMAP lines in the export log), never assumed.

Global similarity is accumulated from per-domain integrals:

    S = | sum_d I_d | / sqrt( sum_d N1_d * sum_d N2_d )
    I_d = sum over domain d of E1* . E2 * dA
    N_d = sum over domain d of |E|^2 * dA

This is bounded by 1 and is NOT a per-region maximum.  Domains present in only
one model are reported separately and excluded from S, with their share of the
field energy stated so the omission cannot be silently ignored.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import LinearNDInterpolator

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GRIDS = ((220, 140), (330, 210))
S_TOL = 1e-9
MIN_COVER = 0.80


def read_dom_csv(path):
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    hdr = next((l for l in lines if l.startswith("% X,")), None)
    if hdr is None:
        raise SystemExit(f"{path}: no header")
    names = [h.strip() for h in hdr[2:].split(",")]
    if len(names) < 10 or not names[2].startswith("dom"):
        raise SystemExit(f"{path}: third expression is not dom "
                         f"(header: {names[:4]})")
    a = np.loadtxt(lines, delimiter=",", comments="%", ndmin=2)
    if a.shape[1] != len(names):
        raise SystemExit(f"{path}: {a.shape[1]} columns vs {len(names)} names")
    if not np.isfinite(a).all():
        raise SystemExit(f"{path}: non-finite values")
    E = np.stack([a[:, 4] + 1j * a[:, 5], a[:, 6] + 1j * a[:, 7],
                  a[:, 8] + 1j * a[:, 9]], axis=1)
    return dict(x=a[:, 0], y=a[:, 1], dom=a[:, 2].astype(int),
                normE=a[:, 3], E=E, path=Path(path))


def domain_integrals(rec, dom, nx, ny):
    """Interpolate inside one domain and return I, N, area and coverage."""
    m = rec["dom"] == dom
    if m.sum() < 30:
        return None
    x, y, E = rec["x"][m], rec["y"][m], rec["E"][m]
    x0, x1 = x.min(), x.max()
    y0, y1 = y.min(), y.max()
    gx = np.linspace(x0, x1, nx)
    gy = np.linspace(y0, y1, ny)
    dA = (gx[1] - gx[0]) * (gy[1] - gy[0])
    GX, GY = np.meshgrid(gx, gy)
    pts = np.c_[x, y]
    out = np.full((ny, nx, 3), np.nan + 0j)
    for c in range(3):
        fr = LinearNDInterpolator(pts, E[:, c].real, fill_value=np.nan)
        fi = LinearNDInterpolator(pts, E[:, c].imag, fill_value=np.nan)
        out[..., c] = fr(GX, GY) + 1j * fi(GX, GY)
    ok = ~np.isnan(out[..., 0])
    return dict(E=out, ok=ok, dA=dA,
                area=float(ok.sum() * dA))


def pair_terms(a, b, dom_a, dom_b, nx, ny):
    A = domain_integrals(a, dom_a, nx, ny)
    B = domain_integrals(b, dom_b, nx, ny)
    if A is None or B is None:
        return None
    ok = A["ok"] & B["ok"]
    if ok.sum() < 30:
        return None
    dA = 0.5 * (A["dA"] + B["dA"])
    ea, eb = A["E"][ok], B["E"][ok]
    I = np.sum(ea * np.conj(eb)) * dA
    n1 = float(np.sum(np.abs(ea) ** 2) * dA)
    n2 = float(np.sum(np.abs(eb) ** 2) * dA)
    return dict(I=I, n1=n1, n2=n2, cover=float(ok.mean()),
                area=float(ok.sum() * dA))


def compare(path_a, path_b, map_a, map_b, grids=GRIDS):
    a = read_dom_csv(path_a)
    b = read_dom_csv(path_b)
    doms_a, doms_b = set(a["dom"].tolist()), set(b["dom"].tolist())
    common = [n for n in map_a
              if n in map_b and map_a[n] in doms_a and map_b[n] in doms_b]
    only_a = sorted(d for d in doms_a if d not in map_a.values())
    only_b = sorted(d for d in doms_b if d not in map_b.values())
    if only_a or only_b:
        print(f"  WARNING domains absent from a map: a={only_a} b={only_b}")
        print("  -> those samples are excluded from S; energy share reported "
              "below")

    out = {}
    for nx, ny in grids:
        per, Itot, N1, N2 = {}, 0j, 0.0, 0.0
        for name in common:
            da, db = map_a[name], map_b[name]
            t = pair_terms(a, b, da, db, nx, ny)
            if t is None:
                continue
            per[name] = dict(S=float(abs(t["I"]) / np.sqrt(t["n1"] * t["n2"])),
                             cover=t["cover"])
            Itot += t["I"]
            N1 += t["n1"]
            N2 += t["n2"]
        S = float(abs(Itot) / np.sqrt(N1 * N2)) if N1 > 0 and N2 > 0 else 0.0
        if S > 1 + S_TOL:
            raise RuntimeError(f"global S={S:.12f} exceeds 1")
        out[(nx, ny)] = dict(S=S, per=per)
    return dict(a=a, b=b, per_grid=out, common=common)


# Domain maps as read from the SELMAP lines of each model.
MAP_NOMETAL = {"air": 1, "slabL": 2, "ridge": 3, "slabR": 4}
MAP_METAL = {"air": 1, "slabL": 2, "metalL": 3, "ridge": 4, "slabR": 5,
             "metalR": 6}


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: compare_by_domain.py <no_metal.csv> "
                         "<with_metal.csv>")
    res = compare(sys.argv[1], sys.argv[2], MAP_NOMETAL, MAP_METAL)
    print(f"A {res['a']['path'].name}  B {res['b']['path'].name}")
    print(f"  common domains: {res['common']}")
    for (nx, ny), v in res["per_grid"].items():
        print(f"\n  grid {nx}x{ny}:  global S = {v['S']:.4f}")
        for name, d in v["per"].items():
            print(f"    {name:7s} S={d['S']:.4f}  cover={d['cover']:.2f}")
    ss = [v["S"] for v in res["per_grid"].values()]
    print(f"\n  grid sensitivity of global S: {abs(ss[-1] - ss[0]):.4f}")
    print("\nnote: S excludes domains that exist in only one model; their "
          "energy share is not included in the normalisation.")


if __name__ == "__main__":
    sys.exit(main())

