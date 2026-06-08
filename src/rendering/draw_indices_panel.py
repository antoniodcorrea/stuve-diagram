"""Draw the combined legend + soaring-indices panel: one monospace box, upper
right (left of the wind-barb column).

The series legend (Temperature, Dew point, Tmax parcel) sits on top with real
line samples, then the convective, stability and airmass numbers follow in
aligned label/value rows grouped under three headings. Missing values (a level
below ground, no cloud) show as a dash rather than a number.
"""

from matplotlib.lines import Line2D

from src.rendering.constants import (
    MS_TO_KNOTS,
    PANEL_ANCHOR,
    PANEL_BORDER_PAD,
    PANEL_BOX_ALPHA,
    PANEL_BOX_PAD,
    PANEL_BOX_ROUNDING,
    PANEL_FONT_SIZE,
    PANEL_HANDLE_LENGTH,
    PANEL_HANDLE_TEXT_PAD,
    PANEL_LABEL_SPACING,
    PANEL_LABEL_WIDTH,
    PANEL_VALUE_WIDTH,
    PARCEL_LINEWIDTH,
)

_MISSING = "—"


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


def draw_indices_panel(ax, indices):
    # Series legend with real line samples, then the data rows on blank handles so
    # everything lines up in one monospace box.
    handles = [
        Line2D([], [], color="black", lw=1.0),
        Line2D([], [], color="black", lw=1.0, ls=":"),
        Line2D([], [], color="black", lw=PARCEL_LINEWIDTH),
    ]
    # Pad the legend names to a full data row width: markerfirst=False right-aligns
    # the label text, so a full-width label keeps the name on the left (aligned with
    # the data labels) and the line sample falls in the right-hand value column.
    width = PANEL_LABEL_WIDTH + PANEL_VALUE_WIDTH
    labels = [f"{name:<{width}}" for name in ("Temperature", "Dew point", "Tmax parcel")]
    for row in [""] + _panel_rows(indices):
        handles.append(Line2D([], [], linestyle="none", marker="none"))
        labels.append(row)

    legend = ax.legend(
        handles, labels, loc="upper left", bbox_to_anchor=PANEL_ANCHOR,
        prop={"family": "monospace", "size": PANEL_FONT_SIZE}, markerfirst=False,
        labelspacing=PANEL_LABEL_SPACING, handlelength=PANEL_HANDLE_LENGTH,
        handletextpad=PANEL_HANDLE_TEXT_PAD, borderpad=PANEL_BORDER_PAD,
        borderaxespad=0.0)
    legend.set_zorder(8)

    frame = legend.get_frame()
    frame.set_boxstyle(f"round,pad={PANEL_BOX_PAD},rounding_size={PANEL_BOX_ROUNDING}")
    frame.set_facecolor("white")
    frame.set_edgecolor("gray")
    frame.set_linewidth(0.4)
    frame.set_alpha(PANEL_BOX_ALPHA)
