"""App-level configuration and the shared diagram bounds.

Holds only the constants that cross package boundaries (the plot bounds, used by
both rendering and the thermodynamic field grid) plus entry-point configuration.
Domain-specific constants live in each package's own constants module.
"""

# Plot bounds (same as the reference diagram); shared by rendering and the grid
PRESSURE_BOTTOM_HPA, PRESSURE_TOP_HPA = 1020.0, 95.0
TEMPERATURE_MIN_CELSIUS, TEMPERATURE_MAX_CELSIUS = -95.0, 45.0

# Figure rendering
FIGURE_SIZE_INCHES = (9, 8)
FIGURE_DPI = 150
FIGURE_PAD_INCHES = 0.35       # margin around the saved figure (breathing room)

# Output directory for the rendered diagrams
OUTPUT_DIR = "./output"
