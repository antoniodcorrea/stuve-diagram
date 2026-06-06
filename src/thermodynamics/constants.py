"""Thermodynamic and background-grid constants."""

# Thermodynamic constants (matching the reference MATLAB computation)
KAPPA = 0.2854                      # R/cp for dry air
LATENT_HEAT_VAPORISATION = 2.501e6  # latent heat of vaporisation [J/kg]
SPECIFIC_HEAT_DRY_AIR = 1005.7      # specific heat of dry air at constant pressure [J/(kg K)]
ZERO_CELSIUS_IN_KELVIN = 273.16     # 0 °C in kelvin
REFERENCE_PRESSURE_HPA = 1000.0     # reference pressure [hPa]

# Bolton (1980) saturation vapour pressure coefficients
SATURATION_VAPOUR_PRESSURE_BASE_HPA = 6.112
SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF = 17.67
SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS = 243.5

# Ratio of the molar masses of water vapour and dry air
DRY_AIR_TO_WATER_VAPOUR_RATIO = 0.622

# Percent (relative humidity) to fraction
PERCENT_TO_FRACTION = 100.0

# Background grid (temperature / pressure) sampling
GRID_TEMPERATURE_STEP_CELSIUS = 5.0
GRID_PRESSURE_STEP_HPA = 10.0
GRID_RANGE_EPSILON = 0.01           # nudge so np.arange includes the upper bound
