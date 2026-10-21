import csv, math, re
import numpy as np

P = 2.85261315
NB = 114
DX = P / NB
LAM = 1.55e-6
ITEMS = ("PEy", "PE14y", "EOy", "PEz", "MB")
pat = re.compile(r"BINB2 f_GHz=(\S+) item=(\S+) j=(\d+) xc_um=(\S+) Re=(\S+) Im=(\S+)")

bins = {}
raw = []
for line in open("step6b2.log", encoding="utf-8", errors="ignore"):
    mt = pat.search(line)
    if not mt:
        continue
    f, it, j, xc, re_, im_ = mt.groups()
    raw.append([f, it, j, xc, re_, im_])
    bins.setdefault(f, {}).setdefault(it, np.zeros(NB, complex))[int(j)] = float(re_) + 1j * float(im_)
assert len(raw) == 2 * 5 * NB, len(raw)

with open("bins_step6b2.csv", "w", newline="\n") as fh:
    fh.write("f_GHz,item,j,xc_um,Re,Im\n")
    for r in raw:
        fh.write(",".join(r) + "\n")

x = (np.arange(NB) + 0.5) * DX
harm_rows, win_rows = [], []
for f, D in bins.items():
    groups = {
        "PEtot": D["PEy"] + D["PE14y"] + D["PEz"],
        "EOtot": D["EOy"],
        "MB": D["MB"],
    }
    groups["TOT"] = groups["PEtot"] + groups["EOtot"] + groups["MB"]
    for name, a in groups.items():
        for n in range(8):
            c = np.mean(a * np.exp(-2j * np.pi * n * x / P)) * (1 if n == 0 else 2)
            harm_rows.append([f, name, n, f"{abs(c):.6e}"])
            print(f"HARM2 f={f} {name} n={n} amp={abs(c):.6e}")
    for w in (0.3, 0.5, 0.8, 1.0, 1.4):
        m = round(w / DX)
        best = None
        for j0 in range(NB):
            idx = [(j0 + q) % NB for q in range(m)]
            t = groups["TOT"][idx].mean()
            if best is None or abs(t) > best[0]:
                best = (abs(t), j0, idx)
        a, j0, idx = best
        comp = {k: D[k][idx].mean() for k in ITEMS}
        phiL = 2 * math.pi / LAM * a * 1e-3
        vpil = LAM / (2 * a) * 100
        row = [f, w, m, j0, f"{j0 * DX:.6f}"]
        for k in ITEMS:
            row += [f"{comp[k].real:.6e}", f"{comp[k].imag:.6e}"]
        row += [f"{a:.6e}", f"{phiL:.6f}", f"{vpil:.6f}"]
        win_rows.append(row)
        print(f"WIN2 f={f} w={w} m={m} j0={j0} x0_um={j0 * DX:.6f} abs_tot={a:.6e} phiL_rad_per_mmV={phiL:.4f} VpiL_Vcm={vpil:.4f}")

with open("harm_step6b2.csv", "w", newline="\n") as fh:
    wr = csv.writer(fh, lineterminator="\n")
    wr.writerow(["f_GHz", "group", "n", "amp_per_V"])
    wr.writerows(harm_rows)
with open("win_step6b2.csv", "w", newline="\n") as fh:
    wr = csv.writer(fh, lineterminator="\n")
    hdr = ["f_GHz", "w_um", "m_bins", "j0", "x0_um"]
    for k in ITEMS:
        hdr += [k + "_Re", k + "_Im"]
    wr.writerow(hdr + ["abs_tot_per_V", "phiL_rad_per_mmV", "VpiL_Vcm"])
    wr.writerows(win_rows)
