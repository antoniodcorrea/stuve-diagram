"""Compose the rendering pipeline into a saved Stüve diagram."""

import matplotlib.pyplot as plt

from src.config.constants import FIGURE_DPI, FIGURE_PAD_INCHES, FIGURE_SIZE_INCHES
from src.rendering.configure_axes import configure_axes
from src.rendering.draw_altitude_labels import draw_altitude_labels
from src.rendering.draw_background import draw_background
from src.rendering.draw_cape import draw_cape
from src.rendering.draw_hodograph import draw_hodograph
from src.rendering.draw_indices_panel import draw_indices_panel
from src.rendering.draw_levels import draw_levels
from src.rendering.draw_overlay_profile import draw_overlay_profile
from src.rendering.draw_parcel import draw_parcel
from src.rendering.draw_profile import draw_profile
from src.rendering.draw_wind_barbs import draw_wind_barbs


def render_diagram(sounding, parcel, indices, overlay_sounding, subtitle, output_path,
                   projection):
    figure, ax = plt.subplots(figsize=FIGURE_SIZE_INCHES)
    draw_background(ax, projection)
    draw_profile(ax, sounding, projection)
    draw_overlay_profile(ax, overlay_sounding, projection)
    draw_parcel(ax, parcel, sounding, projection)
    draw_cape(ax, indices, sounding, projection)
    draw_levels(ax, indices, projection)
    draw_altitude_labels(ax, sounding, projection)
    draw_wind_barbs(ax, sounding, projection)
    draw_hodograph(ax, sounding)
    configure_axes(ax, subtitle, projection)
    # After configure_axes: the panel measures its laid-out text to place the
    # legend line samples, so the axes box must be final first.
    draw_indices_panel(ax, indices, show_overlay=overlay_sounding is not None)
    figure.savefig(output_path, dpi=FIGURE_DPI, bbox_inches="tight",
                   pad_inches=FIGURE_PAD_INCHES)
    plt.close(figure)
