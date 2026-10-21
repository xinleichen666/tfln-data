"""Acceptance audit across refinement rounds, with provenance checks.

The earlier driver printed PASS while only checking norms and shares; the
stability of S and of the complex overlap between consecutive rounds was
computed by hand and never enforced.  Here those checks are part of the
verdict, and every round must be traceable to the runs that produced it.

Nothing is evaluated: this only reads existing artefacts.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cellspec as C                      # noqa: E402
import compare_integrals as CI            # noqa: E402
import compare_weighted as CW             # noqa: E402
import run_grid as RG                     # noqa: E402


def check_rounds(rounds, ds_tol=0.005, dz_tol=0.005, final_only_norm=True):
    """Pure acceptance logic over a sequence of rounds (oldest first).

    Each round: dict(tag, cells, area, ratios{model: ratio}, S, z_re, z_im).
    Returns (problems, steps).

    The 1 % norm criterion applies to the grid that is to be accepted (the
    last one); earlier rounds are steps in the sequence and are reported but
    not required to pass, otherwise a converging sequence could never be
    accepted merely because its first step was coarse.
    """
    problems, steps = [], []
    for i, r in enumerate(rounds):
        if not np.isfinite([r["S"], r["z_re"], r["z_im"]]).all():
            problems.append(f"{r['tag']}: non-finite similarity")
        if abs(r["area"] - 15.028) > 1e-9:
            problems.append(f"{r['tag']}: area {r['area']:.9f} != 15.028")
        if r["cells"] <= 0:
            problems.append(f"{r['tag']}: no cells")
        last = (i == len(rounds) - 1)
        if last or not final_only_norm:
            for name, ratio in r["ratios"].items():
                if abs(ratio - 1) > 0.01:
                    problems.append(f"{r['tag']}/{name}: norm off by "
                                    f"{100*(ratio-1):+.2f} %")
    for a, b in zip(rounds[:-1], rounds[1:]):
        dS = abs(b["S"] - a["S"])
        dz = float(np.hypot(b["z_re"] - a["z_re"], b["z_im"] - a["z_im"]))
        steps.append((a["tag"], b["tag"], dS, dz))
        if dS > ds_tol:
            problems.append(f"S changed by {dS:.4f} between {a['tag']} and "
                            f"{b['tag']} (tolerance {ds_tol})")
        if dz > dz_tol:
            problems.append(f"complex overlap changed by {dz:.4f} between "
                            f"{a['tag']} and {b['tag']} (tolerance {dz_tol})")
    return problems, steps


def sha256(path, limit=None):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        read = 0
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
            read += len(b)
            if limit is not None and read >= limit:
                break
    return h.hexdigest()


def load_fields(tag, cells):
    """Fields for a round: rec_<tag>/*.csv, else the grid run points.csv."""
    sp = C.arrays(cells)
    E, src = {}, {}
    for name, _f, _m, _i in RG.MODELS:
        rec = HERE / "runs" / f"rec_{tag}" / f"{name}.csv"
        if rec.exists():
            a = np.loadtxt(rec, delimiter=",", skiprows=1)
            if a.shape[0] != len(cells):
                raise SystemExit(f"{tag}/{name}: {a.shape[0]} rows vs "
                                 f"{len(cells)} cells")
            if np.max(np.abs(a[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
                raise SystemExit(f"{tag}/{name}: coordinates differ")
            E[name] = np.stack([a[:, 2] + 1j * a[:, 3],
                                a[:, 4] + 1j * a[:, 5],
                                a[:, 6] + 1j * a[:, 7]], axis=1)
            src[name] = str(rec.relative_to(HERE))
            continue
        hits = sorted((HERE / "runs").glob(f"*_{tag}_{name}"))
        if len(hits) != 1:
            raise SystemExit(f"{tag}/{name}: expected one run, got {hits}")
        a = np.loadtxt(hits[0] / "points.csv", delimiter=",", skiprows=1)
        if a.shape[0] != len(cells):
            raise SystemExit(f"{tag}/{name}: {a.shape[0]} points vs {len(cells)}")
        if np.max(np.abs(a[:, :2] - np.c_[sp["x"], sp["y"]])) > 1e-9:
            raise SystemExit(f"{tag}/{name}: coordinates differ")
        E[name] = np.stack([a[:, 4] + 1j * a[:, 5], a[:, 6] + 1j * a[:, 7],
                            a[:, 8] + 1j * a[:, 9]], axis=1)
        src[name] = str((hits[0] / "points.csv").relative_to(HERE))
    return sp, E, src


def provenance(tag):
    """Which runs exist for this tag, and how often each model was evaluated."""
    import re
    rows, counts = [], {}
    for d in sorted((HERE / "runs").glob(f"*_{tag}*")):
        if not d.is_dir():
            continue
        log = d / "eval.log"
        m = d.name
        model = ("nom" if m.endswith("nom") else
                 "met" if m.endswith("met") else
                 "eqfix" if m.endswith("eqfix") else "?")
        npts, neff = "?", "?"
        if log.exists():
            txt = log.read_text(encoding="utf-8", errors="replace")
            s = re.search(r"SHAPE expr=\d+ sol=\d+ pts=(\d+)", txt)
            n = re.search(r"MODENEFF sol=\d+ re=(\S+) im=(\S+)", txt)
            if s:
                npts = int(s.group(1))
            if n:
                neff = f"{n.group(1)},{n.group(2)}"
        rows.append(dict(dir=d.name, model=model, points=npts, neff=neff))
        counts[model] = counts.get(model, 0) + 1
    dups = {k: v for k, v in counts.items() if v > 1}
    return rows, dups



def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", nargs="+",
                    default=["adapt3", "rec1all", "rec2", "rec3low"])
    ap.add_argument("--manifest", default="MANIFEST.json")
    a = ap.parse_args()

    ref = RG.load_ref()
    rounds, sources, round_extra = [], {}, []
    for tag in a.rounds:
        cp = HERE / "runs" / f"cells_{tag}.csv"
        if not cp.exists():
            raise SystemExit(f"missing cell list {cp}")
        cells = [tuple(float(v) for v in ln.split(","))
                 for ln in cp.read_text(encoding="utf-8").splitlines()[1:]
                 if ln.strip()]
        chk = C.check(cells)
        sp, E, src = load_fields(tag, cells)
        sources[tag] = src
        ratios = {}
        share_bad = []
        for name, _f, _m, _i in RG.MODELS:
            rows, tr, ts, bad, contrib = CI.run_compare(
                ref[name], E[name], sp["w"], sp["region"])
            ratios[name] = ts / tr
            share_bad.extend(f"{name}: {b}" for b in bad
                             if "share" in b or "component" in b)
        if share_bad:
            round_extra.extend(f"{tag}: {b}" for b in share_bad)
        S = CW.similarity(E["nom"], E["met"], sp["w"])
        I = np.sum(sp["w"] * np.sum(np.conj(E["nom"]) * E["met"], axis=1))
        n0 = np.sum(sp["w"] * np.sum(np.abs(E["nom"]) ** 2, axis=1))
        n1 = np.sum(sp["w"] * np.sum(np.abs(E["met"]) ** 2, axis=1))
        z = I / np.sqrt(n0 * n1)
        rounds.append(dict(tag=tag, cells=len(cells), area=chk["area"],
                           ratios=ratios, S=float(S), z_re=float(z.real),
                           z_im=float(z.imag), problems=list(chk["problems"])))
        print(f"  {tag:9s} {len(cells):6d} cells  "
              f"nom {ratios['nom']:.5f} met {ratios['met']:.5f} "
              f"eqfix {ratios['eqfix']:.5f}  S {S:.6f} "
              f"z {z.real:.6f}{z.imag:+.6f}i")

    problems, steps = check_rounds(rounds)
    for r in rounds:
        for p in r["problems"]:
            problems.append(f"{r['tag']}: {p}")
    # region and polarisation problems must reach the verdict too; they were
    # previously computed and then dropped
    problems.extend(round_extra)

    print("\nconsecutive changes")
    for t0, t1, dS, dz in steps:
        flag = "ok" if (dS <= 0.005 and dz <= 0.005) else "TOO LARGE"
        print(f"  {t0:9s} -> {t1:9s}  dS {dS:.4f}  |dz| {dz:.4f}   {flag}")

    print("\nprovenance")
    all_dups = []
    for tag in a.rounds:
        rows, dups = provenance(tag)
        print(f"  {tag}: {len(rows)} run directories, "
              f"{len(dups)} duplicated dir/model pairs")
        for r in rows:
            print(f"     {r['dir']:44s} {r['model']:6s} pts {str(r['points']):>6s} "
                  f"neff {r['neff']}")
        all_dups.extend((tag, d) for d in dups)
    if all_dups:
        print("  NOTE: repeated evaluations exist.  Assembly uses each value "
              "once, but these runs were executed more than once and are "
              "reported as such.")

    man = dict(rounds=rounds,
               steps=[dict(a=t0, b=t1, dS=dS, dz=dz)
                      for t0, t1, dS, dz in steps],
               sources=sources,
               duplicates=[list(map(str, d)) for d in all_dups],
               problems=problems)

    # file hashes: what exactly was accepted
    files = []
    targets = sorted((HERE / "runs").glob("integrals_*/integrals.csv"))
    targets += sorted((HERE / "runs").glob("cells_*.csv"))
    targets += sorted((HERE / "runs").glob("recursive_*.json"))
    targets += sorted((HERE / "runs").glob("rec_*/*.csv"))
    targets += sorted((HERE.parents[1] / "out").glob("final_*.mph"))
    for p in targets:
        files.append(dict(path=str(p.relative_to(HERE.parents[1])),
                          size=p.stat().st_size, sha256=sha256(p)))
    man["files"] = files
    (HERE / "runs" / a.manifest).write_text(
        json.dumps(man, indent=2), encoding="utf-8")
    print(f"\nmanifest: {len(files)} files hashed -> runs/{a.manifest}")

    print(f"\nRESULT {'PASS' if not problems else 'FAIL'}")
    for p in problems:
        print("  PROBLEM: " + p)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
