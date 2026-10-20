"""Photoelastic overlap of idt_3d_sus eigenmodes, using the Photo.java / Sweep.java conventions.

COMSOL axes: x = acoustic period direction = light propagation (ring tangential),
y = film normal (LN 0..500 nm), z = aperture = crystal z (optic axis, TE polarisation).
X-cut LN: crystal x || +y, crystal y || -x, crystal z || z.
TE (extraordinary) index change:
    d(1/n^2)_3 = p31*(S1+S2) + p33*S3,  S1 = eYY, S2 = eXX, S3 = eZZ.
Weights: x top-hat window (x > xa)*(x < xa+w), y: cos^2(kTE (y - h/2)) from the slab TE0 mode,
z: either uniform over the finger aperture or a Gaussian waveguide-width window (FWHM Wz) at z0.
Normalisation: unit LN strain energy; g in 1/sqrt(J). Fields are the exported real (phase 0) shapes.
"""
from __future__ import annotations
import csv, glob, sys
from pathlib import Path
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from scipy.optimize import brentq

DATA = Path(__file__).resolve().parents[1] / "data"
CACHE = Path("/tmp/idt3d_sus_grid_cache")
P = 2.58e-6
H_LN = 500e-9
Z0, Z1 = 2e-6, 12e-6
PE = {"p31": 0.178, "p33": 0.088}
NE, LAM = 2.138, 1.55e-6


def kte_slab(n=NE, h=H_LN, lam=LAM, n_clad=1.0):
    k0 = 2 * np.pi / lam
    f = lambda k: k * np.tan(k * h / 2) - np.sqrt((n**2 - n_clad**2) * k0**2 - k**2)
    kmax = k0 * np.sqrt(n**2 - n_clad**2) * 0.9999
    return brentq(f, 1e-3 * k0, min(kmax, np.pi / h * 0.9999))


KTE = kte_slab()


def grid():
    x = np.linspace(0, P, 130, endpoint=False) + P / 260
    y = np.linspace(0.5 * H_LN / 25, H_LN - 0.5 * H_LN / 25, 25)
    z = np.linspace(0, 14e-6, 141)
    return x, y, z


def mode_grids(path):
    CACHE.mkdir(exist_ok=True)
    c = CACHE / (Path(path).stem + ".npz")
    if c.exists():
        d = np.load(c)
        return {k: d[k] for k in d.files}
    d = np.genfromtxt(path, delimiter=",", names=True)
    ln = d["y_m"] <= H_LN + 1e-12
    pts = np.c_[d["x_m"], d["y_m"], d["z_m"]][ln]
    x, y, z = grid()
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    out = {}
    for k, col in {"xx": "eXX", "yy": "eYY", "zz": "eZZ", "W": "strain_energy_density_J_m3"}.items():
        out[k] = LinearNDInterpolator(pts, d[col][ln])(X, Y, Z)
    np.savez(c, **out)
    return out


def analyse(path, wx_list, wz_list):
    x, y, z = grid()
    g = mode_grids(path)
    dx, dy, dz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
    U = np.nansum(g["W"]) * dx * dy * dz
    pe = np.nan_to_num(PE["p33"] * g["zz"] + PE["p31"] * (g["xx"] + g["yy"]))
    wy = np.cos(KTE * (y - H_LN / 2)) ** 2
    wy /= wy.sum()
    pey = np.einsum("y,xyz->xz", wy, pe)
    zin = (z >= Z0) & (z <= Z1)
    res = {}
    for wx in wx_list:
        xas = np.linspace(0, P - wx, 33)
        wins = np.array([((x > xa) & (x < xa + wx)).astype(float) for xa in xas])
        wins /= wins.sum(1, keepdims=True)
        lines = np.einsum("ax,xz->az", wins, pey)
        Wu = zin / (zin.sum() * dz)
        gu = np.abs(lines @ Wu * dz) / np.sqrt(U)
        i = gu.argmax()
        res[(wx, "uniform")] = (gu[i], xas[i], z[zin].mean())
        for wz in wz_list:
            s = wz / 2.355
            best = (0, 0, 0)
            for z0 in z[zin]:
                Wz = np.exp(-0.5 * ((z - z0) / s) ** 2) * zin
                Wz /= Wz.sum() * dz
                gl = np.abs(lines @ Wz * dz) / np.sqrt(U)
                j = gl.argmax()
                if gl[j] > best[0]:
                    best = (gl[j], xas[j], z0)
            res[(wx, f"Wz={wz*1e6:.1f}um")] = best
    return res


def main():
    summ = list(csv.DictReader(open(DATA / "modes_eigen_scan.csv")))
    files = sorted(glob.glob(str(DATA / "fields" / "*.csv")))
    wx_list = [0.5e-6, 0.95e-6, 1.3e-6, P / 2]
    wz_list = [0.5e-6, 1.0e-6, 2.0e-6]
    rows = []
    for r, fp in zip(summ, files):
        for (wx, zmode), (gv, xa, z0) in analyse(fp, wx_list, wz_list).items():
            rows.append(dict(mode=r["mode_index"], f_GHz=r["freq_GHz"], v2=r["frac_v2_LN"], u2=r["frac_u2_LN"],
                             w2=r["frac_w2_LN"], wx_um=round(wx * 1e6, 3), z_window=zmode,
                             g_best=f"{gv:.4e}", xa_best_um=f"{xa*1e6:.3f}", z0_best_um=f"{z0*1e6:.2f}"))
        print("done mode", r["mode_index"], file=sys.stderr)
    out = DATA.parent / "analysis" / "ao_overlap_summary.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("kTE =", KTE, "1/m;  wrote", out)


if __name__ == "__main__":
    main()
