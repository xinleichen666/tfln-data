"""True recursive refinement: children of a probe set become the next grid.

Differences from the earlier attempt, which silently restarted from the n=12
grid every time:

  * the input is a cell list plus the fields already evaluated on it, so a
    round genuinely continues from the previous grid;
  * children are probed and compared with their parent, so the decision uses a
    measured change at the current scale, not a stale n=6 -> n=12 estimate;
  * the refined grid reuses the probe values, so no point is evaluated twice;
  * every cell is counted against a budget before anything is run.

The pure functions below are unit tested; main() is the only part that touches
COMSOL.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cellspec as C                      # noqa: E402


def choose_candidates(cells, probe_budget, min_side=C.MIN_SIDE, score=None):
    """Pick cells worth probing, highest score first, within the probe budget.

    The default score is the cell area (truncation error scales with it).  In
    practice the field-weighted score is better: a large cell in empty air
    cannot contribute to the integral, so probing it wastes budget.
    """
    if score is None:
        score = [(c[1] - c[0]) * (c[3] - c[2]) for c in cells]
    order = sorted(range(len(cells)), key=lambda i: -float(score[i]))
    picked, npts = [], 0
    for i in order:
        kids = C.split4(cells[i], min_side)
        if len(kids) == 1:
            continue
        if npts + len(kids) > probe_budget:
            break
        picked.append(i)
        npts += len(kids)
    return picked, npts


def child_layout(cells, picked, min_side=C.MIN_SIDE):
    """Flat layout of the probe points and how they map back to parents."""
    pts, spans = [], []
    for i in picked:
        kids = C.split4(cells[i], min_side)
        spans.append((len(pts), len(pts) + len(kids)))
        for k in kids:
            pts.append((0.5 * (k[0] + k[1]), 0.5 * (k[2] + k[3])))
    return np.array(pts).reshape(-1, 2), spans


def indicators(cells, parent_I, child_I, tot_ref):
    """Relative integral change per cell: |sum(children) - parent| / total.

    parent_I, child_I: dicts keyed by cell index.  Only cells present in both
    are scored; everything else stays at zero.
    """
    ind = np.zeros(len(cells))
    for i, ci in child_I.items():
        ind[i] = abs(ci - parent_I[i]) / tot_ref
    return ind


def assemble(cells, flags, parent_E, child_E, spans, min_side=C.MIN_SIDE):
    """Build the refined grid and its fields from parent and child values.

    Every point is used exactly once: a flagged cell contributes its children
    (already probed), an unflagged cell contributes its own value.
    """
    new_cells = []
    rows = {name: [] for name in parent_E}
    for i, cell in enumerate(cells):
        if flags[i]:
            kids = C.split4(cell, min_side)
            a, b = spans[i]
            if b - a != len(kids):
                raise ValueError("probe span does not match the child count")
            for j, k in enumerate(kids):
                new_cells.append(k)
                for name in parent_E:
                    rows[name].append(child_E[name][a + j])
        else:
            new_cells.append(cell)
            for name in parent_E:
                rows[name].append(parent_E[name][i])
    out = {name: np.array(v) for name, v in rows.items()}
    for name, arr in out.items():
        if arr.shape[0] != len(new_cells):
            raise ValueError("assembled field does not match the grid")
    return new_cells, out



def load_grid(prevtag, cells_path):
    """Cells plus the fields already evaluated on them."""
    import run_grid as RG
    cells = [tuple(float(v) for v in ln.split(","))
             for ln in Path(cells_path).read_text(encoding="utf-8").splitlines()[1:]
             if ln.strip()]
    sp = C.arrays(cells)
    E, dom = {}, {}
    for name, _f, _m, _i in RG.MODELS:
        rec = HERE / "runs" / f"rec_{prevtag}" / f"{name}.csv"
        if rec.exists():
            a = np.loadtxt(rec, delimiter=",", skiprows=1)
            if a.shape[0] != len(cells):
                raise SystemExit(f"{name}: {a.shape[0]} rows vs {len(cells)}")
            if np.max(np.abs(a[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
                raise SystemExit(f"{name}: saved coordinates do not match")
            E[name] = np.stack([a[:, 2] + 1j * a[:, 3], a[:, 4] + 1j * a[:, 5],
                                a[:, 6] + 1j * a[:, 7]], axis=1)
            dom[name] = None
            continue
        hits = sorted((HERE / "runs").glob(f"*_{prevtag}_{name}"))
        if len(hits) != 1:
            raise SystemExit(f"expected one run for {prevtag}_{name}, got {hits}")
        a = np.loadtxt(hits[0] / "points.csv", delimiter=",", skiprows=1)
        if a.shape[0] != len(cells):
            raise SystemExit(f"{name}: {a.shape[0]} points vs {len(cells)} cells")
        if np.max(np.abs(a[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
            raise SystemExit(f"{name}: coordinates differ from the cell list")
        E[name] = np.stack([a[:, 4] + 1j * a[:, 5], a[:, 6] + 1j * a[:, 7],
                            a[:, 8] + 1j * a[:, 9]], axis=1)
        dom[name] = a[:, 2].astype(int)
    return cells, sp, E, dom


def main():
    import argparse
    import compare_integrals as CI
    import compare_weighted as CW
    import evalpoints as EP
    import run_grid as RG
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--prev", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--budget", type=int, default=20000)
    ap.add_argument("--probe", type=int, default=18000)
    ap.add_argument("--share", type=float, default=1e-4)
    ap.add_argument("--min-side", type=float, default=C.MIN_SIDE)
    a = ap.parse_args()

    cells, sp, E, dom = load_grid(a.prev, a.cells)
    ref = RG.load_ref()
    tot_ref = {k: sum(v[0] for v in d.values()) for k, d in ref.items()}
    w = sp["w"]
    print(f"round {a.tag}: start from {len(cells)} cells ({a.prev})")

    # probe where the field actually is: area x |E|^2 summed over the models
    score = np.zeros(len(cells))
    for name, _f, _m, _i in RG.MODELS:
        score += w * np.sum(np.abs(E[name]) ** 2, axis=1)
    picked, nprobe = choose_candidates(cells, a.probe, min_side=a.min_side, score=score)
    print(f"  candidates {len(picked)}, probe points {nprobe} "
          f"(budget {a.probe})")
    if nprobe > a.probe:
        raise SystemExit("probe budget exceeded")

    pts, spans = child_layout(cells, picked, a.min_side)
    sp_map = {i: (spans[k][0], spans[k][1]) for k, i in enumerate(picked)}
    par_reg = sp["region"]
    child_E = {}
    for name, fname, metal, _i in RG.MODELS:
        arr, neff, run = EP.eval_points(RG.OUT / fname, RG.SOLNUM,
                                        pts[:, 0], pts[:, 1],
                                        f"{a.tag}_probe_{name}")
        want = []
        for k, i in enumerate(picked):
            s0, s1 = spans[k]
            want.extend([RG.DOM[metal == "1"][par_reg[i]]] * (s1 - s0))
        got = arr[:, 2].astype(int)
        bad = np.where(got != np.array(want))[0]
        if bad.size:
            raise SystemExit(f"{name}: {bad.size} probe domain mismatches")
        child_E[name] = np.stack([arr[:, 4] + 1j * arr[:, 5],
                                  arr[:, 6] + 1j * arr[:, 7],
                                  arr[:, 8] + 1j * arr[:, 9]], axis=1)
        print(f"  {name}: {arr.shape[0]} probe points, domains ok, "
              f"neff {neff[0]:.12f}")

    # indicator: measured change between a cell and its children, per model
    ind = np.zeros(len(cells))
    for name, _f, _m, _i in RG.MODELS:
        v_par = np.sum(np.abs(E[name]) ** 2, axis=1)
        v_ch = np.sum(np.abs(child_E[name]) ** 2, axis=1)
        parent_I, child_I = {}, {}
        for k, i in enumerate(picked):
            s0, s1 = spans[k]
            kids = C.split4(cells[i], a.min_side)
            cw = np.array([(c[1] - c[0]) * (c[3] - c[2]) for c in kids])
            parent_I[i] = v_par[i] * w[i]
            child_I[i] = float(np.sum(v_ch[s0:s1] * cw))
        ind = np.maximum(ind, indicators(cells, parent_I, child_I,
                                         tot_ref[name]))


    order = np.argsort(-ind)
    flags = np.zeros(len(cells), dtype=bool)
    final_n = len(cells)
    for k in order:
        if ind[k] < a.share:
            break
        if k not in sp_map:
            continue          # cannot refine a cell that was not probed
        growth = len(C.split4(cells[k], a.min_side)) - 1
        if final_n + growth > a.budget:
            continue
        flags[k] = True
        final_n += growth
    print(f"  flagged {int(flags.sum())} cells -> {final_n} cells "
          f"(budget {a.budget}); max indicator {ind.max():.2e}")

    new_cells, newE = assemble(cells, flags, E, child_E, sp_map, a.min_side)
    chk = C.check(new_cells)
    print(f"  new grid {len(new_cells)} cells, area {chk['area']:.9f}, "
          f"min side {chk['info']['min_side']*1000:.2f} nm")
    if chk["problems"]:
        raise SystemExit("refined grid failed: " + "; ".join(chk["problems"]))
    nsp = C.arrays(new_cells)
    rec = HERE / "runs" / f"rec_{a.tag}"
    rec.mkdir(parents=True, exist_ok=True)
    for name in newE:
        cols = np.column_stack([nsp["x"], nsp["y"],
                                newE[name][:, 0].real, newE[name][:, 0].imag,
                                newE[name][:, 1].real, newE[name][:, 1].imag,
                                newE[name][:, 2].real, newE[name][:, 2].imag])
        np.savetxt(rec / f"{name}.csv", cols, delimiter=",",
                   header="x,y,Exre,Exim,Eyre,Eyim,Ezre,Ezim", comments="")
    np.savetxt(HERE / "runs" / f"cells_{a.tag}.csv", np.array(new_cells),
               delimiter=",", header="x0,x1,y0,y1", comments="", fmt="%.9f")

    print("\nagainst the domain-integral reference")
    ok = True
    for name, _f, _m, _i in RG.MODELS:
        rows, tr, ts, bad, contrib = CI.run_compare(
            ref[name], newE[name], nsp["w"], nsp["region"])
        print(f"  {name:6s} total ratio {ts/tr:.5f} ({100*(ts/tr-1):+.2f} %)  "
              f"{'PASS' if not bad else 'FAIL'}")
        for b in bad:
            print("     " + b)
        ok = ok and not bad

    S = CW.similarity(newE["nom"], newE["met"], nsp["w"])
    I = np.sum(nsp["w"] * np.sum(np.conj(newE["nom"]) * newE["met"], axis=1))
    n0 = np.sum(nsp["w"] * np.sum(np.abs(newE["nom"]) ** 2, axis=1))
    n1 = np.sum(nsp["w"] * np.sum(np.abs(newE["met"]) ** 2, axis=1))
    z = I / np.sqrt(n0 * n1)
    Se = CW.similarity(newE["nom"], newE["eqfix"], nsp["w"])
    print(f"\n  S(nom,met) = {S:.6f}   overlap {z.real:.6f}{z.imag:+.6f}i   "
          f"S(nom,eqfix) = {Se:.6f}")
    (HERE / "runs" / f"recursive_{a.tag}.json").write_text(json.dumps(
        dict(start=len(cells), cells=len(new_cells), flagged=int(flags.sum()),
             probe_points=int(nprobe), area=chk["area"], S=float(S),
             z_re=float(z.real), z_im=float(z.imag), S_eq=float(Se)),
        indent=2), encoding="utf-8")
    print(f"\nRESULT {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

