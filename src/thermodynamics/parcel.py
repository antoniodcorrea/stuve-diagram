"""Convective parcel ascent for the forecast-max-temperature (Tmax) method.

Lifts a surface parcel at the day's forecast maximum temperature dry-adiabatically
and follows its (conserved) mixing ratio. The dry adiabat meeting the environment
marks the thermal top; the dry adiabat meeting the parcel's mixing-ratio line
marks the cloud base (LCL).
"""

import numpy as np

from src.config.constants import PRESSURE_TOP_HPA
from src.thermodynamics.column import first_crossing
from src.thermodynamics.constants import (
    DRY_AIR_TO_WATER_VAPOUR_RATIO,
    KAPPA,
    ZERO_CELSIUS_IN_KELVIN,
)
from src.thermodynamics.saturation import (
    dew_point_from_vapour_pressure,
    saturation_vapour_pressure,
)

PARCEL_PRESSURE_STEP_HPA = 1.0


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
    surface_vapour_pressure = saturation_vapour_pressure(surface_dew_point)
    mixing_ratio = (DRY_AIR_TO_WATER_VAPOUR_RATIO * surface_vapour_pressure
                    / (surface_pressure - surface_vapour_pressure))
    vapour_pressure = (mixing_ratio * pressures
                       / (DRY_AIR_TO_WATER_VAPOUR_RATIO + mixing_ratio))
    parcel_dew_point = dew_point_from_vapour_pressure(vapour_pressure)

    # Environment temperature interpolated onto the parcel's pressure grid.
    ascending = np.argsort(environment_pressure)
    environment_at_parcel = np.interp(
        pressures, np.asarray(environment_pressure)[ascending],
        np.asarray(environment_temperature)[ascending])

    return {
        "pressures": pressures,
        "temperature": parcel_temperature,
        "dew_point": parcel_dew_point,
        "thermal_top_pressure": first_crossing(
            pressures, parcel_temperature - environment_at_parcel),
        "cloud_base_pressure": first_crossing(
            pressures, parcel_temperature - parcel_dew_point),
    }
