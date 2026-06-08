import numpy as np

from src.thermodynamics.moist_parcel import moist_parcel_profile


def test_profile_starts_at_the_start_temperature():
    profile = moist_parcel_profile(1000.0, 25.0, 15.0)
    assert profile["pressures"][0] == 1000.0
    assert round(profile["temperature"][0], 2) == 25.0


def test_lcl_is_below_the_start_for_a_moist_parcel():
    profile = moist_parcel_profile(1000.0, 25.0, 15.0)
    assert 800.0 < profile["lcl_pressure"] < 1000.0


def test_saturated_ascent_is_warmer_than_a_dry_adiabat_aloft():
    # Above the LCL the released latent heat keeps the parcel warmer than the
    # dry adiabat would (the moist lapse rate is gentler).
    profile = moist_parcel_profile(1000.0, 25.0, 15.0)
    lcl = profile["lcl_pressure"]
    level = np.flatnonzero(profile["pressures"] < lcl - 100)[0]
    dry_adiabat = (25.0 + 273.16) * (profile["pressures"][level] / 1000.0) ** 0.2854 - 273.16
    assert profile["temperature"][level] > dry_adiabat


def test_drier_parcel_has_a_higher_lcl():
    moist = moist_parcel_profile(1000.0, 25.0, 18.0)
    dry = moist_parcel_profile(1000.0, 25.0, 5.0)
    assert dry["lcl_pressure"] < moist["lcl_pressure"]
