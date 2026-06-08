import pandas as pd

from src.sounding.constants import SOUNDING_COLUMNS
from src.thermodynamics.wind import bulk_shear, mean_layer_wind, wind_components

# Surface to upper levels, wind veering and strengthening with height.
PRESSURE = [1000.0, 900.0, 800.0, 700.0, 500.0]
ALTITUDE = [0.0, 1000.0, 2000.0, 3000.0, 6000.0]
TEMPERATURE = [20.0, 13.0, 6.0, -2.0, -20.0]
DEW_POINT = [10.0, 5.0, -2.0, -10.0, -28.0]
WIND_DIRECTION = [180.0, 200.0, 220.0, 240.0, 270.0]
WIND_SPEED = [5.0, 10.0, 15.0, 20.0, 30.0]


def _sounding():
    rows = list(zip(PRESSURE, ALTITUDE, TEMPERATURE, DEW_POINT, WIND_DIRECTION, WIND_SPEED))
    return pd.DataFrame(rows, columns=SOUNDING_COLUMNS)


def test_wind_components_for_a_southerly_wind_blow_north():
    # A 180° wind comes from the south, so it blows toward the north (+v, ~0 u).
    u, v = wind_components(180.0, 10.0)
    assert round(float(u), 6) == 0.0
    assert round(float(v), 6) == 10.0


def test_mean_layer_wind_speed_lies_within_the_layer_range():
    _, speed = mean_layer_wind(_sounding(), top_pressure=700.0)
    assert 5.0 < speed < 20.0


def test_bulk_shear_grows_with_the_wind_difference():
    # From 5 m/s near the surface to ~30 m/s at 6 km, with veering: a large shear.
    assert bulk_shear(_sounding()) > 20.0
