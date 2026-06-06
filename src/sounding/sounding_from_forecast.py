"""Build a sounding DataFrame for one hour of an Open-Meteo forecast."""

import pandas as pd

from src.sounding.constants import OPEN_METEO_PRESSURE_LEVELS_HPA, SOUNDING_COLUMNS
from src.thermodynamics.dew_point import dew_point_from_humidity


def sounding_from_forecast(forecast, hour_index):
    """Sounding for the given hour: the real surface point plus the pressure
    levels above the ground (levels below the surface are underground)."""
    hourly = forecast["hourly"]
    surface_pressure = hourly["surface_pressure"][hour_index]

    rows = [[surface_pressure,
             forecast["elevation"],
             hourly["temperature_2m"][hour_index],
             hourly["dew_point_2m"][hour_index],
             hourly["wind_direction_10m"][hour_index],
             hourly["wind_speed_10m"][hour_index]]]

    for level in OPEN_METEO_PRESSURE_LEVELS_HPA:
        if level >= surface_pressure:
            continue
        temperature = hourly[f"temperature_{level}hPa"][hour_index]
        relative_humidity = hourly[f"relative_humidity_{level}hPa"][hour_index]
        altitude = hourly[f"geopotential_height_{level}hPa"][hour_index]
        wind_direction = hourly[f"wind_direction_{level}hPa"][hour_index]
        wind_speed = hourly[f"wind_speed_{level}hPa"][hour_index]
        rows.append([level, altitude, temperature,
                     dew_point_from_humidity(temperature, relative_humidity),
                     wind_direction, wind_speed])
    return pd.DataFrame(rows, columns=SOUNDING_COLUMNS)
