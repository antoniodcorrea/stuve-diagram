"""Constants for drawing and styling the Stüve diagram."""

# Subtitle times, formatted METAR-style as DDHHMM
METAR_TIME_FORMAT = "%d%H%M"

GRAMS_PER_KILOGRAM = 1000.0

BOX_ASPECT = 1174 / 1374            # height / width of the reference plot box

# Potential-temperature contour levels (°C, relative to 0 °C in kelvin)
THETA_LEVEL_MIN_CELSIUS = -30.0
THETA_LEVEL_MAX_CELSIUS = 150.0
THETA_LEVEL_STEP_CELSIUS = 10.0

# Saturation mixing ratio contour levels (g/kg)
MIXING_RATIO_LEVELS_G_PER_KG = [0.01, 0.1, 0.2, 0.3, 1, 2, 4, 6, 8, 10, 12, 16,
                                20, 30, 40, 50, 60, 70, 80, 90]

# Isobars and isotherms drawn as reference lines
ISOBAR_STEP_HPA = 100
ISOBAR_MIN_HPA = 100
ISOBAR_MAX_HPA = 1000
ISOTHERM_MIN_CELSIUS = -90
ISOTHERM_MAX_CELSIUS = 50
ISOTHERM_STEP_CELSIUS = 10

# Altitude labels
ALTITUDE_LABEL_STEP_METRES = 1000
ALTITUDE_LABEL_STEP_FEET = 5000
ALTITUDE_LABEL_LEFT_OFFSET_CELSIUS = 1   # metres column: x = TEMPERATURE_MIN + this
ALTITUDE_FEET_OFFSET_CELSIUS = 9         # feet column, to the right of the metres
METRES_TO_FEET = 3.28084
# Skip altitude labels this close to the top, so their text stays inside the box
ALTITUDE_LABEL_TOP_MARGIN_HPA = 4

# Wind barbs
BARB_LEVEL_STEP_HPA = 100
LOWEST_BARB_MAX_GAP_HPA = 400            # include lowest level only within this gap
MIN_BARB_GAP_HPA = 25                    # drop the level barb if the surface is this close
BARB_COLUMN_INSET_CELSIUS = 5            # x = TEMPERATURE_MAX - this inset
BARB_LENGTH = 6
BARB_LINEWIDTH = 0.5
MS_TO_KNOTS = 1.94384
WIND_LABEL_FONT_SIZE = 5
WIND_LABEL_COLOR = "gray"
WIND_LABEL_OFFSET_POINTS = 8             # wind label this many points below the barb
# Empirical scale from a barb path's local units to rendered display points,
# used to place each label under the barb's true horizontal centre
BARB_PATH_TO_POINTS = 3.1

# Font sizes
ALTITUDE_LABEL_FONT_SIZE = 6
TICK_LABEL_FONT_SIZE = 7
LEGEND_FONT_SIZE = 8
# Legend upper-right corner (axes fraction), shifted left of the wind barb column
LEGEND_ANCHOR = (0.86, 0.99)

# Title: a heavy "STÜVE" heading over a lighter location/time subtitle
DIAGRAM_NAME = "Stüve"
HEADING_FONT_SIZE = 17
HEADING_FONT_WEIGHT = "extra bold"
HEADING_OFFSET_POINTS = 36     # height of the heading above the axes top
SUBTITLE_FONT_SIZE = 10
SUBTITLE_PAD = 12              # space (points) between the subtitle and the plot
