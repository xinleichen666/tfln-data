"""Step 7 feed network with resonance spread between segments.

Each 100 um segment i gets its own frequency offset d_i: Y_i(f) = Y(f - d_i), tot_i(f) = tot(f - d_i), taken from one 3D
wide-sweep log (complex tot = PE + EO + MB). Segments are wired s in series x q in parallel. For a string current I_j the
segment terminal voltage follows the distributed RC finger model; the modulating (intrinsic) voltage is I_seg / (Y_i lz).
Phases add as complex numbers. Drive is scaled so |sum phase| = pi; the drive frequency is re-optimised per realisation.
Spread models: random Gaussian sigma (Monte Carlo) and a linear gradient end-to-end across the device.
Usage: python post_step7_spread.py <log>  -> step7_spread.log
"""
import cmath
import math
import os
import random
import re
import sys

D = os.path.dirname(os.path.abspath(__file__))
LAM = 1.55e-6
K0 = 2 * math.pi / LAM
RHO = 2.8e-8
R0 = 50.0
NPAIRS = 4
NMC = 100


def read(path):
    fs, Ys, ts, cfg = [], [], [], {}
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
    order = sorted(range(len(fs)), key=lambda i: fs[i])
    return [fs[i] for i in order], [Ys[i] for i in order], [ts[i] for i in order], cfg


def interp(fs, vs, f):
    if f <= fs[0]:
        return vs[0]
    if f >= fs[-1]:
        return vs[-1]
    lo, hi = 0, len(fs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if fs[mid] <= f:
            lo = mid
        else:
            hi = mid
    a = (f - fs[lo]) / (fs[hi] - fs[lo])
    return vs[lo] * (1 - a) + vs[hi] * a


def z_seg(Yl, lz, r):
    Y = Yl
    g = cmath.sqrt(2 * r * Y)
    return (r / g) / cmath.tanh(g * lz / 2) + r * lz / 2


def network(f, offs, s, fs, Ys, ts, lz, r):
    K = len(offs)
    q = K // s
    seg = []
    for d in offs:
        Y = interp(fs, Ys, f - d)
        t = interp(fs, ts, f - d)
        if Y is None:
            return None
        seg.append((Y, t, z_seg(Y, lz, r)))
    # unit source-side voltage on the parallel bank; string current = 1 / sum Z
    phi, Pl, Yt = 0j, 0.0, 0j
    for j in range(q):
        grp = seg[j * s:(j + 1) * s]
        Zstr = sum(z for _, _, z in grp)
        I = 1 / Zstr
        Yt += I
        for Y, t, z in grp:
            phi += K0 * t * I / Y
            Pl += z.real * abs(I) ** 2 / 2
    k = math.pi / abs(phi)
    Pl *= k * k
    Zt = 1 / Yt
    G = (Zt - R0) / (Zt + R0)
    return Pl / (1 - abs(G) ** 2), Pl, Zt


def best_over_f(offs, s, fs, Ys, ts, lz, r, fgrid):
    best = None
    for f in fgrid:
        v = network(f, offs, s, fs, Ys, ts, lz, r)
        if v and (best is None or v[0] < best[0]):
            best = (v[0], f, v[2])
    return best


fs, Ys, ts, cfg = read(os.path.join(D, sys.argv[1]))
lz = cfg["lz"]
r = RHO / (0.25 * cfg["p"] * cfg["t"]) / NPAIRS
fpk = fs[max(range(len(fs)), key=lambda i: abs(ts[i]))]
fgrid = [fpk + 0.0002 * i for i in range(-20, 21)]
out = [f"SPREAD7 case={cfg['case']} lz_um={lz*1e6:.0f} f_pk={fpk:.6f} r_ohm_per_m={r:.3e} nmc={NMC}"]
random.seed(7)
for L, s in [(1e-3, 2), (1e-3, 1), (1e-3, 5), (2e-3, 2)]:
    K = round(L / lz)
    if K % s:
        continue
    base = best_over_f([0.0] * K, s, fs, Ys, ts, lz, r, fgrid)
    out.append(f"BASE7S L_mm={L*1e3:.1f} K={K} series={s} parallel={K//s} f={base[1]:.6f} P_av_mW={base[0]*1e3:.3f} "
               f"Zt=({base[2].real:.1f},{base[2].imag:.1f})")
    for sig in [0.25, 0.5, 1.0, 2.0, 4.0]:
        res = []
        for _ in range(NMC):
            offs = [random.gauss(0, sig * 1e-3) for _ in range(K)]
            res.append(best_over_f(offs, s, fs, Ys, ts, lz, r, fgrid)[0])
        res.sort()
        out.append(f"RAND7S L_mm={L*1e3:.1f} series={s} sigma_MHz={sig:.2f} P_med_mW={res[NMC//2]*1e3:.3f} "
                   f"P_p90_mW={res[int(NMC*0.9)]*1e3:.3f} ratio_med={res[NMC//2]/base[0]:.3f} ratio_p90={res[int(NMC*0.9)]/base[0]:.3f}")
    for span in [0.5, 1.0, 2.0, 4.0]:
        offs = [span * 1e-3 * (i / (K - 1) - 0.5) for i in range(K)]
        b = best_over_f(offs, s, fs, Ys, ts, lz, r, fgrid)
        out.append(f"GRAD7S L_mm={L*1e3:.1f} series={s} span_MHz={span:.2f} P_av_mW={b[0]*1e3:.3f} ratio={b[0]/base[0]:.3f} f={b[1]:.6f}")

text = "\n".join(out)
print(text)
with open(os.path.join(D, "step7_spread.log"), "w", encoding="utf-8") as fh:
    fh.write(text + "\n")
