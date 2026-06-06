"""Compute the adiabatic and mixing-ratio fields over the background grid.

The grid lives in (temperature, pressure**kappa) space, as in adiabats_plot.m.
"""

import numpy as np

from src.config.constants import (
    PRESSURE_BOTTOM_HPA,
    PRESSURE_TOP_HPA,
    TEMPERATURE_MAX_CELSIUS,
    TEMPERATURE_MIN_CELSIUS,
)
from src.thermodynamics.constants import (
    DRY_AIR_TO_WATER_VAPOUR_RATIO,
    GRID_PRESSURE_STEP_HPA,
    GRID_RANGE_EPSILON,
    GRID_TEMPERATURE_STEP_CELSIUS,
    KAPPA,
    LATENT_HEAT_VAPORISATION,
    REFERENCE_PRESSURE_HPA,
    SATURATION_VAPOUR_PRESSURE_BASE_HPA,
    SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS,
    SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF,
    SPECIFIC_HEAT_DRY_AIR,
    ZERO_CELSIUS_IN_KELVIN,
)


def compute_adiabatic_fields():
    """Return the background grid and the fields plotted as contours.

    The returned dict carries the meshgrid (temperature, pressure_axis) plus the
    potential temperature, equivalent potential temperature, and saturation
    mixing ratio evaluated on it.
    """
    temperatures = np.arange(
        TEMPERATURE_MIN_CELSIUS,
        TEMPERATURE_MAX_CELSIUS + GRID_RANGE_EPSILON,
        GRID_TEMPERATURE_STEP_CELSIUS,
    )
    pressures = np.arange(
        PRESSURE_TOP_HPA,
        PRESSURE_BOTTOM_HPA + GRID_RANGE_EPSILON,
        GRID_PRESSURE_STEP_HPA,
    )
    temperature, pressure_axis = np.meshgrid(temperatures, pressures ** KAPPA)

    temperature_kelvin = temperature + ZERO_CELSIUS_IN_KELVIN
    potential_temperature = temperature_kelvin * (REFERENCE_PRESSURE_HPA ** KAPPA / pressure_axis)

    saturation_vapour_pressure = SATURATION_VAPOUR_PRESSURE_BASE_HPA * np.exp(
        SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF * temperature
        / (temperature + SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS)
    )
    saturation_mixing_ratio = (
        DRY_AIR_TO_WATER_VAPOUR_RATIO * saturation_vapour_pressure
        / (pressure_axis ** (1.0 / KAPPA) - saturation_vapour_pressure)
    )
    saturation_specific_humidity = saturation_mixing_ratio / (saturation_mixing_ratio + 1.0)
    equivalent_potential_temperature = potential_temperature * np.exp(
        LATENT_HEAT_VAPORISATION * saturation_specific_humidity
        / SPECIFIC_HEAT_DRY_AIR / temperature_kelvin
    )

    return {
        "temperature": temperature,
        "pressure_axis": pressure_axis,
        "potential_temperature": potential_temperature,
        "equivalent_potential_temperature": equivalent_potential_temperature,
        "saturation_mixing_ratio": saturation_mixing_ratio,
    }
