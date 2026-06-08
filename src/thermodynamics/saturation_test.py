from src.thermodynamics.saturation import (
    dew_point_from_vapour_pressure,
    mixing_ratio,
    saturation_mixing_ratio,
    saturation_vapour_pressure,
)


def test_saturation_vapour_pressure_at_zero_is_the_base():
    assert round(saturation_vapour_pressure(0.0), 3) == 6.112


def test_dew_point_inverts_the_saturation_vapour_pressure():
    vapour_pressure = saturation_vapour_pressure(12.3)
    assert round(dew_point_from_vapour_pressure(vapour_pressure), 2) == 12.3


def test_mixing_ratio_grows_with_vapour_pressure():
    assert mixing_ratio(10.0, 1000.0) > mixing_ratio(5.0, 1000.0)


def test_saturation_mixing_ratio_about_8_grams_at_10c_1000hpa():
    # ~7.7 g/kg at 10 °C, 1000 hPa (textbook value).
    assert 0.006 < saturation_mixing_ratio(10.0, 1000.0) < 0.009
