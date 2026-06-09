"""Overlay a second sounding's temperature line (dashed) on the diagram, as a
reference for how the profile evolves by peak heating. Only the line, nothing
else; same line weight as the main temperature profile."""

from src.rendering.constants import OVERLAY_PROFILE_LINEWIDTH, TEMPERATURE_COLOR


def draw_overlay_profile(ax, overlay_sounding, projection):
    if overlay_sounding is None:
        return
    x, y = projection.to_xy(overlay_sounding.temperature, overlay_sounding.pressure)
    ax.plot(x, y, color=TEMPERATURE_COLOR, lw=OVERLAY_PROFILE_LINEWIDTH, ls="--", zorder=5)
