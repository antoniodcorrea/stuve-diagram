"""Fetch the Open-Meteo pressure-level forecast as a parsed JSON dict."""

import json
import urllib.parse
import urllib.request

from src.sounding.constants import (
    OPEN_METEO_FORECAST_DAYS,
    OPEN_METEO_MODEL,
    OPEN_METEO_PRESSURE_LEVELS_HPA,
    OPEN_METEO_SURFACE_VARIABLES,
    OPEN_METEO_TIMEOUT_SECONDS,
    OPEN_METEO_TIMEZONE,
    OPEN_METEO_URL,
    OPEN_METEO_VARIABLES,
    OPEN_METEO_WIND_SPEED_UNIT,
)


def fetch_open_meteo(latitude, longitude):
    """Return the parsed Open-Meteo forecast for every hour and pressure level."""
    hourly_variables = list(OPEN_METEO_SURFACE_VARIABLES) + [
        f"{variable}_{level}hPa"
        for level in OPEN_METEO_PRESSURE_LEVELS_HPA
        for variable in OPEN_METEO_VARIABLES]
    query = urllib.parse.urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(hourly_variables),
        "models": OPEN_METEO_MODEL,
        "forecast_days": OPEN_METEO_FORECAST_DAYS,
        "wind_speed_unit": OPEN_METEO_WIND_SPEED_UNIT,
        "timezone": OPEN_METEO_TIMEZONE,
    })
    with urllib.request.urlopen(f"{OPEN_METEO_URL}?{query}",
                                timeout=OPEN_METEO_TIMEOUT_SECONDS) as response:
        return json.load(response)
