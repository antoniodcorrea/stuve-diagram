import math

import numpy as np

from src.thermodynamics.dew_point import dew_point_from_humidity


def test_saturated_air_dew_point_equals_temperature():
    # At 100 % relative humidity the dew point is the air temperature.
    assert dew_point_from_humidity(20.0, 100.0) == 20.0


def test_dew_point_below_temperature_when_unsaturated():
    assert dew_point_from_humidity(20.0, 50.0) < 20.0


def test_lower_humidity_gives_lower_dew_point():
    assert dew_point_from_humidity(20.0, 30.0) < dew_point_from_humidity(20.0, 80.0)


def test_bone_dry_air_is_nan():
    assert math.isnan(dew_point_from_humidity(20.0, 0.0))


def test_vectorised_over_arrays():
    result = dew_point_from_humidity(np.array([20.0, 20.0]), np.array([100.0, 50.0]))
    assert result[0] == 20.0
    assert result[1] < 20.0
