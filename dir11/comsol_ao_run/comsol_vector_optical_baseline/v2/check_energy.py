"""Strict cross-check of mode attenuation against dissipated power.

alpha_mode   = 2 k0 |Im(neff)|
alpha_energy = Pdiss(metal) / Pflow

PASS requires ALL of:
  * an ENERGY line for every NEFF mode, and vice versa
  * every Im(neff) < 0 and every dampz > 0
  * every Pflow finite and > 0
  * every ratio within 5 % of unity

Usage:
  python check_energy.py out/run_tag.log
  python check_energy.py --selftest
"""
import math
import re
import sys
from pathlib import Path

K0 = 2 * math.pi / 1.55e-6
TOL = 0.05


def parse(text):
    neff = {}
    for m in re.finditer(r"NEFF mode=(\d+) re=(\S+) im=(\S+) dampz=(\S+)", text):
        neff[int(m.group(1))] = (float(m.group(2)), float(m.group(3)),
                                 float(m.group(4)))
    energy = {}
    for m in re.finditer(r"ENERGY mode=(\d+) Pdiss=(\S+) Pflow=(\S+)", text):
        energy[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
    return neff, energy


def evaluate(text, verbose=True):
    neff, energy = parse(text)
    problems = []
    if not energy:
        return False, ["no ENERGY lines (check ENBAL_FAILED)"]
    if set(neff) != set(energy):
        problems.append(f"mode sets differ: neff {sorted(neff)} vs "
                        f"energy {sorted(energy)}")
    for mode in sorted(set(neff) & set(energy)):
        pd, pf = energy[mode]
        re_n, im_n, dampz = neff[mode]
        # finite checks first: NaN compares false with everything and would
        # otherwise slip through every later test
        if not all(math.isfinite(v) for v in (pd, pf, re_n, im_n, dampz)):
            problems.append(f"mode {mode}: non-finite value "
                            f"(Pdiss={pd}, Pflow={pf}, re={re_n}, "
                            f"im={im_n}, dampz={dampz})")
            continue
        if not (pf > 0):
            problems.append(f"mode {mode}: Pflow not positive ({pf})")
            continue
        if im_n >= 0:
            problems.append(f"mode {mode}: Im(neff)={im_n} not negative")
        if dampz <= 0:
            problems.append(f"mode {mode}: dampz={dampz} not positive")
        a_m = 2 * K0 * abs(im_n)
        a_e = pd / pf
        if a_m == 0:
            problems.append(f"mode {mode}: zero alpha_mode")
            continue
        ratio = a_e / a_m
        if abs(ratio - 1) > TOL:
            problems.append(f"mode {mode}: alpha ratio {ratio:.4f} "
                            f"outside {TOL:.0%}")
        if verbose:
            print(f"{mode:4d} {im_n:11.3e} {a_m:12.3e} {a_e:13.3e} "
                  f"{ratio:7.4f}")
    return len(problems) == 0, problems


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        good = ("NEFF mode=1 re=1.80 im=-1.0e-2 dampz=1.0e4\n"
                "NEFF mode=2 re=1.70 im=-2.0e-2 dampz=2.0e4\n"
                "ENERGY mode=1 Pdiss=1.0e-7 Pflow=1.234e-12\n"
                "ENERGY mode=2 Pdiss=2.0e-7 Pflow=1.234e-12\n")
        badsign = good.replace("im=-1.0e-2", "im=+1.0e-2")
        badratio = good.replace("Pdiss=1.0e-7", "Pdiss=2.0e-7")
        missing = good.replace("ENERGY mode=2 Pdiss=2.0e-7 Pflow=1.234e-12\n", "")
        zeropf = good.replace("Pflow=1.234e-12", "Pflow=0", 1)
        nan_case = good.replace("im=-1.0e-2", "im=nan")
        inf_case = good.replace("Pflow=1.234e-12", "Pflow=inf", 1)
        cases = [("good", good, True), ("bad sign", badsign, False),
                 ("bad ratio", badratio, False), ("missing mode", missing, False),
                 ("zero flow", zeropf, False), ("nan value", nan_case, False),
                 ("inf value", inf_case, False)]
        ok_all = True
        for name, text, expect in cases:
            ok, probs = evaluate(text, verbose=False)
            same = (ok == expect)
            ok_all = ok_all and same
            print(f"{name:14s} -> {'PASS' if ok else 'FAIL'}"
                  f"{'' if same else '   <-- guard broken'}")
            for p in probs[:2]:
                print(f"                 {p}")
        print("\nSELFTEST " + ("PASS" if ok_all else "FAIL"))
        return 0 if ok_all else 1

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if path is None or not path.exists():
        raise SystemExit("give a COMSOL log file, or --selftest")
    print(path.name)
    print(f"{'mode':>4s} {'Im(neff)':>11s} {'alpha_mode':>12s} "
          f"{'alpha_energy':>13s} {'ratio':>7s}")
    ok, problems = evaluate(path.read_text(encoding="utf-8", errors="replace"))
    for p in problems:
        print("  PROBLEM: " + p)
    print("\n" + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

