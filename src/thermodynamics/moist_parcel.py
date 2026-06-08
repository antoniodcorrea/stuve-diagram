"""Lift a parcel through the whole column: dry adiabat to the LCL, then a
pseudo-adiabat above it.

The Tmax parcel in `parcel.py` only needs the dry adiabat and the mixing-ratio
line (thermal top and cloud base). The convective indices (CAPE, LFC, EL, cloud
top) need the saturated ascent above the lifting condensation level too, which
is what this module adds.
"""

import numpy as np

from src.config.constants import PRESSURE_TOP_HPA
from src.thermodynamics.constants import (
    DRY_AIR_TO_WATER_VAPOUR_RATIO,
    GAS_CONSTANT_DRY_AIR,
    KAPPA,
    LATENT_HEAT_VAPORISATION,
    SPECIFIC_HEAT_DRY_AIR,
    ZERO_CELSIUS_IN_KELVIN,
)
from src.thermodynamics.saturation import (
    dew_point_from_vapour_pressure,
    mixing_ratio,
    saturation_mixing_ratio,
    saturation_vapour_pressure,
)

PARCEL_PRESSURE_STEP_HPA = 1.0


def _pseudoadiabat_lapse(temperature_kelvin, pressure):
    """Pseudo-adiabatic dT/dp (K/hPa) for a saturated parcel."""
    rs = saturation_mixing_ratio(temperature_kelvin - ZERO_CELSIUS_IN_KELVIN, pressure)
    numerator = 1.0 + LATENT_HEAT_VAPORISATION * rs / (GAS_CONSTANT_DRY_AIR * temperature_kelvin)
    denominator = 1.0 + (LATENT_HEAT_VAPORISATION ** 2 * rs * DRY_AIR_TO_WATER_VAPOUR_RATIO
                         / (SPECIFIC_HEAT_DRY_AIR * GAS_CONSTANT_DRY_AIR * temperature_kelvin ** 2))
    return (GAS_CONSTANT_DRY_AIR * temperature_kelvin / (SPECIFIC_HEAT_DRY_AIR * pressure)
            * numerator / denominator)


def moist_parcel_profile(start_pressure, start_temperature, start_dew_point,
                         top_pressure=PRESSURE_TOP_HPA):
    """Lift a parcel from (start_pressure, start_temperature, start_dew_point).

    Returns the parcel temperature (°C) on a fine pressure grid running from the
    start pressure up to `top_pressure`, plus the LCL pressure (None if the
    parcel never saturates within the column).
    """
    pressures = np.arange(start_pressure, top_pressure, -PARCEL_PRESSURE_STEP_HPA)

    # Dry adiabat (constant potential temperature) through the start point.
    start_temperature_kelvin = start_temperature + ZERO_CELSIUS_IN_KELVIN
    dry_temperature = start_temperature_kelvin * (pressures / start_pressure) ** KAPPA

    # Mixing-ratio line: the unsaturated parcel keeps its start mixing ratio.
    start_mixing_ratio = mixing_ratio(saturation_vapour_pressure(start_dew_point), start_pressure)
    vapour_pressure = (start_mixing_ratio * pressures
                       / (DRY_AIR_TO_WATER_VAPOUR_RATIO + start_mixing_ratio))
    dew_point_kelvin = dew_point_from_vapour_pressure(vapour_pressure) + ZERO_CELSIUS_IN_KELVIN

    # LCL: the first level where the dry adiabat cools to the mixing-line dew point.
    saturated = np.flatnonzero(dry_temperature <= dew_point_kelvin)
    if saturated.size == 0:
        return {"pressures": pressures,
                "temperature": dry_temperature - ZERO_CELSIUS_IN_KELVIN,
                "lcl_pressure": None}

    lcl_index = saturated[0]
    temperature_kelvin = dry_temperature.copy()

    # Integrate the pseudo-adiabat upward from the LCL, one pressure step at a time.
    for level in range(lcl_index + 1, pressures.size):
        previous = temperature_kelvin[level - 1]
        step = pressures[level] - pressures[level - 1]
        temperature_kelvin[level] = previous + _pseudoadiabat_lapse(previous, pressures[level - 1]) * step

    return {"pressures": pressures,
            "temperature": temperature_kelvin - ZERO_CELSIUS_IN_KELVIN,
            "lcl_pressure": pressures[lcl_index]}
