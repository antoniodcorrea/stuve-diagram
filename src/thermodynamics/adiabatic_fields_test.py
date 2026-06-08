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
from src.thermodynamics.saturation import saturation_vapour_pressure


def _physical(fields):
    # Saturation vapour pressure below the total pressure: the physical region.
    return fields["pressure"] > saturation_vapour_pressure(fields["temperature"])


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


def test_fields_are_finite_in_the_physical_region():
    fields = compute_adiabatic_fields()
    physical = _physical(fields)
    for name, field in fields.items():
        assert np.all(np.isfinite(field[physical])), name


def test_mixing_ratio_is_masked_where_vapour_pressure_exceeds_total_pressure():
    fields = compute_adiabatic_fields()
    unphysical = ~_physical(fields)
    assert unphysical.any()
    assert np.all(np.isnan(fields["saturation_mixing_ratio"][unphysical]))


def test_equivalent_potential_temperature_exceeds_potential_temperature():
    # Adding the latent-heat term can only raise theta-e above theta.
    fields = compute_adiabatic_fields()
    physical = _physical(fields)
    assert np.all(
        fields["equivalent_potential_temperature"][physical]
        >= fields["potential_temperature"][physical])
