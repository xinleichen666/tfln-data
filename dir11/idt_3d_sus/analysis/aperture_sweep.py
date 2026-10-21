"""Analyze fresh COMSOL eigenmode exports across suspended IDT aperture lengths.

Exports are the COMSOL Data CSVs emitted by D:\\comsol_ao_run\\idt_3d_sus\\aperture_sweep\\ApertureRun.java.
The calculation follows ao_overlap.py: x-period averaged photoelastic index perturbation,
slab TE0/TM0 y weighting, and a Gaussian optical waveguide window along z.
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from scipy.optimize import brentq

P = 2.58e-6
H_LN = 500e-9
Z0 = 2e-6
Z_MARGIN = 2e-6
EDGE_BAND = 1e-6
PE = {"p11": -0.026, "p12": 0.090, "p13": 0.133, "p31": 0.179, "p33": 0.071}
NE, NO, LAM = 2.138, 2.211, 1.55e-6


def kte_slab(n: float) -> float:
    k0 = 2 * np.pi / LAM
    f = lambda k: k * np.tan(k * H_LN / 2) - np.sqrt((n**2 - 1.0) * k0**2 - k**2)
    kmax = k0 * np.sqrt(n**2 - 1.0) * 0.9999
    return brentq(f, 1e-3 * k0, min(kmax, np.pi / H_LN * 0.9999))

K = {"TE": kte_slab(NE), "TM": kte_slab(NO)}


def read_summary(path: Path) -> np.ndarray:
    return np.loadtxt(path, delimiter=",", comments="%", ndmin=2, encoding="utf-8")


def regular_grid(wap_um: float):
    wap = wap_um * 1e-6
    wstack = wap + 4e-6
    x = np.linspace(0, P, 130, endpoint=False) + P / 260
    y = np.linspace(0.5 * H_LN / 25, H_LN - 0.5 * H_LN / 25, 25)
    z = np.linspace(0, wstack, int(round(wstack / 0.1e-6)) + 1)
    return x, y, z


def interpolate_fields(path: Path, wap_um: float):
    # COMSOL Data export has three node-index columns before x,y,z and the four fields.
    raw = np.loadtxt(path, delimiter=",", comments="%", ndmin=2, encoding="utf-8")
    yraw = raw[:, 4]
    ln = yraw <= H_LN + 1e-12
    pts = raw[ln, 3:6]
    x, y, z = regular_grid(wap_um)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    # Interpolate all four fields together so SciPy builds only one Delaunay triangulation.
    values = LinearNDInterpolator(pts, raw[ln, 6:10])(X, Y, Z)
    out = {key: values[..., j] for j, key in enumerate(("xx", "yy", "zz", "W"))}
    return x, y, z, out


def pe_and_y_weight(g, y, pol):
    if pol == "TE":
        pe = -(NE**3 / 2) * (PE["p33"] * g["zz"] + PE["p31"] * (g["xx"] + g["yy"]))
        k = K["TE"]
    else:
        pe = -(NO**3 / 2) * (PE["p11"] * g["yy"] + PE["p12"] * g["xx"] + PE["p13"] * g["zz"])
        k = K["TM"]
    wy = np.cos(k * (y - H_LN / 2)) ** 2
    return np.nan_to_num(pe), wy / wy.sum()


def coupling_profile(x, y, z, g, pol, fwhm_um):
    dx, dy, dz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
    U = np.nansum(g["W"]) * dx * dy * dz
    pe, wy = pe_and_y_weight(g, y, pol)
    # A waveguide propagating along x averages over one acoustic period in x.
    line = np.einsum("xy,xyz->z", np.full((len(x), len(y)), 1 / len(x)) * wy[None, :], pe)
    mask_ap = (z >= Z0) & (z <= Z0 + (z[-1] - 4e-6))
    z_ap = z[mask_ap]
    values = []
    sigma = fwhm_um * 1e-6 / 2.355
    for zc in z_ap:
        wz = np.exp(-0.5 * ((z - zc) / sigma) ** 2) * mask_ap
        norm = wz.sum() * dz
        if norm <= 0:
            values.append(np.nan)
        else:
            values.append(abs(line @ wz * dz) / norm / np.sqrt(U))
    return z_ap, np.asarray(values), U


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exports", type=Path, required=True, help="Folder containing Wap_*um_mode_*.csv and summary CSVs")
    ap.add_argument("--output", type=Path, required=True, help="Output folder for the analysis CSVs")
    ap.add_argument("--lengths", type=float, nargs="+", default=[4, 4.5, 4.75, 5, 5.25, 5.5, 6, 8, 10, 12, 14, 16])
    ap.add_argument("--widths", type=float, nargs="+", default=[0.5, 1.0, 1.5], help="Optical Gaussian FWHM in um")
    ap.add_argument("--target-ghz", type=float, default=3.33, help="Center frequency for the TE, 1 um recommendation table")
    ap.add_argument("--target-half-band-mhz", type=float, default=50, help="Half width of the target-frequency band")
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    mode_rows, overlap_rows = [], []
    for wap_um in args.lengths:
        label = f"Wap_{wap_um:g}um"
        summary_path = args.exports / f"{label}_modes_summary.csv"
        summary = read_summary(summary_path)
        for i, row in enumerate(summary, start=1):
            f_hz, _, e_ln, e_al, u2, v2, w2 = row[:7]
            total_e, total_d = abs(e_ln) + abs(e_al), abs(u2) + abs(v2) + abs(w2)
            mode_rows.append({
                "aperture_um": f"{wap_um:g}", "mode": i, "freq_GHz": f"{f_hz/1e9:.9f}",
                "frac_strain_LN": f"{abs(e_ln)/total_e:.6f}", "frac_strain_Al": f"{abs(e_al)/total_e:.6f}",
                "frac_u2_LN": f"{abs(u2)/total_d:.6f}", "frac_v2_LN": f"{abs(v2)/total_d:.6f}",
                "frac_w2_LN": f"{abs(w2)/total_d:.6f}",
            })
            field = args.exports / f"{label}_mode_{i:02d}_{f_hz/1e9:.6f}GHz.csv"
            x, y, z, g = interpolate_fields(field, wap_um)
            for pol in ("TE", "TM"):
                for width in args.widths:
                    zp, gv, U = coupling_profile(x, y, z, g, pol, width)
                    valid = np.isfinite(gv)
                    zvalid, gvalid = zp[valid], gv[valid]
                    if not len(gvalid):
                        continue
                    z1 = Z0 + wap_um * 1e-6
                    edge = (zvalid <= Z0 + EDGE_BAND) | (zvalid >= z1 - EDGE_BAND)
                    interior = (zvalid >= Z0 + Z_MARGIN) & (zvalid <= z1 - Z_MARGIN)
                    ia = int(np.argmax(gvalid))
                    ie = int(np.argmax(np.where(edge, gvalid, -np.inf)))
                    if interior.any():
                        ii = np.where(interior)[0][np.argmax(gvalid[interior])]
                        gi, zi = gvalid[ii], zvalid[ii]
                    else:
                        gi, zi = np.nan, np.nan
                    ge, ze = gvalid[ie], zvalid[ie]
                    overlap_rows.append({
                        "aperture_um": f"{wap_um:g}", "interior_span_um": f"{max(wap_um - 4, 0):g}",
                        "mode": i, "freq_GHz": f"{f_hz/1e9:.9f}",
                        "pol": pol, "waveguide_FWHM_um": f"{width:g}",
                        "g_all": f"{gvalid[ia]:.6e}", "z_all_um": f"{zvalid[ia]*1e6:.2f}",
                        "g_edge_1um": f"{ge:.6e}", "z_edge_um": f"{ze*1e6:.2f}",
                        "g_interior_2um": f"{gi:.6e}" if np.isfinite(gi) else "",
                        "z_interior_um": f"{zi*1e6:.2f}" if np.isfinite(zi) else "",
                        "edge_to_interior": f"{ge/gi:.5f}" if np.isfinite(gi) and gi != 0 else "",
                        "strain_energy_LN_J": f"{U:.6e}",
                    })
            print(f"done {label} mode {i}/{len(summary)}", flush=True)
    target_rows = [r for r in overlap_rows
                   if r["pol"] == "TE" and float(r["waveguide_FWHM_um"]) == 1.0
                   and abs(float(r["freq_GHz"]) - args.target_ghz) <= args.target_half_band_mhz / 1000]
    recommendations = []
    for wap in args.lengths:
        candidates = [r for r in target_rows if float(r["aperture_um"]) == wap and r["g_interior_2um"]]
        if not candidates:
            continue
        best = max(candidates, key=lambda r: float(r["g_interior_2um"]))
        edge = max(candidates, key=lambda r: float(r["g_edge_1um"]))
        recommendations.append({
            "aperture_um": best["aperture_um"], "interior_span_um": best["interior_span_um"],
            "target_band_GHz": f"{args.target_ghz-args.target_half_band_mhz/1000:.3f}-{args.target_ghz+args.target_half_band_mhz/1000:.3f}",
            "mode": best["mode"], "freq_GHz": best["freq_GHz"],
            "g_interior_best": best["g_interior_2um"], "z_interior_um": best["z_interior_um"],
            "g_edge_same_mode": best["g_edge_1um"], "z_edge_same_mode_um": best["z_edge_um"],
            "edge_to_interior_same_mode": best["edge_to_interior"],
            "g_edge_peak_any_mode": edge["g_edge_1um"], "edge_peak_mode": edge["mode"],
            "edge_peak_freq_GHz": edge["freq_GHz"], "edge_peak_z_um": edge["z_edge_um"],
        })
    outputs = (("aperture_sweep_modes.csv", mode_rows),
               ("aperture_sweep_overlap.csv", overlap_rows),
               ("aperture_sweep_recommendation.csv", recommendations))
    for name, rows in outputs:
        if not rows:
            continue
        path = args.output / name
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        print("Wrote", path, "rows", len(rows))


if __name__ == "__main__":
    main()




