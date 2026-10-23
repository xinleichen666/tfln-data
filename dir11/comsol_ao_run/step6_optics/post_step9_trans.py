"""Step 9 post-processing: mode-matching of the TE0 mode across an abrupt suspended / on-oxide transition.

Reads the fields exported by Step9Trans (s9tr_<case>[f].txt: x, y, Re/Im of Ex, Ey, Hx, Hy on a grid).
For modes a (incident) and b (transmitted), with N_x = int (E_x x H_x*)_z dA,
  A = int (E_a x H_b*)_z dA,   C = int (E_b* x H_a)_z dA
Continuity of E_t and H_t, projected onto H_b* and E_b* (single mode each side), gives
  r = (C - A)/(C + A),   t = 2 A C /((A + C) N_b),   T = |t|^2 Re N_b / Re N_a,   R = |r|^2.
eta_ov = |A|^2/(Re N_a Re N_b) is the plain overlap (power coupling, no reflection).
"""
import sys, os, math
import numpy as np

D = r"D:\comsol_ao_run"
OUT = os.path.join(D, "step6_optics", "step9_trans.log")


def load(case):
    f = os.path.join(D, "s9tr_%s.txt" % case)
    a = np.loadtxt(f)
    x, y = a[:, 0], a[:, 1]
    xs, ys = np.unique(x), np.unique(y)
    nx, ny = len(xs), len(ys)
    assert a.shape[0] == nx * ny, (a.shape, nx, ny)
    # rows: x fastest
    idx = np.lexsort((x, y))
    a = a[idx]
    def comp(k):
        return (a[:, 2 + 2 * k] + 1j * a[:, 3 + 2 * k]).reshape(ny, nx)
    ex, ey, hx, hy = comp(0), comp(1), comp(2), comp(3)
    return xs, ys, ex, ey, hx, hy


def pz(e1x, e1y, h2x, h2y):
    return e1x * np.conj(h2y) - e1y * np.conj(h2x)


def match(a, b):
    xs, ys, eax, eay, hax, hay = a
    _, _, ebx, eby, hbx, hby = b
    dA = (xs[1] - xs[0]) * (ys[1] - ys[0])
    Na = np.sum(pz(eax, eay, hax, hay)) * dA
    Nb = np.sum(pz(ebx, eby, hbx, hby)) * dA
    A = np.sum(pz(eax, eay, hbx, hby)) * dA
    # C = int (E_b* x H_a)_z = Ebx* Hay - Eby* Hax
    C = np.sum(np.conj(ebx) * hay - np.conj(eby) * hax) * dA
    r = (C - A) / (C + A)
    t = 2 * A * C / ((A + C) * Nb)
    T = abs(t) ** 2 * Nb.real / Na.real
    R = abs(r) ** 2
    eta = abs(A) ** 2 / (Na.real * Nb.real)
    eE = abs(np.sum(eax * np.conj(ebx) + eay * np.conj(eby))) ** 2 / (
        np.sum(abs(eax) ** 2 + abs(eay) ** 2) * np.sum(abs(ebx) ** 2 + abs(eby) ** 2))
    eH = abs(np.sum(hax * np.conj(hbx) + hay * np.conj(hby))) ** 2 / (
        np.sum(abs(hax) ** 2 + abs(hay) ** 2) * np.sum(abs(hbx) ** 2 + abs(hby) ** 2))
    return dict(T=T, R=R, eta=eta, eE=eE, eH=eH, lossdB=-10 * math.log10(T), lossdB_ov=-10 * math.log10(eta),
                rest=1 - T - R, Na=Na, Nb=Nb)


def main():
    sfx = sys.argv[1] if len(sys.argv) > 1 else ""
    lines = []
    cases = [c for c in ("S0", "SF", "O2", "O1", "O4") if os.path.exists(os.path.join(D, "s9tr_%s%s.txt" % (c, sfx)))]
    F = {c: load(c + sfx) for c in cases}
    pairs = [("S0", "S0"), ("O2", "O2"), ("SF", "S0"), ("S0", "O2"), ("SF", "O2"), ("S0", "O1"), ("S0", "O4"), ("O2", "S0")]
    for a, b in pairs:
        if a not in F or b not in F:
            continue
        m = match(F[a], F[b])
        s = ("TRANSM9 mesh=%s from=%s to=%s T=%.6f R=%.3e eta_ov=%.6f eta_E=%.6f eta_H=%.6f loss_dB=%.4f loss_ov_dB=%.4f rest=%.3e" %
             (sfx or "m", a, b, m["T"], m["R"], m["eta"], m["eE"], m["eH"], m["lossdB"], m["lossdB_ov"], m["rest"]))
        print(s)
        lines.append(s)
    with open(OUT, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
