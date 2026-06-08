"""Draw a wind hodograph as an inset in the upper-left corner.

The wind tips (u, v in knots) from the surface upward are joined into a curve;
range rings are spaced in knots. Restricted to the lower/mid troposphere
(>= 400 hPa) so the soaring-relevant shear and turning stay legible instead of
being dwarfed by the jet aloft.
"""

import numpy as np
from matplotlib.patches import Circle

from src.rendering.constants import (
    HODOGRAPH_BOUNDS,
    HODOGRAPH_FINE_RING_MAX_KNOTS,
    HODOGRAPH_FINE_RING_STEP_KNOTS,
    HODOGRAPH_FONT_SIZE,
    HODOGRAPH_LINEWIDTH,
    HODOGRAPH_RING_STEP_KNOTS,
    MS_TO_KNOTS,
)
from src.rendering.label_box import translucent_label_bbox

HODOGRAPH_PRESSURE_FLOOR_HPA = 400.0


def draw_hodograph(ax, sounding):
    layer = sounding[sounding.pressure >= HODOGRAPH_PRESSURE_FLOOR_HPA]
    speed_knots = layer.wind_speed.to_numpy() * MS_TO_KNOTS
    direction = np.deg2rad(layer.wind_direction.to_numpy())
    u = -speed_knots * np.sin(direction)
    v = -speed_knots * np.cos(direction)

    inset = ax.inset_axes(HODOGRAPH_BOUNDS)
    inset.set_aspect("equal")
    inset.set_xticks([])
    inset.set_yticks([])
    for spine in inset.spines.values():
        spine.set_visible(False)
    inset.patch.set_visible(False)   # no square background; a circle is added below

    # Finer rings (10 kt) for light/moderate winds, coarser (20 kt) for strong ones.
    step = (HODOGRAPH_FINE_RING_STEP_KNOTS
            if speed_knots.max() <= HODOGRAPH_FINE_RING_MAX_KNOTS
            else HODOGRAPH_RING_STEP_KNOTS)
    rings = max(step, int(np.ceil(speed_knots.max() / step) * step))
    # Circular translucent background, behind the rings and the wind curve.
    inset.add_patch(Circle((0, 0), rings, facecolor="white", edgecolor="none",
                           alpha=0.6, zorder=0))
    for radius in range(step, rings + 1, step):
        inset.add_patch(Circle((0, 0), radius, fill=False, edgecolor="gray",
                               linewidth=0.4, alpha=0.5))
        inset.annotate(f"{radius}", xy=(0, radius), fontsize=HODOGRAPH_FONT_SIZE,
                       color="gray", ha="center", va="bottom")
    inset.axhline(0, color="gray", lw=0.4, alpha=0.5)
    inset.axvline(0, color="gray", lw=0.4, alpha=0.5)

    inset.plot(u, v, color="black", lw=HODOGRAPH_LINEWIDTH, zorder=5)
    inset.plot(u[0], v[0], "o", color="black", markersize=2, zorder=6)
    limit = rings * 1.1
    inset.set_xlim(-limit, limit)
    inset.set_ylim(-limit, limit)
    title = inset.set_title("Hodograph (kt)", fontsize=HODOGRAPH_FONT_SIZE, color="black")
    title.set_bbox(translucent_label_bbox())
