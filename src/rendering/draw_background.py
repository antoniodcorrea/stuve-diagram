"""Draw the Stüve background: adiabats, mixing ratio, isobars, isotherms."""

import numpy as np

from src.rendering.constants import (
    GRAMS_PER_KILOGRAM,
    ISOBAR_MAX_HPA,
    ISOBAR_MIN_HPA,
    ISOBAR_STEP_HPA,
    ISOTHERM_MAX_CELSIUS,
    ISOTHERM_MIN_CELSIUS,
    ISOTHERM_STEP_CELSIUS,
    MIXING_RATIO_LEVELS_G_PER_KG,
    THETA_LEVEL_MAX_CELSIUS,
    THETA_LEVEL_MIN_CELSIUS,
    THETA_LEVEL_STEP_CELSIUS,
)
from src.thermodynamics.adiabatic_fields import compute_adiabatic_fields
from src.thermodynamics.constants import GRID_RANGE_EPSILON, ZERO_CELSIUS_IN_KELVIN
from src.thermodynamics.pressure_coordinate import pressure_to_axis


def draw_background(ax):
    fields = compute_adiabatic_fields()
    temperature = fields["temperature"]
    pressure_axis = fields["pressure_axis"]

    contour_levels = np.arange(
        THETA_LEVEL_MIN_CELSIUS,
        THETA_LEVEL_MAX_CELSIUS + GRID_RANGE_EPSILON,
        THETA_LEVEL_STEP_CELSIUS,
    ) + ZERO_CELSIUS_IN_KELVIN

    # Dry adiabats: potential temperature contours (solid)
    ax.contour(temperature, pressure_axis, fields["potential_temperature"],
               levels=contour_levels, colors="black", linewidths=0.5,
               alpha=0.3, linestyles="solid", zorder=1)

    # Saturated adiabats: equivalent potential temperature contours (dashed)
    ax.contour(temperature, pressure_axis, fields["equivalent_potential_temperature"],
               levels=contour_levels, colors="black", linewidths=0.5,
               alpha=0.3, linestyles="dashed", zorder=1)

    # Saturation mixing ratio contours (g/kg, dotted)
    ax.contour(temperature, pressure_axis,
               fields["saturation_mixing_ratio"] * GRAMS_PER_KILOGRAM,
               levels=MIXING_RATIO_LEVELS_G_PER_KG, colors="black",
               linewidths=0.8, alpha=0.3, linestyles="dotted", zorder=1)

    # Isobars + pressure labels (every 100 hPa)
    isobars = list(range(ISOBAR_MIN_HPA, ISOBAR_MAX_HPA + 1, ISOBAR_STEP_HPA))
    for isobar_pressure in isobars:
        ax.axhline(pressure_to_axis(isobar_pressure), color="gray", lw=0.5,
                   alpha=0.4, zorder=0)
    ax.set_yticks([pressure_to_axis(isobar_pressure) for isobar_pressure in isobars])
    ax.set_yticklabels(isobars)

    # Isotherms
    for isotherm_temperature in range(ISOTHERM_MIN_CELSIUS, ISOTHERM_MAX_CELSIUS,
                                      ISOTHERM_STEP_CELSIUS):
        ax.axvline(isotherm_temperature, color="gray", lw=0.5, alpha=0.4, zorder=0)
