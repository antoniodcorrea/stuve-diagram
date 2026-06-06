from src.thermodynamics.constants import KAPPA
from src.thermodynamics.pressure_coordinate import pressure_to_axis


def test_applies_kappa_exponent():
    assert pressure_to_axis(1000.0) == 1000.0 ** KAPPA


def test_monotonic_increasing_with_pressure():
    assert pressure_to_axis(500.0) < pressure_to_axis(1000.0)
