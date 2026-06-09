"""Dew point from temperature and relative humidity (Bolton 1980, inverted)."""

import numpy as np

from src.thermodynamics.constants import PERCENT_TO_FRACTION
from src.thermodynamics.saturation import (
    dew_point_from_vapour_pressure,
    saturation_vapour_pressure,
)


def dew_point_from_humidity(temperature_celsius, relative_humidity_percent):
    """Dew point (°C) for a temperature (°C) and relative humidity (%)."""
    vapour_pressure = (relative_humidity_percent / PERCENT_TO_FRACTION
                       * saturation_vapour_pressure(temperature_celsius))
    # Bone-dry air (0 % humidity) yields no vapour pressure, so the dew point is
    # undefined (NaN); silence the expected log(0) warning.
    with np.errstate(divide="ignore", invalid="ignore"):
        return dew_point_from_vapour_pressure(vapour_pressure)
