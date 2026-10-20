"""Normalize COMSOL Data export CSVs and build summary tables for idt_3d_sus."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(r"D:\comsol_ao_run")
OUT = Path(r"D:\tfln\tfln-data\dir11\idt_3d_sus\data")
FIELDS = OUT / "fields"

COLS = [
    "x_m",
    "y_m",
    "z_m",
    "u_m",
    "v_m",
    "w_m",
    "strain_energy_density_J_m3",
    "eXX",
    "eYY",
    "eZZ",
    "eXY",
    "eYZ",
    "eXZ",
    "mises_N_m2",
]


def parse_comsol_export(src: Path, dst: Path) -> None:
    with src.open(encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    data_start = 0
    for i, line in enumerate(lines):
        if not line.startswith("%"):
            data_start = i
            break
    with dst.open("w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(COLS)
        for line in lines[data_start:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 17:
                continue
            # COMSOL repeats x,y,z then 14 field columns (coords duplicated in export).
            w.writerow(parts[3:17])


def read_log_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    return raw.decode("utf-8", errors="replace")


def build_modes_summary() -> None:
    row_re = re.compile(
        r"ROW f_GHz=(?P<f>[\d.]+) k_rad_m=(?P<k>[\deE+\-.]+) "
        r"fracLN=(?P<fln>[\d.]+) fracAl=(?P<fal>[\d.]+) "
        r"pu=(?P<pu>[\d.]+) pv=(?P<pv>[\d.]+) pw=(?P<pw>[\d.]+)"
    )
    text = read_log_text(ROOT / "idt_3d_sus" / "rows.txt")
    rows = []
    for i, m in enumerate(row_re.finditer(text), start=1):
        rows.append(
            {
                "mode_index": i,
                "freq_GHz": m.group("f"),
                "k_rad_m": m.group("k"),
                "frac_strain_LN": m.group("fln"),
                "frac_strain_Al": m.group("fal"),
                "frac_u2_LN": m.group("pu"),
                "frac_v2_LN": m.group("pv"),
                "frac_w2_LN": m.group("pw"),
            }
        )
    out = OUT / "modes_eigen_scan.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def aperture_centerlines() -> None:
    p_half = 2.58e-6 / 2
    y_mid = 250e-9
    tol_x, tol_y = 80e-9, 80e-9
    for src in sorted(FIELDS.glob("idt3d_sus_mode_*_displacement_strain.csv")):
        rows = []
        with src.open(encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                x = float(row["x_m"])
                y = float(row["y_m"])
                if abs(x - p_half) > tol_x or abs(y - y_mid) > tol_y:
                    continue
                rows.append(row)
        rows.sort(key=lambda d: float(d["z_m"]))
        out = OUT / src.name.replace("_displacement_strain.csv", "_aperture_centerline.csv")
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else COLS)
            w.writeheader()
            w.writerows(rows)


def copy_period_source() -> None:
    src = ROOT / "idt_2d_sus" / "rows_final.txt"
    dst = OUT / "period_source_2d_sus_p2p58.csv"
    row_re = re.compile(
        r"ROW p_um=2\.5800 f_GHz=(?P<f>[\d.]+).*pu=(?P<pu>[\d.]+) pv=(?P<pv>[\d.]+)"
    )
    lines = ["freq_GHz,frac_u2_LN,frac_v2_LN,note"]
    for m in row_re.finditer(read_log_text(src)):
        lines.append(f"{m.group('f')},{m.group('pu')},{m.group('pv')},2D suspended unit cell p=2.58um")
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    FIELDS.mkdir(parents=True, exist_ok=True)
    for src in sorted(ROOT.glob("idt3d_sus_mode_*_field.csv")):
        dst = FIELDS / src.name.replace("_field.csv", "_displacement_strain.csv")
        parse_comsol_export(src, dst)
    build_modes_summary()
    copy_period_source()
    aperture_centerlines()
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
