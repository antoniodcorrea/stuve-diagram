"""Select the morning sounding hour from the forecast time array."""

from datetime import date, timedelta

from src.sounding.constants import TARGET_HOUR_LOCAL


def select_target_hour(forecast_times, day_offset=0, hour=TARGET_HOUR_LOCAL):
    """Return the (hour_index, forecast_time) of the target hour, or None.

    `forecast_times` are the local ISO timestamps from the forecast, whose first
    entry is today at 00:00. `day_offset` picks the day relative to that first
    entry (0 = today, 1 = tomorrow); `hour` is the local hour to render.
    """
    first_day = date.fromisoformat(forecast_times[0][:10])
    target_day = (first_day + timedelta(days=day_offset)).isoformat()
    forecast_time = f"{target_day}T{hour:02d}:00"
    if forecast_time in forecast_times:
        return forecast_times.index(forecast_time), forecast_time
    return None
