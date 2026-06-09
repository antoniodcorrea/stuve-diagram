"""Label the convective levels (LCL, CCL, LFC, EL) with their name placed just
beside the curve each sits on — never on top of it — and any two that would land
on each other nudged apart.

Drawn after the axes are final, so positions can be measured. Each label is
anchored in data coordinates (stable across the save), offset to the side and
nudged vertically in points (likewise stable), with the spacing worked out from
the axes' physical height. The altitude of every level is read off the left scale,
so the labels carry only the name.
"""

from src.rendering.constants import (
    LEVEL_LABEL_COLOR,
    LEVEL_LABEL_FONT_SIZE,
    LEVEL_LABEL_MIN_GAP_POINTS,
    LEVEL_LABEL_SIDE_GAP_POINTS,
)
from src.rendering.label_box import translucent_label_bbox
from src.thermodynamics.column import interp_at

POINTS_PER_INCH = 72.0


def _collect(indices, parcel):
    """Each present level as (pressure, anchor_temperature, name), anchored on the
    curve it belongs to so the label can sit just to its side."""
    profile = indices["parcel_profile"]
    specs = []

    el = indices["el_pressure"]
    lcl = profile["lcl_pressure"]
    if el is not None and lcl is not None and el < lcl:
        specs.append((el, float(interp_at(profile["pressures"], profile["temperature"], el)), "EL"))

    lfc = indices["lfc_pressure"]
    if lfc is not None:
        specs.append((lfc, float(interp_at(profile["pressures"], profile["temperature"], lfc)), "LFC"))

    ccl = indices["ccl_pressure"]
    if ccl is not None and indices["ccl_temperature"] is not None:
        specs.append((ccl, indices["ccl_temperature"], "CCL"))

    # LCL on a blue day only: the cloud base sits above the thermal top, so it is
    # not drawn as a cloud-base line, but the lifting condensation level still matters.
    cloud_base = parcel["cloud_base_pressure"]
    thermal_top = parcel["thermal_top_pressure"] or parcel["pressures"][-1]
    if cloud_base is not None and cloud_base < thermal_top:
        specs.append((cloud_base,
                      float(interp_at(parcel["pressures"], parcel["temperature"], cloud_base)), "LCL"))

    return specs


def draw_level_labels(ax, indices, parcel, projection):
    specs = _collect(indices, parcel)
    if not specs:
        return

    ax.figure.canvas.draw()
    axes_height_points = (ax.get_position().height
                          * ax.figure.get_size_inches()[1] * POINTS_PER_INCH)
    to_axes = ax.transAxes.inverted()

    labels = []
    for pressure, anchor_temperature, text in specs:
        x_data, y_data = projection.to_xy(anchor_temperature, pressure)
        y_axes = to_axes.transform(ax.transData.transform((float(x_data), float(y_data))))[1]
        anchor_points = y_axes * axes_height_points
        labels.append({"x": float(x_data), "y": float(y_data),
                       "anchor_points": anchor_points, "points": anchor_points, "text": text})

    # Top-down: any label closer than the minimum to the one above is pushed down.
    ordered = sorted(labels, key=lambda label: label["points"], reverse=True)
    for upper, lower in zip(ordered, ordered[1:]):
        if upper["points"] - lower["points"] < LEVEL_LABEL_MIN_GAP_POINTS:
            lower["points"] = upper["points"] - LEVEL_LABEL_MIN_GAP_POINTS

    for label in labels:
        dy = label["points"] - label["anchor_points"]
        ax.annotate(label["text"], xy=(label["x"], label["y"]),
                    xytext=(LEVEL_LABEL_SIDE_GAP_POINTS, dy), textcoords="offset points",
                    ha="left", va="center", color=LEVEL_LABEL_COLOR,
                    fontsize=LEVEL_LABEL_FONT_SIZE, annotation_clip=False, zorder=7,
                    bbox=translucent_label_bbox())
