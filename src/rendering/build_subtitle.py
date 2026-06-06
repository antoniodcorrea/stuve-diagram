"""Build the subtitle: location and METAR-style local times (DDHHMM)."""

from datetime import datetime

from src.rendering.constants import METAR_TIME_FORMAT


def build_subtitle(location_query, forecast_time, generated_at_local):
    """Two-line uppercase subtitle: location, then valid and obtained times.

    `forecast_time` is the local ISO timestamp the diagram is valid for and
    `generated_at_local` is the local datetime the data was obtained.
    """
    valid = datetime.fromisoformat(forecast_time).strftime(METAR_TIME_FORMAT)
    obtained = generated_at_local.strftime(METAR_TIME_FORMAT)
    return f"{location_query.upper()}\n{valid}LT ({obtained}LT)"
