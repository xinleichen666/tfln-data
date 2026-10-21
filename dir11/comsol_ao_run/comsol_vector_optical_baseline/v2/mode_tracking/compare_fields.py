"""Region-by-region comparison of two complex mode fields.

Why region-wise: the exports contain duplicated coordinates at material
interfaces, where the field is discontinuous (measured spreads of tens to
hundreds of V/m).  Interpolating across such an interface mixes two different
values.  Here each geometric region is interpolated only from the samples that
lie inside it, and the interface band is left unassigned.

Regions are GEOMETRIC PROXIES for the material domains (ridge / left slab /
right slab / upper air / lower air).  They are not COMSOL domain identifiers.

Similarity (area weighted, conjugated, normalised):

    S = | sum E1* . E2 | / sqrt( sum |E1|^2 * sum |E2|^2 )

S is bounded by 1 (Cauchy-Schwarz).  A value above 1 + 1e-9 raises an error
instead of being clipped.  S is necessary but not sufficient for a branch
claim: adjacent-parameter continuity, polarisation and the competing candidate
must also be reported.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import LinearNDInterpolator

import read_fields

BOXES = {
    "ridge": (0.9675, 1.6125, 0.000, 0.500),
    "slabL": (0.000, 0.9675, 0.000, 0.250),
    "slabR": (1.6125, 2.580, 0.000, 0.250),
    "airTop": (-1.600, 4.180, 0.500, 1.600),
    "airBot": (-1.600, 4.180, -1.000, 0.000),
}
XMIN, XMAX = -1.6, 4.18
YMIN, YMAX = -1.0, 1.6
MARGIN = 0.008          # um, keeps samples away from interfaces
GRIDS = ((300, 160), (450, 240))
S_TOL = 1e-9
MIN_COVER = 0.80


def _dedupe(rec, policy):
    """Return x, y, E for a record under the requested duplicate policy."""
    if not rec.dup_groups:
        return rec.x, rec.y, rec.E
    if policy == "reject":
        raise read_fields.FieldDataError(
            f"{rec.path.name}: {len(rec.dup_groups)} duplicated coordinates "
            f"and policy is 'reject'")
    if policy == "first":
        drop = np.concatenate([g[1:] for g in rec.dup_groups])
        keep = np.setdiff1d(np.arange(rec.x.size), drop)
        return rec.x[keep], rec.y[keep], rec.E[keep]
    if policy == "average":
        uniq = np.unique(np.round(np.c_[rec.x, rec.y] / 1e-12),
                         axis=0) * 1e-12
        acc = np.zeros((uniq.shape[0], 3), dtype=complex)
        cnt = np.zeros(uniq.shape[0])
        key_all = np.round(np.c_[rec.x, rec.y] / 1e-12).astype(np.int64)
        key_uni = np.round(uniq / 1e-12).astype(np.int64)
        lut = {tuple(k): i for i, k in enumerate(key_uni)}
        for j, k in enumerate(key_all):
            i = lut[tuple(k)]
            acc[i] += rec.E[j]
            cnt[i] += 1
        acc /= cnt[:, None]
        return uniq[:, 0], uniq[:, 1], acc
    raise ValueError(f"unknown duplicate policy {policy!r}")


def _region_fields(x, y, E, box, nx, ny, margin=MARGIN):
    """Interpolate one field inside one box, using only that box's samples."""
    x0, x1, y0, y1 = box
    inside = ((x > x0 + margin) & (x < x1 - margin)
              & (y > y0 + margin) & (y < y1 - margin))
    if inside.sum() < 20:
        return None
    gx = np.linspace(x0 + margin, x1 - margin, nx)
    gy = np.linspace(y0 + margin, y1 - margin, ny)
    GX, GY = np.meshgrid(gx, gy)
    pts = np.c_[x[inside], y[inside]]
    out = np.empty((ny, nx, 3), dtype=complex)
    assigned = np.zeros((ny, nx), dtype=bool)
    for c in range(3):
        val = E[inside, c]
        fr = LinearNDInterpolator(pts, val.real, fill_value=np.nan)
        fi = LinearNDInterpolator(pts, val.imag, fill_value=np.nan)
        r, i = fr(GX, GY), fi(GX, GY)
        out[..., c] = np.where(np.isnan(r), 0.0, r) + \
            1j * np.where(np.isnan(i), 0.0, i)
        assigned |= ~np.isnan(r)
    return dict(GX=GX, GY=GY, E=out, assigned=assigned)


def similarity(A, B, assigned=None):
    """Bounded conjugated similarity over assigned points only."""
    if assigned is not None:
        A, B = A[assigned], B[assigned]
    a, b = A.ravel(), B.ravel()
    if a.size == 0:
        return 0.0
    num = abs(np.vdot(a, b))
    den = np.sqrt(np.vdot(a, a).real * np.vdot(b, b).real)
    if den == 0:
        return 0.0
    s = float(num / den)
    if s > 1 + S_TOL:
        raise RuntimeError(f"similarity {s:.12f} exceeds 1 beyond tolerance")
    return s


def compare(ref_path, cand_path, dup_policy="average", grids=GRIDS):
    ref = read_fields.read_export(ref_path)
    cand = read_fields.read_export(cand_path)
    rx, ry, rE = _dedupe(ref, dup_policy)
    cx, cy, cE = _dedupe(cand, dup_policy)

    per_grid = {}
    for nx, ny in grids:
        regions = {}
        total_assigned = total = 0
        for name, box in BOXES.items():
            a = _region_fields(rx, ry, rE, box, max(8, nx // 3), max(8, ny // 3))
            b = _region_fields(cx, cy, cE, box, max(8, nx // 3), max(8, ny // 3))
            if a is None or b is None:
                regions[name] = dict(S=None, cover=0.0)
                continue
            both = a["assigned"] & b["assigned"]
            cover = float(both.mean())
            regions[name] = dict(S=similarity(a["E"], b["E"], both),
                                 cover=cover)
            total_assigned += int(both.sum())
            total += int(both.size)
        per_grid[(nx, ny)] = dict(regions=regions,
                                  coverage=(total_assigned / total if total else 0.0))
    return dict(ref=ref, cand=cand, per_grid=per_grid,
                dup_policy=dup_policy)


def summarise(result, verbose=True):
    fine = result["per_grid"][GRIDS[-1]]
    coarse = result["per_grid"][GRIDS[0]]
    ss = [v["S"] for v in fine["regions"].values() if v["S"] is not None]
    ss_c = [v["S"] for v in coarse["regions"].values() if v["S"] is not None]
    cov = min(fine["coverage"], coarse["coverage"])
    if verbose:
        print(f"  dup policy          {result['dup_policy']}")
        print(f"  coverage            {cov:.2f}")
        for name, v in fine["regions"].items():
            s = "n/a" if v["S"] is None else f"{v['S']:.4f}"
            print(f"    {name:7s} S={s:6s} cover={v['cover']:.2f}")
    max_s = max(ss) if ss else 0.0
    sens = max(abs(x - y) for x, y in zip(sorted(ss), sorted(ss_c))) if ss else 0.0
    return dict(max_region_S=max_s, grid_sensitivity=sens, coverage=cov,
                regions={k: v["S"] for k, v in fine["regions"].items()})



if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        raise SystemExit("usage: compare_fields.py <ref.csv> <cand.csv> "
                         "[--policy average|first|reject]")
    policy = "average"
    if "--policy" in sys.argv:
        policy = sys.argv[sys.argv.index("--policy") + 1]
    res = compare(sys.argv[1], sys.argv[2], dup_policy=policy)
    print(f"reference {res['ref'].path.name}  neff={res['ref'].neff_tag}")
    print(f"candidate {res['cand'].path.name}  neff={res['cand'].neff_tag}")
    out = summarise(res)
    print(f"\n  max region S        {out['max_region_S']:.4f}")
    print(f"  grid sensitivity    {out['grid_sensitivity']:.4f}")
    print(f"  coverage            {out['coverage']:.2f}")
    if out["coverage"] < MIN_COVER:
        print(f"  WARNING: coverage below {MIN_COVER:.2f} - regions not "
              "comparable")
    print("\nnote: S is a per-region shape similarity; a branch claim also "
          "needs parameter continuity, polarisation and the competing "
          "candidate's score.")

