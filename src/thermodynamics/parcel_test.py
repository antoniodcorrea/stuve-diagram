from src.thermodynamics.parcel import parcel_ascent

# A stable environment (~2 °C / 100 hPa) over a 1000 hPa surface.
ENVIRONMENT_PRESSURE = [1000.0, 900.0, 800.0, 700.0, 600.0]
ENVIRONMENT_TEMPERATURE = [20.0, 18.0, 16.0, 14.0, 12.0]


def _ascent():
    return parcel_ascent(
        surface_pressure=1000.0, max_temperature=30.0, surface_dew_point=10.0,
        environment_pressure=ENVIRONMENT_PRESSURE,
        environment_temperature=ENVIRONMENT_TEMPERATURE)


def test_dry_adiabat_starts_at_the_max_temperature():
    parcel = _ascent()
    assert parcel["pressures"][0] == 1000.0
    assert parcel["temperature"][0] == 30.0


def test_thermal_top_is_where_the_adiabat_meets_the_environment():
    parcel = _ascent()
    # The 30 °C dry adiabat cools below the environment between 800 and 900 hPa.
    assert 800.0 < parcel["thermal_top_pressure"] < 900.0


def test_cloud_base_is_where_the_adiabat_meets_the_mixing_line():
    parcel = _ascent()
    # The dew-point depression closes between 700 and 800 hPa.
    assert 700.0 < parcel["cloud_base_pressure"] < 800.0


def test_mixing_line_dew_point_starts_at_the_surface_dew_point():
    parcel = _ascent()
    assert round(parcel["dew_point"][0], 2) == 10.0


def test_thermal_top_is_none_when_the_parcel_never_outruns_the_environment():
    # Max temperature already below the surface environment: no crossing above.
    parcel = parcel_ascent(
        surface_pressure=1000.0, max_temperature=10.0, surface_dew_point=5.0,
        environment_pressure=ENVIRONMENT_PRESSURE,
        environment_temperature=ENVIRONMENT_TEMPERATURE)
    assert parcel["thermal_top_pressure"] is None
