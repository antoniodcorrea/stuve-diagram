"""Constants for the sounding data sources (geocoder + Open-Meteo)."""

# Sounding schema shared by every data source
SOUNDING_COLUMNS = ["pressure", "altitude", "temperature", "dew_point",
                    "wind_direction", "wind_speed"]

# Local hour of the morning sounding to render. Picked before convection starts,
# so the overnight inversion is intact and the Tmax dry adiabat gives a realistic
# thermal top (the forecast-max-temperature method for soaring).
TARGET_HOUR_LOCAL = 7

# Geocoder (Nominatim)
GEOCODER_URL = "https://nominatim.openstreetmap.org/search"
GEOCODER_USER_AGENT = "stuve-diagram/1.0"
GEOCODER_TIMEOUT_SECONDS = 25

# Open-Meteo data source
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_MODEL = "gfs_seamless"
OPEN_METEO_FORECAST_DAYS = 2
OPEN_METEO_WIND_SPEED_UNIT = "ms"
OPEN_METEO_TIMEZONE = "auto"          # forecast times in the location's local time
OPEN_METEO_TIMEOUT_SECONDS = 30
# Pressure levels offered by Open-Meteo, from the surface upward (hPa)
OPEN_METEO_PRESSURE_LEVELS_HPA = [1000, 975, 950, 925, 900, 850, 800, 750, 700,
                                  650, 600, 550, 500, 450, 400, 350, 300, 250,
                                  200, 150, 100, 70, 50, 40, 30, 20, 15, 10]
# Per-level variables the Stüve diagram needs (relative_humidity feeds the dew
# point, geopotential_height feeds the altitude)
OPEN_METEO_VARIABLES = ["temperature", "relative_humidity", "geopotential_height",
                        "wind_speed", "wind_direction"]
# Surface variables: the station sits above sea level, so pressure levels below
# the surface are underground and must be dropped in favour of this real point
OPEN_METEO_SURFACE_VARIABLES = ["surface_pressure", "temperature_2m", "dew_point_2m",
                                "wind_speed_10m", "wind_direction_10m"]
# Daily variables: the forecast maximum temperature feeds the Tmax parcel ascent
OPEN_METEO_DAILY_VARIABLES = ["temperature_2m_max"]
