"""Draw altitude labels on the left edge: the ground level, then metres every
1000 m and feet every 5000 ft above it."""

import numpy as np

from src.config.constants import PRESSURE_TOP_HPA
from src.rendering.constants import (
    ALTITUDE_FEET_OFFSET_CELSIUS,
    ALTITUDE_LABEL_FONT_SIZE,
    ALTITUDE_LABEL_LEFT_OFFSET_CELSIUS,
    ALTITUDE_LABEL_STEP_FEET,
    ALTITUDE_LABEL_STEP_METRES,
    ALTITUDE_LABEL_TOP_MARGIN_HPA,
    METRES_TO_FEET,
)


def _annotate(ax, altitude_metres, sounding, projection, text, label_x, va="center"):
    pressure = np.interp(altitude_metres, sounding.altitude, sounding.pressure)
    if pressure < PRESSURE_TOP_HPA + ALTITUDE_LABEL_TOP_MARGIN_HPA:
        return
    ax.annotate(text, xy=(label_x, projection.pressure_to_y(pressure)),
                fontsize=ALTITUDE_LABEL_FONT_SIZE, color="gray", va=va)


def _first_above(ground, step):
    """First multiple of `step` strictly above the ground level."""
    return (int(ground) // step + 1) * step


def draw_altitude_labels(ax, sounding, projection):
    left_edge = projection.xlim[0]
    metres_x = left_edge + ALTITUDE_LABEL_LEFT_OFFSET_CELSIUS
    feet_x = left_edge + ALTITUDE_FEET_OFFSET_CELSIUS

    # Ground level: the minimum altitude, sitting just above its line.
    ground_metres = sounding.altitude.min()
    ground_feet = ground_metres * METRES_TO_FEET
    _annotate(ax, ground_metres, sounding, projection, f"{ground_metres:,.0f} m.",
              metres_x, va="bottom")
    _annotate(ax, ground_metres, sounding, projection, f"{ground_feet:,.0f} ft.",
              feet_x, va="bottom")

    # Round steps above the ground (anything at or below it is underground).
    highest_metres = int(sounding.altitude.max())
    for altitude in range(_first_above(ground_metres, ALTITUDE_LABEL_STEP_METRES),
                          highest_metres + 1, ALTITUDE_LABEL_STEP_METRES):
        _annotate(ax, altitude, sounding, projection, f"{altitude:,.0f} m.", metres_x)

    highest_feet = int(highest_metres * METRES_TO_FEET)
    for feet in range(_first_above(ground_feet, ALTITUDE_LABEL_STEP_FEET),
                      highest_feet + 1, ALTITUDE_LABEL_STEP_FEET):
        _annotate(ax, feet / METRES_TO_FEET, sounding, projection,
                  f"{feet:,.0f} ft.", feet_x)
