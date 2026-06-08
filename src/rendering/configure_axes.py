"""Configure axis limits, ticks, fonts, labels, legend and title."""

from src.config.constants import PRESSURE_BOTTOM_HPA
from src.rendering.constants import (
    HEADING_FONT_SIZE,
    HEADING_FONT_WEIGHT,
    HEADING_OFFSET_POINTS,
    ISOTHERM_MAX_CELSIUS,
    ISOTHERM_MIN_CELSIUS,
    ISOTHERM_STEP_CELSIUS,
    SUBTITLE_FONT_SIZE,
    SUBTITLE_PAD,
    TICK_LABEL_FONT_SIZE,
)


def configure_axes(ax, subtitle, projection):
    # Temperature ticks sit where each isotherm meets the bottom isobar. Set them
    # before the limits, as out-of-window tick positions would otherwise widen it.
    bottom_y = projection.pressure_to_y(PRESSURE_BOTTOM_HPA)
    temperatures = range(ISOTHERM_MIN_CELSIUS, ISOTHERM_MAX_CELSIUS, ISOTHERM_STEP_CELSIUS)
    ax.set_xticks([projection.x_at(temperature, bottom_y) for temperature in temperatures])
    ax.set_xticklabels([f"{temperature}°" for temperature in temperatures])
    ax.set_xlim(*projection.xlim)
    ax.set_ylim(*projection.ylim)
    ax.tick_params(labelsize=TICK_LABEL_FONT_SIZE)
    for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
        tick_label.set_fontweight("bold")
    ax.set_box_aspect(projection.box_aspect)
    ax.set_xlabel("T (°C)")
    ax.set_ylabel("p (hPa)")
    # Heavy diagram-name heading above the lighter two-line subtitle
    ax.set_title(subtitle, fontsize=SUBTITLE_FONT_SIZE, pad=SUBTITLE_PAD)
    ax.annotate(projection.name.upper(), xy=(0.5, 1.0), xycoords="axes fraction",
                xytext=(0, HEADING_OFFSET_POINTS), textcoords="offset points",
                ha="center", va="bottom", fontsize=HEADING_FONT_SIZE,
                fontweight=HEADING_FONT_WEIGHT)
