"""Configure axis limits, ticks, fonts, labels, legend and title."""

from src.config.constants import (
    PRESSURE_BOTTOM_HPA,
    PRESSURE_TOP_HPA,
    TEMPERATURE_MAX_CELSIUS,
    TEMPERATURE_MIN_CELSIUS,
)
from src.rendering.constants import (
    BOX_ASPECT,
    DIAGRAM_NAME,
    HEADING_FONT_SIZE,
    HEADING_FONT_WEIGHT,
    HEADING_OFFSET_POINTS,
    ISOTHERM_MAX_CELSIUS,
    ISOTHERM_MIN_CELSIUS,
    ISOTHERM_STEP_CELSIUS,
    LEGEND_ANCHOR,
    LEGEND_FONT_SIZE,
    SUBTITLE_FONT_SIZE,
    SUBTITLE_PAD,
    TICK_LABEL_FONT_SIZE,
)
from src.thermodynamics.pressure_coordinate import pressure_to_axis


def configure_axes(ax, subtitle):
    ax.set_xlim(TEMPERATURE_MIN_CELSIUS, TEMPERATURE_MAX_CELSIUS)
    ax.set_ylim(pressure_to_axis(PRESSURE_BOTTOM_HPA), pressure_to_axis(PRESSURE_TOP_HPA))
    ax.set_xticks(range(ISOTHERM_MIN_CELSIUS, ISOTHERM_MAX_CELSIUS, ISOTHERM_STEP_CELSIUS))
    ax.xaxis.set_major_formatter(lambda value, _: f"{int(round(value))}°")
    ax.tick_params(labelsize=TICK_LABEL_FONT_SIZE)
    for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
        tick_label.set_fontweight("bold")
    ax.set_box_aspect(BOX_ASPECT)
    ax.set_xlabel("T (°C)")
    ax.set_ylabel("p (hPa)")
    # Heavy "STÜVE" heading above the lighter two-line subtitle
    ax.set_title(subtitle, fontsize=SUBTITLE_FONT_SIZE, pad=SUBTITLE_PAD)
    ax.annotate(DIAGRAM_NAME.upper(), xy=(0.5, 1.0), xycoords="axes fraction",
                xytext=(0, HEADING_OFFSET_POINTS), textcoords="offset points",
                ha="center", va="bottom", fontsize=HEADING_FONT_SIZE,
                fontweight=HEADING_FONT_WEIGHT)
    ax.legend(loc="upper right", bbox_to_anchor=LEGEND_ANCHOR,
              fontsize=LEGEND_FONT_SIZE)
