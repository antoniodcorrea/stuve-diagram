"""Draw the 0 °C freezing level (with a right-edge label), plus the cumulus cloud
(the saturated adiabat from cloud base to the equilibrium level). The convective
levels (CCL/EL/LFC/LCL) are labelled beside the curves by `draw_level_labels`."""

from matplotlib.transforms import blended_transform_factory

from src.rendering.constants import (
    CLOUD_LINEWIDTH,
    FREEZING_LEVEL_ALPHA,
    FREEZING_LEVEL_COLOR,
    FREEZING_LEVEL_DASHES,
    FREEZING_LEVEL_LINEWIDTH,
    LEVEL_LABEL_COLOR,
    LEVEL_LABEL_FONT_SIZE,
    THERMAL_TOP_LABEL_RIGHT_GAP_POINTS,
)
from src.rendering.label_box import translucent_label_bbox


def _level_line(ax, pressure, alpha, projection):
    ax.axhline(projection.pressure_to_y(pressure), color=FREEZING_LEVEL_COLOR,
               lw=FREEZING_LEVEL_LINEWIDTH, ls=FREEZING_LEVEL_DASHES, alpha=alpha, zorder=3)


def _isotherm(ax, pressure, text, alpha, projection):
    if pressure is None:
        return
    _level_line(ax, pressure, alpha, projection)
    # Pinned near the right edge (like "Thermal top"), clear of the parcel-line
    # labels (LFC/EL/CCL) which can sit at the same level on a given sounding.
    ax.annotate(text, xy=(1.0, projection.pressure_to_y(pressure)),
                xycoords=blended_transform_factory(ax.transAxes, ax.transData),
                xytext=(-THERMAL_TOP_LABEL_RIGHT_GAP_POINTS, 0), textcoords="offset points",
                color=LEVEL_LABEL_COLOR, fontsize=LEVEL_LABEL_FONT_SIZE,
                ha="right", va="center", annotation_clip=False, zorder=7,
                bbox=translucent_label_bbox())


def draw_levels(ax, indices, projection):
    _isotherm(ax, indices["freezing_pressure"], "0 °C", FREEZING_LEVEL_ALPHA, projection)

    profile = indices["parcel_profile"]
    el = indices["el_pressure"]
    lcl = profile["lcl_pressure"]
    # The cumulus only exists when the parcel condenses (LCL) and stays buoyant up
    # to an equilibrium level above it.
    if el is not None and lcl is not None and el < lcl:
        cloud = (profile["pressures"] <= lcl) & (profile["pressures"] >= el)
        ax.plot(*projection.to_xy(profile["temperature"][cloud], profile["pressures"][cloud]),
                color="black", lw=CLOUD_LINEWIDTH, zorder=6)
