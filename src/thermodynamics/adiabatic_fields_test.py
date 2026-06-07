import numpy as np

from src.config.constants import (
    GRID_TEMPERATURE_MIN_CELSIUS,
    PRESSURE_BOTTOM_HPA,
    PRESSURE_TOP_HPA,
    TEMPERATURE_MAX_CELSIUS,
)
from src.thermodynamics.adiabatic_fields import compute_adiabatic_fields
from src.thermodynamics.constants import (
    GRID_PRESSURE_STEP_HPA,
    GRID_TEMPERATURE_STEP_CELSIUS,
)


def test_returns_all_expected_fields():
    fields = compute_adiabatic_fields()
    assert set(fields) == {
        "temperature",
        "pressure",
        "potential_temperature",
        "equivalent_potential_temperature",
        "saturation_mixing_ratio",
    }


def test_grid_shape_matches_the_bounds_and_steps():
    fields = compute_adiabatic_fields()
    n_temperatures = int(round(
        (TEMPERATURE_MAX_CELSIUS - GRID_TEMPERATURE_MIN_CELSIUS)
        / GRID_TEMPERATURE_STEP_CELSIUS)) + 1
    n_pressures = int(round(
        (PRESSURE_BOTTOM_HPA - PRESSURE_TOP_HPA) / GRID_PRESSURE_STEP_HPA)) + 1
    expected = (n_pressures, n_temperatures)
    for field in fields.values():
        assert field.shape == expected


def test_fields_are_finite():
    fields = compute_adiabatic_fields()
    for name, field in fields.items():
        assert np.all(np.isfinite(field)), name


def test_equivalent_potential_temperature_exceeds_potential_temperature():
    # Adding the latent-heat term can only raise theta-e above theta.
    fields = compute_adiabatic_fields()
    assert np.all(
        fields["equivalent_potential_temperature"] >= fields["potential_temperature"])
