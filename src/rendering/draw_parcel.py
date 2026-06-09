"""Draw the Tmax convective parcel: the dry adiabat and mixing-ratio line, with
the thermal top and cloud base they imply marked as horizontal levels."""

from matplotlib.transforms import blended_transform_factory

from src.config.constants import PRESSURE_BOTTOM_HPA, PRESSURE_TOP_HPA
from src.rendering.constants import (
    FREEZING_LEVEL_DASHES,
    PARCEL_COLOR,
    PARCEL_LINE_COLOR,
    PARCEL_LABEL_COLOR,
    PARCEL_GHOST_ALPHA,
    PARCEL_GHOST_LINEWIDTH,
    PARCEL_LABEL_FONT_SIZE,
    PARCEL_CLOUD_BASE_LABEL_GAP_POINTS,
    PARCEL_LABEL_OFFSET_POINTS,
    PARCEL_LEVEL_LINEWIDTH,
    PARCEL_LINEWIDTH,
    PARCEL_TICK_LINEWIDTH,
    PARCEL_TMAX_AXIS_OVERSHOOT,
    THERMAL_TOP_LABEL_RIGHT_GAP_POINTS,
)
from src.rendering.label_box import translucent_label_bbox
from src.thermodynamics.column import interp_at


def _label(ax, x, y, label, place="right", gap=PARCEL_LABEL_OFFSET_POINTS):
    # "right_edge": pin the label `gap` points from the diagram's right edge, at the
    # data y; x is taken from the axes (fraction 1.0), y from the data.
    if place == "right_edge":
        xy, xycoords, offset, ha, va = (
            (1.0, y), blended_transform_factory(ax.transAxes, ax.transData),
            (-gap, 0), "right", "center")
    else:
        xy, xycoords = (x, y), "data"
        offset, ha, va = {
            "right": ((gap, 0), "left", "center"),
            "left": ((-gap, 0), "right", "center"),
            "below": ((0, -gap), "center", "top"),
            "above": ((0, gap), "center", "bottom"),
        }[place]
    ax.annotate(label, xy=xy, xycoords=xycoords, xytext=offset, textcoords="offset points",
                color=PARCEL_LABEL_COLOR, fontsize=PARCEL_LABEL_FONT_SIZE,
                ha=ha, va=va, multialignment="center", annotation_clip=False,
                bbox=translucent_label_bbox(), zorder=7)


def _mark_tmax(ax, parcel, label, projection):
    temperature = parcel["temperature"][0]
    y_top = projection.pressure_to_y(parcel["pressures"][0])
    y_axis = projection.pressure_to_y(PRESSURE_BOTTOM_HPA)
    axis_span = y_axis - projection.pressure_to_y(PRESSURE_TOP_HPA)
    y_bottom = y_axis + axis_span * PARCEL_TMAX_AXIS_OVERSHOOT
    x_top = projection.x_at(temperature, y_top)
    x_axis = projection.x_at(temperature, y_axis)
    # Thin continuation of the adiabat down the isotherm to the T axis.
    ax.plot([x_top, x_axis], [y_top, y_axis], color=PARCEL_LINE_COLOR,
            lw=PARCEL_LINEWIDTH, zorder=6)
    # Thick vertical tick poking through the T axis at the Tmax value.
    ax.plot([x_axis, x_axis], [y_axis, y_bottom], color=PARCEL_COLOR,
            lw=PARCEL_TICK_LINEWIDTH, clip_on=False, zorder=6)
    # Label at the start of the Tmax parcel line (its surface point), to the right.
    _label(ax, x_top, y_top, label, place="right")


def _mark_line(ax, pressure, anchor_temperature, label, projection, place="right",
               gap=PARCEL_LABEL_OFFSET_POINTS):
    y = projection.pressure_to_y(pressure)
    ax.axhline(y, color=PARCEL_COLOR, lw=PARCEL_LEVEL_LINEWIDTH,
               ls=FREEZING_LEVEL_DASHES, zorder=4)
    x = None if anchor_temperature is None else projection.x_at(anchor_temperature, y)
    _label(ax, x, y, label, place=place, gap=gap)


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
            color=PARCEL_LINE_COLOR, lw=PARCEL_LINEWIDTH, label="Tmax parcel", zorder=6)

    # On a blue day the cloud base sits above the thermal top: ghost the adiabat
    # up to it (dashed) so it visibly meets the mixing-ratio line at the LCL.
    if blue_day and cloud_base is not None:
        ghost = (pressures <= thermal_top) & (pressures >= cloud_base)
        ax.plot(*projection.to_xy(parcel["temperature"][ghost], pressures[ghost]),
                color=PARCEL_LINE_COLOR, lw=PARCEL_GHOST_LINEWIDTH, ls="--",
                alpha=PARCEL_GHOST_ALPHA, zorder=6)
        # The LCL where the ghosted adiabat meets the mixing-ratio line is labelled
        # by draw_level_labels (which declutters it against the CCL and EL).

    # Mixing-ratio line from the surface up to the cloud base (LCL).
    moisture = pressures >= (cloud_base or pressures[-1])
    ax.plot(*projection.to_xy(parcel["dew_point"][moisture], pressures[moisture]),
            color=PARCEL_LINE_COLOR, lw=PARCEL_LINEWIDTH, zorder=6)

    _mark_tmax(ax, parcel, f"Tmax\n{parcel['temperature'][0]:.0f}°C", projection)
    # Thermal top label pinned a fixed distance from the diagram's right edge; the
    # cloud-base one stays anchored to the left of the sounding line. The altitude
    # is read off the left scale, so the horizontal-line labels carry only the name.
    _mark_line(ax, thermal_top, None, "Thermal top", projection,
               place="right_edge", gap=THERMAL_TOP_LABEL_RIGHT_GAP_POINTS)
    # No cloud base on a blue day (it would sit above the thermal top). Its label
    # sits further left than the thermal-top one, so the two never overlap when the
    # levels are close together.
    if cloud_base is not None and not blue_day:
        environment_temperature = interp_at(
            sounding.pressure.values, sounding.temperature.values, cloud_base)
        _mark_line(ax, cloud_base, environment_temperature, "Cloud base", projection,
                   place="left", gap=PARCEL_CLOUD_BASE_LABEL_GAP_POINTS)
