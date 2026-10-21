import csv, math
import numpy as np

P = 2.85261315
NB = 114
DX = P / NB
LAM = 1.55e-6

bins = {}
with open("bins_step6b1.csv", newline="") as fh:
    rows = list(csv.reader(fh))
for r in rows[1:]:
    if not r or r[0].startswith("#") or r[0] == "f_GHz":
        break
    f, it, j = r[0], r[1], int(r[2])
    bins.setdefault(f, {}).setdefault(it, np.zeros(NB, complex))[j] = float(r[4]) + 1j * float(r[5])

x = (np.arange(NB) + 0.5) * DX
harm_rows, win_rows = [], []
for f, D in bins.items():
    groups = {
        "PEtot": D["PE"] + D["PE14"],
        "EOtot": D["EO22"] + D["EO13"],
        "MB": D["MB"],
    }
    groups["TOT"] = groups["PEtot"] + groups["EOtot"] + groups["MB"]
    for name, a in groups.items():
        for n in range(8):
            c = np.mean(a * np.exp(-2j * np.pi * n * x / P)) * (1 if n == 0 else 2)
            harm_rows.append([f, name, n, f"{abs(c):.6e}"])
            print(f"HARM f={f} {name} n={n} amp={abs(c):.6e}")
    for w in (0.3, 0.5, 0.8, 1.0, 1.4):
        m = round(w / DX)
        best = None
        for j0 in range(NB):
            idx = [(j0 + q) % NB for q in range(m)]
            t = groups["TOT"][idx].mean()
            if best is None or abs(t) > best[0]:
                best = (abs(t), j0, idx)
        a, j0, idx = best
        comp = {k: D[k][idx].mean() for k in ("PE", "PE14", "EO22", "EO13", "MB")}
        phiL = 2 * math.pi / LAM * a * 1e-3
        vpil = LAM / (2 * a) * 100
        row = [f, w, m, j0, f"{j0 * DX:.6f}"]
        for k in ("PE", "PE14", "EO22", "EO13", "MB"):
            row += [f"{comp[k].real:.6e}", f"{comp[k].imag:.6e}"]
        row += [f"{a:.6e}", f"{phiL:.6f}", f"{vpil:.6f}"]
        win_rows.append(row)
        print(f"WIN f={f} w={w} m={m} j0={j0} x0_um={j0 * DX:.6f} abs_tot={a:.6e} phiL_rad_per_mmV={phiL:.4f} VpiL_Vcm={vpil:.4f}")

with open("harm_step6b1.csv", "w", newline="") as fh:
    wr = csv.writer(fh)
    wr.writerow(["f_GHz", "group", "n", "amp_per_V"])
    wr.writerows(harm_rows)
with open("win_step6b1.csv", "w", newline="") as fh:
    wr = csv.writer(fh)
    hdr = ["f_GHz", "w_um", "m_bins", "j0", "x0_um"]
    for k in ("PE", "PE14", "EO22", "EO13", "MB"):
        hdr += [k + "_Re", k + "_Im"]
    wr.writerow(hdr + ["abs_tot_per_V", "phiL_rad_per_mmV", "VpiL_Vcm"])
    wr.writerows(win_rows)
