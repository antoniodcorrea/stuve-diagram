"""Saturation thermodynamics (Bolton 1980) shared by the parcel and index code.

Small, pure helpers: the saturation vapour pressure and the conversions between
vapour pressure, mixing ratio and dew point that every moist computation needs.
"""

import numpy as np

from src.thermodynamics.constants import (
    DRY_AIR_TO_WATER_VAPOUR_RATIO,
    SATURATION_VAPOUR_PRESSURE_BASE_HPA,
    SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS,
    SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF,
)


def saturation_vapour_pressure(temperature_celsius):
    """Saturation vapour pressure (hPa) over water for a temperature (°C)."""
    return SATURATION_VAPOUR_PRESSURE_BASE_HPA * np.exp(
        SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF * temperature_celsius
        / (temperature_celsius + SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS))


def dew_point_from_vapour_pressure(vapour_pressure):
    """Dew point (°C) for a vapour pressure (hPa), inverting Bolton (1980)."""
    log_ratio = np.log(vapour_pressure / SATURATION_VAPOUR_PRESSURE_BASE_HPA)
    return (SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS * log_ratio
            / (SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF - log_ratio))


def mixing_ratio(vapour_pressure, pressure):
    """Mixing ratio (kg/kg) for a vapour pressure and total pressure (both hPa)."""
    return (DRY_AIR_TO_WATER_VAPOUR_RATIO * vapour_pressure
            / (pressure - vapour_pressure))


def saturation_mixing_ratio(temperature_celsius, pressure):
    """Saturation mixing ratio (kg/kg) at a temperature (°C) and pressure (hPa)."""
    return mixing_ratio(saturation_vapour_pressure(temperature_celsius), pressure)
