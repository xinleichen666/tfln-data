"""One-shot pack of photoelastic logs into data/*.csv (UTF-8)."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(r"D:\comsol_ao_run\photoelastic")
OUT = Path(__file__).resolve().parents[1] / "data"


def read_log(path: Path) -> str:
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    return raw.decode("utf-8", errors="replace")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_log(ROOT / "rows.txt")
    sweep = read_log(ROOT / "sweep_rows.txt")

    slab = []
    for m in re.finditer(
        r"SLAB_(TE|TM) neff=([\d.]+) ng=([\d.]+) GammaE=([\d.]+) kappa=([\deE+\-.]+)",
        rows,
    ):
        slab.append(
            {
                "pol": m.group(1),
                "neff": m.group(2),
                "ng": m.group(3),
                "GammaE": m.group(4),
                "kappa_1_per_m": m.group(5),
            }
        )
    with (OUT / "slab_analytic_500nm.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(slab[0].keys()))
        w.writeheader()
        w.writerows(slab)

    eig = []
    for m in re.finditer(
        r"EIG f_GHz=([\d.]+) fi_MHz=([\d.]+) fracLN=([\d.]+) pu=([\d.]+) pv=([\d.]+)",
        rows,
    ):
        eig.append(
            {
                "f_GHz": m.group(1),
                "fi_MHz": m.group(2),
                "frac_strain_LN": m.group(3),
                "frac_u2_LN": m.group(4),
                "frac_v2_LN": m.group(5),
            }
        )
    with (OUT / "eigenmodes_2d_suspended.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(eig[0].keys()))
        w.writeheader()
        w.writerows(eig)

    fd = []
    for m in re.finditer(
        r"FD f_GHz=([\d.]+) Vmax=([\d.]+) vmax_pm=([\d.]+) vrms_pm=([\d.]+) "
        r"vmean_pm=([\d.]+) S1pk=([\deE+\-.]+) S2pk=([\deE+\-.]+) dfTE_GHz=([\d.]+)",
        rows,
    ):
        fd.append(
            {
                "f_GHz": m.group(1),
                "Vmax": m.group(2),
                "vmax_pm": m.group(3),
                "vrms_pm": m.group(4),
                "vmean_pm": m.group(5),
                "S1pk": m.group(6),
                "S2pk": m.group(7),
                "dfTE_GHz": m.group(8),
            }
        )
    with (OUT / "drive_frequency_detuning.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fd[0].keys()))
        w.writeheader()
        w.writerows(fd)

    win = []
    for m in re.finditer(
        r"WIN w_um=([\d.]+) x0_um=([\d.]+) df_GHz=([\d.]+) df23_GHz=([\d.]+) xi=([\d.]+)",
        sweep,
    ):
        w_um, x0 = float(m.group(1)), float(m.group(2))
        win.append(
            {
                "period_um": "2.8326",
                "window_w_um": m.group(1),
                "window_x0_um": m.group(2),
                "window_x1_um": f"{x0 + w_um:.4f}",
                "df_GHz": m.group(3),
                "df_ng23_GHz": m.group(4),
                "xi": m.group(5),
            }
        )
    with (OUT / "light_window_sweep.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(win[0].keys()))
        w.writeheader()
        w.writerows(win)

    best = re.search(
        r"BEST w_um=([\d.]+) x0_um=([\d.]+) df_GHz=([\d.]+) df23_GHz=([\d.]+) xi=([\d.]+)",
        sweep,
    )
    assert best
    with (OUT / "light_window_best.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "period_um",
                "window_w_um",
                "window_x0_um",
                "window_x1_um",
                "df_GHz",
                "df_ng23_GHz",
                "xi",
            ]
        )
        w0, x0 = float(best.group(1)), float(best.group(2))
        w.writerow(
            [
                "2.8326",
                best.group(1),
                best.group(2),
                f"{x0 + w0:.4f}",
                best.group(3),
                best.group(4),
                best.group(5),
            ]
        )

    print("Wrote", OUT)


if __name__ == "__main__":
    main()
