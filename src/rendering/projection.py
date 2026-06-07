"""Coordinate projections for the two diagram types: Stüve and Skew-T log-P.

Both map (temperature °C, pressure hPa) to plot (x, y). The vertical y depends
only on pressure in both projections; the horizontal x is the bare temperature
for the Stüve and a pressure-skewed temperature for the Skew-T. Every drawing
step works through `to_xy`, so the same sounding, parcel and field code feeds
both diagrams.
"""

import math

import numpy as np

from src.config.constants import (
    PRESSURE_BOTTOM_HPA,
    PRESSURE_TOP_HPA,
    TEMPERATURE_MAX_CELSIUS,
    TEMPERATURE_MIN_CELSIUS,
)
from src.rendering.constants import BOX_ASPECT, SKEWT_BOX_ASPECT, SKEWT_XLIM
from src.thermodynamics.constants import REFERENCE_PRESSURE_HPA
from src.thermodynamics.pressure_coordinate import pressure_to_axis

# Skew chosen so the isotherms render at 45°. An isotherm's display slope is
# box_aspect * (x-range / y-range) / skew, so 45° (slope 1) fixes the skew.
SKEWT_SKEW = (SKEWT_BOX_ASPECT * (SKEWT_XLIM[1] - SKEWT_XLIM[0])
              / math.log(PRESSURE_BOTTOM_HPA / PRESSURE_TOP_HPA))


class _Projection:
    def to_xy(self, temperature, pressure):
        y = self.pressure_to_y(pressure)
        return self.x_at(temperature, y), y

    @property
    def ylim(self):
        return self.pressure_to_y(PRESSURE_BOTTOM_HPA), self.pressure_to_y(PRESSURE_TOP_HPA)


class StuveProjection(_Projection):
    """x = T, y = p**kappa: straight dry adiabats, vertical isotherms."""

    name = "Stüve"
    slug = "stuve"
    box_aspect = BOX_ASPECT
    xlim = (TEMPERATURE_MIN_CELSIUS, TEMPERATURE_MAX_CELSIUS)

    def pressure_to_y(self, pressure):
        return pressure_to_axis(np.asarray(pressure, dtype=float))

    def x_at(self, temperature, y):
        return np.asarray(temperature, dtype=float)


class SkewTProjection(_Projection):
    """y = ln(p0/p) (log-P), x = T + skew*y: horizontal isobars, tilted isotherms."""

    name = "Skew-T"
    slug = "skewt"
    box_aspect = SKEWT_BOX_ASPECT
    xlim = SKEWT_XLIM

    def pressure_to_y(self, pressure):
        return np.log(REFERENCE_PRESSURE_HPA / np.asarray(pressure, dtype=float))

    def x_at(self, temperature, y):
        return np.asarray(temperature, dtype=float) + SKEWT_SKEW * np.asarray(y, dtype=float)


PROJECTIONS = [StuveProjection(), SkewTProjection()]
