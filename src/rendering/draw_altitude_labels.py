"""Draw altitude labels on the left edge: metres every 1000 m, feet every 5000 ft."""

import numpy as np

from src.config.constants import PRESSURE_TOP_HPA, TEMPERATURE_MIN_CELSIUS
from src.rendering.constants import (
    ALTITUDE_FEET_OFFSET_CELSIUS,
    ALTITUDE_LABEL_FONT_SIZE,
    ALTITUDE_LABEL_LEFT_OFFSET_CELSIUS,
    ALTITUDE_LABEL_STEP_FEET,
    ALTITUDE_LABEL_STEP_METRES,
    ALTITUDE_LABEL_TOP_MARGIN_HPA,
    METRES_TO_FEET,
)
from src.thermodynamics.pressure_coordinate import pressure_to_axis


def _annotate(ax, altitude_metres, sounding, text, label_x):
    pressure = np.interp(altitude_metres, sounding.altitude, sounding.pressure)
    if pressure < PRESSURE_TOP_HPA + ALTITUDE_LABEL_TOP_MARGIN_HPA:
        return
    ax.annotate(text, xy=(label_x, pressure_to_axis(pressure)),
                fontsize=ALTITUDE_LABEL_FONT_SIZE, color="gray", va="center")


def draw_altitude_labels(ax, sounding):
    metres_x = TEMPERATURE_MIN_CELSIUS + ALTITUDE_LABEL_LEFT_OFFSET_CELSIUS
    feet_x = TEMPERATURE_MIN_CELSIUS + ALTITUDE_FEET_OFFSET_CELSIUS

    highest_metres = int(sounding.altitude.max())
    for altitude in range(ALTITUDE_LABEL_STEP_METRES, highest_metres + 1,
                          ALTITUDE_LABEL_STEP_METRES):
        _annotate(ax, altitude, sounding, f"{altitude:,.0f} m.", metres_x)

    highest_feet = int(highest_metres * METRES_TO_FEET)
    for feet in range(ALTITUDE_LABEL_STEP_FEET, highest_feet + 1,
                      ALTITUDE_LABEL_STEP_FEET):
        _annotate(ax, feet / METRES_TO_FEET, sounding, f"{feet:,.0f} ft.", feet_x)
