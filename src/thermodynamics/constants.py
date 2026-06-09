"""Thermodynamic and background-grid constants."""

# Thermodynamic constants (matching the reference MATLAB computation)
KAPPA = 0.2854                      # R/cp for dry air
LATENT_HEAT_VAPORISATION = 2.501e6  # latent heat of vaporisation [J/kg]
SPECIFIC_HEAT_DRY_AIR = 1005.7      # specific heat of dry air at constant pressure [J/(kg K)]
GAS_CONSTANT_DRY_AIR = 287.04       # specific gas constant for dry air [J/(kg K)] (= KAPPA * cp)
GRAVITY = 9.80665                   # standard gravity [m/s^2]
WATER_DENSITY = 1000.0              # liquid water density [kg/m^3]
ZERO_CELSIUS_IN_KELVIN = 273.16     # 0 °C in kelvin
REFERENCE_PRESSURE_HPA = 1000.0     # reference pressure [hPa]
HPA_TO_PASCAL = 100.0               # hPa -> Pa

# Bolton (1980) saturation vapour pressure coefficients
SATURATION_VAPOUR_PRESSURE_BASE_HPA = 6.112
SATURATION_VAPOUR_PRESSURE_NUMERATOR_COEFF = 17.67
SATURATION_VAPOUR_PRESSURE_DENOMINATOR_OFFSET_CELSIUS = 243.5

# Ratio of the molar masses of water vapour and dry air
DRY_AIR_TO_WATER_VAPOUR_RATIO = 0.622

# Percent (relative humidity) to fraction
PERCENT_TO_FRACTION = 100.0

# Estimated thermal updraft speed: a parcel that releases dry buoyant energy B
# would reach sqrt(2 B) in pure parcel theory. Real thermals climb at a small
# fraction of that — entrainment and drag bleed off most of the buoyancy. The
# energy is measured against the temperature profile at the hour of peak heating
# (the air the thermals actually rise through). This factor calibrates the
# estimate into the soaring range (~1–5 m/s).
THERMAL_UPDRAFT_EFFICIENCY = 0.15

# Background grid (temperature / pressure) sampling
GRID_TEMPERATURE_STEP_CELSIUS = 5.0
GRID_PRESSURE_STEP_HPA = 10.0
GRID_RANGE_EPSILON = 0.01           # nudge so np.arange includes the upper bound
