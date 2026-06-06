"""Select a day's target hours from the forecast time array."""

from datetime import date, timedelta

from src.sounding.constants import TARGET_HOURS_LOCAL


def select_target_hours(forecast_times, day_offset=0):
    """Return (hour_index, forecast_time) pairs for every target hour of a day.

    `forecast_times` are the local ISO timestamps from the forecast, whose first
    entry is today at 00:00. `day_offset` picks the day relative to that first
    entry (0 = today, 1 = tomorrow).
    """
    first_day = date.fromisoformat(forecast_times[0][:10])
    target_day = (first_day + timedelta(days=day_offset)).isoformat()
    selected = []
    for target_hour in TARGET_HOURS_LOCAL:
        forecast_time = f"{target_day}T{target_hour:02d}:00"
        if forecast_time in forecast_times:
            selected.append((forecast_times.index(forecast_time), forecast_time))
    return selected
