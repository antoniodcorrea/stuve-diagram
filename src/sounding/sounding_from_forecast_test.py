import pandas as pd

from src.sounding.constants import (
    OPEN_METEO_PRESSURE_LEVELS_HPA,
    SOUNDING_COLUMNS,
)
from src.sounding.sounding_from_forecast import sounding_from_forecast


def _build_forecast(surface_pressure):
    """A two-hour forecast with constant, level-derived dummy values."""
    hourly = {
        "surface_pressure": [surface_pressure, surface_pressure],
        "temperature_2m": [25.0, 26.0],
        "dew_point_2m": [10.0, 11.0],
        "wind_speed_10m": [3.0, 4.0],
        "wind_direction_10m": [180.0, 190.0],
    }
    for level in OPEN_METEO_PRESSURE_LEVELS_HPA:
        hourly[f"temperature_{level}hPa"] = [float(level) / 100, 0.0]
        hourly[f"relative_humidity_{level}hPa"] = [50.0, 50.0]
        hourly[f"geopotential_height_{level}hPa"] = [float(level) * 10, 0.0]
        hourly[f"wind_speed_{level}hPa"] = [5.0, 5.0]
        hourly[f"wind_direction_{level}hPa"] = [270.0, 270.0]
    return {"elevation": 1000.0, "hourly": hourly}


def test_returns_dataframe_with_expected_columns():
    sounding = sounding_from_forecast(_build_forecast(950.0), hour_index=0)
    assert isinstance(sounding, pd.DataFrame)
    assert list(sounding.columns) == SOUNDING_COLUMNS


def test_first_row_is_the_surface_point():
    sounding = sounding_from_forecast(_build_forecast(950.0), hour_index=0)
    surface = sounding.iloc[0]
    assert surface["pressure"] == 950.0
    assert surface["altitude"] == 1000.0      # forecast elevation
    assert surface["temperature"] == 25.0
    assert surface["dew_point"] == 10.0
    assert surface["wind_direction"] == 180.0
    assert surface["wind_speed"] == 3.0


def test_levels_at_or_below_surface_are_dropped():
    sounding = sounding_from_forecast(_build_forecast(950.0), hour_index=0)
    pressures = sounding["pressure"].tolist()
    # Surface point is 950, and the 1000/975/950 levels are underground.
    assert pressures[0] == 950.0
    assert all(level < 950.0 for level in pressures[1:])
    assert 925.0 in pressures


def test_honours_the_hour_index():
    sounding = sounding_from_forecast(_build_forecast(950.0), hour_index=1)
    assert sounding.iloc[0]["temperature"] == 26.0


def test_dew_point_is_computed_for_levels():
    sounding = sounding_from_forecast(_build_forecast(950.0), hour_index=0)
    # Each level is at 50 % humidity, so its dew point is below its temperature.
    aloft = sounding.iloc[1]
    assert aloft["dew_point"] < aloft["temperature"]
