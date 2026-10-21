"""Strict reader for COMSOL 2D Data exports of a complex E field.

Design rules (from the agreed writing guide):
  * columns are located by header name, never by position;
  * length unit comes from the metadata block, never inferred from magnitudes;
  * every value must be finite; a single NaN rejects the whole file;
  * duplicate coordinates are reported, never silently averaged here;
  * header text is decoded strictly, so mojibake fails loudly instead of
    corrupting field names.

A returned record keeps the duplicate groups so the caller can decide policy.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

LENGTH_UNITS = {"m", "um", "µm", "micron", "microns"}


class FieldDataError(Exception):
    """Raised when an export cannot be used without guessing."""


@dataclass
class FieldRecord:
    path: Path
    model: str
    date: str
    version: str
    nodes: int
    unit: str
    neff_tag: str
    x: np.ndarray
    y: np.ndarray
    E: np.ndarray                 # (n, 3) complex, Ex/Ey/Ez
    norm: np.ndarray              # exported |E| for cross-checking only
    norm_rel_mismatch: float
    dup_groups: list = field(default_factory=list)   # arrays of row indices
    dup_max_spread: float = 0.0

    @property
    def dup_extra(self) -> int:
        return int(sum(g.size - 1 for g in self.dup_groups))


def _parse_meta(lines):
    meta, names = {}, None
    for raw in lines:
        if not raw.startswith("%"):
            continue
        body = raw[1:].strip()
        if body.startswith("X,"):
            names = [h.strip() for h in body.split(",")]
            continue
        if "," in body:
            k, v = body.split(",", 1)
            meta[k.strip().lower()] = v.strip().strip('"')
    return names, meta


def _column_map(names, path):
    idx = {}
    for i, n in enumerate(names):
        m = re.fullmatch(r"(real|imag)\(ewfd\.E([xyz])\)\s*(?:\(([^)]*)\))?.*", n)
        if m:
            idx[(m.group(2), m.group(1))] = i
        elif n.startswith("ewfd.normE"):
            idx[("norm", "")] = i
    need = [(c, p) for c in "xyz" for p in ("real", "imag")]
    missing = [k for k in need if k not in idx]
    if missing:
        raise FieldDataError(f"{path.name}: missing field columns {missing}")
    if ("norm", "") not in idx:
        raise FieldDataError(f"{path.name}: missing ewfd.normE column")
    return idx


def read_export(path, dedupe_tol=1e-12):
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise FieldDataError(f"{path.name}: header is not valid UTF-8 ({exc})")
    lines = text.splitlines()
    names, meta = _parse_meta(lines)
    if names is None:
        raise FieldDataError(f"{path.name}: no '% X,' header line")

    unit = meta.get("length unit", "")
    if unit.lower() not in LENGTH_UNITS:
        raise FieldDataError(f"{path.name}: unsupported length unit {unit!r}")

    idx = _column_map(names, path)
    data = np.loadtxt(lines, delimiter=",", comments="%", ndmin=2)
    if data.size == 0:
        raise FieldDataError(f"{path.name}: no data rows")
    if data.shape[1] != len(names):
        raise FieldDataError(
            f"{path.name}: {data.shape[1]} data columns but header declares "
            f"{len(names)}")
    if not np.isfinite(data).all():
        rows, cols = np.where(~np.isfinite(data))
        raise FieldDataError(
            f"{path.name}: {rows.size} non-finite entries, first at "
            f"row {rows[0] + 1}, column {cols[0] + 1}")

    x = data[:, 0].copy()
    y = data[:, 1].copy()
    if unit.lower() == "m":
        x *= 1e6
        y *= 1e6

    E = np.stack([data[:, idx[(c, "real")]] + 1j * data[:, idx[(c, "imag")]]
                  for c in "xyz"], axis=1)
    norm = data[:, idx[("norm", "")]]

    rebuilt = np.sqrt(np.sum(np.abs(E) ** 2, axis=1))
    denom = max(float(np.linalg.norm(norm)), 1e-30)
    mismatch = float(np.linalg.norm(rebuilt - norm) / denom)

    key = np.round(np.c_[x, y] / dedupe_tol).astype(np.int64)
    uniq, inv, counts = np.unique(key, axis=0, return_inverse=True,
                                  return_counts=True)
    groups = [np.where(inv == g)[0] for g in np.where(counts > 1)[0]]
    spread = 0.0
    for g in groups:
        spread = max(spread, float(np.max(np.abs(E[g] - E[g][0]))))

    tag = re.search(r"@\s*([0-9.eE+-]+(?:[+-][0-9.eE+-]+i)?)",
                    names[idx[("x", "real")]])
    return FieldRecord(
        path=path,
        model=meta.get("model", "?"),
        date=meta.get("date", "?"),
        version=meta.get("version", "?"),
        nodes=int(data.shape[0]),
        unit=unit,
        neff_tag=tag.group(1) if tag else "?",
        x=x, y=y, E=E, norm=norm,
        norm_rel_mismatch=mismatch,
        dup_groups=groups,
        dup_max_spread=spread,
    )
