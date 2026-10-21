"""Step 6g-2: electrode series resistance, Z_in(f), and source power for V_pi with a 50-ohm source.

Inputs: F6F lines of step6f.log (|tot| per volt and Y per metre of aperture, one 15-cell supercell, 12 finger pairs).
Output: step6g_power.log
"""
import cmath
import math
import os
import re

D = os.path.dirname(os.path.abspath(__file__))
LAM = 1.55e-6
K0 = 2 * math.pi / LAM
RHO = 2.8e-8
T_AL = 100e-9
W_F = 0.25 * 2.71043685e-6
NPAIR = 12
R0 = 50.0
LS = [1e-3, 5e-3]
PEAKS = {"MAIN": 3.338550, "LOW": 3.318700}
SETS = {"MAIN": ["stdM", "stdY"], "LOW": ["stdL1", "stdL2"]}
LOGS = ["step6f.log", "step6gY.log"]

r_f = RHO / (W_F * T_AL)        # ohm/m, one finger
r_g = r_f / NPAIR               # ohm/m, 12 fingers in parallel (hot group; ground group identical)

pat = re.compile(r"^F6F set=(\S+) f_GHz=([\d.]+) .*abs_tot=([-\d.e+]+) ReY_Spm=([-\d.e+]+) ImY_Spm=([-\d.e+]+)")
rows = {}
for lg in LOGS:
    p = os.path.join(D, lg)
    if not os.path.exists(p):
        continue
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            m = pat.match(line)
            if m:
                s, f, tot, ry, iy = m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5))
                rows.setdefault(s, {})[f] = (tot, complex(ry, iy))


def z_models(Y, L):
    """Y in S/m. Returns dict of input impedances and helpers."""
    z_ideal = 1 / (Y * L)
    z_lump = 2 * r_f * L / NPAIR + z_ideal
    g = cmath.sqrt(2 * r_g * Y)
    z_dist = (r_g / g) / cmath.tanh(g * L / 2) + r_g * L / 2
    return z_ideal, z_lump, z_dist, g


def p_ac_dist(Y, L, g, I, n=4001):
    """acoustic (shunt) power for the distributed line, |V(z)|^2 integrated numerically."""
    a = I * r_g / (g * cmath.sinh(g * L / 2))
    s = 0.0
    for i in range(n):
        z = L * i / (n - 1)
        v = a * cmath.cosh(g * (z - L / 2))
        wgt = 0.5 if i in (0, n - 1) else 1.0
        s += wgt * abs(v) ** 2
    return Y.real / 2 * s * L / (n - 1)


def metrics(Z, I):
    P_in = Z.real * abs(I) ** 2 / 2
    R = Z.real
    q_l = math.sqrt(max(R, R0) / min(R, R0) - 1) if R > 0 else float("nan")
    gam = (Z - R0) / (Z + R0)
    p_unm = P_in / (1 - abs(gam) ** 2)
    return P_in, q_l, abs(gam), p_unm


out = []
out.append(f"CFG6G rho={RHO:.2e} ohm*m t_Al={T_AL*1e9:.0f} nm w_finger={W_F*1e6:.4f} um N_pairs={NPAIR} "
           f"r_finger={r_f:.4e} ohm/m ({r_f*1e-3:.1f} ohm/mm) source R0={R0:.0f} ohm; bus bars ideal")
out.append("CFG6G I_pi = pi*|Y|/(k0*|tot|) holds for both lumped and distributed (integral of V dz = I/Y); "
           "P_in = Re(Z_in)*|I_pi|^2/2; lossless L-match => P_source = P_in")
out.append("CFG6G lumped: R_s = 2*rho*L/(w*t)/12 (hot + ground, full finger length, as specified); "
           "distributed: opposite-end-fed RC line, Z_in = (r/g)coth(gL/2) + rL/2, g = sqrt(2 r Y), r = r_finger/12")

for name, f_pk in PEAKS.items():
    data = {}
    for s in SETS[name]:
        data.update(rows.get(s, {}))
    fs = sorted(data)
    for L in LS:
        best = {}
        for f in fs:
            tot, Y = data[f]
            I = math.pi * abs(Y) / (K0 * tot)
            zi, zl, zd, g = z_models(Y, L)
            for lab, Z in (("ideal", zi), ("lumped", zl), ("distributed", zd)):
                P = metrics(Z, I)[0]
                if lab not in best or P < best[lab][1]:
                    best[lab] = (f, P, tot, Y, Z, I)
        f = min(fs, key=lambda x: abs(x - f_pk))
        tot, Y = data[f]
        I = math.pi * abs(Y) / (K0 * tot)
        zi, zl, zd, g = z_models(Y, L)
        Rs = 2 * r_f * L / NPAIR
        for lab, Z in (("ideal", zi), ("lumped", zl), ("distributed", zd)):
            P_in, q_l, gm, p_unm = metrics(Z, I)
            if lab == "ideal":
                p_ac = P_in
            elif lab == "lumped":
                p_ac = Y.real * L * abs(I / (Y * L)) ** 2 / 2
            else:
                p_ac = p_ac_dist(Y, L, g, I)
            extra = ""
            if lab == "distributed":
                extra = (f" gamma=({g.real:.4e},{g.imag:.4e})/m |gamma*L|={abs(g*L):.3f} decay_len_um={1e6/g.real:.1f}"
                         f" |V(L/2)/V(0)|={abs(1/cmath.cosh(g*L/2)):.4f}")
            if lab == "lumped":
                extra = f" R_s_ohm={Rs:.3f}"
            out.append(
                f"PWR6G set={name} L_mm={L*1e3:.0f} model={lab} f_GHz={f:.6f} abs_tot={tot:.4e} Y_Spm=({Y.real:.4e},{Y.imag:.4e}) "
                f"Zin_ohm=({Z.real:.4f},{Z.imag:.4f}) I_pi_A={I:.4f} |V_in|_V={abs(Z*I):.3f} "
                f"P_source_matched_mW={P_in*1e3:.2f} P_acoustic_mW={p_ac*1e3:.2f} electrode_loss_frac={1-p_ac/P_in:.4f} "
                f"Lmatch_Q={q_l:.2f} |Gamma|_unmatched={gm:.4f} P_av_unmatched_mW={p_unm*1e3:.2f}{extra}")
            bf, bp, bt, bY, bZ, bI = best[lab]
            edge = bf in (fs[0], fs[-1])
            out.append(f"PWR6G_BEST set={name} L_mm={L*1e3:.0f} model={lab} f_min_GHz={bf:.6f} "
                       f"P_source_matched_min_mW={bp*1e3:.2f} abs_tot={bt:.4e} Y_Spm=({bY.real:.4e},{bY.imag:.4e}) "
                       f"Zin_ohm=({bZ.real:.4f},{bZ.imag:.4f}) I_pi_A={bI:.4f} at_window_edge={edge} "
                       f"window_GHz=[{fs[0]:.4f},{fs[-1]:.4f}]")

    best_l = None
    for j in range(241):
        L = 10 ** (-5 + j * (math.log10(5e-3) + 5) / 240)
        for f in fs:
            tot, Y = data[f]
            I = math.pi * abs(Y) / (K0 * tot)
            Z = z_models(Y, L)[2]
            P = Z.real * I ** 2 / 2
            if best_l is None or P < best_l[0]:
                best_l = (P, L, f, Z, I, tot, z_models(Y, L)[3])
    P, L, f, Z, I, tot, g = best_l
    out.append(f"PWR6G_LOPT set={name} model=distributed scan L=10um..5mm x all f: L_opt_um={L*1e6:.1f} f_GHz={f:.6f} "
               f"P_source_matched_mW={P*1e3:.2f} Zin_ohm=({Z.real:.4f},{Z.imag:.4f}) I_pi_A={I:.4f} |V_in|_V={abs(Z*I):.3f} "
               f"abs_tot={tot:.4e} |gamma*L|={abs(g*L):.3f}")

text = "\n".join(out)
print(text)
with open(os.path.join(D, "step6g_power.log"), "w", encoding="utf-8") as fh:
    fh.write(text + "\n")
