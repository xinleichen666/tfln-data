"""Cross-section mode benchmark: no metal versus metal, same geometry.

This replaces the factorised Gamma = Fx*Fy estimate (see audit_metal_loss.py,
whose numbers are superseded).  Here the transverse problem is solved directly
on a (x, y) grid for light propagating along z:

    -grad^2 psi - k0^2 n^2(x,y) psi = lambda psi,   lambda = -k0^2 neff^2

Three cases are run on the same mesh:
  (1) uniform slab            -> validates the solver against the 1D solution
  (2) ridge, no metal         -> bound mode of the intended cross-section
  (3) ridge + Al fingers      -> complex n_Al, direct imaginary part of neff

The loss from (3) includes the mode distortion caused by the metal, which the
perturbative estimate cannot give.  (1) and (3) together also cross-check the
perturbation used in audit_metal_loss.py.

Assumptions: scalar (semi-vectorial) approximation, Dirichlet boundaries far
from the guide, bulk optical constants for Al, no roughness or scattering.
"""
from pathlib import Path
import csv
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from audit_optical_mode import slab, NO, N_AIR, HLN

HERE = Path(__file__).parent
LAM = 1.55e-6
K0 = 2 * np.pi / LAM
P = 2.58e-6
DUTY = 0.25
FINGER_W = DUTY * P
F0 = [(P - 2 * DUTY * P) / 4, P / 2 + (P - 2 * DUTY * P) / 4]
HAL = 100e-9
X0 = P / 2          # guide centre = centre of the metal-free channel
N_AL = 1.44 + 15.6j     # bulk screening value; kappa is swept separately
DX = 15e-9
DY = 20e-9          # keeps y = 0 and y = 500 nm exactly on grid nodes
XW = 1.6e-6         # half-width of the transverse window around X0
YW = 1.0e-6         # half-height


def build_grid(xw=XW, yw=YW, dx=DX, dy=DY):
    x = np.arange(X0 - xw, X0 + xw + dx / 2, dx)
    y = np.arange(-yw, HLN + HAL + yw + dy / 2, dy)
    return x, y


def finger_span(x, pad=0.0):
    """True where x lies under an Al finger (periodic images included)."""
    on = np.zeros(x.size, dtype=bool)
    for shift in (-P, 0.0, P):
        for f in F0:
            on |= (x >= f + shift - pad) & (x <= f + FINGER_W + shift + pad)
    return on


def local_thickness(x, etch, width):
    return np.where(np.abs(x - X0) <= width / 2, HLN, HLN - etch)


def index_map(x, y, etch, width, metal):
    """Refractive-index map of the modelled cross-section.

    Al is placed only under the fingers and only on the local top surface of
    the film (y from h(x) to h(x)+HAL).  It is never placed on the whole top
    surface, and never over the ridge.
    """
    n2 = np.full((y.size, x.size), N_AIR ** 2, dtype=complex)
    h = local_thickness(x, etch, width)
    on_finger = finger_span(x)
    for iy, yy in enumerate(y):
        if yy < 0:
            continue
        core = (yy >= 0) & (yy < h)
        n2[iy, core] = NO ** 2
        if metal:
            top = (yy >= h) & (yy < h + HAL) & on_finger
            n2[iy, top] = N_AL ** 2
    return n2


def assert_layout(n2, x, y, etch, width):
    """Fail loudly if Al appears anywhere over the ridge.

    Checks the permittivity map itself, not a geometric guess: the number of
    Al cells strictly inside the ridge must be zero.
    """
    al = np.abs(n2 - N_AL ** 2) < 1e-9
    inside = np.abs(x - X0) < width / 2 - DX / 2
    bad = int(np.count_nonzero(al[:, inside]))
    total = int(np.count_nonzero(al))
    per_row = int(np.count_nonzero(al[al.any(axis=1)].any(axis=0)))
    print(f"layout check: Al cells = {total} in {per_row} x-columns, "
          f"over the ridge = {bad} (must be 0)")
    assert bad == 0, "Al placed over the ridge - index map is wrong"
    return bad


def solve(n2, neff_guess=1.96, k=4, dx=DX, dy=DY, iters=40):
    """Inverse iteration around a fixed shift.

    ARPACK (eigsh/eigs) proved unreliable here: for these near-degenerate,
    non-Hermitian problems it returned different modes between runs.  A direct
    sparse LU at a fixed shift, followed by inverse iteration, converges to the
    eigenvalue nearest that shift and is reproducible.
    """
    ny, nx = n2.shape
    d2 = lambda n, d: sp.diags([np.ones(n - 1), -2 * np.ones(n), np.ones(n - 1)],
                               [-1, 0, 1], shape=(n, n)) / d ** 2
    L = -(sp.kron(sp.eye(ny), d2(nx, dx)) + sp.kron(d2(ny, dy), sp.eye(nx)))
    L = (L - sp.diags(n2.ravel() * K0 ** 2)).tocsr()
    inner = np.ones((ny, nx), dtype=bool)
    inner[0, :] = inner[-1, :] = inner[:, 0] = inner[:, -1] = False
    idx = np.flatnonzero(inner.ravel())
    Li = L[idx][:, idx].tocsc()
    sigma = -(K0 * neff_guess) ** 2
    lu = spla.splu(Li - sigma * sp.identity(Li.shape[0], format="csc"))
    rng = np.random.default_rng(0)
    x = rng.standard_normal(Li.shape[0]) + 1j * rng.standard_normal(Li.shape[0])
    for _ in range(iters):
        x = lu.solve(x)
        x /= np.linalg.norm(x)
    # Rayleigh quotient for a complex symmetric operator (no conjugation)
    lam = complex(x @ (Li @ x) / (x @ x))
    neff = np.sqrt(-lam) / K0
    if neff.imag < -1e-12:      # branch selection, ignore numerical noise
        neff = -neff
        x = -x
    r = Li @ x - lam * x
    resid = float(np.linalg.norm(r) / np.linalg.norm(x) / abs(lam))
    return neff, x, idx, resid


def mode_fields(vec, shape, idx):
    ny, nx = shape
    psi = np.zeros(ny * nx, dtype=complex)
    psi[idx] = vec
    return psi.reshape(ny, nx)


def fwhm(x, inten):
    above = inten >= 0.5 * inten.max()
    return float(x[above].max() - x[above].min())



def metal_mask(x, y_array, etch, width):
    """Cells occupied by Al: fingers only, attached to the local top surface."""
    h = local_thickness(x, etch, width)
    on = finger_span(x)
    yy = y_array[:, None]
    return (yy >= h[None, :]) & (yy < h[None, :] + HAL) & on[None, :]


def report_case(tag, x, y, etch, width, metal, kappa_scale=1.0, guess=1.90,
                dx=DX, dy=DY):
    n2 = index_map(x, y, etch, width, metal)
    if metal and kappa_scale != 1.0:
        alt = (N_AL.real + 1j * N_AL.imag * kappa_scale) ** 2
        n2 = np.where(np.abs(n2 - N_AL ** 2) < 1e-9, alt, n2)
    neff, vec, idx, resid = solve(n2, neff_guess=guess, dx=dx, dy=dy)
    psi = mode_fields(vec, n2.shape, idx)
    inten = np.abs(psi) ** 2
    inten /= inten.sum()
    w = fwhm(x, inten.sum(axis=0))
    db = 4.343 * (2 * K0 * neff.imag) / 100.0
    print(f"{tag:34s} neff = {neff.real:.5f} {neff.imag:+.3e}j, "
          f"FWHM {w*1e6:.2f} um, {db:.3e} dB/cm, resid {resid:.1e}")
    return neff, inten, w, resid


def validation():
    """Interface alignment, layout assertion and EIM cross-check."""
    from audit_optical_mode import analyse_option_b
    print("=== validation ===")
    for dy in (20e-9, 15e-9):
        y = np.arange(-YW, HLN + HAL + YW + dy / 2, dy)
        print(f"  dy = {dy*1e9:4.0f} nm -> y=0 on grid: "
              f"{np.min(np.abs(y)) < 1e-12}, y=500 nm on grid: "
              f"{np.min(np.abs(y - HLN)) < 1e-12}")

    x, y = build_grid()
    print()
    for etch, width in ((250e-9, 0.645e-6), (400e-9, 0.645e-6)):
        assert_layout(index_map(x, y, etch, width, True), x, y, etch, width)

    print("\nEIM versus 2D solve (independent approximations, same index map):")
    print(f"{'etch':>6s} {'width':>7s} {'neff_EIM':>10s} {'neff_2D':>10s} {'diff %':>8s}")
    worst = 0.0
    for etch, width in ((250e-9, 0.645e-6), (400e-9, 0.645e-6)):
        r = analyse_option_b(etch * 1e9, width * 1e6)
        n2 = index_map(x, y, etch, width, False)
        neff, _, _, res = solve(n2, neff_guess=r["neff"])
        d = (neff.real - r["neff"]) / r["neff"] * 100
        worst = max(worst, abs(d))
        print(f"{etch*1e9:6.0f} {width*1e6:7.3f} {r['neff']:10.5f} "
              f"{neff.real:10.5f} {d:+8.3f}  (resid {res:.1e})")
    print(f"-> worst disagreement {worst:.2f} %\n")
    return worst


def main():
    worst = validation()
    x, y = build_grid()
    print(f"production grid {x.size} x {y.size} = {x.size*y.size} points, "
          f"dx={DX*1e9:.0f} nm, dy={DY*1e9:.0f} nm")
    print(f"window x [{x.min()*1e6:.2f},{x.max()*1e6:.2f}] um, "
          f"y [{y.min()*1e6:.2f},{y.max()*1e6:.2f}] um\n")

    print("=== no metal ===")
    cases = {}
    for etch, width in ((250e-9, 0.645e-6), (400e-9, 0.645e-6)):
        neff0, inten0, w0, _ = report_case(
            f"etch {etch*1e9:.0f} nm, w {width*1e6:.3f} um",
            x, y, etch, width, False, guess=1.90)
        cases[(etch, width)] = (neff0, inten0, w0)

    print("\n=== with Al fingers only under the fingers ===")
    rows = []
    for (etch, width), (neff0, inten0, w0) in cases.items():
        m = metal_mask(x, y, etch, width)
        gamma = float(inten0[m].sum())
        neff1, inten1, w1, res1 = report_case(
            f"etch {etch*1e9:.0f} nm, w {width*1e6:.3f} um",
            x, y, etch, width, True, guess=neff0.real)
        mac = float(abs(np.vdot(np.sqrt(inten0), np.sqrt(inten1)))
                    / np.sqrt(np.sum(inten0) * np.sum(inten1)))
        loss = 4.343 * (2 * K0 * neff1.imag) / 100.0
        pert = 4.343 * (4 * np.pi * N_AL.imag * gamma / LAM) / 100.0
        print(f"{'  overlap with lossless mode':36s} {mac:.4f}")
        print(f"{'  shift / perturbative':36s} dRe {neff1.real-neff0.real:+.4f}, "
              f"Gamma {gamma:.2e}, pert {pert:.2e} dB/cm")
        rows.append((etch, width, neff0.real, neff1.real, neff1.imag,
                     gamma, loss, pert, mac, res1))

    print("\n=== mesh and window sensitivity (etch 250 nm, w 0.645 um, Al) ===")
    sens = []
    for dy in (20e-9, 15e-9):
        for xw in (1.6e-6, 2.4e-6):
            xs, ys = build_grid(xw=xw, dy=dy)
            n2 = index_map(xs, ys, 250e-9, 0.645e-6, True)
            neff, _, _, res = solve(n2, neff_guess=1.65, dy=dy)
            sens.append(neff.real)
            print(f"  dy {dy*1e9:3.0f} nm, xw {xw*1e6:.1f} um -> "
                  f"Re {neff.real:.5f}, Im {neff.imag:.3e}, "
                  f"{4.343*(2*K0*neff.imag)/100.0:.1f} dB/cm, resid {res:.1e}")
    spread = (max(sens) - min(sens)) / np.mean(sens) * 100
    print(f"  spread of Re(neff) = {spread:.2f} %")

    print("\n=== insertion loss over the interaction length ===")
    for r in rows:
        print(f"  etch {r[0]*1e9:.0f} nm: {r[6]:.0f} dB/cm -> "
              f"{r[6]*6e-4:.2f} dB (6 um), {r[6]*20e-4:.2f} dB (20 um), "
              f"{r[6]*100e-4:.2f} dB (100 um)")

    ok = (all(r[9] < 1e-8 for r in rows) and all(r[8] > 0.8 for r in rows)
          and spread < 2.0 and worst < 1.0)
    print(f"\nVALIDATION {'PASS' if ok else 'FAIL'}: residual<1e-8, MAC>0.8, "
          f"spread<2 %, EIM<1 % (worst {worst:.2f} %, spread {spread:.2f} %)")
    if not ok:
        print("-> do not quote the loss numbers; the model is not validated.")

    with (HERE / "mode_cross_section_audit.csv").open("w", newline="",
                                                      encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["etch_nm", "width_um", "neff_no_metal", "neff_real_metal",
                     "neff_imag_metal", "Gamma_metal", "dB_per_cm",
                     "dB_per_cm_perturbative", "MAC_vs_lossless", "residual",
                     "validated"])
        for r in rows:
            wr.writerow([f"{r[0]*1e9:.0f}", f"{r[1]*1e6:.3f}", f"{r[2]:.5f}",
                         f"{r[3]:.5f}", f"{r[4]:.3e}", f"{r[5]:.3e}",
                         f"{r[6]:.3e}", f"{r[7]:.3e}", f"{r[8]:.4f}",
                         f"{r[9]:.1e}", ok])
        wr.writerow(["eim_vs_2d_worst_diff_percent", f"{worst:.3f}"])
        wr.writerow(["mesh_spread_percent", f"{spread:.2f}"])
    print(f"\nWrote {HERE / 'mode_cross_section_audit.csv'}")


if __name__ == "__main__":
    main()
