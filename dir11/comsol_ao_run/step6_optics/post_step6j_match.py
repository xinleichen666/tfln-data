"""Step 6j post-processing: series/parallel grouping of K feed segments to approach 50 ohm, no matching network.

K = s*q segments of length L/K each (distributed RC line, same model as post_step6h.py). s segments in series, q strings in
parallel: Z_tot = Z_seg*s/q. Each segment still needs the V_pi drive, i.e. current I_pi/K, as in the all-parallel case, so
P_load = K*Re(Z_seg)*|I_pi/K|^2/2 is unchanged by the grouping; a 50 ohm source must supply
the available power P_av = P_load/(1-|Gamma|^2), Gamma = (Z_tot-50)/(Z_tot+50). Bus bars, crossings and isolation ideal.
Segments shorter than SEG_MIN are not allowed (the 2D cross-section assumption needs segments much longer than the gaps).
Usage: python post_step6j_match.py <log> [<log> ...]  -> step6j_match.log
"""
import cmath
import math
import os
import re
import sys

D = os.path.dirname(os.path.abspath(__file__))
LAM = 1.55e-6
K0 = 2 * math.pi / LAM
RHO = 2.8e-8
R0 = 50.0
LS = [0.1e-3, 0.2e-3, 0.5e-3, 1e-3, 2e-3]
KS = [1, 2, 4, 8, 16, 32, 64]
SEG_MIN = 25e-6


def read(path):
    data, cfg = {}, {}
    pat = re.compile(r"^F6J set=\S+ f_GHz=([\d.]+) .*abs_tot=([-\d.e+]+) ReY_Spm=([-\d.e+]+) ImY_Spm=([-\d.e+]+)")
    peaks = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = pat.match(line)
            if m:
                data[float(m.group(1))] = (float(m.group(2)), complex(float(m.group(3)), float(m.group(4))))
            m = re.match(r"^CFG6J case=(\S+) p_um=([\d.]+) NP=(\d+) .*hAl_nm=(\d+) nPairs=(\d+) .*ridge=1.0um x (\d+)nm", line)
            if m:
                cfg = dict(case=m.group(1), p=float(m.group(2)) * 1e-6, np=int(m.group(3)), t=float(m.group(4)) * 1e-9,
                           npairs=int(m.group(5)), hr=int(m.group(6)))
            m = re.match(r"^PEAK6J set=\S+ f_peak_GHz=([\d.]+) abs_tot_peak=([-\d.e+]+)", line)
            if m:
                peaks.append((float(m.group(1)), float(m.group(2))))
    return data, cfg, peaks


def z_seg(Y, l, r):
    g = cmath.sqrt(2 * r * Y)
    return (r / g) / cmath.tanh(g * l / 2) + r * l / 2


def evaluate(tot, Y, L, r, K, s):
    q = K // s
    I = math.pi * abs(Y) / (K0 * tot)
    Zs = z_seg(Y, L / K, r)
    P_load = K * Zs.real * (I / K) ** 2 / 2
    Zt = Zs * s / q
    G = (Zt - R0) / (Zt + R0)
    P_av = P_load / (1 - abs(G) ** 2)
    return P_av, P_load, Zt, I


out = []
for lg in sys.argv[1:]:
    data, cfg, peaks = read(os.path.join(D, lg))
    if not data or not cfg:
        out.append(f"MISSING {lg}")
        continue
    w = 0.25 * cfg["p"]
    r = RHO / (w * cfg["t"]) / cfg["npairs"]
    out.append(f"CASEM case={cfg['case']} NP={cfg['np']} npairs={cfg['npairs']} hR_nm={cfg['hr']} p_um={cfg['p']*1e6:.4f} "
               f"w_finger_um={w*1e6:.4f} r_group_ohm_per_mm={r*1e-3:.2f}")
    fs = sorted(data)
    for fpk, tpk in peaks:
        reg = [f for f in fs if fpk - 0.004 <= f <= fpk + 0.004]
        tot0, Y0 = data[min(reg, key=lambda x: abs(x - fpk))]
        PL = Y0.real * (LAM / (2 * tot0)) ** 2 / 2
        out.append(f"PKM case={cfg['case']} f_GHz={fpk:.6f} abs_tot={tot0:.4e} Y_Spm=({Y0.real:.2f},{Y0.imag:.2f}) P*L_ideal_Wm={PL:.3e}")
        for L in LS:
            best = None
            for K in KS:
                if K > 1 and L / K < SEG_MIN:
                    continue
                for s in [d for d in range(1, K + 1) if K % d == 0]:
                    for f in reg:
                        P_av, P_load, Zt, I = evaluate(*data[f], L, r, K, s)
                        if best is None or P_av < best[0]:
                            best = (P_av, P_load, Zt, K, s, f)
            P_av, P_load, Zt, K, s, f = best
            out.append(f"MATCHM case={cfg['case']} f_pk={fpk:.4f} L_mm={L*1e3:.1f} best: K={K} series={s} parallel={K//s} f_GHz={f:.6f} "
                       f"Z_tot_ohm=({Zt.real:.2f},{Zt.imag:.2f}) P_load_mW={P_load*1e3:.2f} P_source_avail_mW={P_av*1e3:.2f} "
                       f"ideal_mW={PL/L*1e3:.2f}")

text = "\n".join(out)
print(text)
with open(os.path.join(D, "step6j_match.log"), "w", encoding="utf-8") as fh:
    fh.write(text + "\n")
