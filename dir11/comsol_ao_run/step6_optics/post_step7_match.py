"""Step 7 post-processing: series/parallel grouping using the 3D segment results (bus bars, finger tips, gaps included).

The 3D cell is one feed segment of length Lz, so K = L/Lz segments; s in series, q = K/s strings in parallel.
Y per length from the 3D model already contains the bus-bar capacitance. Same distributed RC finger model, drive and
50 ohm source as post_step6j_match.py. Frequencies are restricted to the main peak (|tot| >= 0.5 of the peak).
Usage: python post_step7_match.py <log> [<log> ...]  -> step7_match.log
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
NPAIRS = 4


def read(path):
    data, cfg, peak = {}, {}, None
    pat = re.compile(r"^F7 f_GHz=([\d.]+) .*abs_tot=([-\d.e+]+) ReY_Spm=([-\d.e+]+) ImY_Spm=([-\d.e+]+)")
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = pat.match(line)
            if m:
                data[float(m.group(1))] = (float(m.group(2)), complex(float(m.group(3)), float(m.group(4))))
            m = re.match(r"^CFG7 case=(\S+) bus=(\S+) (?:trench=\S+ )?Lz_um=([\d.]+) hxy_nm=(\d+) hz_nm=(\d+) p_um=([\d.]+) .*hAl_nm=(\d+)", line)
            if m:
                cfg = dict(case=m.group(1), bus=m.group(2) == "true", lz=float(m.group(3)) * 1e-6, hxy=int(m.group(4)),
                           hz=int(m.group(5)), p=float(m.group(6)) * 1e-6, t=float(m.group(7)) * 1e-9)
            m = re.match(r"^PEAK7 set=\S+ f_peak_GHz=([\d.]+) abs_tot_peak=([-\d.e+]+)", line)
            if m and peak is None:
                peak = (float(m.group(1)), float(m.group(2)))
    return data, cfg, peak


def z_seg(Y, l, r):
    g = cmath.sqrt(2 * r * Y)
    return (r / g) / cmath.tanh(g * l / 2) + r * l / 2


def evaluate(tot, Y, L, lz, r, K, s):
    q = K // s
    I = math.pi * abs(Y) / (K0 * tot)
    Zs = z_seg(Y, lz, r)
    P_load = K * Zs.real * (I / K) ** 2 / 2
    Zt = Zs * s / q
    G = (Zt - R0) / (Zt + R0)
    return P_load / (1 - abs(G) ** 2), P_load, Zt


out = []
for lg in sys.argv[1:]:
    data, cfg, peak = read(os.path.join(D, lg))
    if not data or not cfg or not cfg["bus"]:
        out.append(f"SKIP {lg}")
        continue
    r = RHO / (0.25 * cfg["p"] * cfg["t"]) / NPAIRS
    fpk, apk = peak
    reg = [f for f in sorted(data) if data[f][0] >= 0.5 * apk]
    tot0, Y0 = data[min(data, key=lambda x: abs(x - fpk))]
    PLpk = Y0.real * (LAM / (2 * tot0)) ** 2 / 2
    fb = min(reg, key=lambda f: data[f][1].real / data[f][0] ** 2)
    PLb = data[fb][1].real * (LAM / (2 * data[fb][0])) ** 2 / 2
    out.append(f"CASE7M case={cfg['case']} Lz_um={cfg['lz']*1e6:.0f} hxy_nm={cfg['hxy']} hz_nm={cfg['hz']} n_freq={len(data)} "
               f"n_mainpeak={len(reg)} f_pk={fpk:.6f} abs_tot={tot0:.4e} Y_Spm=({Y0.real:.2f},{Y0.imag:.2f}) PL_peak_Wm={PLpk:.3e} "
               f"f_best={fb:.6f} PL_best_Wm={PLb:.3e}")
    for L in LS:
        K = round(L / cfg["lz"])
        best = None
        for s in [d for d in range(1, K + 1) if K % d == 0]:
            for f in reg:
                P_av, P_load, Zt = evaluate(*data[f], L, cfg["lz"], r, K, s)
                if best is None or P_av < best[0]:
                    best = (P_av, P_load, Zt, s, f)
        P_av, P_load, Zt, s, f = best
        out.append(f"MATCH7 case={cfg['case']} L_mm={L*1e3:.1f} K={K} series={s} parallel={K//s} f_GHz={f:.6f} "
                   f"Z_tot_ohm=({Zt.real:.1f},{Zt.imag:.1f}) P_load_mW={P_load*1e3:.2f} P_source_avail_mW={P_av*1e3:.2f}")

text = "\n".join(out)
print(text)
with open(os.path.join(D, "step7_match.log"), "w", encoding="utf-8") as fh:
    fh.write(text + "\n")
