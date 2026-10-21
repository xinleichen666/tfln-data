"""Optical confinement audit (effective-index method, 1550 nm).

The current manuscript weights the acoustic strain with a *Gaussian* optical
intensity of 1 um FWHM.  This script asks what optical mode the modelled
geometry can actually support, for the two propagation directions that are
compatible with the material basis declared in the COMSOL model.

Option A: light along global x (= crystal y).  Transverse plane (y, z).
          No index step along z inside the film; the film is 10 um wide in z
          (Wap + 4 um) and air-clad.  Aluminium covers 50% of every period
          along x, so this direction is optically blocked.
Option B: light along global z (= crystal z, optic axis).  Transverse plane
          (x, y).  To avoid the metal the guide must fit inside the 0.645 um
          metal-free channel, and lateral confinement requires an etch that
          the acoustic model does not contain.

Method: effective-index method.  A 1D slab solve gives the vertical effective
index; a second 1D solve gives the lateral mode.  This is a scalar, first-order
estimate: adequate to test whether a 1 um FWHM mode is physically available in
this geometry, not to design a waveguide.
"""
from pathlib import Path
import csv
import numpy as np

LAM = 1.55e-6
K0 = 2 * np.pi / LAM
NE, NO = 2.138, 2.211
N_AIR = 1.0
HLN = 500e-9
WSTACK = 10e-6
FINGER_W = 0.25 * 2.58e-6
GAP = 2.58e-6 / 2 - FINGER_W
HERE = Path(__file__).parent


def slab(n_f, n_c, n_s, h, pol="TE"):
    """Fundamental slab mode; pol='TE' -> E parallel to the interfaces."""
    lo, hi = max(n_c, n_s) + 1e-9, n_f - 1e-9

    def resid(neff):
        kap = K0 * np.sqrt(max(n_f ** 2 - neff ** 2, 0.0))
        gc = K0 * np.sqrt(max(neff ** 2 - n_c ** 2, 0.0))
        gs = K0 * np.sqrt(max(neff ** 2 - n_s ** 2, 0.0))
        if kap <= 0:
            return -np.pi
        if pol == "TE":
            rhs = np.arctan(gc / kap) + np.arctan(gs / kap)
        else:
            rhs = (np.arctan((n_f ** 2 / n_c ** 2) * gc / kap)
                   + np.arctan((n_f ** 2 / n_s ** 2) * gs / kap))
        return kap * h - rhs

    if resid(lo) <= 0:
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if resid(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def lateral(n_core, n_clad, w):
    """Fundamental symmetric lateral mode of a strip of width w."""
    lo, hi = n_clad + 1e-9, n_core - 1e-9

    def resid(neff):
        kap = K0 * np.sqrt(max(n_core ** 2 - neff ** 2, 0.0))
        gam = K0 * np.sqrt(max(neff ** 2 - n_clad ** 2, 0.0))
        if kap <= 0:
            return -np.pi / 2
        return kap * w / 2 - np.arctan(gam / kap)

    if resid(lo) <= 0:
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if resid(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def profile(core, clad, neff, half, span=2.5):
    """Sampled normalised intensity |psi|^2 over [-span*half, span*half]."""
    x = np.linspace(-span * half, span * half, 4001)
    kap = K0 * np.sqrt(max(core ** 2 - neff ** 2, 0.0))
    gam = K0 * np.sqrt(max(neff ** 2 - clad ** 2, 0.0))
    inside = np.abs(x) <= half
    amp = np.where(inside, np.cos(kap * np.abs(x)),
                   np.cos(kap * half) * np.exp(-gam * (np.abs(x) - half)))
    inten = amp ** 2
    inten /= np.trapezoid(inten, x)
    return x, inten


def fwhm(x, inten):
    above = inten >= 0.5 * inten.max()
    return float(x[above].max() - x[above].min())


def analyse_option_a():
    v = slab(NE, N_AIR, N_AIR, HLN, pol="TE")
    if v is None:
        return None
    lat = lateral(v, N_AIR, WSTACK)
    if lat is None:
        return None
    x, inten = profile(v, N_AIR, lat, WSTACK / 2)
    return dict(vertical_neff=v, neff=lat, fwhm_z_um=fwhm(x, inten) * 1e6)


def analyse_option_b(etch_nm, width_um):
    core = slab(NO, N_AIR, N_AIR, HLN, pol="TE")
    clad = slab(NO, N_AIR, N_AIR, HLN - etch_nm * 1e-9, pol="TE")
    if core is None or clad is None or core <= clad:
        return None
    lat = lateral(core, clad, width_um * 1e-6)
    if lat is None:
        return None
    x, inten = profile(core, clad, lat, width_um * 1e-6 / 2)
    outside = np.abs(x) > GAP / 2
    return dict(core_neff=core, clad_neff=clad, neff=lat,
                fwhm_x_um=fwhm(x, inten) * 1e6,
                frac_outside_gap=float(np.trapezoid(inten[outside], x[outside])))


def vertical_metrics(neff, pol="TE"):
    """Vertical (y) intensity FWHM and fraction of power inside the 500 nm film."""
    half = HLN / 2
    y, inten = profile(NE if pol == "TE" else NO, N_AIR, neff, half)
    inside = np.abs(y) <= half
    return fwhm(y, inten) * 1e9, float(np.trapezoid(inten[inside], y[inside]))


def main():
    print(f"lambda = {LAM*1e6:.3f} um, LN {HLN*1e9:.0f} nm, air-clad membrane")
    print(f"metal-free channel along x = {GAP*1e6:.3f} um, "
          f"film width along z = {WSTACK*1e6:.1f} um\n")

    a = analyse_option_a()
    print("=== Option A: light along x, transverse plane (y, z) ===")
    if a:
        print(f"vertical slab neff (500 nm LN, air/air) : {a['vertical_neff']:.5f}")
        print(f"lateral (z) guided neff over 10 um      : {a['neff']:.5f}")
        print(f"lateral intensity FWHM                  : {a['fwhm_z_um']:.2f} um")
        vy, vg = vertical_metrics(a["vertical_neff"])
        print(f"vertical intensity FWHM (y)             : {vy:.0f} nm, "
              f"power inside the 500 nm film: {vg*100:.1f}%")
        print(f"-> geometry offers a ~{a['fwhm_z_um']:.1f} um wide mode, not the 1.0 um")
        print("   FWHM Gaussian assumed in the manuscript.")
        print("-> light along x also crosses Al fingers covering 50% of each")
        print("   period, so this direction is not usable for a low-loss guide.")

    print("\n=== Option B: light along z (optic axis), transverse plane (x, y) ===")
    print(f"guide width limited by the metal-free channel ({GAP*1e6:.3f} um)")
    rows = []
    for etch in (100, 150, 200, 250, 300, 400):
        for width in (0.40, 0.50, 0.645, 1.00):
            r = analyse_option_b(etch, width)
            if r is None:
                continue
            rows.append((etch, width, r))
            print(f"etch {etch:3d} nm  width {width:.3f} um -> neff {r['neff']:.5f} "
                  f"(core {r['core_neff']:.4f}, clad {r['clad_neff']:.4f}), "
                  f"FWHM {r['fwhm_x_um']:.2f} um, outside gap "
                  f"{r['frac_outside_gap']*100:5.1f}%")

    print("\nInterpretation (first-order scalar EIM):")
    print("- an air-clad 500 nm LN membrane is a weakly confined optical slab;")
    print("  its vertical mode extends well into the air cladding;")
    print("- the present acoustic geometry has no lateral index step at all, so")
    print("  a lateral optical mode only exists after an etch that the acoustic")
    print("  model does not contain;")
    print("- any etch deep enough to confine light laterally also changes the")
    print("  acoustic mode and the IDT boundary conditions.")

    with (HERE / "optical_mode_audit.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["option", "etch_nm", "width_um", "vertical_neff", "neff",
                    "fwhm_um", "frac_outside_gap"])
        if a:
            w.writerow(["A", 0, WSTACK * 1e6, round(a["vertical_neff"], 6),
                        round(a["neff"], 6), round(a["fwhm_z_um"], 3), ""])
        for etch, width, r in rows:
            w.writerow(["B", etch, width, round(r["core_neff"], 6),
                        round(r["neff"], 6), round(r["fwhm_x_um"], 3),
                        round(r["frac_outside_gap"], 5)])
    print(f"\nWrote {HERE / 'optical_mode_audit.csv'}")


if __name__ == "__main__":
    main()


