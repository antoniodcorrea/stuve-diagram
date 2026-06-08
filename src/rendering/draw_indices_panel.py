"""Draw the combined legend + soaring-indices panel: one monospace box, upper
left (right of the altitude labels).

A LEYEND section on top names the three series, each with a line sample
right-aligned in the value column; the convective, stability and airmass numbers
follow in aligned label/value rows under three headings. Missing values (a level
below ground, no cloud) show as a dash rather than a number.
"""

from matplotlib.lines import Line2D

from src.rendering.constants import (
    MS_TO_KNOTS,
    OVERLAY_PROFILE_LINEWIDTH,
    PANEL_ANCHOR,
    PANEL_BOX_ALPHA,
    PANEL_BOX_PAD,
    PANEL_BOX_ROUNDING,
    PANEL_FONT_SIZE,
    PANEL_LABEL_WIDTH,
    PANEL_LINESPACING,
    PANEL_SAMPLE_CHARS,
    PANEL_VALUE_WIDTH,
    PARCEL_LINEWIDTH,
)

_MISSING = "—"

# The three plotted series and the line style of each sample.
_SERIES = [
    ("Temperature", {}),
    ("Dew point", {"ls": ":"}),
    ("Tmax parcel", {"lw": PARCEL_LINEWIDTH}),
]


def _value(value, template):
    return _MISSING if value is None else template.format(value)


def _row(label, value):
    return f"{label:<{PANEL_LABEL_WIDTH}}{value:>{PANEL_VALUE_WIDTH}}"


def _knots(speed_ms):
    return None if speed_ms is None else speed_ms * MS_TO_KNOTS


def _panel_rows(indices):
    thermal_index = (f"{_value(indices['thermal_index_850'], '{:+.0f}')}"
                     f"/{_value(indices['thermal_index_700'], '{:+.0f}')}")
    mean_wind = (f"{_value(indices.get('mean_wind_direction'), '{:.0f}')}°"
                 f"/{_value(_knots(indices.get('mean_wind_speed')), '{:.0f}')}kt")
    return [
        "THERMALS",
        _row("Trigger T", _value(indices["trigger_temperature"], "{:.0f} °C")),
        _row("Working bd", _value(indices["working_band_m"], "{:,.0f} m")),
        _row("Cloud base", _value(indices["cloud_base_m"], "{:,.0f} m")),
        _row("Cloud top", _value(indices["cloud_top_m"], "{:,.0f} m")),
        _row("TI 850/700", thermal_index),
        "",
        "STABILITY",
        _row("CAPE", _value(indices["cape"], "{:,.0f} J/kg")),
        _row("CIN", _value(indices["cin"], "{:,.0f} J/kg")),
        _row("Lifted idx", _value(indices["lifted_index"], "{:+.0f} °C")),
        _row("Showalter", _value(indices["showalter_index"], "{:+.0f} °C")),
        _row("K-index", _value(indices["k_index"], "{:.0f}")),
        _row("Total Tot.", _value(indices["total_totals"], "{:.0f}")),
        "",
        "AIRMASS",
        _row("Freezing", _value(indices["freezing_altitude"], "{:,.0f} m")),
        _row("Prec.water", _value(indices["precipitable_water"], "{:.0f} mm")),
        _row("Mean wind", mean_wind),
        _row("Shear 6km", _value(_knots(indices.get("bulk_shear")), "{:.0f} kt")),
    ]


def draw_indices_panel(ax, indices, show_overlay=False):
    # Whole box is left-aligned monospace text; the series rows leave the value
    # column blank for the line samples drawn over them.
    series = _SERIES + ([("Tmax temp.", {"ls": "--", "lw": OVERLAY_PROFILE_LINEWIDTH})]
                        if show_overlay else [])
    rows = (["LEYEND"] + [name for name, _ in series] + [""] + _panel_rows(indices))
    text = ax.text(
        *PANEL_ANCHOR, "\n".join(rows), transform=ax.transAxes, ha="left", va="top",
        family="monospace", fontsize=PANEL_FONT_SIZE, linespacing=PANEL_LINESPACING, zorder=8,
        bbox=dict(boxstyle=f"round,pad={PANEL_BOX_PAD},rounding_size={PANEL_BOX_ROUNDING}",
                  facecolor="white", edgecolor="gray", linewidth=0.4, alpha=PANEL_BOX_ALPHA))

    # Line samples, right-aligned in the value column, on the series rows (1..3).
    figure = ax.figure
    figure.canvas.draw()
    box = text.get_window_extent(figure.canvas.get_renderer())
    row_height = box.height / len(rows)
    char_width = box.width / max(len(row) for row in rows)
    to_axes = ax.transAxes.inverted()
    for index, (_name, style) in enumerate(series, start=1):
        y = box.y1 - (index + 0.5) * row_height
        (x_left, y_axes), (x_right, _) = to_axes.transform(
            [(box.x1 - PANEL_SAMPLE_CHARS * char_width, y), (box.x1, y)])
        ax.add_line(Line2D([x_left, x_right], [y_axes, y_axes], transform=ax.transAxes,
                           color="black", lw=style.get("lw", 1.0), ls=style.get("ls", "-"),
                           zorder=9))
