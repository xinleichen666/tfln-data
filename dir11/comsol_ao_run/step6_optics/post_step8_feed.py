"""Step 8: feed network with real rails, beam traces and pads (nodal analysis, 1 mm device).

Segment data (Y per length, complex tot per volt) come from the 3D support-beam case (100 um segments, 0.5 um bus,
period 1.84 um, beam + Al routing). Each segment is split into a left and a right half (Y/2 each; finger resistance
per half doubles, so Z_half = 2 Z_seg); each half contributes half of the segment's phase for equal drive.

Topology: strings of s segments. Gaps between segments carry one net each: every s-th gap is driven, alternately
signal and ground; the other gaps are floating series nodes. Odd strings are mirrored (the A fingers join the top bus),
so all strings add in phase. A driven gap is tied through its beam trace and an anchor lead to a rail tap.
  A  : signal + ground rails on both sides of the film; the two sides meet at one GS pad pair at the feed end.
  C  : rails on one side only; at every driven gap an air bridge ties the left and right bus bars (bridge R included,
       optical absorption of the bridges is computed separately).
  ideal: every driven gap tied directly to the source (reproduces post_step7 results).
Rails: series R' (DC, metal thickness tm) and L' (from the vacuum capacitance), shunt C' between signal and ground
rails (2D electrostatics, step8_rail.log), as pi sections between taps. Source 50 ohm; required available power for
|sum phase| = pi, drive frequency optimised within +-4 MHz of the peak.
Usage: python post_step8_feed.py <seg_log>  -> step8_feed.log
"""
import cmath
import math
import os
import re
import sys

import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
LAM = 1.55e-6
K0 = 2 * math.pi / LAM
RHO_AL = 2.8e-8
R0 = 50.0
NPAIRS = 4
C_LIGHT = 2.998e8


def read_seg(path):
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
    o = sorted(range(len(fs)), key=lambda i: fs[i])
    return [fs[i] for i in o], [Ys[i] for i in o], [ts[i] for i in o], cfg


def read_rails(path):
    c = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = re.match(r"^RAIL8 ws_um=(\S+) g_um=(\S+) wg_um=(\S+) vac=(\S+) C_pF_per_mm=(\S+)", line)
            if m:
                c[(float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4) == "true")] = float(m.group(5)) * 1e-9
    out = {}
    for (ws, g, wg, vac), v in c.items():
        if not vac and (ws, g, wg, True) in c:
            C0 = c[(ws, g, wg, True)]
            out[(ws, g, wg)] = dict(C=v, L=1 / (C_LIGHT ** 2 * C0))
    return out


def z_seg(Y, lz, r):
    g = cmath.sqrt(2 * r * Y)
    return (r / g) / cmath.tanh(g * lz / 2) + r * lz / 2


class Net:
    def __init__(self):
        self.n = 0
        self.el = []

    def node(self):
        self.n += 1
        return self.n - 1

    def add(self, a, b, Z):
        self.el.append((a, b, Z))

    def solve(self, src, gnd, w):
        """1 V open-circuit source with R0 between node src and node gnd (gnd is the reference)."""
        Yn = np.zeros((self.n, self.n), complex)
        for a, b, Z in self.el:
            y = 1 / Z
            for p, q in ((a, b), (b, a)):
                if p is not None:
                    Yn[p, p] += y
                    if q is not None:
                        Yn[p, q] -= y
        Yn[src, src] += 1 / R0
        I = np.zeros(self.n, complex)
        I[src] = 1 / R0
        keep = [i for i in range(self.n) if i != gnd]
        V = np.zeros(self.n, complex)
        V[keep] = np.linalg.solve(Yn[np.ix_(keep, keep)], I[keep])
        return V


def build(topo, f, Y, t, cfg, prm):
    """Returns (phase per 1 V open-circuit source, input impedance)."""
    w = 2 * math.pi * f * 1e9
    lz = cfg["lz"]
    K = prm["K"]
    s = prm["s"]
    r = RHO_AL / (0.25 * cfg["p"] * cfg["t"]) / NPAIRS
    Zh = 2 * z_seg(Y, lz, r) + 2 * prm["Rbus"]
    net = Net()
    sides = ("L", "R")
    bus = {(sd, g): net.node() for sd in sides for g in range(K + 1)}
    gnd = net.node()
    src = net.node()
    halves = []
    for k in range(K):
        mirrored = (k // s) % 2 == 1
        for sd in sides:
            net.add(bus[(sd, k)], bus[(sd, k + 1)], Zh)
            halves.append((bus[(sd, k)], bus[(sd, k + 1)], mirrored))
    driven = [g for g in range(K + 1) if g % s == 0]
    pol = {g: ("S" if (g // s) % 2 == 0 else "G") for g in driven}
    if topo == "ideal":
        for g in driven:
            for sd in sides:
                net.add(bus[(sd, g)], src if pol[g] == "S" else gnd, prm["Rtiny"])
    else:
        rail_sides = sides if topo == "A" else ("L",)
        if topo == "C":
            for g in driven:
                net.add(bus[("L", g)], bus[("R", g)], prm["Rbridge"])
        Zser = lambda dz: (prm["Rs"] + 1j * w * prm["Lr"]) * dz
        Zgser = lambda dz: (prm["Rg"]) * dz
        zfeed = prm["zfeed"] * K * lz
        for sd in rail_sides:
            pts = sorted(set([zfeed] + [g * lz for g in driven]))
            sn = {z: net.node() for z in pts}
            gn = {z: net.node() for z in pts}
            for z0, z1 in zip(pts[:-1], pts[1:]):
                dz = z1 - z0
                net.add(sn[z0], sn[z1], Zser(dz))
                net.add(gn[z0], gn[z1], Zgser(dz) + 1j * w * 1e-18)
                Zc = 1 / (1j * w * prm["Cr"] * dz / 2)
                net.add(sn[z0], gn[z0], Zc)
                net.add(sn[z1], gn[z1], Zc)
            net.add(sn[zfeed], src, prm["Rtiny"])
            net.add(gn[zfeed], gnd, prm["Rtiny"])
            for g in driven:
                tgt = sn[g * lz] if pol[g] == "S" else gn[g * lz]
                bs = [sd] if topo == "A" else ["L"]
                for b in bs:
                    net.add(bus[(b, g)], tgt, prm["Rbeam"])
        net.add(src, gnd, 1 / (1j * w * prm["Cpad"]))
    V = net.solve(src, gnd, w)
    phi = 0j
    for a, b, mir in halves:
        I = (V[a] - V[b]) / Zh
        Vint = I / (Y * lz / 2)
        phi += (-1 if mir else 1) * K0 * t * (lz / 2) * Vint
    Iin = (1 - V[src]) / R0
    return phi, V[src] / Iin


def required_power(topo, fs, Ys, ts, cfg, prm, fpk):
    best = None
    for f, Y, t in zip(fs, Ys, ts):
        if abs(f - fpk) > 0.004:
            continue
        phi, Zin = build(topo, f, Y, t, cfg, prm)
        Vs = math.pi / abs(phi)
        P = Vs ** 2 / (8 * R0)
        if best is None or P < best[0]:
            best = (P, f, Zin)
    return best


fs, Ys, ts, cfg = read_seg(os.path.join(D, sys.argv[1]))
rails = read_rails(os.path.join(D, "step8_rail.log"))
fpk = fs[max(range(len(fs)), key=lambda i: abs(ts[i]))]
out = [f"FEED8 seg={cfg['case']} lz_um={cfg['lz']*1e6:.0f} f_pk={fpk:.6f}"]
base = dict(K=10, Rtiny=1e-3, Cpad=10e-15, Rbridge=1.0, zfeed=0.0)
for s in (2, 1):
    p = dict(base, s=s, Rbus=0.0, Rbeam=1e-3, Rs=0, Rg=0, Lr=0, Cr=1e-30)
    b = required_power("ideal", fs, Ys, ts, cfg, p, fpk)
    out.append(f"IDEAL8 series={s} P_mW={b[0]*1e3:.3f} f={b[1]:.6f} Zin=({b[2].real:.1f},{b[2].imag:.1f})")
for tm in (100e-9, 500e-9):
    rbus = RHO_AL * 3.4e-6 / (0.5e-6 * 100e-9) / 3
    rbeam = RHO_AL * 6e-6 / (1.5e-6 * 100e-9) + RHO_AL * 20e-6 / (5e-6 * tm)
    for (ws, g, wg), rc in sorted(rails.items()):
        for s in (2, 1):
            for topo in ("A", "C"):
                for zf in (0.0, 0.5):
                    p = dict(base, s=s, Rbus=rbus, Rbeam=rbeam, Rs=RHO_AL / (ws * 1e-6 * tm), Rg=RHO_AL / (wg * 1e-6 * tm),
                             Lr=rc["L"], Cr=rc["C"], zfeed=zf)
                    b = required_power(topo, fs, Ys, ts, cfg, p, fpk)
                    out.append(f"RAILNET8 tm_nm={tm*1e9:.0f} ws_um={ws:.0f} g_um={g:.0f} wg_um={wg:.0f} topo={topo} feed={'end' if zf == 0 else 'mid'} "
                               f"series={s} Rs_ohm_per_mm={p['Rs']*1e-3:.2f} Cr_pF_per_mm={rc['C']*1e9:.4f} Lr_nH_per_mm={rc['L']*1e6:.4f} "
                               f"Rbeam_ohm={rbeam:.2f} P_mW={b[0]*1e3:.3f} f={b[1]:.6f} Zin=({b[2].real:.1f},{b[2].imag:.1f})")
text = "\n".join(out)
print(text)
with open(os.path.join(D, "step8_feed.log"), "w", encoding="utf-8") as fh:
    fh.write(text + "\n")
