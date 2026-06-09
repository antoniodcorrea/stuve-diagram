"""Vertical-column helpers shared by the thermodynamics and the diagram drawing:
interpolate a profile to a pressure level, and find where a difference first
crosses zero going up the column."""

import numpy as np


def interp_at(pressures, values, targets):
    """Linearly interpolate `values` (defined on `pressures`, hPa) to `targets`.

    Sorts by pressure first, since `np.interp` requires an increasing x.
    """
    pressures = np.asarray(pressures, dtype=float)
    order = np.argsort(pressures)
    return np.interp(targets, pressures[order], np.asarray(values, dtype=float)[order])


def first_crossing(pressures, difference):
    """Pressure where `difference` first drops to <= 0 going up, interpolated.

    `difference` is positive at the surface (index 0) and decreases upward;
    returns None if it never crosses within the column.
    """
    pressures = np.asarray(pressures, dtype=float)
    difference = np.asarray(difference, dtype=float)
    below = np.flatnonzero(difference <= 0)
    if below.size == 0 or below[0] == 0:
        return None
    upper = below[0]
    lower = upper - 1
    span = difference[lower] - difference[upper]
    fraction = difference[lower] / span
    return pressures[lower] + (pressures[upper] - pressures[lower]) * fraction
