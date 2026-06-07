"""Compose the rendering pipeline into a saved Stüve diagram."""

import matplotlib.pyplot as plt

from src.config.constants import FIGURE_DPI, FIGURE_PAD_INCHES, FIGURE_SIZE_INCHES
from src.rendering.configure_axes import configure_axes
from src.rendering.draw_altitude_labels import draw_altitude_labels
from src.rendering.draw_background import draw_background
from src.rendering.draw_parcel import draw_parcel
from src.rendering.draw_profile import draw_profile
from src.rendering.draw_wind_barbs import draw_wind_barbs


def render_diagram(sounding, parcel, subtitle, output_path):
    figure, ax = plt.subplots(figsize=FIGURE_SIZE_INCHES)
    draw_background(ax)
    draw_profile(ax, sounding)
    draw_parcel(ax, parcel, sounding)
    draw_altitude_labels(ax, sounding)
    draw_wind_barbs(ax, sounding)
    configure_axes(ax, subtitle)
    figure.savefig(output_path, dpi=FIGURE_DPI, bbox_inches="tight",
                   pad_inches=FIGURE_PAD_INCHES)
    plt.close(figure)
