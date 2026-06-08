"""Compute the adiabatic and mixing-ratio fields over the background grid.

The grid lives in (temperature, pressure) space; the diagram projection maps it
to plot coordinates, so the same fields serve both the Stüve and Skew-T diagrams.
"""

import numpy as np

from src.config.constants import (
    GRID_TEMPERATURE_MIN_CELSIUS,
    PRESSURE_BOTTOM_HPA,
    PRESSURE_TOP_HPA,
    TEMPERATURE_MAX_CELSIUS,
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

    The returned dict carries the (temperature, pressure) meshgrid plus the
    potential temperature, equivalent potential temperature, and saturation
    mixing ratio evaluated on it.
    """
    temperatures = np.arange(
        GRID_TEMPERATURE_MIN_CELSIUS,
        TEMPERATURE_MAX_CELSIUS + GRID_RANGE_EPSILON,
        GRID_TEMPERATURE_STEP_CELSIUS,
    )
    pressures = np.arange(
        PRESSURE_TOP_HPA,
        PRESSURE_BOTTOM_HPA + GRID_RANGE_EPSILON,
        GRID_PRESSURE_STEP_HPA,
    )
    temperature, pressure = np.meshgrid(temperatures, pressures)

    temperature_kelvin = temperature + ZERO_CELSIUS_IN_KELVIN
    potential_temperature = temperature_kelvin * (REFERENCE_PRESSURE_HPA / pressure) ** KAPPA

    saturation_vapour_pressure = SATURATION_VAPOUR_PRESSURE_BASE_HPA * np.exp(
        SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF * temperature
        / (temperature + SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS)
    )
    # In the warm, low-pressure corner the saturation vapour pressure exceeds the
    # total pressure: an unphysical region where the mixing ratio would go negative.
    # Mask it (NaN) so the contour algorithm doesn't draw a spurious band across the
    # +inf/-inf jump at the boundary.
    with np.errstate(divide="ignore", invalid="ignore"):
        saturation_mixing_ratio = np.where(
            pressure > saturation_vapour_pressure,
            DRY_AIR_TO_WATER_VAPOUR_RATIO * saturation_vapour_pressure
            / (pressure - saturation_vapour_pressure),
            np.nan,
        )
    saturation_specific_humidity = saturation_mixing_ratio / (saturation_mixing_ratio + 1.0)
    equivalent_potential_temperature = potential_temperature * np.exp(
        LATENT_HEAT_VAPORISATION * saturation_specific_humidity
        / SPECIFIC_HEAT_DRY_AIR / temperature_kelvin
    )

    return {
        "temperature": temperature,
        "pressure": pressure,
        "potential_temperature": potential_temperature,
        "equivalent_potential_temperature": equivalent_potential_temperature,
        "saturation_mixing_ratio": saturation_mixing_ratio,
    }
