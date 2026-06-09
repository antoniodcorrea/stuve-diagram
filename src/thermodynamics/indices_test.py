import pandas as pd

from src.sounding.constants import SOUNDING_COLUMNS
from src.thermodynamics.indices import (
    cape_cin,
    compute_indices,
    convective_temperature,
    freezing_level,
    isotherm_level,
    k_index,
    mixing_layer_lapse_rate,
    precipitable_water,
    thermal_strength,
)
from src.thermodynamics.moist_parcel import moist_parcel_profile
from src.thermodynamics.parcel import parcel_ascent

# A moderately unstable lowland sounding (surface 1000 hPa, ~6.5 °C/km lapse).
PRESSURE = [1000.0, 900.0, 850.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 200.0]
ALTITUDE = [100.0, 1000.0, 1500.0, 1950.0, 3000.0, 4200.0, 5600.0, 7200.0, 9200.0, 11800.0]
TEMPERATURE = [20.0, 13.0, 9.0, 6.0, -2.0, -10.0, -20.0, -32.0, -46.0, -56.0]
DEW_POINT = [13.0, 7.0, 3.0, -1.0, -9.0, -18.0, -30.0, -42.0, -56.0, -66.0]
WIND_DIRECTION = [200.0] * 10
WIND_SPEED = [5.0, 8.0, 10.0, 12.0, 15.0, 18.0, 20.0, 22.0, 25.0, 30.0]

MAX_TEMPERATURE = 28.0


def _sounding():
    rows = list(zip(PRESSURE, ALTITUDE, TEMPERATURE, DEW_POINT, WIND_DIRECTION, WIND_SPEED))
    return pd.DataFrame(rows, columns=SOUNDING_COLUMNS)


def _indices():
    sounding = _sounding()
    parcel = parcel_ascent(sounding.pressure[0], MAX_TEMPERATURE, sounding.dew_point[0],
                           sounding.pressure.values, sounding.temperature.values)
    return compute_indices(sounding, parcel, MAX_TEMPERATURE)


def test_cape_is_positive_for_an_unstable_parcel():
    profile = moist_parcel_profile(1000.0, MAX_TEMPERATURE, 13.0)
    energy = cape_cin(profile, PRESSURE, TEMPERATURE)
    assert energy["cape"] > 0
    assert energy["el_pressure"] < energy["lfc_pressure"]  # EL is higher up (lower hPa)


def test_freezing_level_sits_between_the_zero_crossing_levels():
    pressure, altitude = freezing_level(PRESSURE, TEMPERATURE, ALTITUDE)
    # Temperature passes through 0 °C between 800 and 700 hPa.
    assert 700.0 < pressure < 800.0
    assert 1950.0 < altitude < 3000.0


def test_convective_temperature_is_warmer_than_the_morning_surface():
    trigger, ccl = convective_temperature(1000.0, 13.0, PRESSURE, TEMPERATURE)
    assert trigger > 20.0
    assert ccl < 1000.0


def test_k_index_is_a_finite_number():
    assert isinstance(k_index(PRESSURE, TEMPERATURE, DEW_POINT), float)


def test_icing_isotherm_sits_above_the_freezing_level():
    freezing_pressure, _ = freezing_level(PRESSURE, TEMPERATURE, ALTITUDE)
    icing_pressure, icing_altitude = isotherm_level(PRESSURE, TEMPERATURE, ALTITUDE, -10.0)
    # −10 °C is reached higher up (lower pressure, greater altitude) than 0 °C.
    assert icing_pressure < freezing_pressure
    assert icing_altitude > 1950.0


def test_mixing_layer_lapse_rate_is_positive_for_a_normal_lapse():
    parcel = parcel_ascent(PRESSURE[0], MAX_TEMPERATURE, DEW_POINT[0], PRESSURE, TEMPERATURE)
    lapse = mixing_layer_lapse_rate(PRESSURE, TEMPERATURE, ALTITUDE,
                                    parcel["thermal_top_pressure"])
    assert lapse > 0


def test_thermal_strength_is_positive_with_a_working_band():
    parcel = parcel_ascent(PRESSURE[0], MAX_TEMPERATURE, DEW_POINT[0], PRESSURE, TEMPERATURE)
    speed, excess = thermal_strength(parcel, PRESSURE, TEMPERATURE, ALTITUDE)
    assert speed > 0
    assert excess > 0


def test_thermal_strength_is_none_without_a_thermal_top():
    speed, excess = thermal_strength({"thermal_top_pressure": None}, PRESSURE, TEMPERATURE, ALTITUDE)
    assert speed is None and excess is None


def test_precipitable_water_is_positive():
    assert precipitable_water(PRESSURE, DEW_POINT) > 0


def test_precipitable_water_ignores_bone_dry_nan_levels():
    dew_point = DEW_POINT[:-1] + [float("nan")]
    assert precipitable_water(PRESSURE, dew_point) > 0


def test_blue_day_reports_no_cloud_base():
    # Cloud base above the thermal top: the panel must not claim a cloud base.
    parcel = {"thermal_top_pressure": 850.0, "cloud_base_pressure": 700.0}
    indices = compute_indices(_sounding(), parcel, MAX_TEMPERATURE)
    assert indices["cloud_base_m"] is None
    assert indices["cloud_top_m"] is None


def test_normal_day_reports_a_cloud_base():
    parcel = {"thermal_top_pressure": 700.0, "cloud_base_pressure": 850.0}
    indices = compute_indices(_sounding(), parcel, MAX_TEMPERATURE)
    assert indices["cloud_base_m"] is not None


def test_compute_indices_exposes_every_panel_key():
    indices = _indices()
    for key in ["cape", "cin", "lifted_index", "showalter_index", "k_index",
                "total_totals", "trigger_temperature", "thermal_index_850",
                "thermal_index_700", "freezing_altitude", "precipitable_water",
                "working_band_m", "cloud_base_m", "parcel_profile"]:
        assert key in indices
