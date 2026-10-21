"""Geometric definition of the modelled cross-section regions.

These masks come from the geometry that the COMSOL model actually builds, so
they are independent evidence for where each domain must be.  They are used to

  * verify that every exported sample carries the domain label that its
    coordinates imply (a mismatch means the domain map is wrong), and
  * decide, for any grid point, which region it belongs to -- so a region is
    never interpolated into the interior of another one (an air point cloud
    triangulates across the holes left by the solids, which silently fills
    them).

Coordinates are micrometres, x is horizontal and y is vertical.
"""
import numpy as np

XMIN, XMAX = -1.6, 4.18
YMIN, YMAX = -1.0, 1.6

FILM_X = (0.0, 2.58)
RIDGE = (0.9675, 1.6125, 0.0, 0.5)
SLAB_L = (0.0, 0.9675, 0.0, 0.25)
SLAB_R = (1.6125, 2.58, 0.0, 0.25)
AL_L = (0.3225, 0.9675, 0.25, 0.35)
AL_R = (1.6125, 2.2575, 0.25, 0.35)

EPS = 1e-9


def _in(box, x, y):
    x0, x1, y0, y1 = box
    return (x >= x0 - EPS) & (x <= x1 + EPS) & (y >= y0 - EPS) & (y <= y1 + EPS)


def classify(x, y, metal):
    """Return the region name for every sample.

    Metal is tested before air because the electrodes sit above the slab and
    would otherwise be labelled as air.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    name = np.full(x.shape, "air", dtype=object)
    # ridges and slabs first: they occupy the film
    name[_in(SLAB_L, x, y)] = "slabL"
    name[_in(SLAB_R, x, y)] = "slabR"
    name[_in(RIDGE, x, y)] = "ridge"
    if metal:
        name[_in(AL_L, x, y)] = "metalL"
        name[_in(AL_R, x, y)] = "metalR"
    outside = (x < XMIN) | (x > XMAX) | (y < YMIN) | (y > YMAX)
    name[outside] = "outside"
    return name
