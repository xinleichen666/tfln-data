"""Optical validation of ONE cross-section: three meshes plus a boundary test.

Scope agreed for this round, nothing more:

  * one cross-section: 500 nm LN, 250 nm etch, 645 nm ridge, guide centred in
    the metal-free channel, 100 nm Al under the fingers only;
  * 1550 nm, light along z (the optic axis);
  * two cases: no metal, with metal;
  * three mesh levels and one boundary expansion;
  * complex fields retained, complex overlap used for branch tracking.

Physical note: light propagates along the crystal optic axis, so birefringence
vanishes and both polarisations see n_o = 2.211.  The model is still SCALAR
(one transverse field component): it does not enforce vector field continuity
at the high-contrast LN/air and LN/Al interfaces, and it cannot describe
metal-induced polarisation conversion.  Those remain for a full-vector solve.

Pass/fail is decided by the criteria printed at the end; if any fails, the
numbers must not be used downstream.
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from audit_mode_cross_section import solve, mode_fields, index_map, N_AL, HAL, X0

HERE = Path(__file__).parent
FIG = HERE / "figs"
LAM = 1.55e-6
K0 = 2 * np.pi / LAM
HLN = 500e-9
ETCH = 250e-9
WIDTH = 0.645e-6
YW = 1.0e-6
XW0 = 1.6e-6
MESHES = [(20.0, 25.0), (15.0, 20.0), (12.5, 12.5)]   # nm, (dx, dy)


def make_grid(dx_target_nm, dy_nm, xw=XW0):
    """Uniform grid with both ridge edges exactly on nodes, symmetric in x."""
    n_w = max(4, int(round(WIDTH / (dx_target_nm * 1e-9))))
    dx = WIDTH / n_w
    n_l = max(4, int(round((xw - WIDTH / 2) / dx)))
    x = X0 + dx * np.arange(-(n_l + n_w), n_l + 1)
    dy = dy_nm * 1e-9
    y = np.arange(-YW, HLN + HAL + YW + dy / 2, dy)
    return x, y, dx, dy


def solve_case(x, y, dx, dy, metal, guess):
    n2 = index_map(x, y, ETCH, WIDTH, metal)
    neff, vec, idx, resid = solve(n2, neff_guess=guess, dx=dx, dy=dy)
    return neff, mode_fields(vec, n2.shape, idx), resid, n2


def sample(psi, x, y, xc, yc):
    """Nearest-neighbour resampling of a mode onto a common grid."""
    ix = np.clip(np.searchsorted(x, xc), 0, x.size - 1)
    iy = np.clip(np.searchsorted(y, yc), 0, y.size - 1)
    return psi[np.ix_(iy, ix)]


def overlap(a, b):
    """Normalised unconjugated overlap of two lossy eigenmodes."""
    na, nb = np.sqrt(np.sum(a * a)), np.sqrt(np.sum(b * b))
    if na == 0 or nb == 0:
        return 0.0, 0.0
    c = np.sum(a * b) / (na * nb)
    return float(abs(c)), float(np.degrees(np.angle(c)))


def loss_db_cm(neff):
    return 4.343 * (2 * K0 * abs(neff.imag)) / 100.0



def run(verbose=True):
    xc, yc, _, _ = make_grid(MESHES[0][0], MESHES[0][1])
    rows, prev_metal = [], None
    if verbose:
        print(f"cross-section: LN {HLN*1e9:.0f} nm, etch {ETCH*1e9:.0f} nm, "
              f"ridge {WIDTH*1e6:.3f} um, Al {HAL*1e9:.0f} nm, "
              f"lambda {LAM*1e6:.2f} um, light along z")
        print(f"{'mesh':>13s} {'case':>9s} {'Re(neff)':>10s} {'Im(neff)':>11s} "
              f"{'dB/cm':>9s} {'resid':>9s} {'|ovl|':>7s} {'arg':>7s}")
    for dxn, dyn in MESHES:
        x, y, dx, dy = make_grid(dxn, dyn)
        tag = f"{dxn:.1f}/{dyn:.1f}nm"
        for metal in (False, True):
            neff, psi, res, n2 = solve_case(x, y, dx, dy, metal,
                                            guess=1.72 if metal else 1.84)
            row = dict(mesh=tag, case="metal" if metal else "no metal",
                       dx=dx, dy=dy, neff=neff, resid=res,
                       loss=loss_db_cm(neff), ovl=np.nan, arg=np.nan,
                       x=x, y=y, psi=psi, n2=n2)
            if metal:
                a = sample(psi, x, y, xc, yc)
                if prev_metal is not None:
                    b = sample(prev_metal["psi"], prev_metal["x"],
                               prev_metal["y"], xc, yc)
                    row["ovl"], row["arg"] = overlap(b, a)
                prev_metal = row
            rows.append(row)
            if verbose:
                print(f"{tag:>13s} {row['case']:>9s} {neff.real:10.5f} "
                      f"{neff.imag:+11.3e} {row['loss']:9.1f} {res:.1e} "
                      f"{row['ovl']:7.4f} {row['arg']:7.1f}")
    return rows


def boundary_test():
    print("\nboundary expansion (middle mesh, metal):")
    out = []
    dxn, dyn = MESHES[1]
    for xw in (XW0, 2.4e-6):
        x, y, dx, dy = make_grid(dxn, dyn, xw=xw)
        neff, psi, res, n2 = solve_case(x, y, dx, dy, True, guess=1.72)
        out.append(dict(xw=xw, neff=neff, loss=loss_db_cm(neff), resid=res))
        print(f"  xw {xw*1e6:.1f} um -> Re {neff.real:.5f}, "
              f"{loss_db_cm(neff):.1f} dB/cm, resid {res:.1e}")
    return out



def figures(rows):
    tag = f"{MESHES[1][0]:.1f}/{MESHES[1][1]:.1f}nm"
    ref = [r for r in rows if r["case"] == "metal" and r["mesh"] == tag]
    if not ref:
        return
    r = ref[0]
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.4))
    ax[0].pcolormesh(r["x"] * 1e6, r["y"] * 1e6, np.real(r["n2"]),
                     shading="auto", cmap="viridis")
    ax[0].set_title("real part of n^2 (structure)")
    ax[0].set_xlabel("x (um)")
    ax[0].set_ylabel("y (um)")
    ax[0].set_aspect("equal")
    for case, ls in (("no metal", "-"), ("metal", "--")):
        sel = [q for q in rows if q["case"] == case and q["mesh"] == tag]
        if sel:
            ax[1].plot(sel[0]["x"] * 1e6, np.abs(sel[0]["psi"]).sum(axis=0),
                       ls, lw=1.2, label=case)
    ax[1].set_title("|psi| summed over y")
    ax[1].set_xlabel("x (um)")
    ax[1].legend()
    fig.tight_layout()
    out = FIG / "cross_section_and_mode.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"\nfigure: {out}")


def verdict(rows, bnd):
    last_tag = f"{MESHES[-1][0]:.1f}/{MESHES[-1][1]:.1f}nm"
    prev_tag = f"{MESHES[-2][0]:.1f}/{MESHES[-2][1]:.1f}nm"
    last = [r for r in rows if r["mesh"] == last_tag and r["case"] == "metal"][0]
    prev = [r for r in rows if r["mesh"] == prev_tag and r["case"] == "metal"][0]
    d_re = abs(last["neff"].real - prev["neff"].real) / abs(prev["neff"].real) * 100
    d_loss = abs(last["loss"] - prev["loss"]) / max(prev["loss"], 1e-12) * 100
    ovl = last["ovl"]
    d_b_re = abs(bnd[1]["neff"].real - bnd[0]["neff"].real) / abs(bnd[0]["neff"].real) * 100
    d_b_loss = abs(bnd[1]["loss"] - bnd[0]["loss"]) / max(bnd[0]["loss"], 1e-12) * 100
    checks = [
        ("residual < 1e-8", all(r["resid"] < 1e-8 for r in rows), ""),
        ("dRe(neff), last two meshes < 0.1 %", d_re < 0.1, f"{d_re:.3f} %"),
        ("loss change, last two meshes < 5 %", d_loss < 5.0, f"{d_loss:.2f} %"),
        ("|overlap|, last two meshes > 0.99", (ovl == ovl) and ovl > 0.99,
         f"{ovl:.4f}"),
        ("boundary dRe < 0.1 %", d_b_re < 0.1, f"{d_b_re:.3f} %"),
        ("boundary loss change < 10 %", d_b_loss < 10.0, f"{d_b_loss:.2f} %"),
    ]
    print("\n=== verdict ===")
    for name, ok, val in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
              + (f"   ({val})" if val else ""))
    ok = all(c[1] for c in checks)
    print(f"\nOVERALL: {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("-> numbers may not be used downstream; fix the failing check first.")
    return checks, ok


def main():
    FIG.mkdir(exist_ok=True)
    rows = run()
    bnd = boundary_test()
    figures(rows)
    checks, ok = verdict(rows, bnd)
    with (HERE / "optical_validation.csv").open("w", newline="",
                                                encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["mesh", "case", "dx_nm", "dy_nm", "neff_real", "neff_imag",
                    "loss_dB_cm", "residual", "overlap_prev", "overlap_arg_deg"])
        for r in rows:
            w.writerow([r["mesh"], r["case"], f"{r['dx']*1e9:.2f}",
                        f"{r['dy']*1e9:.2f}", f"{r['neff'].real:.6f}",
                        f"{r['neff'].imag:.4e}", f"{r['loss']:.2f}",
                        f"{r['resid']:.1e}", f"{r['ovl']:.4f}", f"{r['arg']:.1f}"])
        for b in bnd:
            w.writerow([f"xw{b['xw']*1e6:.1f}um", "metal", "", "",
                        f"{b['neff'].real:.6f}", f"{b['neff'].imag:.4e}",
                        f"{b['loss']:.2f}", f"{b['resid']:.1e}", "", ""])
        w.writerow(["overall", "PASS" if ok else "FAIL"])
    print(f"\nWrote {HERE / 'optical_validation.csv'}")


if __name__ == "__main__":
    main()

