"""Draw wind barbs in a column inside the diagram.

One barb per 100 hPa level that has a measurement (nearest measured level to
each), plus the lowest level of all as long as it is within 400 hPa of the next
barb. Direction is the bearing the wind comes from (meteorological), so the u/v
components point where it blows toward.
"""

import numpy as np
from matplotlib.transforms import offset_copy

from src.rendering.constants import (
    BARB_COLUMN_INSET_CELSIUS,
    BARB_LENGTH,
    BARB_LEVEL_STEP_HPA,
    BARB_LINEWIDTH,
    BARB_PATH_TO_POINTS,
    LOWEST_BARB_MAX_GAP_HPA,
    MIN_BARB_GAP_HPA,
    MS_TO_KNOTS,
)


def draw_wind_barbs(ax, sounding, projection):
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
    # Barbs follow the meteorological convention (half = 5, full = 10, pennant =
    # 50 knots), so the components must be in knots, not the m/s of the source.
    wind_speed_knots = wind_speed * MS_TO_KNOTS
    wind_u = -wind_speed_knots * np.sin(direction_radians)
    wind_v = -wind_speed_knots * np.cos(direction_radians)
    barb_x = projection.xlim[1] - BARB_COLUMN_INSET_CELSIUS
    barb_y = projection.pressure_to_y(barb_levels_data.pressure.to_numpy())

    # Centre each barb on the column and anchor it by the bottom of its staff. The
    # glyph (staff plus feathers) sits off to one side of and below its anchor, so
    # measure its drawn shape and offset it to put its horizontal centre on the
    # column and its lowest point on the level line.
    for x, y_value, u, v in zip(np.full(len(barb_y), barb_x), barb_y, wind_u, wind_v):
        barb = ax.barbs(x, y_value, u, v, length=BARB_LENGTH, linewidth=BARB_LINEWIDTH,
                        color="black", zorder=6)
        vertices = barb.get_paths()[0].vertices
        x_offset = -(vertices[:, 0].min() + vertices[:, 0].max()) / 2 * BARB_PATH_TO_POINTS
        lift = max(0.0, -vertices[:, 1].min()) * BARB_PATH_TO_POINTS
        barb.remove()
        ax.barbs(x, y_value, u, v, length=BARB_LENGTH, linewidth=BARB_LINEWIDTH,
                 color="black", zorder=6,
                 transform=offset_copy(ax.transData, fig=ax.figure, x=x_offset, y=lift,
                                       units="points"))
