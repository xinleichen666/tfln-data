"""Photoelastic overlap of idt_3d_sus eigenmodes, using the Photo.java / Sweep.java conventions.

COMSOL axes: x = acoustic period direction = light propagation (ring tangential),
y = film normal (LN 0..500 nm), z = aperture = crystal z (optic axis, TE polarisation).
X-cut LN: crystal x || +y, crystal y || -x, crystal z || z.
TE (extraordinary) index change:
    d(1/n^2)_3 = p31*(S1+S2) + p33*S3,  S1 = eYY, S2 = eXX, S3 = eZZ.
Weights: x top-hat window (x > xa)*(x < xa+w), y: cos^2(kTE (y - h/2)) from the slab TE0 mode,
z: either uniform over the finger aperture or a Gaussian waveguide-width window (FWHM Wz) at z0.
TM branch (E || geometry y = crystal x, ordinary): d(1/n^2) = p11*S1 + p12*S2 + p13*S3, dn = -(no^3/2)*d(1/n^2).
Photoelastic constants as in photoelastic_p283/scripts/Photo.java (Weis & Gaylord / Andrushchak).
Run on a new export (same CSV layout and aperture_geometry.csv as data/):
    python ao_overlap.py --data <dir containing aperture_geometry.csv, modes_eigen_scan.csv, fields/> --tag p2p8326_wap10
The default entry point is the light-along-x study: net x-average of the index change at a
z-localised waveguide (Gaussian FWHM Wz), best z0 over the whole aperture and over the interior
(>= 2 um from each finger end).
Normalisation: unit LN strain energy; g in 1/sqrt(J). Fields are the exported real (phase 0) shapes.
"""
from __future__ import annotations
import csv, glob, sys
from pathlib import Path
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from scipy.optimize import brentq

import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("--data", default=str(Path(__file__).resolve().parents[1] / "data"))
_ap.add_argument("--tag", default="")
ARGS, _ = _ap.parse_known_args()
DATA = Path(ARGS.data)
CACHE = Path("/tmp/idt3d_sus_grid_cache") / (ARGS.tag or "default")


def _geom():
    g = {r["parameter"]: float(r["value"]) for r in csv.DictReader(open(DATA / "aperture_geometry.csv"))
         if r["value"].replace(".", "", 1).replace("e", "", 1).replace("-", "", 1).isdigit()}
    return g


_G = _geom()
P = _G["period_p"] * 1e-6
H_LN = _G.get("LN_thickness_hLn", 500) * 1e-9
Z0 = _G["aperture_start_z0"] * 1e-6
Z1 = Z0 + _G["aperture_length_Wap"] * 1e-6
ZW = _G["stack_width_Wstack"] * 1e-6
PE = {"p11": -0.026, "p12": 0.090, "p13": 0.133, "p31": 0.179, "p33": 0.071}
NE, NO, LAM = 2.138, 2.211, 1.55e-6


def kte_slab(n=NE, h=H_LN, lam=LAM, n_clad=1.0):
    k0 = 2 * np.pi / lam
    f = lambda k: k * np.tan(k * h / 2) - np.sqrt((n**2 - n_clad**2) * k0**2 - k**2)
    kmax = k0 * np.sqrt(n**2 - n_clad**2) * 0.9999
    return brentq(f, 1e-3 * k0, min(kmax, np.pi / h * 0.9999))


KTE = kte_slab()
KTM = kte_slab(n=NO)


def grid():
    x = np.linspace(0, P, 130, endpoint=False) + P / 260
    y = np.linspace(0.5 * H_LN / 25, H_LN - 0.5 * H_LN / 25, 25)
    z = np.linspace(0, ZW, int(round(ZW / 0.1e-6)) + 1)
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


def analyse(path, wx_list, wz_list, pol="TE"):
    x, y, z = grid()
    g = mode_grids(path)
    dx, dy, dz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
    U = np.nansum(g["W"]) * dx * dy * dz
    if pol == "TE":
        pe = -(NE**3 / 2) * (PE["p33"] * g["zz"] + PE["p31"] * (g["xx"] + g["yy"]))
        kk = KTE
    else:
        pe = -(NO**3 / 2) * (PE["p11"] * g["yy"] + PE["p12"] * g["xx"] + PE["p13"] * g["zz"])
        kk = KTM
    pe = np.nan_to_num(pe)
    wy = np.cos(kk * (y - H_LN / 2)) ** 2
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


def pe_and_wy(g, y, pol):
    if pol == "TE":
        pe = -(NE**3 / 2) * (PE["p33"] * g["zz"] + PE["p31"] * (g["xx"] + g["yy"]))
        kk = KTE
    else:
        pe = -(NO**3 / 2) * (PE["p11"] * g["yy"] + PE["p12"] * g["xx"] + PE["p13"] * g["zz"])
        kk = KTM
    wy = np.cos(kk * (y - H_LN / 2)) ** 2
    return np.nan_to_num(pe), wy / wy.sum()


def lightx_study(path, pol, wz_list, margin):
    """Light along x: net x-average of d(n) at a z-localised waveguide, normalised to unit LN strain energy."""
    x, y, z = grid()
    g = mode_grids(path)
    dx, dy, dz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
    U = np.nansum(g["W"]) * dx * dy * dz
    pe, wy = pe_and_wy(g, y, pol)
    line = np.einsum("xy,xyz->z", np.full((len(x), len(y)), 1 / len(x)) * wy[None, :], pe)
    zin = (z >= Z0) & (z <= Z1)
    out = {}
    for wz in wz_list:
        s = wz / 2.355
        res = []
        for z0 in z[zin]:
            Wz = np.exp(-0.5 * ((z - z0) / s) ** 2) * zin
            Wz /= Wz.sum() * dz
            res.append((abs(line @ Wz * dz) / np.sqrt(U), z0))
        res = np.array(res)
        ib = res[:, 0].argmax()
        inner = (res[:, 1] >= Z0 + margin) & (res[:, 1] <= Z1 - margin)
        ii = np.where(inner)[0][res[inner, 0].argmax()] if inner.any() else ib
        out[wz] = dict(g_all=res[ib, 0], z0_all=res[ib, 1], g_in=res[ii, 0], z0_in=res[ii, 1])
    return out


def main_lightx():
    summ = list(csv.DictReader(open(DATA / "modes_eigen_scan.csv")))
    files = sorted(glob.glob(str(DATA / "fields" / "*.csv")))
    wz_list = [0.5e-6, 1.0e-6, 1.5e-6]
    margin = 2e-6
    rows = []
    for r, fp in zip(summ, files):
        for pol in ("TE", "TM"):
            for wz, v in lightx_study(fp, pol, wz_list, margin).items():
                rows.append(dict(pol=pol, mode=r["mode_index"], f_GHz=r["freq_GHz"], v2=r["frac_v2_LN"],
                                 u2=r["frac_u2_LN"], w2=r["frac_w2_LN"], Wz_um=round(wz * 1e6, 2),
                                 g_all=f"{v['g_all']:.4e}", z0_all_um=f"{v['z0_all']*1e6:.2f}",
                                 g_interior=f"{v['g_in']:.4e}", z0_interior_um=f"{v['z0_in']*1e6:.2f}"))
    out = DATA.parent / "analysis" / f"ao_overlap_lightx{('_' + ARGS.tag) if ARGS.tag else ''}.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("p =", P * 1e6, "um, aperture", (Z1 - Z0) * 1e6, "um, margin 2 um; wrote", out)


def main():
    summ = list(csv.DictReader(open(DATA / "modes_eigen_scan.csv")))
    files = sorted(glob.glob(str(DATA / "fields" / "*.csv")))
    wx_list = [0.5e-6, P / 2, P]
    wz_list = [0.5e-6, 1.0e-6]
    rows = []
    for r, fp in zip(summ, files):
      for pol in ("TE", "TM"):
        for (wx, zmode), (gv, xa, z0) in analyse(fp, wx_list, wz_list, pol).items():
            rows.append(dict(pol=pol, mode=r["mode_index"], f_GHz=r["freq_GHz"], v2=r["frac_v2_LN"], u2=r["frac_u2_LN"],
                             w2=r["frac_w2_LN"], wx_um=round(wx * 1e6, 3), z_window=zmode,
                             g_best=f"{gv:.4e}", xa_best_um=f"{xa*1e6:.3f}", z0_best_um=f"{z0*1e6:.2f}"))
      print("done mode", r["mode_index"], file=sys.stderr)
    out = DATA.parent / "analysis" / "ao_overlap_summary.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("kTE =", KTE, "1/m;  wrote", out)


if __name__ == "__main__":
    main_lightx()
