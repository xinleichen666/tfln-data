"""Order-of-magnitude audit of the optical response implied by the current model.

Post-processing only; nothing is re-solved.  Two existing exports are used:

  Wap_6um_mode_06_3.304066GHz.csv
      the manuscript's 6 um candidate.  Columns (10): x,y,z,x,y,z,eXX,eYY,eZZ,Ws
  idt3d_sus_mode_06_f3.302387GHz_field.csv
      the 10 um base model.  Columns (17): x,y,z,x,y,z,u,v,w,Ws,
      eXX,eYY,eZZ,eXY,eYZ,eXZ, mises

For the extraordinary polarization (Option A) the photoelastic contraction
contains no shear term, so the 6 um export is complete for that quantity.
Shear and displacement exist only in the 10 um export, which is why the
moving-boundary estimate is labelled with its own geometry.

Questions
  Q1  How strongly does the assumed 1 um FWHM Gaussian change the weighted
      photoelastic average compared with a mode this geometry supports?
  Q2  What drive would the modelled response need to reach the operating point
      of the earlier ring model (beta = 0.55/3.33 rad)?
  Q3  Is the omitted moving-boundary term negligible?

Nodal quadrature (every node weighted equally) is used for ratios only; the
eigenvectors carry arbitrary normalisation, so no absolute value here is a
prediction.
"""
from pathlib import Path
import csv
import numpy as np

from audit_optical_mode import slab, lateral, profile, NE, N_AIR, HLN, WSTACK

HERE = Path(__file__).parent
ROOT = Path(r"D:\comsol_ao_run")
DATA6 = ROOT / "Wap_6um_mode_06_3.304066GHz.csv"
DATA10 = ROOT / "idt3d_sus_mode_06_f3.302387GHz_field.csv"
LAM = 1.55e-6
K0 = 2 * np.pi / LAM
P31, P33 = 0.179, 0.071
Z0 = 2e-6
DN_PER_V_REPORTED = 1.545e-7      # driven photoelastic estimate, 5.5 um centre
ZC = 5.5e-6


def load(path):
    with path.open("r", encoding="latin-1") as fh:
        a = np.loadtxt(fh, delimiter=",", comments="%")
    n = a.shape[1]
    x, y, z = a[:, 0], a[:, 1], a[:, 2]
    if n == 10:      # eXX,eYY,eZZ at 6..8, Ws at 9; no displacement, no shear
        exx, eyy, ezz = a[:, 6], a[:, 7], a[:, 8]
        u = v = w = exz = None
    elif n == 17:    # u,v,w at 6..8, Ws at 9, strains at 10..15, mises at 16
        u, v, w = a[:, 6], a[:, 7], a[:, 8]
        exx, eyy, ezz = a[:, 10], a[:, 11], a[:, 12]
        exz = a[:, 15]
    else:
        raise SystemExit(f"{path.name}: unexpected column count {n}")
    keep = (y >= -1e-9) & (y <= HLN + 1e-9)
    wap = float(z.max() - 4e-6)   # Wstack = Wap + 2 um margin on each side
    print(f"{path.name}: {n} columns, {keep.sum()} LN nodes, "
          f"z_max {z.max()*1e6:.2f} um -> inferred aperture {wap*1e6:.1f} um")
    return dict(x=x[keep], y=y[keep], z=z[keep], exx=exx[keep], eyy=eyy[keep],
                ezz=ezz[keep], u=None if u is None else u[keep],
                v=None if v is None else v[keep], w=None if w is None else w[keep],
                exz=None if exz is None else exz[keep], wap=wap)


def optical_weights():
    v_neff = slab(NE, N_AIR, N_AIR, HLN, pol="TE")
    lat_neff = lateral(v_neff, N_AIR, WSTACK)
    # vertical profile: core index is the LN index, NOT the effective index
    y, iy = profile(NE, N_AIR, v_neff, HLN / 2, span=3.0)
    z, iz = profile(v_neff, N_AIR, lat_neff, WSTACK / 2, span=1.2)

    def phi2(yy):
        return np.interp(yy, y, iy)

    def psi2(zz, zc):
        return np.interp(zz - zc, z, iz)

    return phi2, psi2, v_neff, lat_neff, z, iz


def gauss2(zz, zc, fwhm):
    return np.exp(-4 * np.log(2) * ((zz - zc) / fwhm) ** 2)


def wmean(values, weights):
    return float(np.sum(values * weights) / np.sum(weights))



def q0(d, phi2):
    """Is the one-period average used by the proxy a phase-resolved measure?

    Compares the plain nodal average of dn with its acoustic-wavevector
    Fourier component exp(-iKx).  If the two differ substantially and the
    plain average changes sign between z bins, the proxy is dominated by
    sampling, not by the phase-matched acousto-optic contribution.
    """
    K = 2 * np.pi / 2.58e-6
    dn = -(NE ** 3 / 2) * (P31 * (d["eyy"] + d["exx"]) + P33 * d["ezz"])
    w = phi2(d["y"])
    ph = K * d["x"]
    sw = w.sum()
    plain = float((w * dn).sum() / sw)
    fc = float((w * dn * np.cos(ph)).sum() / sw)
    fs = float((w * dn * np.sin(ph)).sum() / sw)
    amp = float(np.hypot(fc, fs))
    print("\n=== Q0: is the one-period average a phase-resolved quantity? ===")
    print(f"plain nodal average      {plain:+.3e}")
    print(f"K-component (Re, Im)     {fc:+.3e}, {fs:+.3e}")
    print(f"|K-component|            {amp:.3e}")
    print(f"ratio |plain| / |K|      {abs(plain)/amp:.1f}")
    print(f"mean |dn|                {float((w*np.abs(dn)).sum()/sw):.3e}")
    frac_top = float(np.mean(d["y"] > 0.45e-6))
    print(f"share of nodes above y = 450 nm: {frac_top*100:.1f}% "
          "(mesh clustering biases unweighted node sums)")
    edges = np.linspace(d["z"].min(), d["z"].max(), 21)
    idx = np.digitize(d["z"], edges) - 1
    rows = []
    for i in range(20):
        m = idx == i
        if m.sum() < 20:
            continue
        p = float((w[m] * dn[m]).sum() / w[m].sum())
        a = float(np.hypot((w[m]*dn[m]*np.cos(ph[m])).sum(),
                           (w[m]*dn[m]*np.sin(ph[m])).sum()) / w[m].sum())
        rows.append((float((edges[i]+edges[i+1])/2*1e6), int(m.sum()), p, a))
    print(f"{'z_um':>6s} {'n':>6s} {'plain':>12s} {'|K|':>12s}")
    for zc, n, p, a in rows:
        print(f"{zc:6.2f} {n:6d} {p:+12.3e} {a:12.3e}")
    flips = sum(1 for i in range(1, len(rows)) if rows[i][2] * rows[i-1][2] < 0)
    print(f"sign changes of the plain average between adjacent z bins: {flips}")
    print("-> the plain average and its K-component differ by about an order of")
    print("   magnitude and the plain average changes sign along z.  Two readings")
    print("   are possible and this export cannot separate them: (i) the field")
    print("   really alternates along z, or (ii) unweighted node sampling does not")
    print("   integrate the acoustic phase.  Either way the plain average is not a")
    print("   validated figure of merit; it must be replaced by a volume-weighted,")
    print("   phase-explicit integral computed inside COMSOL before any ranking.")
    return plain, amp, rows, flips


def q1(d, phi2, psi2):
    """Optical weighting comparison.  Note: inherits the Q0 caveat."""
    dn = -(NE ** 3 / 2) * (P31 * (d["eyy"] + d["exx"]) + P33 * d["ezz"])
    wg = phi2(d["y"]) * gauss2(d["z"], ZC, 1e-6)
    wr = phi2(d["y"]) * psi2(d["z"], ZC)
    g, r = wmean(dn, wg), wmean(dn, wr)
    print("\n=== Q1: optical weighting on the 6 um candidate ===")
    print(f"1.0 um FWHM Gaussian : <dn> = {g:+.4e}")
    print(f"supported EIM mode   : <dn> = {r:+.4e}")
    print(f"ratio |real|/|gauss| : {abs(r)/abs(g):.4f}")
    print(f"coherence |<dn>|/<|dn|>: gauss {abs(g)/wmean(abs(dn), wg):.4f}, "
          f"real {abs(r)/wmean(abs(dn), wr):.4f}")
    print("   small coherence -> positive and negative regions cancel, so the")
    print("   number follows the weighting more than the acoustics.")
    t1, t2 = P31 * (d["eyy"] + d["exx"]), P33 * d["ezz"]
    print(f"   |p31(e_xx+e_yy)| = {abs(wmean(t1, wr)):.3e}, "
          f"|p33 e_zz| = {abs(wmean(t2, wr)):.3e}, "
          f"|sum| = {abs(wmean(t1 + t2, wr)):.3e}")

    zc = np.linspace(Z0, Z0 + d["wap"], 161)
    out = {}
    for tag, wfun in (("gauss", lambda c: gauss2(d["z"], c, 1e-6)),
                      ("real", lambda c: psi2(d["z"], c))):
        vals = np.array([abs(wmean(dn, phi2(d["y"]) * wfun(c))) for c in zc])
        edge = (zc <= Z0 + 1e-6) | (zc >= Z0 + d["wap"] - 1e-6)
        inner = (zc >= Z0 + 2e-6) & (zc <= Z0 + d["wap"] - 2e-6)
        out[tag] = vals
        print(f"   {tag:5s}: best edge {vals[edge].max():.4e}, "
              f"best interior {vals[inner].max():.4e}, "
              f"edge/interior {vals[edge].max()/vals[inner].max():.3f}")
    print(f"   placement spread over the aperture: gauss "
          f"{out['gauss'].max()/out['gauss'].min():.2f}x, "
          f"real {out['real'].max()/out['real'].min():.2f}x")
    return dn, g, r, out


def q2(g, r):
    ratio = abs(r) / abs(g)
    dn_per_V = DN_PER_V_REPORTED * ratio
    beta_t = 0.55 / 3.33
    print("\n=== Q2: drive needed for the earlier ring operating point ===")
    print(f"reported {DN_PER_V_REPORTED:.3e} /V (1 um Gaussian, 5.5 um centre)")
    print(f"rescaled to the supported mode: {dn_per_V:.3e} /V  (x{ratio:.3f})")
    print(f"operating point beta = {beta_t:.4f} rad (0.55 GHz at 3.33 GHz)")
    print(f"{'L_int':>7s} {'beta/V':>12s} {'V for beta_t':>15s} {'P (50 ohm)':>14s}")
    for L in (6e-6, 20e-6, 100e-6):
        b = K0 * dn_per_V * L
        V = beta_t / b
        print(f"{L*1e6:6.0f}um {b:12.3e} {V:14.3e} V {V**2/(2*50):13.3e} W")
    b100 = K0 * dn_per_V * 100e-6
    print(f"weak-modulation PM at 1 V, 100 um: single-sideband fraction "
          f"(beta/2)^2 = {(b100/2)**2:.2e}")
    print(f"old model implies beta/V = {beta_t/0.0258:.2f} rad/V; "
          f"this route gives {b100:.2e} rad/V")
    print("CAUTION: these two numbers are NOT the same quantity.  The ring model")
    print("uses a cavity detuning per volt after an external VpiL calibration from")
    print("another device; the number above is a single-pass phase index.  The")
    print("comparison is recorded only to show that no calibration currently links")
    print("them.  It must not be quoted as a performance gap.")
    return dn_per_V, b100


def q3(d, phi2, psi2, v_neff):
    print("\n=== Q3: moving boundary vs photoelastic (10 um export) ===")
    if d["v"] is None:
        print("no displacement in this export")
        return None
    ymin, ymax = d["y"].min(), d["y"].max()
    wr = phi2(d["y"]) * psi2(d["z"], ZC)
    dn = -(NE ** 3 / 2) * (P31 * (d["eyy"] + d["exx"]) + P33 * d["ezz"])
    pe = abs(wmean(dn, wr))

    def surf(mask):
        return wmean(np.abs(d["v"][mask]), psi2(d["z"][mask], ZC))

    top = np.abs(d["y"] - ymax) < 10e-9
    bot = np.abs(d["y"] - ymin) < 10e-9
    vt, vb = surf(top), surf(bot)
    dn_mb = ((NE ** 2 - 1) / (2 * v_neff)) * (
        phi2(np.array([ymax]))[0] * vt + phi2(np.array([ymin]))[0] * vb)
    print(f"mean |v_y| top {vt*1e12:.2f} pm, bottom {vb*1e12:.2f} pm "
          "(mode-weighted, arbitrary normalisation)")
    print(f"|dn_MB| = {abs(dn_mb):.3e} vs |<dn_PE>| = {pe:.3e}; "
          f"MB/PE = {abs(dn_mb)/pe:.1f}")
    print("CAUTION: the surface displacement was taken as |v_y| without projecting")
    print("onto the local surface normal or keeping the sign, so cancellations are")
    print("lost and this ratio is an upper bound of unknown accuracy.  It is")
    print("recorded only to show that MB cannot be assumed negligible; the")
    print("quantity must be computed properly, not quoted.")
    return abs(dn_mb) / pe



def main():
    phi2, psi2, v_neff, lat_neff, zv, izv = optical_weights()
    fw = zv[izv >= 0.5 * izv.max()]
    print(f"\nEIM: vertical neff {v_neff:.5f}, lateral neff {lat_neff:.5f}, "
          f"lateral intensity FWHM {(fw.max()-fw.min())*1e6:.2f} um")

    d6 = load(DATA6)
    plain, kamp, rows, flips = q0(d6, phi2)
    dn, g, r, out = q1(d6, phi2, psi2)
    dn_per_V, b100 = q2(g, r)

    d10 = load(DATA10)
    mb = q3(d10, phi2, psi2, v_neff)

    with (HERE / "response_magnitude_audit.csv").open("w", newline="",
                                                      encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "value", "note"])
        w.writerow(["plain_one_period_average", plain, "unweighted nodal sum"])
        w.writerow(["K_component_amplitude", kamp, "phase-matched component"])
        w.writerow(["plain_over_K", abs(plain) / kamp, "aliasing inflation factor"])
        w.writerow(["z_bin_sign_changes", flips, "of 20 bins"])
        w.writerow(["wmean_dn_gaussian_1um", g, "proxy level, see Q0"])
        w.writerow(["wmean_dn_supported_mode", r, "proxy level, see Q0"])
        w.writerow(["coherence_gaussian",
                    abs(g) / wmean(abs(dn), phi2(d6["y"]) * gauss2(d6["z"], ZC, 1e-6)), ""])
        w.writerow(["coherence_supported",
                    abs(r) / wmean(abs(dn), phi2(d6["y"]) * psi2(d6["z"], ZC)), ""])
        w.writerow(["ratio_supported_over_gaussian", abs(r) / abs(g), ""])
        w.writerow(["dn_per_V_rescaled", dn_per_V,
                    "ratio applied to the reported value"])
        w.writerow(["beta_per_V_L100um", b100, "rad/V"])
        if mb is not None:
            w.writerow(["MB_over_PE", mb, "10 um export, order of magnitude"])
    print(f"\nWrote {HERE / 'response_magnitude_audit.csv'}")


if __name__ == "__main__":
    main()
