"""Geometry audit for the suspended 3D TFLN IDT model.

Pure arithmetic reproduction of the parameters hard-coded in
D:\\comsol_ao_run\\idt_3d_sus\\aperture_sweep\\ApertureRun.java
and D:\\comsol_ao_run\\idt_3d_sus\\Idt3dSus.java.

The purpose is to make explicit what the model geometry does and does not
contain, in particular (i) how much of the periodic direction is covered by
aluminium and (ii) how wide the metal-free channel is.  No solver is run.
"""
from pathlib import Path
import csv

# Parameters exactly as set in ApertureRun.build()
P = 2.58e-6          # acoustic period, x
DUTY = 0.25
HLN = 500e-9         # LN thickness, y
HAL = 100e-9         # Al thickness, y
Z0 = 2e-6            # electrode start, z
WAP = 6e-6           # nominal aperture, z
MARGIN = 2e-6        # margin beyond each electrode end

FINGER_W = DUTY * P                       # bAp size along x
FINGER_X1 = (P - 2 * DUTY * P) / 4        # bAp x position
FINGER_X2 = P / 2 + (P - 2 * DUTY * P) / 4  # bAn x position
WSTACK = WAP + 2 * MARGIN                 # bLn size along z


def main():
    rows = []
    rows.append(("period_p_um", P * 1e6))
    rows.append(("finger_width_x_um", FINGER_W * 1e6))
    rows.append(("finger1_x_range_um", (FINGER_X1 * 1e6, (FINGER_X1 + FINGER_W) * 1e6)))
    rows.append(("finger2_x_range_um", (FINGER_X2 * 1e6, (FINGER_X2 + FINGER_W) * 1e6)))
    # metal coverage seen by light travelling along x
    metal = 2 * FINGER_W
    rows.append(("metal_length_per_period_x_um", metal * 1e6))
    rows.append(("metal_fraction_along_x", metal / P))
    # metal-free channel between finger 1 and finger 2
    gap = FINGER_X2 - (FINGER_X1 + FINGER_W)
    rows.append(("free_gap_between_fingers_x_um", gap * 1e6))
    # thin-film extent
    rows.append(("film_thickness_y_nm", HLN * 1e9))
    rows.append(("film_total_width_z_um", WSTACK * 1e6))
    rows.append(("aperture_z_um", WAP * 1e6))
    rows.append(("film_width_scales_with_aperture", True))

    print("=== Suspended 3D IDT geometry (reproduced from Java constants) ===")
    for k, v in rows:
        print(f"{k:34s} {v}")

    print("\n=== Consequence for optical propagation ===")
    print(f"Along x (acoustic periodic direction): Al covers {metal / P * 100:.1f}% "
          f"of every period ({metal * 1e6:.3f} of {P * 1e6:.3f} um).")
    print("  -> a low-loss optical waveguide cannot propagate along x in this geometry.")
    print(f"Metal-free channel between fingers along x: {gap * 1e6:.3f} um.")
    print(f"Film width along z: {WSTACK * 1e6:.3f} um, no lateral index step inside it,")
    print("  -> no lateral optical confinement in z; only the LN/air edges at z=0 and")
    print(f"     z={WSTACK * 1e6:.1f} um provide an index step.")
    print("\nNote: Wap and the film width are changed together (Wstack = Wap + 4 um),")
    print("so an 'aperture sweep' also sweeps the total film width.")

    out = Path(__file__).with_name("geometry_audit.csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "value"])
        for k, v in rows:
            w.writerow([k, v])
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
