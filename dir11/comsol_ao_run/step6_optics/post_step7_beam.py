"""Step 7 support beams: summary per case against the no-beam reference (same mesh, period, bus width).

Per log: main-peak frequency, drive Q, peak P*L, ratio to the reference, number of side peaks (local maxima of |tot|
above 20% of the main peak within the sweep), and the L = 1 mm source power for 2 series x 5 parallel and 10 parallel
(same distributed-RC network as post_step7_spread.py, drive frequency optimised within +-4 MHz of the peak).
Usage: python post_step7_beam.py <ref_log> <log> [<log> ...]  -> step7_beam.log
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
NPAIRS = 4


def read(path):
    fs, Ys, ts, cfg, peak = [], [], [], {}, None
    pat = re.compile(r"^F7 f_GHz=([\d.]+) PE=\(([^,]+),([^)]+)\) EO=\(([^,]+),([^)]+)\) MB=\(([^,]+),([^)]+)\) "
                     r"abs_tot=\S+ ReY_Spm=(\S+) ImY_Spm=(\S+)")
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = pat.match(line)
            if m:
                v = [float(x) for x in m.groups()]
                fs.append(v[0])
                ts.append(complex(v[1], v[2]) + complex(v[3], v[4]) + complex(v[5], v[6]))
                Ys.append(complex(v[7], v[8]))
            m = re.match(r"^CFG7 case=(\S+) .*Lz_um=([\d.]+) .*p_um=([\d.]+) .*hAl_nm=(\d+)", line)
            if m:
                cfg = dict(case=m.group(1), lz=float(m.group(2)) * 1e-6, p=float(m.group(3)) * 1e-6, t=float(m.group(4)) * 1e-9)
            m = re.match(r"^PEAK7 set=\S+ f_peak_GHz=([\d.]+) abs_tot_peak=(\S+) FWHM_MHz=(\S+) Q=(\S+) ReY_Spm=(\S+)", line)
            if m and peak is None:
                peak = dict(f=float(m.group(1)), a=float(m.group(2)), fwhm=float(m.group(3)), q=float(m.group(4)), rey=float(m.group(5)))
    o = sorted(range(len(fs)), key=lambda i: fs[i])
    return [fs[i] for i in o], [Ys[i] for i in o], [ts[i] for i in o], cfg, peak


def z_seg(Y, lz, r):
    g = cmath.sqrt(2 * r * Y)
    return (r / g) / cmath.tanh(g * lz / 2) + r * lz / 2


def power(Y, t, K, s, lz, r):
    q = K // s
    Zs = z_seg(Y, lz, r)
    I = 1 / (s * Zs)
    phi = q * s * K0 * t * I / Y
    k = math.pi / abs(phi)
    Pl = K * Zs.real * abs(I * k) ** 2 / 2
    Zt = Zs * s / q
    G = (Zt - R0) / (Zt + R0)
    return Pl / (1 - abs(G) ** 2), Zt


def summary(path):
    fs, Ys, ts, cfg, pk = read(path)
    a = [abs(x) for x in ts]
    PL = pk["rey"] * (LAM / (2 * pk["a"])) ** 2 / 2
    side = sum(1 for i in range(1, len(a) - 1) if a[i] > a[i - 1] and a[i] >= a[i + 1] and a[i] > 0.2 * pk["a"]
               and abs(fs[i] - pk["f"]) > 1e-6)
    r = RHO / (0.25 * cfg["p"] * cfg["t"]) / NPAIRS
    K = round(1e-3 / cfg["lz"])
    res = {}
    for s in (2, 1):
        best = None
        for i, f in enumerate(fs):
            if abs(f - pk["f"]) > 0.004:
                continue
            P, Zt = power(Ys[i], ts[i], K, s, cfg["lz"], r)
            if best is None or P < best[0]:
                best = (P, Zt, f)
        res[s] = best
    return cfg["case"], pk, PL, side, res


ref = summary(os.path.join(D, sys.argv[1]))
out = []
for lg in sys.argv[1:]:
    case, pk, PL, side, res = summary(os.path.join(D, lg))
    out.append(f"BEAMSUM case={case} f_pk={pk['f']:.6f} df_MHz={(pk['f']-ref[1]['f'])*1e3:+.2f} Q_drv={pk['q']:.0f} "
               f"Q_ratio={pk['q']/ref[1]['q']:.3f} PL_peak={PL:.3e} PL_ratio={PL/ref[2]:.3f} side_peaks={side} "
               f"P1mm_2s5p_mW={res[2][0]*1e3:.2f} Z=({res[2][1].real:.0f},{res[2][1].imag:.0f}) "
               f"P1mm_10p_mW={res[1][0]*1e3:.2f} Z=({res[1][1].real:.0f},{res[1][1].imag:.0f})")
text = "\n".join(out)
print(text)
with open(os.path.join(D, "step7_beam.log"), "w", encoding="utf-8") as fh:
    fh.write(text + "\n")
