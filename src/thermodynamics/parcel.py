"""Convective parcel ascent for the forecast-max-temperature (Tmax) method.

Lifts a surface parcel at the day's forecast maximum temperature dry-adiabatically
and follows its (conserved) mixing ratio. The dry adiabat meeting the environment
marks the thermal top; the dry adiabat meeting the parcel's mixing-ratio line
marks the cloud base (LCL).
"""

import numpy as np

from src.config.constants import PRESSURE_TOP_HPA
from src.thermodynamics.constants import (
    DRY_AIR_TO_WATER_VAPOUR_RATIO,
    KAPPA,
    SATURATION_VAPOUR_PRESSURE_BASE_HPA,
    SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS,
    SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF,
    ZERO_CELSIUS_IN_KELVIN,
)

PARCEL_PRESSURE_STEP_HPA = 1.0


def _saturation_vapour_pressure(temperature_celsius):
    return SATURATION_VAPOUR_PRESSURE_BASE_HPA * np.exp(
        SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF * temperature_celsius
        / (temperature_celsius + SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS))


def _dew_point_from_vapour_pressure(vapour_pressure):
    log_ratio = np.log(vapour_pressure / SATURATION_VAPOUR_PRESSURE_BASE_HPA)
    return (SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS * log_ratio
            / (SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF - log_ratio))


def _first_crossing(pressures, difference):
    """Pressure where `difference` first drops to zero, linearly interpolated.

    `difference` is positive at the surface (index 0) and decreases upward.
    Returns None if it never reaches zero within the column.
    """
    below = np.flatnonzero(difference <= 0)
    if below.size == 0 or below[0] == 0:
        return None
    upper = below[0]
    lower = upper - 1
    span = difference[lower] - difference[upper]
    fraction = difference[lower] / span
    return pressures[lower] + (pressures[upper] - pressures[lower]) * fraction


def parcel_ascent(surface_pressure, max_temperature, surface_dew_point,
                  environment_pressure, environment_temperature):
    """Lift the Tmax parcel and locate the thermal top and cloud base.

    Returns the parcel curves on a fine pressure grid plus the thermal-top and
    cloud-base pressures (either may be None if not reached in the column).
    """
    pressures = np.arange(surface_pressure, PRESSURE_TOP_HPA, -PARCEL_PRESSURE_STEP_HPA)

    # Dry adiabat through the surface point (constant potential temperature).
    max_temperature_kelvin = max_temperature + ZERO_CELSIUS_IN_KELVIN
    parcel_temperature = (max_temperature_kelvin
                          * (pressures / surface_pressure) ** KAPPA
                          - ZERO_CELSIUS_IN_KELVIN)

    # Mixing-ratio line: the unsaturated parcel keeps its surface mixing ratio.
    surface_vapour_pressure = _saturation_vapour_pressure(surface_dew_point)
    mixing_ratio = (DRY_AIR_TO_WATER_VAPOUR_RATIO * surface_vapour_pressure
                    / (surface_pressure - surface_vapour_pressure))
    vapour_pressure = (mixing_ratio * pressures
                       / (DRY_AIR_TO_WATER_VAPOUR_RATIO + mixing_ratio))
    parcel_dew_point = _dew_point_from_vapour_pressure(vapour_pressure)

    # Environment temperature interpolated onto the parcel's pressure grid.
    ascending = np.argsort(environment_pressure)
    environment_at_parcel = np.interp(
        pressures, np.asarray(environment_pressure)[ascending],
        np.asarray(environment_temperature)[ascending])

    return {
        "pressures": pressures,
        "temperature": parcel_temperature,
        "dew_point": parcel_dew_point,
        "thermal_top_pressure": _first_crossing(
            pressures, parcel_temperature - environment_at_parcel),
        "cloud_base_pressure": _first_crossing(
            pressures, parcel_temperature - parcel_dew_point),
    }
