"""Convert a pressure to the Stüve diagram vertical coordinate."""

from src.thermodynamics.constants import KAPPA


def pressure_to_axis(pressure):
    """Vertical coordinate for a pressure (hPa)."""
    return pressure ** KAPPA
