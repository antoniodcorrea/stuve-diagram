import numpy as np

from src.rendering.constants import SKEWT_SKEW
from src.rendering.projection import SkewTProjection, StuveProjection
from src.thermodynamics.constants import KAPPA, REFERENCE_PRESSURE_HPA


def test_stuve_x_is_the_bare_temperature():
    stuve = StuveProjection()
    x, y = stuve.to_xy(np.array([-10.0, 20.0]), np.array([850.0, 500.0]))
    assert list(x) == [-10.0, 20.0]
    np.testing.assert_allclose(y, np.array([850.0, 500.0]) ** KAPPA)


def test_skewt_pressure_is_log_p():
    skewt = SkewTProjection()
    np.testing.assert_allclose(
        skewt.pressure_to_y(np.array([1000.0, 500.0])),
        np.log(REFERENCE_PRESSURE_HPA / np.array([1000.0, 500.0])))


def test_skewt_x_is_skewed_by_pressure():
    skewt = SkewTProjection()
    y = skewt.pressure_to_y(500.0)
    x, _ = skewt.to_xy(0.0, 500.0)
    # At 0 °C the skew offset is the full skew times the log-pressure height.
    assert np.isclose(x, SKEWT_SKEW * y)


def test_isobars_share_one_height_across_temperatures():
    # y depends only on pressure, so an isobar is horizontal in both projections.
    for projection in (StuveProjection(), SkewTProjection()):
        _x, y = projection.to_xy(np.array([-30.0, 30.0]), np.array([700.0, 700.0]))
        assert y[0] == y[1]
