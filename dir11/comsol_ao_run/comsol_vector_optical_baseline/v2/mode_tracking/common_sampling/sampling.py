"""Common sampling partition shared by every model.

The window is cut by every geometric boundary first, then each interval is
subdivided.  A cell centre therefore always lies strictly inside one region and
its area weight is the cell area -- no value is inferred from point spacing.

    x edges: window, film start, electrode edges, ridge edges, film end
    y edges: window, film bottom, slab top, electrode top, film top

Both models use the same centres and the same weights; only the material and
the domain numbering differ.
"""
import numpy as np

import regions as R

X_EDGES = [-1.6, 0.0, 0.3225, 0.9675, 1.6125, 2.2575, 2.58, 4.18]
Y_EDGES = [-1.0, 0.0, 0.25, 0.35, 0.5, 1.6]


def cells(n=3, x_edges=None, y_edges=None):
    """Return centres, weights and the expected region of every cell."""
    xe = np.asarray(X_EDGES if x_edges is None else x_edges, dtype=float)
    ye = np.asarray(Y_EDGES if y_edges is None else y_edges, dtype=float)
    xs = []
    for a, b in zip(xe[:-1], xe[1:]):
        for c in (np.arange(n) + 0.5) / n * (b - a) + a:
            xs.append(float(c))
    ys = []
    for a, b in zip(ye[:-1], ye[1:]):
        for c in (np.arange(n) + 0.5) / n * (b - a) + a:
            ys.append(float(c))
    dx = (xe[1:] - xe[:-1]) / n
    dy = (ye[1:] - ye[:-1]) / n

    pts, wts = [], []
    for i, x in enumerate(xs):
        wx = dx[i // n]
        for j, y in enumerate(ys):
            pts.append((x, y))
            wts.append(wx * dy[j // n])
    pts = np.asarray(pts)
    wts = np.asarray(wts)

    names = R.classify(pts[:, 0], pts[:, 1], metal=True)
    # electrodes only exist in the metal model, but the region name is fixed by
    # geometry; the caller decides which names are meaningful for a model
    return dict(x=pts[:, 0], y=pts[:, 1], w=wts,
                region=np.asarray(names, dtype=object), n=n)


def check(sample, n_window_area=None):
    """Consistency checks that must pass before any evaluation."""
    problems = []
    if not (sample["w"] > 0).all():
        problems.append("non-positive cell weights")
    area = float(sample["w"].sum())
    if n_window_area is not None and abs(area - n_window_area) > 1e-9:
        problems.append(f"weight sum {area:.9f} != window {n_window_area:.9f}")
    bad = [i for i, r in enumerate(sample["region"]) if r == "outside"]
    if bad:
        problems.append(f"{len(bad)} cells outside the window")
    return dict(area=area, problems=problems,
                counts={r: int((sample["region"] == r).sum())
                        for r in sorted(set(sample["region"]))})
