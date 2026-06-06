"""Draw wind barbs in a column inside the diagram.

One barb per 100 hPa level that has a measurement (nearest measured level to
each), plus the lowest level of all as long as it is within 400 hPa of the next
barb. Direction is the bearing the wind comes from (meteorological), so the u/v
components point where it blows toward.
"""

import numpy as np

from src.config.constants import TEMPERATURE_MAX_CELSIUS
from src.rendering.constants import (
    BARB_COLUMN_INSET_CELSIUS,
    BARB_LENGTH,
    BARB_LEVEL_STEP_HPA,
    BARB_LINEWIDTH,
    BARB_PATH_TO_POINTS,
    LOWEST_BARB_MAX_GAP_HPA,
    MIN_BARB_GAP_HPA,
    MS_TO_KNOTS,
    WIND_LABEL_COLOR,
    WIND_LABEL_FONT_SIZE,
    WIND_LABEL_OFFSET_POINTS,
)
from src.thermodynamics.pressure_coordinate import pressure_to_axis


def draw_wind_barbs(ax, sounding):
    barb_levels = range(BARB_LEVEL_STEP_HPA, int(sounding.pressure.max()) + 1,
                        BARB_LEVEL_STEP_HPA)
    barb_indices = {(sounding.pressure - level).abs().idxmin() for level in barb_levels}

    lowest_index = sounding.pressure.idxmax()
    level_pressures = sounding.pressure[sorted(barb_indices)]
    gap_to_lowest = sounding.pressure[lowest_index] - level_pressures.max()
    if gap_to_lowest < LOWEST_BARB_MAX_GAP_HPA:
        # If the surface nearly coincides with the lowest level, drop that level
        # so the two barbs don't overlap; keep the real surface point.
        if gap_to_lowest < MIN_BARB_GAP_HPA:
            barb_indices.discard(level_pressures.idxmax())
        barb_indices.add(lowest_index)

    barb_levels_data = sounding.loc[sorted(barb_indices)]
    direction_radians = np.deg2rad(barb_levels_data.wind_direction.to_numpy())
    wind_speed = barb_levels_data.wind_speed.to_numpy()
    wind_u = -wind_speed * np.sin(direction_radians)
    wind_v = -wind_speed * np.cos(direction_radians)
    barb_x = TEMPERATURE_MAX_CELSIUS - BARB_COLUMN_INSET_CELSIUS
    barb_y = pressure_to_axis(barb_levels_data.pressure).to_numpy()

    barbs = ax.barbs(np.full(len(barb_levels_data), barb_x), barb_y, wind_u, wind_v,
                     length=BARB_LENGTH, linewidth=BARB_LINEWIDTH, color="black", zorder=6)

    # The barb body sits off to one side of its anchor; center each label under the
    # barb's true horizontal centre (path centre scaled to rendered display points).
    for barb_path, y_value, speed in zip(barbs.get_paths(), barb_y, wind_speed):
        path_center = (barb_path.vertices[:, 0].min() + barb_path.vertices[:, 0].max()) / 2
        label = f"{int(round(speed * MS_TO_KNOTS))} kts. / {int(round(speed))} ms."
        ax.annotate(label, xy=(barb_x, y_value),
                    xytext=(path_center * BARB_PATH_TO_POINTS, -WIND_LABEL_OFFSET_POINTS),
                    textcoords="offset points", ha="center", va="top",
                    color=WIND_LABEL_COLOR, fontsize=WIND_LABEL_FONT_SIZE, zorder=6)
