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
from src.config.constants import PRESSURE_BOTTOM_HPA, PRESSURE_TOP_HPA
from src.thermodynamics.adiabatic_fields import compute_adiabatic_fields
from src.thermodynamics.constants import GRID_RANGE_EPSILON, ZERO_CELSIUS_IN_KELVIN


def draw_background(ax, projection):
    fields = compute_adiabatic_fields()
    x, y = projection.to_xy(fields["temperature"], fields["pressure"])

    contour_levels = np.arange(
        THETA_LEVEL_MIN_CELSIUS,
        THETA_LEVEL_MAX_CELSIUS + GRID_RANGE_EPSILON,
        THETA_LEVEL_STEP_CELSIUS,
    ) + ZERO_CELSIUS_IN_KELVIN

    # Dry adiabats: potential temperature contours (solid)
    ax.contour(x, y, fields["potential_temperature"],
               levels=contour_levels, colors="black", linewidths=0.5,
               alpha=0.3, linestyles="solid", zorder=1)

    # Saturated adiabats: equivalent potential temperature contours (dashed)
    ax.contour(x, y, fields["equivalent_potential_temperature"],
               levels=contour_levels, colors="black", linewidths=0.5,
               alpha=0.3, linestyles="dashed", zorder=1)

    # Saturation mixing ratio contours (g/kg, dotted)
    ax.contour(x, y, fields["saturation_mixing_ratio"] * GRAMS_PER_KILOGRAM,
               levels=MIXING_RATIO_LEVELS_G_PER_KG, colors="black",
               linewidths=0.8, alpha=0.3, linestyles="dotted", zorder=1)

    # Isobars + pressure labels (every 100 hPa): horizontal in both projections
    isobars = list(range(ISOBAR_MIN_HPA, ISOBAR_MAX_HPA + 1, ISOBAR_STEP_HPA))
    for isobar_pressure in isobars:
        ax.axhline(projection.pressure_to_y(isobar_pressure), color="gray", lw=0.5,
                   alpha=0.4, zorder=0)
    ax.set_yticks([projection.pressure_to_y(isobar_pressure) for isobar_pressure in isobars])
    ax.set_yticklabels(isobars)

    # Isotherms: vertical on the Stüve, tilted on the Skew-T, so draw each as a
    # line from the bottom isobar to the top through the projection.
    ends = np.array([PRESSURE_BOTTOM_HPA, PRESSURE_TOP_HPA])
    for isotherm_temperature in range(ISOTHERM_MIN_CELSIUS, ISOTHERM_MAX_CELSIUS,
                                      ISOTHERM_STEP_CELSIUS):
        line_x, line_y = projection.to_xy(np.full(2, isotherm_temperature), ends)
        ax.plot(line_x, line_y, color="gray", lw=0.5, alpha=0.4, zorder=0)
