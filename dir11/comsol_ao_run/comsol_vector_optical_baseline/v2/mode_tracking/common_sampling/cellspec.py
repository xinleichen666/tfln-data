"""Explicit cell list shared by every model, with adaptive refinement.

The earlier sampler subdivided every geometric interval by the same number of
parts.  That is neither driven by where the field actually varies nor able to
place extra points where the error is.  Here a cell is an explicit rectangle
(x0, x1, y0, y1); refinement replaces a cell by four children, so the list is
always a partition of the window and can be checked rather than assumed:

  * areas sum to the window area,
  * every base cell is covered exactly once (checked through the tree),
  * no cell is smaller than a floor tied to the mesh size.

Weights are cell areas.  Nothing here depends on a particular model.
"""
import numpy as np

import regions as R

X_EDGES = [-1.6, 0.0, 0.3225, 0.9675, 1.6125, 2.2575, 2.58, 4.18]
Y_EDGES = [-1.0, 0.0, 0.25, 0.35, 0.5, 1.6]
WINDOW = (4.18 + 1.6) * (1.6 + 1.0)
MIN_SIDE = 0.015          # um; the mesh itself is 25 nm


def base_cells(n):
    """Uniform starting partition: n subdivisions of every geometric interval."""
    out = []
    for i in range(len(X_EDGES) - 1):
        a, b = X_EDGES[i], X_EDGES[i + 1]
        for p in range(n):
            x0 = a + (b - a) * p / n
            x1 = a + (b - a) * (p + 1) / n
            for j in range(len(Y_EDGES) - 1):
                c, d = Y_EDGES[j], Y_EDGES[j + 1]
                for q in range(n):
                    y0 = c + (d - c) * q / n
                    y1 = c + (d - c) * (q + 1) / n
                    out.append((x0, x1, y0, y1))
    return out


def split4(cell, min_side=MIN_SIDE):
    """Split into as many children as the size floor allows.

    Splitting only x or only y is allowed: a band that is already thinner than
    the floor in y can still be refined along x.
    """
    x0, x1, y0, y1 = cell
    can_x = (x1 - x0) * 0.5 >= min_side
    can_y = (y1 - y0) * 0.5 >= min_side
    xm, ym = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
    if can_x and can_y:
        return [(x0, xm, y0, ym), (xm, x1, y0, ym),
                (x0, xm, ym, y1), (xm, x1, ym, y1)]
    if can_x:
        return [(x0, xm, y0, y1), (xm, x1, y0, y1)]
    if can_y:
        return [(x0, x1, y0, ym), (x0, x1, ym, y1)]
    return [cell]


def arrays(cells):
    x = np.array([0.5 * (c[0] + c[1]) for c in cells])
    y = np.array([0.5 * (c[2] + c[3]) for c in cells])
    w = np.array([(c[1] - c[0]) * (c[3] - c[2]) for c in cells])
    region = np.asarray(R.classify(x, y, metal=True), dtype=object)
    return dict(x=x, y=y, w=w, region=region, cells=list(cells))


def _interval_index(edges, a, b, tol=1e-12):
    for i in range(len(edges) - 1):
        if a >= edges[i] - tol and b <= edges[i + 1] + tol:
            return i
    return -1


def check(cells, window=WINDOW, min_side=MIN_SIDE):
    """Structural checks that must pass before any evaluation.

    Overlap is tested between actual rectangles, not only inside one y band, so
    two cells at different heights that intersect are caught.  Every cell must
    also lie inside one geometric interval pair; a cell straddling a material
    edge would make its region label ambiguous.
    """
    problems = []
    if not cells:
        return dict(area=0.0, problems=["no cells"], counts={}, info={})
    w = np.array([(c[1] - c[0]) * (c[3] - c[2]) for c in cells])
    area = float(w.sum())
    if not np.isfinite(w).all() or (w <= 0).any():
        problems.append("non-positive or non-finite cell area")
    if abs(area - window) > 1e-9:
        problems.append(f"area {area:.9f} != window {window:.9f}")

    groups = {}
    for c, wi in zip(cells, w):
        i = _interval_index(X_EDGES, c[0], c[1])
        j = _interval_index(Y_EDGES, c[2], c[3])
        if i < 0 or j < 0:
            problems.append(f"cell straddles a geometric edge: {c}")
            break
        groups.setdefault((i, j), []).append((c, float(wi)))

    for (i, j), items in groups.items():
        base = (X_EDGES[i + 1] - X_EDGES[i]) * (Y_EDGES[j + 1] - Y_EDGES[j])
        s = sum(wi for _c, wi in items)
        if abs(s - base) > 1e-9:
            problems.append(f"base cell {(i, j)} covered by {s:.9f} != {base:.9f}")
            break
        items.sort(key=lambda t: t[0][0])
        for p in range(len(items)):
            x0, x1, y0, y1 = items[p][0]
            for q in range(p + 1, len(items)):
                X0, X1, Y0, Y1 = items[q][0]
                if X0 >= x1 - 1e-12:
                    break
                if min(y1, Y1) - max(y0, Y0) > 1e-12:
                    problems.append(f"overlap between {(x0, x1, y0, y1)} "
                                    f"and {(X0, X1, Y0, Y1)}")
                    break
            if any("overlap" in p2 for p2 in problems):
                break
        if any("overlap" in p2 for p2 in problems):
            break

    small = [c for c in cells if min(c[1] - c[0], c[3] - c[2]) < min_side - 1e-12]
    info = dict(min_side=min(min(c[1] - c[0], c[3] - c[2]) for c in cells),
                below_floor=len(small))
    names = np.asarray(R.classify(
        np.array([0.5 * (c[0] + c[1]) for c in cells]),
        np.array([0.5 * (c[2] + c[3]) for c in cells]), metal=True))
    counts = {r: int((names == r).sum())
              for r in ("air", "ridge", "slabL", "slabR", "metalL", "metalR")}
    return dict(area=area, problems=problems, counts=counts, info=info)


def uniform_bands(n_air, n_film, film_top=0.5):
    """Uniform grid using one density in air and another inside the film.

    A clean doubling of the whole window would put y cells at 4 nm inside the
    100 nm electrode band, far below the 25 nm mesh.  Refining only where the
    optical field lives tests the same question without that waste.
    """
    out = []
    for i in range(len(X_EDGES) - 1):
        a, b = X_EDGES[i], X_EDGES[i + 1]
        for j in range(len(Y_EDGES) - 1):
            c, d = Y_EDGES[j], Y_EDGES[j + 1]
            n = n_film if (c >= -1e-12 and c < film_top - 1e-12) else n_air
            for p in range(n):
                x0 = a + (b - a) * p / n
                x1 = a + (b - a) * (p + 1) / n
                for q in range(n):
                    y0 = c + (d - c) * q / n
                    y1 = c + (d - c) * (q + 1) / n
                    out.append((x0, x1, y0, y1))
    return out


def nest(n_coarse, n_fine, x_int, y_int):
    """Indices of the four fine cells inside each coarse cell, for n_fine = 2n."""
    idx = []
    for i in range(x_int):
        for p in range(n_coarse):
            for j in range(y_int):
                for q in range(n_coarse):
                    kids = []
                    for aa in (0, 1):
                        for bb in (0, 1):
                            kids.append((i * n_fine + 2 * p + aa)
                                        * y_int * n_fine
                                        + (j * n_fine + 2 * q + bb))
                    idx.append(kids)
    return np.array(idx)


def refine_with_parents(cells, flags, min_side=MIN_SIDE):
    """Replace flagged cells by their children and record the parent index."""
    out, par = [], []
    for i, (cell, f) in enumerate(zip(cells, flags)):
        kids = split4(cell, min_side) if f else [cell]
        for k in kids:
            out.append(k)
            par.append(i)
    return out, np.array(par, dtype=int)


def refine(cells, flags, min_side=MIN_SIDE):
    """Replace flagged cells by their children; flagged cells at the floor stay."""
    return refine_with_parents(cells, flags, min_side)[0]
