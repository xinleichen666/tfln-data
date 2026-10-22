"""Step 6j post-processing: electrode-limited source power for V_pi (Shao orientation, period 1.9389 um, NP=11).

Cases: T100 (NP=15, Al 100 nm; data from step6f.log + step6gY.log), T200/T300 (NP=15, Al 200/300 nm) and NP11/NP9/NP7 (NP=11/9/7, Al 100 nm)
from step6h_<case>.log. Distributed RC model of post_step6g.py; segmented feeding with K parallel segments of length L/K.
Output: step6j_power.log
"""
import cmath
import math
import os
import re

D = os.path.dirname(os.path.abspath(__file__))
LAM = 1.55e-6
K0 = 2 * math.pi / LAM
RHO = 2.8e-8
P_UM = 1.9389
W_F = 0.25 * P_UM * 1e-6
LS_SEG = [0.1e-3, 0.2e-3, 1e-3]
KS = [1, 2, 4, 8, 16, 32]

CASES = {
    "P1938900": dict(t=100e-9, npairs=8, logs=["step6j_P1938900.log"], tag="F6J"),
}
BASE_PEAKS = {"MAIN": 3.338550, "LOW": 3.318700}


def read_case(c):
    cfg = CASES[c]
    pat = re.compile(r"^%s set=(\S+) f_GHz=([\d.]+) .*abs_tot=([-\d.e+]+) ReY_Spm=([-\d.e+]+) ImY_Spm=([-\d.e+]+)" % cfg["tag"])
    data, peaks = {}, {}
    for lg in cfg["logs"]:
        p = os.path.join(D, lg)
        if not os.path.exists(p):
            return None, None
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = pat.match(line)
                if m:
                    data[float(m.group(2))] = (float(m.group(3)), complex(float(m.group(4)), float(m.group(5))))
                m = re.match(r"^MATCH6J case=\S+ pk(\d+) f_drive_GHz=([\d.]+) .*u_frac=([\d.]+) v_frac=([\d.]+) w_frac=([\d.]+) fracAl=([\d.]+)", line)
                if m:
                    u, v, w = float(m.group(3)), float(m.group(4)), float(m.group(5))
                    pol = "v" if v > 0.5 else ("u" if u > 0.5 else ("w" if w > 0.5 else "mixed"))
                    lab = "pk%s_%s" % (m.group(1), pol)
                    peaks[lab] = (float(m.group(2)), u, v, w, float(m.group(6)))
    if c == "T100":
        peaks = {k: (f, None, None, None, None) for k, f in BASE_PEAKS.items()}
    return data, peaks


def z_dist(Y, L, r):
    g = cmath.sqrt(2 * r * Y)
    return (r / g) / cmath.tanh(g * L / 2) + r * L / 2, g


def p_src(tot, Y, L, r, K=1):
    """matched source power for V_pi with K parallel segments of length L/K (current I_pi/K each)."""
    I = math.pi * abs(Y) / (K0 * tot)
    Z, g = z_dist(Y, L / K, r)
    return K * Z.real * (I / K) ** 2 / 2, Z, I, g


out = [f"CFG6J rho={RHO:.2e} ohm*m w_finger={W_F*1e6:.4f} um; distributed opposite-end-fed RC line per segment; "
       f"I_pi = pi|Y|/(k0|tot|); P = K*Re(Z_seg(L/K))*|I_pi/K|^2/2; lossless match to 50 ohm; bus bars and feed network ideal"]
summary = []
for c, cfg in CASES.items():
    data, peaks = read_case(c)
    if data is None:
        out.append(f"CASE6J {c} MISSING")
        continue
    r_f = RHO / (W_F * cfg["t"])
    r = r_f / cfg["npairs"]
    out.append(f"CASE6J {c} t_Al_nm={cfg['t']*1e9:.0f} npairs={cfg['npairs']} r_finger_ohm_per_mm={r_f*1e-3:.1f} r_group_ohm_per_mm={r*1e-3:.2f} npts={len(data)}")
    fs_all = sorted(data)
    for lab, pk in sorted(peaks.items()):
        fpk = pk[0]
        reg = [f for f in fs_all if fpk - 0.003 <= f <= fpk + 0.006]
        f0 = min(reg, key=lambda x: abs(x - fpk))
        tot0, Y0 = data[f0]
        extra = "" if pk[1] is None else f" eig_uvw=({pk[1]:.3f},{pk[2]:.3f},{pk[3]:.3f}) fracAl={pk[4]:.4f}"
        out.append(f"PK6J case={c} peak={lab} f_GHz={f0:.6f} abs_tot={tot0:.4e} Y_Spm=({Y0.real:.4e},{Y0.imag:.4e}) "
                   f"I_pi_A={math.pi*abs(Y0)/(K0*tot0):.4f} region_GHz=[{reg[0]:.4f},{reg[-1]:.4f}] n={len(reg)}{extra}")
        # K=1 optimum over f and L
        best = None
        for j in range(241):
            L = 10 ** (-5 + j * (math.log10(5e-3) + 5) / 240)
            for f in reg:
                P, Z, I, g = p_src(*data[f], L, r)
                if best is None or P < best[0]:
                    best = (P, L, f, Z, I, g)
        P, L, f, Z, I, g = best
        out.append(f"OPT6J case={c} peak={lab} K=1 L_opt_um={L*1e6:.1f} f_GHz={f:.6f} P_source_W={P:.4f} Zin_ohm=({Z.real:.3f},{Z.imag:.3f}) "
                   f"I_pi_A={I:.4f} |V_in|_V={abs(Z*I):.2f} abs_tot={data[f][0]:.4e} at_region_edge={f in (reg[0], reg[-1])}")
        summary.append((c, lab, "K1opt", L, f, P))
        # segmented feeding
        for L in LS_SEG:
            for K in KS:
                Pp, Zp, Ip, gp = p_src(tot0, Y0, L, r, K)
                bf, bP = None, None
                for f in reg:
                    Pf = p_src(*data[f], L, r, K)[0]
                    if bP is None or Pf < bP:
                        bf, bP = f, Pf
                out.append(f"SEG6J case={c} peak={lab} L_mm={L*1e3:.1f} K={K} seg_len_um={L/K*1e6:.1f} "
                           f"at_peak: P_source_W={Pp:.4f} Zseg_ohm=({Zp.real:.3f},{Zp.imag:.3f}) Ztot_ohm=({Zp.real/K:.3f},{Zp.imag/K:.3f}) |gamma*L/K|={abs(gp*L/K):.3f} "
                           f"| f_opt_GHz={bf:.6f} P_source_opt_W={bP:.4f}")
                summary.append((c, lab, f"L{L*1e3:.1f}K{K}", L, bf, bP))
        # best over K (<=8) and L
        bestk = None
        for K in KS:
            for j in range(241):
                L = 10 ** (-5 + j * (math.log10(5e-3) + 5) / 240)
                for f in reg:
                    Pk = p_src(*data[f], L, r, K)[0]
                    if bestk is None or Pk < bestk[0]:
                        bestk = (Pk, K, L, f)
        out.append(f"OPTK6J case={c} peak={lab} best_over_K<=32_L_f: K={bestk[1]} L_um={bestk[2]*1e6:.1f} f_GHz={bestk[3]:.6f} P_source_W={bestk[0]:.4f}")

text = "\n".join(out)
print(text)
with open(os.path.join(D, "step6j_power.log"), "w", encoding="utf-8") as fh:
    fh.write(text + "\n")

