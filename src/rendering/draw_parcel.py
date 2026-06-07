"""Draw the Tmax convective parcel: the dry adiabat and mixing-ratio line, with
the thermal top and cloud base they imply marked at their altitudes."""

import numpy as np

from src.config.constants import PRESSURE_BOTTOM_HPA, PRESSURE_TOP_HPA
from src.rendering.constants import (
    PARCEL_COLOR,
    PARCEL_GHOST_ALPHA,
    PARCEL_GHOST_LINEWIDTH,
    PARCEL_LABEL_BOX_ALPHA,
    PARCEL_LABEL_BOX_PAD,
    PARCEL_LABEL_FONT_SIZE,
    PARCEL_LABEL_OFFSET_POINTS,
    PARCEL_LEVEL_LINEWIDTH,
    PARCEL_LINEWIDTH,
    PARCEL_TICK_LINEWIDTH,
    PARCEL_TMAX_AXIS_OVERSHOOT,
    PARCEL_TMAX_LABEL_RISE_POINTS,
)


def _interp_at(pressure, pressures, values):
    ascending = pressures.argsort()
    return np.interp(pressure, pressures[ascending], values[ascending])


def _altitude_at(pressure, sounding):
    return _interp_at(pressure, sounding.pressure.values, sounding.altitude.values)


def _label(ax, x, y, label, place="right", gap=PARCEL_LABEL_OFFSET_POINTS):
    offset, ha, va = {
        "right": ((gap, 0), "left", "center"),
        "below": ((0, -gap), "center", "top"),
        "above": ((0, gap), "center", "bottom"),
    }[place]
    ax.annotate(label, xy=(x, y), xytext=offset, textcoords="offset points",
                color=PARCEL_COLOR, fontsize=PARCEL_LABEL_FONT_SIZE,
                ha=ha, va=va, multialignment="center", annotation_clip=False,
                bbox=dict(boxstyle=f"square,pad={PARCEL_LABEL_BOX_PAD}",
                          facecolor="white", edgecolor="none",
                          alpha=PARCEL_LABEL_BOX_ALPHA),
                zorder=7)


def _mark_tmax(ax, parcel, label, projection):
    temperature = parcel["temperature"][0]
    y_top = projection.pressure_to_y(parcel["pressures"][0])
    y_axis = projection.pressure_to_y(PRESSURE_BOTTOM_HPA)
    axis_span = y_axis - projection.pressure_to_y(PRESSURE_TOP_HPA)
    y_bottom = y_axis + axis_span * PARCEL_TMAX_AXIS_OVERSHOOT
    x_top = projection.x_at(temperature, y_top)
    x_axis = projection.x_at(temperature, y_axis)
    # Thin continuation of the adiabat down the isotherm to the T axis.
    ax.plot([x_top, x_axis], [y_top, y_axis], color=PARCEL_COLOR,
            lw=PARCEL_LINEWIDTH, zorder=6)
    # Thick vertical tick poking through the T axis at the Tmax value.
    ax.plot([x_axis, x_axis], [y_axis, y_bottom], color=PARCEL_COLOR,
            lw=PARCEL_TICK_LINEWIDTH, clip_on=False, zorder=6)
    _label(ax, x_axis, y_axis, label, place="above", gap=PARCEL_TMAX_LABEL_RISE_POINTS)


def _mark_line(ax, pressure, parcel, label, projection):
    temperature = _interp_at(pressure, parcel["pressures"], parcel["temperature"])
    x, y = projection.to_xy(temperature, pressure)
    ax.axhline(y, color=PARCEL_COLOR, lw=PARCEL_LEVEL_LINEWIDTH, zorder=4)
    _label(ax, x, y, label)


def draw_parcel(ax, parcel, sounding, projection):
    pressures = parcel["pressures"]
    thermal_top = parcel["thermal_top_pressure"] or pressures[-1]
    cloud_base = parcel["cloud_base_pressure"]
    # Blue day: the parcel would condense only above the thermal top, so the
    # thermals die before any cumulus form.
    blue_day = cloud_base is None or cloud_base < thermal_top

    # Dry adiabat (Tmax parcel) from the surface up to the thermal top.
    adiabat = pressures >= thermal_top
    ax.plot(*projection.to_xy(parcel["temperature"][adiabat], pressures[adiabat]),
            color=PARCEL_COLOR, lw=PARCEL_LINEWIDTH, label="Tmax parcel", zorder=6)

    # On a blue day the cloud base sits above the thermal top: ghost the adiabat
    # up to it (dashed) so it visibly meets the mixing-ratio line at the LCL.
    if blue_day and cloud_base is not None:
        ghost = (pressures <= thermal_top) & (pressures >= cloud_base)
        ax.plot(*projection.to_xy(parcel["temperature"][ghost], pressures[ghost]),
                color=PARCEL_COLOR, lw=PARCEL_GHOST_LINEWIDTH, ls="--",
                alpha=PARCEL_GHOST_ALPHA, zorder=6)

    # Mixing-ratio line from the surface up to the cloud base (LCL).
    moisture = pressures >= (cloud_base or pressures[-1])
    ax.plot(*projection.to_xy(parcel["dew_point"][moisture], pressures[moisture]),
            color=PARCEL_COLOR, lw=PARCEL_LINEWIDTH, zorder=6)

    _mark_tmax(ax, parcel, f"Tmax\n{parcel['temperature'][0]:.0f}°C", projection)
    _mark_line(ax, thermal_top, parcel,
               f"Thermal top {_altitude_at(thermal_top, sounding):,.0f} m", projection)
    # No cloud base on a blue day (it would sit above the thermal top).
    if cloud_base is not None and not blue_day:
        _mark_line(ax, cloud_base, parcel,
                   f"Cloud base {_altitude_at(cloud_base, sounding):,.0f} m", projection)
