"""Photoelastic overlap of idt_3d_sus eigenmodes with an unetched-film TE optical window.

Geometry (COMSOL axes): x = acoustic period direction, y = film normal, z = aperture.
Light runs along z through the aperture, polarised along x. Optical intensity is a
top-hat window of width Wx in x (periodic) times a Gaussian in y centred on the film
mid-plane. The coherent phase factor is the z-integral of the photoelastic index change.

Crystal orientation is NOT in the repo (only in the .mph), so three orientation cases are
reported:
  A  x-polarisation is extraordinary:   d(1/n^2) = p33*Sxx + p31*(Syy+Szz)
  B  x-polarisation is ordinary:        d(1/n^2) = p11*Sxx + p12*Syy + p13*Szz   (p14 term dropped)
  S  scalar proxy:                      d(1/n^2) = Sxx
g is normalised to unit LN strain energy: g = |int dz <pe:S>_window| / sqrt(U_LN) in 1/sqrt(J).
"""
from __future__ import annotations
import csv, glob, sys
from pathlib import Path
import numpy as np
from scipy.interpolate import LinearNDInterpolator

DATA = Path(__file__).resolve().parents[1] / "data"
P = 2.58e-6
H_LN = 500e-9
Z0, Z1 = 2e-6, 12e-6
SIGMA_Y = 100e-9
PE = {"p11": 0.036, "p12": 0.072, "p13": 0.092, "p31": 0.178, "p33": 0.088}  # Weis & Gaylord / Dixon

CASES = {
    "A": lambda S: PE["p33"] * S["xx"] + PE["p31"] * (S["yy"] + S["zz"]),
    "B": lambda S: PE["p11"] * S["xx"] + PE["p12"] * S["yy"] + PE["p13"] * S["zz"],
    "S": lambda S: S["xx"],
}


def load_mode(path):
    d = np.genfromtxt(path, delimiter=",", names=True)
    pts = np.c_[d["x_m"], d["y_m"], d["z_m"]]
    ln = d["y_m"] <= H_LN + 1e-12
    cols = {"xx": "eXX", "yy": "eYY", "zz": "eZZ", "W": "strain_energy_density_J_m3"}
    out = {}
    for k, c in cols.items():
        out[k] = LinearNDInterpolator(pts[ln], d[c][ln])
    return out


def grid():
    x = np.linspace(0, P, 130, endpoint=False) + P / 260
    y = np.linspace(0.5 * H_LN / 25, H_LN - 0.5 * H_LN / 25, 25)
    z = np.linspace(0, 14e-6, 141)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    return x, y, z, X, Y, Z


def window(x, y, x0, wx):
    dx = (x - x0 + P / 2) % P - P / 2
    wxv = (np.abs(dx) <= wx / 2).astype(float)
    wyv = np.exp(-0.5 * ((y - H_LN / 2) / SIGMA_Y) ** 2)
    G = wxv[:, None] * wyv[None, :]
    return G / G.sum()


def analyse(path, wx_list=(0.25e-6, 0.5e-6, 1.0e-6, P / 2), x0_scan=None):
    x, y, z, X, Y, Z = grid()
    f = load_mode(path)
    S = {k: f[k](X, Y, Z) for k in ("xx", "yy", "zz")}
    W = f["W"](X, Y, Z)
    dx, dy, dz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
    U = np.nansum(W) * dx * dy * dz
    zin = (z >= Z0) & (z <= Z1)
    res = {}
    if x0_scan is None:
        x0_scan = np.linspace(0, P, 65)
    for cname, fn in CASES.items():
        pe = np.nan_to_num(fn(S))
        for wx in wx_list:
            best = (0, 0, 0)
            for x0 in x0_scan:
                G = window(x, y, x0, wx)
                line = np.einsum("xy,xyz->z", G, pe)
                g = abs(np.trapezoid(line[zin], z[zin])) / np.sqrt(U)
                gabs = np.trapezoid(np.abs(line[zin]), z[zin]) / np.sqrt(U)
                if g > best[0]:
                    best = (g, x0, g / gabs if gabs else 0)
            G = window(x, y, P - wx / 2, wx)
            line = np.einsum("xy,xyz->z", G, pe)
            g_right = abs(np.trapezoid(line[zin], z[zin])) / np.sqrt(U)
            res[(cname, wx)] = dict(g_best=best[0], x0_best=best[1], z_coh=best[2], g_right=g_right)
    return res, U


def main():
    summ = list(csv.DictReader(open(DATA / "modes_eigen_scan.csv")))
    files = sorted(glob.glob(str(DATA / "fields" / "*.csv")))
    out = DATA.parent / "analysis" / "ao_overlap_summary.csv"
    rows = []
    for r, fpath in zip(summ, files):
        res, U = analyse(fpath)
        for (c, wx), v in res.items():
            rows.append(dict(mode=r["mode_index"], f_GHz=r["freq_GHz"], v2=r["frac_v2_LN"], u2=r["frac_u2_LN"],
                             w2=r["frac_w2_LN"], case=c, Wx_um=round(wx * 1e6, 3),
                             g_best=f"{v['g_best']:.4e}", x0_best_um=f"{v['x0_best']*1e6:.3f}",
                             z_coherence=f"{v['z_coh']:.3f}", g_right_end=f"{v['g_right']:.4e}"))
        print("done mode", r["mode_index"], file=sys.stderr)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("wrote", out)


if __name__ == "__main__":
    main()
