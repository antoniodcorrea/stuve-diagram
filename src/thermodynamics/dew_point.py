"""Dew point from temperature and relative humidity (Bolton 1980, inverted)."""

import numpy as np

from src.thermodynamics.constants import (
    PERCENT_TO_FRACTION,
    SATURATION_VAPOUR_PRESSURE_BASE_HPA,
    SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS,
    SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF,
)


def dew_point_from_humidity(temperature_celsius, relative_humidity_percent):
    """Dew point (°C) for a temperature (°C) and relative humidity (%)."""
    saturation_vapour_pressure = SATURATION_VAPOUR_PRESSURE_BASE_HPA * np.exp(
        SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF * temperature_celsius
        / (temperature_celsius + SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS)
    )
    vapour_pressure = (relative_humidity_percent / PERCENT_TO_FRACTION
                       * saturation_vapour_pressure)
    # Bone-dry air (0 % humidity) yields no vapour pressure, so the dew point is
    # undefined (NaN); silence the expected log(0) warning.
    with np.errstate(divide="ignore", invalid="ignore"):
        log_ratio = np.log(vapour_pressure / SATURATION_VAPOUR_PRESSURE_BASE_HPA)
        return (SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS * log_ratio
                / (SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF - log_ratio))
