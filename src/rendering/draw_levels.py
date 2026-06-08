"""Draw the derived levels: the 0 °C freezing level and the cumulus cloud (the
saturated adiabat from cloud base to the equilibrium level), with the level of
free convection and equilibrium level marked on it."""

import numpy as np

from src.rendering.constants import (
    CLOUD_LINEWIDTH,
    FREEZING_LEVEL_ALPHA,
    FREEZING_LEVEL_COLOR,
    FREEZING_LEVEL_DASHES,
    FREEZING_LEVEL_LINEWIDTH,
    LEVEL_LABEL_COLOR,
    LEVEL_LABEL_FONT_SIZE,
)
from src.rendering.label_box import translucent_label_bbox


def _interp_at(pressure, pressures, values):
    order = pressures.argsort()
    return np.interp(pressure, pressures[order], values[order])


def _label(ax, x, y, text):
    ax.annotate(text, xy=(x, y), xytext=(0, 2), textcoords="offset points",
                color=LEVEL_LABEL_COLOR, fontsize=LEVEL_LABEL_FONT_SIZE,
                ha="center", va="bottom", annotation_clip=False, zorder=7,
                bbox=translucent_label_bbox())


def draw_levels(ax, indices, projection):
    freezing_pressure = indices["freezing_pressure"]
    if freezing_pressure is not None:
        x, y = projection.to_xy(0.0, freezing_pressure)
        ax.axhline(y, color=FREEZING_LEVEL_COLOR, lw=FREEZING_LEVEL_LINEWIDTH,
                   ls=FREEZING_LEVEL_DASHES, alpha=FREEZING_LEVEL_ALPHA, zorder=3)
        _label(ax, x, y, "0 °C")

    profile = indices["parcel_profile"]
    el = indices["el_pressure"]
    lcl = profile["lcl_pressure"]
    # The cumulus only exists when the parcel condenses (LCL) and stays buoyant up
    # to an equilibrium level above it.
    if el is not None and lcl is not None and el < lcl:
        cloud = (profile["pressures"] <= lcl) & (profile["pressures"] >= el)
        ax.plot(*projection.to_xy(profile["temperature"][cloud], profile["pressures"][cloud]),
                color="black", lw=CLOUD_LINEWIDTH, zorder=6)
        x, y = projection.to_xy(_interp_at(el, profile["pressures"], profile["temperature"]), el)
        _label(ax, x, y, "EL")

    lfc = indices["lfc_pressure"]
    if lfc is not None:
        x, y = projection.to_xy(_interp_at(lfc, profile["pressures"], profile["temperature"]), lfc)
        _label(ax, x, y, "LFC")
