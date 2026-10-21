"""Reader for COMSOL 2D Data exports of a mode's complex E field.

Header layout (verified against the actual files):
    % X,Y,ewfd.normE (V/m) @ <neff> 1,real(ewfd.Ex) (V/m) @ ...,imag(...),...

The physical columns are located by name, never by position, and the length
unit is taken from the metadata line rather than guessed from coordinate size.

read_mode() also reports diagnostics that matter for interpolation:
  * duplicate (x, y) points and whether their field values agree,
  * the mismatch between the exported normE and |E| rebuilt from components.
"""
import re
from pathlib import Path

import numpy as np

DUP_TOL = 1e-12


class DataError(SystemExit):
    pass


def _header(fh):
    meta = {}
    names = None
    for line in fh:
        if line.startswith("% "):
            body = line[2:].strip()
            if body.startswith("X,"):
                names = [h.strip() for h in body.split(",")]
            elif "," in body:
                k, v = body.split(",", 1)
                meta[k.strip().lower()] = v.strip()
    return names, meta


def read_mode(path, strict=True):
    path = Path(path)
    with path.open(encoding="utf-8", errors="replace") as fh:
        names, meta = _header(fh)
    if names is None:
        raise DataError(f"{path.name}: no '% X,' header line")

    unit = meta.get("length unit", "?")
    if unit.lower() not in ("µm", "um", "micron", "microns", "m"):
        raise DataError(f"{path.name}: unexpected length unit {unit!r}")

    idx = {}
    for i, n in enumerate(names):
        m = re.match(r"(real|imag)\(ewfd\.E([xyz])\)", n)
        if m:
            idx[(m.group(2), m.group(1))] = i
        if n.startswith("ewfd.normE"):
            idx[("norm", "")] = i
    missing = [k for k in [(c, p) for c in "xyz" for p in ("real", "imag")]
               if k not in idx]
    if missing or ("norm", "") not in idx:
        raise DataError(f"{path.name}: missing columns {missing}")

    tag = re.search(r"@\s*([0-9.eE+-]+(?:[+-][0-9.eE+-]+i)?)",
                    names[idx[("x", "real")]])
    neff = tag.group(1) if tag else "?"

    with path.open(encoding="utf-8", errors="replace") as fh:
        a = np.loadtxt(fh, delimiter=",", comments="%")
    if a.ndim != 2 or a.shape[1] != len(names):
        raise DataError(f"{path.name}: {a.shape[1]} columns, "
                        f"header declares {len(names)}")
    if not np.isfinite(a).all():
        bad = int((~np.isfinite(a)).sum())
        raise DataError(f"{path.name}: {bad} non-finite entries")

    x, y = a[:, 0].copy(), a[:, 1].copy()
    if unit.lower() == "m":
        x, y = x * 1e6, y * 1e6

    E = np.stack([a[:, idx[(c, "real")]] + 1j * a[:, idx[(c, "imag")]]
                  for c in "xyz"], axis=1)
    norm = a[:, idx[("norm", "")]]

    diag = dict(path=path, unit=unit, neff=neff, nodes=a.shape[0])
    rebuilt = np.sqrt(np.sum(np.abs(E) ** 2, axis=1))
    diag["norm_mismatch"] = float(
        np.linalg.norm(rebuilt - norm) / max(np.linalg.norm(norm), 1e-30))
    xy = np.c_[x, y]
    _, inv, counts = np.unique(np.round(xy / DUP_TOL).astype(np.int64),
                               axis=0, return_inverse=True,
                               return_counts=True)
    diag["dup_points"] = int((counts > 1).sum())
    diag["dup_extra"] = int(a.shape[0] - counts.size)
    if diag["dup_extra"]:
        # do duplicated coordinates carry identical field values?
        diff = 0.0
        for g in np.where(counts > 1)[0]:
            sel = inv == g
            diff = max(diff, float(np.max(np.abs(E[sel] - E[sel][0]))))
        diag["dup_max_field_spread"] = diff
    else:
        diag["dup_max_field_spread"] = 0.0

    return dict(x=x, y=y, E=E, norm=norm, neff=neff, unit=unit,
                nodes=a.shape[0], diag=diag)
