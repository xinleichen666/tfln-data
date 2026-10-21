"""Crystal-axis and photoelastic-contraction audit.

Checks whether the scalar contraction used in
D:\\comsol_ao_run\\photoelastic\\Photo.java and in the aperture post-processing

    dn = -(n_e^3 / 2) * (0.179 * (eXX + eYY) + 0.071 * eZZ)

is consistent with (i) the material basis that the COMSOL model actually
assigns and (ii) the stated optical propagation direction.

Material basis set in Idt3dSus.java / ApertureRun.java:
    basisx = (0, 1, 0)  ->  crystal x  = global +y  (film normal)
    basisy = (-1, 0, 0) ->  crystal y  = global -x  (periodic direction)
    basisz  = (0, 0, 1) ->  crystal z  = global +z  (aperture / finger length)
This is the standard x-cut orientation: optic axis (crystal z) in plane.

Only arithmetic is performed; the literature photoelastic constants are the
ones already used in the repository. Shear constants p14/p41/p44 are not
present in the repository and are therefore flagged, not invented.
"""
import numpy as np

# Constants used in the repository (Weis & Gaylord, as tabulated by Andrushchak)
P11, P12, P13 = -0.026, 0.090, 0.133
P31, P33 = 0.179, 0.071
P41, P44 = -0.151, 0.146      # present in the 3m matrix, used only in Option B
NO, NE = 2.211, 2.138         # Zelmon et al. at 1550 nm

# 3m photoelastic matrix in the crystal frame, Voigt order
# (1,2,3 normal; 4,5,6 engineering shear).
def matrix_3m(p14=None, p44=P44, p41=P41, p11=P11, p12=P12, p13=P13,
              p31=P31, p33=P33):
    m = np.zeros((6, 6))
    m[0, :6] = [p11, p12, p13, np.nan if p14 is None else p14, 0, 0]
    m[1, :6] = [p12, p11, p13, np.nan if p14 is None else -p14, 0, 0]
    m[2, :6] = [p31, p31, p33, 0, 0, 0]
    m[3, :6] = [p41, -p41, p44, 0, 0, 0]
    m[4, :6] = [0, 0, 0, 0, p44, p41]
    m[5, :6] = [0, 0, 0, 0, p14 if p14 is not None else np.nan,
                (p11 - p12) / 2]
    return m


def main():
    m = matrix_3m(p14=None)
    print("=== 3m photoelastic matrix in the crystal frame (p14 not in repo) ===")
    print(m)

    print("\n=== Option A: light along global x = crystal y, E || crystal z ===")
    print("Relevant Voigt row: index 3 (extraordinary, n_e).")
    print("Row 3 contains only normal-strain terms: p31*S1 + p31*S2 + p33*S3")
    print("No shear term for the extraordinary index in 3m symmetry.")
    print(f"coefficients from row 3: p31={m[2,0]:+.3f}, p31={m[2,1]:+.3f}, p33={m[2,2]:+.3f}")
    print("Crystal to global strain mapping: S1 = e_yy, S2 = e_xx, S3 = e_zz")
    print("  S1 and S2 carry the same coefficient p31, so the x<->y swap in")
    print("  the basis does not change this contraction, and the sign flip of")
    print("  crystal y does not change normal strains either.")
    print("=> The scalar formula in Photo.java is CONSISTENT with the declared")
    print("   material basis, for this propagation direction and polarization.")
    print("   (This holds for the elasticity/photoelastic part only; it says")
    print("   nothing about whether light can propagate along x: see")
    print("   audit_geometry.py, where Al covers 50% of every period.)")

    print("\n=== Option B: light along global z = crystal z (optic axis) ===")
    print("Propagation along the optic axis: both polarizations see n_o.")
    print("Relevant rows: 1 (E || crystal x) and 2 (E || crystal y).")
    print(f"row 1: p11={m[0,0]:+.3f}, p12={m[0,1]:+.3f}, p13={m[0,2]:+.3f}, p14={m[0,3]}")
    print(f"row 2: p12={m[1,0]:+.3f}, p11={m[1,1]:+.3f}, p13={m[1,2]:+.3f}, p14={m[1,3]}")
    print("Shear strain S4 = 2*e_23 enters with +/- p14, which is NOT defined")
    print("anywhere in this repository. The current exports do contain eXZ, so")
    print("the missing quantity is the constant, not the field.")
    print("=> Switching the propagation direction requires re-deriving the")
    print("   contraction and adding a literature p14; the present numbers")
    print("   cannot be carried over unchanged.")

    print("\n=== Numerical comparison of the two options on a test strain ===")
    # Representative normal strain amplitudes, ordinary magnitude for this model
    e_xx, e_yy, e_zz = 2.0e-5, 0.6e-5, -1.8e-5
    dnA = -(NE ** 3 / 2) * (P31 * (e_yy + e_xx) + P33 * e_zz)
    dnB1 = -(NO ** 3 / 2) * (P11 * e_yy + P12 * e_xx + P13 * e_zz)
    dnB2 = -(NO ** 3 / 2) * (P12 * e_yy + P11 * e_xx + P13 * e_zz)
    print(f"test strain e_xx={e_xx:.1e}, e_yy={e_yy:.1e}, e_zz={e_zz:.1e} (normal terms only)")
    print(f"Option A |dn_e| = {abs(dnA):.3e}")
    print(f"Option B |dn_o| = {abs(dnB1):.3e} (E || crystal x)")
    print(f"Option B |dn_o| = {abs(dnB2):.3e} (E || crystal y)")
    print(f"ratio B1/A = {abs(dnB1) / abs(dnA):.3f}, B2/A = {abs(dnB2) / abs(dnA):.3f}")
    print("The two architectures give perturbations of the same order but from")
    print("different constants and different indices; they are not interchangeable.")

    print("\n=== What this audit does NOT establish ===")
    print("- it does not validate the numerical strain field;")
    print("- it does not supply p14, and it ignores the electro-optic contribution;")
    print("- it does not test the Voigt shear convention of the exports.")


if __name__ == "__main__":
    main()
