"""Read-only inspection of existing COMSOL field exports.

Prints one row per file and exits non-zero if any file cannot be used:
  * header/column mismatch, non-finite values, unknown unit  -> hard failure
  * interface duplicates or a normE/|E| mismatch above the stated
    thresholds -> reported and counted as a warning, because they require an
    explicit handling decision rather than silent acceptance.

Usage:
  python inspect_exports.py [glob]
  python inspect_exports.py "..\\out\\f_*.csv"
"""
import glob
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import read_fields as rf

NORM_WARN = 0.01        # 1 % relative mismatch between normE and |E|


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else "../out/f_*.csv"
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit(f"no files match {pattern}")

    print(f"{'file':24s} {'nodes':>6s} {'unit':>4s} {'neff':>18s} "
          f"{'dups':>5s} {'spread':>9s} {'normErr':>8s}  state")
    bad = 0
    warned = 0
    for f in files:
        try:
            r = rf.read_export(f)
        except Exception as exc:
            print(f"{Path(f).name:24s} {'-':>6s} {'-':>4s} {'-':>18s} "
                  f"{'-':>5s} {'-':>9s} {'-':>8s}  REJECT ({exc})")
            bad += 1
            continue
        warn = (r.dup_extra > 0) or (r.norm_rel_mismatch > NORM_WARN)
        warned += int(warn)
        print(f"{r.path.name:24s} {r.nodes:6d} {r.unit:>4s} {r.neff_tag:>18s} "
              f"{r.dup_extra:5d} {r.dup_max_spread:9.2e} "
              f"{r.norm_rel_mismatch*100:7.2f}%  "
              f"{'WARN' if warn else 'ok'}")
        if r.dup_extra:
            print(f"{'':24s} -> {len(r.dup_groups)} duplicated coordinates: "
                  "interface sides; dedupe policy must be stated")

    print(f"\n{len(files) - bad} readable, {bad} rejected, {warned} with "
          "warnings")
    if bad:
        print("RESULT FAIL")
        return 1
    if warned:
        print("RESULT PASS_WITH_WARNINGS - dedupe policy required before "
              "comparison")
        return 0
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
