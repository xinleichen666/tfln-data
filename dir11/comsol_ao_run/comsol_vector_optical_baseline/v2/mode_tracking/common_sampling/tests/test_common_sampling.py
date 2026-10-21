"""Tests for the common sampling and the area-weighted comparison.

The negative cases matter as much as the positive ones: a similarity that
silently accepts NaN, a mismatched weight vector, or fields on different
coordinates would produce a confident and meaningless number.

Run:  python tests/test_common_sampling.py
"""
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))

import compare_weighted as CW           # noqa: E402
import sampling as S                    # noqa: E402

WINDOW = (4.18 + 1.6) * (1.6 + 1.0)
fails = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}  {detail}")
        fails.append(name)


def expect_raise(name, fn, exc=Exception):
    try:
        fn()
    except exc:
        print(f"  ok   {name} (rejected)")
        return
    print(f"  FAIL {name}: no exception")
    fails.append(name)


# ---------------------------------------------------------------- sampling
print("sampling")
for n in (1, 3, 6, 12):
    s = S.cells(n)
    c = S.check(s, WINDOW)
    check(f"n={n} tiles the window", not c["problems"], c["problems"])
    check(f"n={n} point count", s["x"].size == 35 * n * n,
          f"{s['x'].size} vs {35*n*n}")

s = S.cells(3)
# every cell must sit strictly away from every cut line, so it belongs to one
# region without ambiguity
xe = np.asarray(S.X_EDGES)
ye = np.asarray(S.Y_EDGES)
dx = np.min(np.abs(s["x"][:, None] - xe[None, :]))
dy = np.min(np.abs(s["y"][:, None] - ye[None, :]))
check("cell centres avoid x cut lines", dx > 1e-6, f"{dx:.2e}")
check("cell centres avoid y cut lines", dy > 1e-6, f"{dy:.2e}")
check("no cell is 'outside'", "outside" not in set(s["region"].tolist()))
check("regions partition the cells",
      sum((s["region"] == r).sum() for r in set(s["region"])) == s["x"].size)
# each cell's role is unique: the region of a centre must be the same as the
# region of the points just inside the same cell
s2 = S.cells(6)
check("n=6 keeps the same region set",
      set(s2["region"].tolist()) == set(s["region"].tolist()))

# ------------------------------------------------------------ similarity
print("similarity")
rng = np.random.default_rng(0)
N = 40
w = rng.uniform(0.5, 2.0, N)
E = rng.normal(size=(N, 3)) + 1j * rng.normal(size=(N, 3))

check("self similarity is 1", abs(CW.similarity(E, E, w) - 1) < 1e-12)
check("global phase invariant",
      abs(CW.similarity(E, E * np.exp(1j * 0.7), w) - 1) < 1e-12)
check("scaling invariant", abs(CW.similarity(E, 37.0 * E, w) - 1) < 1e-12)
check("conjugation is NOT treated as equality",
      CW.similarity(E, np.conj(E), w) < 0.999)

# orthogonal fields: x-polarised against y-polarised
Ex = np.zeros((N, 3), dtype=complex)
Ex[:, 0] = 1.0
Ey = np.zeros((N, 3), dtype=complex)
Ey[:, 1] = 1.0
check("orthogonal polarisations give 0",
      abs(CW.similarity(Ex, Ey, w)) < 1e-12)

# weights are area weights, so a field living on half the area scores sqrt(1/2)
Ea = np.ones((N, 3), dtype=complex)
Eb = np.ones((N, 3), dtype=complex)
half = np.zeros(N, dtype=bool)
half[: N // 2] = True
Eb[~half] = 0.0
wa = np.ones(N)
exp_s = np.sqrt(wa[half].sum() / wa.sum())
got = CW.similarity(Ea, Eb, wa)
check("area weighting integrates correctly", abs(got - exp_s) < 1e-12,
      f"{got:.6f} vs {exp_s:.6f}")

# non-uniform weights must change the answer, otherwise the weights are ignored
w2 = np.ones(N)
w2[half] *= 9.0
got2 = CW.similarity(Ea, Eb, w2)
check("non-uniform weights are used", abs(got2 - got) > 1e-3,
      f"{got2:.6f} vs {got:.6f}")

# ------------------------------------------------------------- rejections
print("rejections")
bad = E.copy()
bad[3, 1] = np.nan
expect_raise("NaN rejected", lambda: CW.similarity(bad, E, w), ValueError)
expect_raise("weight shape mismatch rejected",
             lambda: CW.similarity(E, E, w[:-1]), ValueError)
expect_raise("negative weight rejected",
             lambda: CW.similarity(E, E, -w), ValueError)
expect_raise("field shape mismatch rejected",
             lambda: CW.similarity(E, E[:, :2], w), ValueError)
check("zero field gives 0",
      CW.similarity(np.zeros((N, 3)), E, w) == 0.0)

# a modified point file must be rejected by the loader
import tempfile                                  # noqa: E402

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    s = S.cells(3)
    good = np.column_stack([np.c_[s["x"], s["y"]],
                            np.ones(s["x"].size), np.zeros((s["x"].size, 8)),
                            s["w"]])
    hdr = ("x,y,dom,normE,Exre,Exim,Eyre,Eyim,Ezre,Ezim,Emag_co,w")

    def write(name, arr):
        p = td / name
        np.savetxt(p, arr, delimiter=",", header=hdr, comments="")
        return p

    p_ok = write("ok.csv", good)
    loaded = CW.load(p_ok, 3)
    check("valid file loads", loaded["E"].shape == (s["x"].size, 3))

    sh = good.copy()
    sh[5, 0] += 1e-3
    expect_raise("shifted coordinate rejected",
                 lambda: CW.load(write("shift.csv", sh), 3), SystemExit)

    wr = good.copy()
    wr[5, 11] *= 2
    expect_raise("wrong weight rejected",
                 lambda: CW.load(write("w.csv", wr), 3), SystemExit)

    n_missing = good[:-1]
    expect_raise("missing rows rejected",
                 lambda: CW.load(write("short.csv", n_missing), 3), SystemExit)

import compare_integrals as CI        # noqa: E402

# ------------------------------------------------- reference comparison
print("reference comparison")
N = 4
E = np.zeros((N, 3), dtype=complex)
E[:, 0] = 1.0                      # purely x-polarised, |Ex| = 1
w = np.array([0.3225, 0.241875, 0.241875, 14.22175])
reg = np.array(["ridge", "slabL", "slabR", "air"], dtype=object)
# with |Ex| = 1 everywhere, the exact integral over a region is its area, so
# the reference must be built the same way or the component check is meaningless
ref_exact = {nm: [float(wi), float(wi), 0.0, 0.0, float(wi)]
             for nm, wi in zip(reg, w)}

rows, tr, ts, bad, contrib = CI.run_compare(ref_exact, E, w, reg)
check("exact agreement passes", not bad, bad)
check("total ratio is 1", abs(ts / tr - 1) < 1e-12, f"{ts/tr:.12f}")

# a uniform shortfall keeps every share identical, so only the total check can
# catch it - this is exactly the case that the earlier comparison missed
rows, tr, ts, bad, contrib = CI.run_compare(
    ref_exact, E * np.sqrt(0.95), w, reg)
check("uniform 5 % shortfall rejected",
      any("total norm off" in b for b in bad), bad)
check("uniform shortfall keeps shares",
      not any("share off" in b for b in bad), bad)

# a large regional distortion must be reported
ref_off = {k: list(v) for k, v in ref_exact.items()}
ref_off["ridge"][0] *= 3.0
rows, tr, ts, bad, contrib = CI.run_compare(ref_off, E, w, reg)
check("regional distortion detected", any("ridge" in b for b in bad), bad)
top = max(contrib, key=lambda x: abs(x[1]))[0]
check("worst region identified", top == "ridge", top)

# a distortion of a region that carries a small share stays invisible in the
# share metric - documented, not hidden
ref_small = {k: list(v) for k, v in ref_exact.items()}
ref_small["slabL"][0] *= 1.02
rows, tr, ts, bad_small, contrib = CI.run_compare(ref_small, E, w, reg)
check("share metric tolerates a 2 % shift of a small region",
      not bad_small, bad_small)

# when the reference has no electrode regions, those cells fold into air
ref_nom = {"ridge": [0.3225, 0.3225, 0, 0, 0.3225],
           "air": [14.22175, 14.22175, 0, 0, 14.22175]}
reg2 = np.array(["ridge", "metalL", "metalR", "air"], dtype=object)
w2 = np.array([0.3225, 0.0645, 0.0645, 14.09275])
rows, tr, ts, bad, contrib = CI.run_compare(ref_nom, E, w2, reg2)
names = [r[0] for r in rows]
check("electrode cells fold into air", "metalL" not in names, names)
check("folded area matches", abs(w2.sum() - (0.3225 + 14.22175)) < 1e-9,
      f"{w2.sum():.6f}")

expect_raise("non-finite field rejected",
             lambda: CI.run_compare(ref_nom, np.full((N, 3), np.nan + 0j), w, reg),
             ValueError)
expect_raise("shape mismatch rejected",
             lambda: CI.run_compare(ref_nom, E, w[:-1], reg), ValueError)

import cellspec as CS                 # noqa: E402

# ------------------------------------------------------------- cell partition
print("cell partition")
for n in (2, 6, 12):
    b = CS.base_cells(n)
    chk = CS.check(b)
    check(f"n={n} partition closes", not chk["problems"], chk["problems"])
    check(f"n={n} cell count", len(b) == 35 * n * n, f"{len(b)}")
    check(f"n={n} no overlap reported", not any("overlap" in p
                                                for p in chk["problems"]))

b = CS.base_cells(6)
kids = CS.nest(6, 12, len(CS.X_EDGES) - 1, len(CS.Y_EDGES) - 1)
w6 = np.array([(c[1] - c[0]) * (c[3] - c[2]) for c in b])
w12 = np.array([(c[1] - c[0]) * (c[3] - c[2]) for c in CS.base_cells(12)])
check("nesting maps four children per cell", kids.shape == (1260, 4), kids.shape)
check("children areas sum to the parent", np.allclose(w12[kids].sum(axis=1), w6))

flags = np.zeros(len(CS.base_cells(12)), dtype=bool)
flags[::50] = True
ref = CS.refine(CS.base_cells(12), flags)
chk = CS.check(ref)
check("refined grid still closes", not chk["problems"], chk["problems"])
check("refined grid grows", len(ref) > 5040, len(ref))
check("refined grid keeps area", abs(chk["area"] - 15.028) < 1e-9)

tiny = (0.0, 0.010, 0.0, 0.010)     # already below the 15 nm floor
check("cell at the floor is not split", CS.split4(tiny) == [tiny])
flat = (0.0, 0.100, 0.0, 0.010)     # thin in y only
kids2 = CS.split4(flat)
check("thin cell splits along x only", len(kids2) == 2
      and all(k[3] == flat[3] for k in kids2), kids2)

# stricter structural checks
print("grid rejection")
good = CS.base_cells(4)
# a cell that straddles the film edge x=0.9675 must be rejected
straddle = list(good) + [(0.9, 1.0, 1.2, 1.3)]
chk = CS.check(straddle)
check("straddling cell rejected",
      any("straddles" in p for p in chk["problems"]), chk["problems"])

# an overlapping pair at different heights must be rejected
dup = list(good) + [good[0]]
chk = CS.check(dup)
check("duplicate cell rejected",
      any("covered by" in p or "overlap" in p for p in chk["problems"]),
      chk["problems"])

# a hole must be rejected (remove one cell)
hole = list(good)
hole.pop(7)
chk = CS.check(hole)
check("hole rejected",
      any("covered by" in p or "!=" in p for p in chk["problems"]),
      chk["problems"])

# the size floor must actually reach split4
big = (0.0, 0.100, 1.0, 1.100)
check("floor honoured by refine",
      CS.refine([big], [True], min_side=0.06) == [big],
      CS.refine([big], [True], min_side=0.06))
check("floor can be lowered",
      len(CS.refine([big], [True], min_side=0.01)) == 4,
      len(CS.refine([big], [True], min_side=0.01)))

# parent indices must point back at the right cell
cells3 = [(0.0, 0.1, 0.0, 0.1), (0.1, 0.2, 0.0, 0.1)]
out, par = CS.refine_with_parents(cells3, [True, False], min_side=0.01)
check("parent map length", len(out) == len(par) == 5, (len(out), len(par)))
check("parent map values", par.tolist() == [0, 0, 0, 0, 1], par.tolist())

ub = CS.uniform_bands(4, 8)
chk = CS.check(ub)
check("band grid closes", not chk["problems"], chk["problems"])
check("band grid refines only the film",
      len(ub) == 7 * 4 * 2 * 4 + 7 * 8 * 3 * 8, len(ub))

import adapt_recursive as AR         # noqa: E402

# ------------------------------------------------------------ recursion logic
print("recursion logic")
cells = CS.uniform_bands(2, 4)
sp = CS.arrays(cells)
N = len(cells)
parent_E = {"m": np.ones((N, 3), dtype=complex)}
picked, npts = AR.choose_candidates(cells, probe_budget=40)
check("candidates fit the probe budget", npts <= 40, npts)
check("candidates are splittable",
      all(len(CS.split4(cells[i])) > 1 for i in picked))
check("largest cell is probed first",
      picked[0] == max(range(N),
                       key=lambda i: (cells[i][1] - cells[i][0])
                       * (cells[i][3] - cells[i][2])))

pts, spans = AR.child_layout(cells, picked)
check("probe layout matches the point count", pts.shape == (npts, 2), pts.shape)
for k, i in enumerate(picked):
    s0, s1 = spans[k]
    kids = CS.split4(cells[i])
    check(f"span {k} matches children", s1 - s0 == len(kids), (s0, s1, len(kids)))
    for j, kd in enumerate(kids):
        cx, cy = pts[s0 + j]
        if not (kd[0] - 1e-12 <= cx <= kd[1] + 1e-12
                and kd[2] - 1e-12 <= cy <= kd[3] + 1e-12):
            check(f"probe {s0+j} inside its child", False, (cx, cy, kd))
            break
    break

# assembly must use every point exactly once and keep the area
flags = np.zeros(N, dtype=bool)
flags[picked[0]] = True
span_map = {i: spans[k] for k, i in enumerate(picked)}
child_E = {"m": np.full((npts, 3), 2.0 + 0j)}
new_cells, newE = AR.assemble(cells, flags, parent_E, child_E, span_map)
chk = CS.check(new_cells)
check("assembled grid closes", not chk["problems"], chk["problems"])
check("assembled field length", newE["m"].shape[0] == len(new_cells))
check("assembled area conserved", abs(chk["area"] - 15.028) < 1e-9)
# one flagged cell with 4 children replaces 1 cell -> net +3
check("assembled cell count", len(new_cells) == N + 3, len(new_cells))
# the flagged cell's children carry the probe value, the rest keep the parent
n2 = int(np.sum(np.abs(newE["m"][:, 0] - 2.0) < 1e-12))
check("child values placed", n2 == 4, n2)

# indicators: a cell whose children do not change scores zero
ind = AR.indicators(cells, {0: 1.0}, {0: 1.0}, 1.0)
check("no change gives zero indicator", ind[0] == 0.0, ind[0])
ind = AR.indicators(cells, {0: 1.0}, {0: 1.5}, 1.0)
check("change gives the relative size", abs(ind[0] - 0.5) < 1e-12, ind[0])

expect_raise("span mismatch rejected",
             lambda: AR.assemble(cells, flags, parent_E, child_E,
                                 {picked[0]: (0, npts + 5)}), ValueError)

import audit as AU                   # noqa: E402

# --------------------------------------------------------------- audit logic
print("audit logic")
def mk(tag, S, zre, zim, ratio=0.999, cells=1000, area=15.028):
    return dict(tag=tag, cells=cells, area=area,
                ratios={"nom": ratio, "met": ratio, "eqfix": ratio},
                S=S, z_re=zre, z_im=zim)


good = [mk("a", 0.5060, 0.5046, 0.0381), mk("b", 0.5058, 0.5043, 0.0381)]
p, s = AU.check_rounds(good)
check("stable sequence passes", not p, p)
check("one step reported", len(s) == 1, s)

# norms fine, but S drifts too much -> must fail
drift = [mk("a", 0.5060, 0.5046, 0.0381), mk("b", 0.5000, 0.5043, 0.0381)]
p, s = AU.check_rounds(drift)
check("S drift rejected", any("S changed" in x for x in p), p)

# norms fine, S fine, but the complex overlap moves -> must fail
phase = [mk("a", 0.5060, 0.5046, 0.0381), mk("b", 0.5060, 0.5046, 0.0450)]
p, s = AU.check_rounds(phase)
check("overlap drift rejected", any("complex overlap" in x for x in p), p)

# the norm criterion applies to the accepted (last) grid only
seq = [mk("a", 0.5, 0.5, 0.0, ratio=0.95), mk("b", 0.5, 0.5, 0.0, ratio=0.999)]
p, s = AU.check_rounds(seq)
check("coarse first step tolerated", not p, p)
p2, s2 = AU.check_rounds(seq, final_only_norm=False)
check("strict mode rejects the coarse step", any("norm off" in x for x in p2), p2)

bad_area = [mk("a", 0.5, 0.5, 0.0, area=15.0)]
p, s = AU.check_rounds(bad_area)
check("wrong area rejected", any("area" in x for x in p), p)

nan_round = [dict(tag="a", cells=1, area=15.028,
                  ratios={"nom": 1.0}, S=float("nan"), z_re=0.0, z_im=0.0)]
p, s = AU.check_rounds(nan_round)
check("non-finite similarity rejected", any("non-finite" in x for x in p), p)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "material_tracking"))
import run_material as RM             # noqa: E402
import track_pair as TP               # noqa: E402

# ------------------------------------------------- material-step guards
print("material step guards")
good = [(str(i), "1.78", "-1e-4", "0.58") for i in range(1, 41)]
check("complete spectrum accepted",
      not RM.check_mode_list(good, 40), RM.check_mode_list(good, 40))

short = good[:-1]
check("missing mode rejected",
      any("expected" in p for p in RM.check_mode_list(short, 40)),
      RM.check_mode_list(short, 40))

dup = good[:-1] + [good[0]]
check("duplicate mode rejected",
      any("duplicate" in p for p in RM.check_mode_list(dup, 40)),
      RM.check_mode_list(dup, 40))

nanmode = good[:-1] + [("40", "nan", "-1e-4", "0.58")]
check("non-finite neff rejected",
      any("non-finite" in p for p in RM.check_mode_list(nanmode, 40)),
      RM.check_mode_list(nanmode, 40))

weird = good[:-1] + [("40", "99.0", "-1e-4", "0.58")]
check("implausible neff rejected",
      any("implausible" in p for p in RM.check_mode_list(weird, 40)),
      RM.check_mode_list(weird, 40))

check("eps expression at t=0 is exactly 1", RM.eps_expr(0.0) == "1",
      RM.eps_expr(0.0))
check("eps expression keeps t", "0.0004" in RM.eps_expr(4e-4),
      RM.eps_expr(4e-4))

# ------------------------------------------------- pairing guards
print("pairing guards")
rank = [(str(i), "0.02", "0.02", "0.0") for i in range(1, 41)]
rank[39] = ("40", "0.999999", "0.999999", "-0.0003")
check("clean pairing accepted", not TP.check_ranking(rank, 40),
      TP.check_ranking(rank, 40))

weak = list(rank)
weak[39] = ("40", "0.950000", "0.95", "0.0")
check("low similarity rejected",
      any("best S" in p for p in TP.check_ranking(weak, 40)),
      TP.check_ranking(weak, 40))

narrow = list(rank)
narrow[32] = ("33", "0.995000", "0.995", "0.0")
check("narrow margin rejected",
      any("margin" in p for p in TP.check_ranking(narrow, 40)),
      TP.check_ranking(narrow, 40))

check("incomplete ranking rejected",
      any("expected" in p for p in TP.check_ranking(rank[:-1], 40)),
      TP.check_ranking(rank[:-1], 40))

nanrank = list(rank)
nanrank[39] = ("40", "nan", "0.0", "0.0")
check("non-finite overlap rejected",
      any("non-finite" in p for p in TP.check_ranking(nanrank, 40)),
      TP.check_ranking(nanrank, 40))

print()
if fails:
    print(f"FAILED {len(fails)}: {', '.join(fails)}")
    sys.exit(1)
print("all tests passed")

