"""Bounded field-shape similarity between two modes, with self-tests.

Definition (conjugated, area-weighted, normalised):

    S = | integral E1* . E2 dA | / sqrt( integral |E1|^2 dA * integral |E2|^2 dA )

S lies in [0, 1] by Cauchy-Schwarz and is invariant to a global complex phase
and to a nonzero real amplitude scaling of either field.

This is a *field-shape similarity*, not a certified biorthogonal projection of a
non-Hermitian eigenproblem.  A high S is necessary but not sufficient to declare
two modes the same branch; ridge fraction, centroid and polarisation must agree
as well, and the value must be stable under grid refinement.

Interface handling: the COMSOL exports contain duplicated coordinates at
material interfaces where the field is discontinuous (measured spreads of tens
to hundreds of V/m).  Duplicates are averaged before resampling and the effect
of that averaging is reported, because a plain point cloud would double-count
interface nodes.

Usage:
  python field_compare.py --selftest
  python field_compare.py <ref.csv> <cand.csv> [--no-dedupe]
"""
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import LinearNDInterpolator

import modeio

GRIDS = ((240, 130), (360, 200))
BOXES = {
    "ridge": (0.9675, 1.6125, 0.0, 0.5),
    "slabL": (-0.001, 0.9675, 0.0, 0.25),
    "slabR": (1.6125, 2.581, 0.0, 0.25),
    "airTop": (-1.6, 4.18, 0.5, 1.6),
    "airBot": (-1.6, 4.18, -1.0, 0.0),
}
XMIN, XMAX = -1.6, 4.18
YMIN, YMAX = -1.0, 1.6


def dedupe(x, y, E, tol=1e-12):
    """Average field values that share a coordinate; report how many merged."""
    key = np.round(np.c_[x, y] / tol).astype(np.int64)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    if uniq.shape[0] == key.shape[0]:
        return x, y, E, 0
    acc = np.zeros((uniq.shape[0], E.shape[1]), dtype=complex)
    cnt = np.zeros(uniq.shape[0])
    np.add.at(acc, inv, E)
    np.add.at(cnt, inv, 1.0)
    acc /= cnt[:, None]
    return uniq[:, 0] * tol, uniq[:, 1] * tol, acc, int(key.shape[0] - uniq.shape[0])


def sample(mode, nx, ny, dedupe_points=True):
    x, y, E = mode["x"], mode["y"], mode["E"]
    merged = 0
    if dedupe_points:
        x, y, E, merged = dedupe(x, y, E)
    gx = np.linspace(XMIN, XMAX, nx)
    gy = np.linspace(YMIN, YMAX, ny)
    GX, GY = np.meshgrid(gx, gy)
    pts = np.c_[x, y]
    out = np.empty((ny, nx, 3), dtype=complex)
    for c in range(3):
        re = LinearNDInterpolator(pts, E[:, c].real, fill_value=0.0)(GX, GY)
        im = LinearNDInterpolator(pts, E[:, c].imag, fill_value=0.0)(GX, GY)
        out[..., c] = re + 1j * im
    return GX, GY, out, merged


def similarity(A, B, mask=None):
    if mask is not None:
        A, B = A[mask], B[mask]
    a, b = A.ravel(), B.ravel()
    num = abs(np.vdot(a, b))
    den = np.sqrt(np.vdot(a, a).real * np.vdot(b, b).real)
    if den == 0:
        return 0.0
    return float(num / den)


def box_mask(GX, GY, box):
    x0, x1, y0, y1 = box
    return (GX >= x0) & (GX <= x1) & (GY >= y0) & (GY <= y1)


def compare(ref_path, cand_path, dedupe_points=True, verbose=True):
    ref = modeio.read_mode(ref_path)
    cand = modeio.read_mode(cand_path)
    results = {}
    for nx, ny in GRIDS:
        GX, GY, Er, m1 = sample(ref, nx, ny, dedupe_points)
        _, _, Ec, m2 = sample(cand, nx, ny, dedupe_points)
        s = similarity(Er, Ec)
        per_box = {k: similarity(Er, Ec, box_mask(GX, GY, b))
                   for k, b in BOXES.items()}
        results[(nx, ny)] = dict(S=s, boxes=per_box, merged=(m1, m2))
        if verbose:
            print(f"  grid {nx}x{ny}: S = {s:.4f}"
                  f"   (merged interface points {m1}/{m2})")
    finest = results[GRIDS[-1]]
    coarse = results[GRIDS[0]]
    return dict(neff_ref=ref["neff"], neff_cand=cand["neff"],
                S=finest["S"], S_coarse=coarse["S"],
                boxes=finest["boxes"],
                grid_sensitivity=abs(finest["S"] - coarse["S"]))


def selftest():
    rng = np.random.default_rng(1)
    a = rng.standard_normal(5000) + 1j * rng.standard_normal(5000)
    b = rng.standard_normal(5000) + 1j * rng.standard_normal(5000)
    checks = []

    checks.append(("self similarity = 1", abs(similarity(a, a) - 1) < 1e-12,
                   f"{similarity(a, a):.15f}"))
    ph = np.exp(1j * 0.837)
    checks.append(("global phase invariance",
                   abs(similarity(a * ph, a) - 1) < 1e-12,
                   f"{similarity(a * ph, a):.15f}"))
    checks.append(("amplitude invariance",
                   abs(similarity(3.7 * a, -0.02 * a) - 1) < 1e-12,
                   f"{similarity(3.7 * a, -0.02 * a):.15f}"))

    # orthogonal construction: b with the a-component removed
    proj = np.vdot(a, b) / np.vdot(a, a)
    orth = b - proj * a
    checks.append(("orthogonal fields -> 0", similarity(a, orth) < 1e-10,
                   f"{similarity(a, orth):.3e}"))

    vals = [similarity(a, b), similarity(a, a), similarity(a, orth),
            similarity(a, a * ph)]
    checks.append(("bounded in [0, 1]",
                   all(-1e-12 <= v <= 1 + 1e-12 for v in vals),
                   f"{min(vals):.3f}..{max(vals):.3f}"))

    # deliberately broken comparison: no normalisation would exceed 1
    raw = abs(np.vdot(a, 3 * a)) / 1.0
    checks.append(("unnormalised value exceeds 1 (control)",
                   raw > 1, f"{raw:.1f}"))

    ok = all(c[1] for c in checks)
    for name, passed, detail in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name:38s} {detail}")
    print("\nSELFTEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        raise SystemExit("usage: --selftest | <ref.csv> <cand.csv> [--no-dedupe]")
    dd = "--no-dedupe" not in sys.argv
    print(f"reference {Path(args[0]).name}")
    print(f"candidate {Path(args[1]).name}  (dedupe={dd})")
    r = compare(args[0], args[1], dedupe_points=dd)
    print(f"\n  neff ref {r['neff_ref']}   cand {r['neff_cand']}")
    print(f"  S (fine grid)      {r['S']:.4f}")
    print(f"  S (coarse grid)    {r['S_coarse']:.4f}")
    print(f"  grid sensitivity   {r['grid_sensitivity']:.4f}")
    print("  per-domain S:")
    for k, v in r["boxes"].items():
        print(f"    {k:7s} {v:.4f}")
    print("\nnote: S is a shape similarity; a branch claim also needs ridge "
          "fraction, centroid, polarisation and grid stability.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

