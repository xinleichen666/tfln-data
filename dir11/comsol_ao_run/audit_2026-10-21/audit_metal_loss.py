"""Metal-induced optical loss constraint for the suspended TFLN IDT.

Screening estimate only.  It answers one design question: how far must the
100 nm Al electrodes be kept from the optical mode before the device is
usable, and what does that imply for the cross-section?

Model
-----
The modal power fraction inside the aluminium is factorised as

    Gamma_metal = Fx(metal) * Fy(above cladding)

where Fx is the lateral fraction of |psi|^2 that falls under the finger
footprint, and Fy is the vertical fraction above a low-index cladding of
thickness t.  Power attenuation is then

    alpha = 4*pi*kappa_Al*Gamma_metal/lambda     [1/m]

with kappa_Al the extinction coefficient of the film.  Bulk values are used;
grain structure, adhesion layers and surface roughness are ignored.

This is deliberately crude.  Its purpose is to turn "metal is a problem"
into a number that a layout can be checked against.
"""
from pathlib import Path
import csv
import numpy as np

from audit_optical_mode import slab, lateral, profile, NO, N_AIR, HLN

HERE = Path(__file__).parent
LAM = 1.55e-6
K0 = 2 * np.pi / LAM
N_CLAD = 1.444
HAL = 100e-9
P = 2.58e-6
DUTY = 0.25
FINGER_W = DUTY * P
FINGER_X = [(P - 2 * DUTY * P) / 4, P / 2 + (P - 2 * DUTY * P) / 4]
KAPPA = (5.0, 10.0, 20.0)


def lateral_profile(etch_nm, width_um, x0):
    """Lateral intensity of a ridge centred at x0, on a +/-1 period window."""
    core = slab(NO, N_AIR, N_AIR, HLN, pol="TE")
    clad = slab(NO, N_AIR, N_AIR, HLN - etch_nm * 1e-9, pol="TE")
    if core is None or clad is None or core <= clad:
        return None, None, None
    neff = lateral(core, clad, width_um * 1e-6)
    if neff is None:
        return None, None, None
    x, i = profile(core, clad, neff, width_um * 1e-6 / 2, span=2.0)
    return x + x0, i, neff


def frac_under_fingers(x, inten):
    m = np.zeros_like(x, dtype=bool)
    for shift in (-P, 0.0, P):
        for f0 in FINGER_X:
            m |= (x >= f0 + shift) & (x <= f0 + FINGER_W + shift)
    return float(np.trapezoid(inten[m], x[m]))


def vertical_above(neff_2d, clad_thickness, n_core=NO):
    """Power fraction above a cladding of the given thickness (Al slab included).

    The vertical profile is the air-clad slab mode of the film itself; the tail
    above the surface decays with the cladding index, not the air index.
    """
    v = slab(n_core, N_AIR, N_AIR, HLN, pol="TE")
    y, inten = profile(n_core, N_AIR, v, HLN / 2, span=3.0)
    surf = float(np.interp(HLN / 2, y, inten))
    gam = K0 * np.sqrt(max(v ** 2 - N_CLAD ** 2, 0.0))
    zz = np.linspace(0, clad_thickness + HAL, 4001)
    iy = surf * np.exp(-2 * gam * zz)
    inside = zz >= clad_thickness
    return float(np.trapezoid(iy[inside], zz[inside]))


def loss_dB_per_cm(gamma_metal, kappa):
    alpha = 4 * np.pi * kappa * gamma_metal / LAM
    return 4.343 * alpha / 100.0


def main():
    print("=== Assumptions ===")
    print(f"lambda {LAM*1e6:.2f} um, Al {HAL*1e9:.0f} nm, period {P*1e6:.2f} um, "
          f"finger {FINGER_W*1e6:.3f} um")
    print("finger x-ranges (um): "
          f"{[(round(f*1e6, 3), round((f+FINGER_W)*1e6, 3)) for f in FINGER_X]}")
    print(f"kappa_Al assumed: {KAPPA} (bulk screening values, not film metrology)")
    print("scalar EIM profiles; no metal-induced mode distortion; no scattering\n")

    rows = []
    print("=== A. guide centred in the metal-free channel (x0 = 1.29 um) ===")
    print(f"{'etch':>6s} {'width':>7s} {'Fx(finger)':>11s} {'t_clad':>7s} "
          f"{'Fy':>10s} {'Gamma':>10s} {'dB/cm':>11s}")
    x0 = P / 2
    for etch in (0, 150, 250, 400):
        for width in (0.50, 0.645):
            x, i, neff = lateral_profile(etch, width, x0)
            if i is None:
                continue
            fx = frac_under_fingers(x, i)
            for t in (0.0, 0.5, 1.0, 1.5, 2.0):
                fy = vertical_above(neff, t * 1e-6)
                g = fx * fy
                rows.append((etch, width, t, fx, fy, g,
                             loss_dB_per_cm(g, 10.0)))
                print(f"{etch:6d} {width:7.3f} {fx:11.3e} {t:7.1f} "
                      f"{fy:10.2e} {g:10.2e} {loss_dB_per_cm(g,10.0):11.3e}")

    print("\n=== B. extra lateral clearance from the ridge edge "
          "(etch 250 nm, width 0.645 um, no cladding) ===")
    x, i, neff = lateral_profile(250, 0.645, x0)
    for gap_nm in (0, 100, 200, 300, 500, 1000):
        half = 0.645e-6 / 2
        m = np.abs(x) > half + gap_nm * 1e-9
        fx = float(np.trapezoid(i[m], x[m]))
        g = fx * vertical_above(neff, 0.0)
        print(f"clearance {gap_nm:4d} nm -> Fx {fx:.2e}, Gamma {g:.2e}, "
              f"{loss_dB_per_cm(g, 10.0):.2e} dB/cm")

    print("\n=== Interpretation ===")
    print("For 1 dB/cm the modal power inside Al must satisfy:")
    for k in KAPPA:
        g_max = 100 / 4.343 / (4 * np.pi * k / LAM)
        print(f"  kappa = {k:4.0f}: Gamma_metal < {g_max:.2e}")
    print("Even 1e-4 of the power inside 100 nm Al costs tens of dB/cm, so the")
    print("electrodes cannot sit on the optical path.  The two workable options")
    print("are a low-index cladding thick enough to expel the tail, or a lateral")
    print("offset of several microns.  Both alter the acoustic boundaries and")
    print("must be re-solved; neither is present in the current model.")

    with (HERE / "metal_loss_audit.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["etch_nm", "width_um", "clad_um", "Fx_finger", "Fy_above",
                    "Gamma_metal", "dB_per_cm_k10"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], f"{r[3]:.3e}", f"{r[4]:.3e}",
                        f"{r[5]:.3e}", f"{r[6]:.3e}"])
    print(f"\nWrote {HERE / 'metal_loss_audit.csv'}")


if __name__ == "__main__":
    main()

