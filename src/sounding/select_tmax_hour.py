"""Select the hour of the day's warmest 2 m temperature from the forecast."""

from datetime import date, timedelta


def select_tmax_hour(forecast_times, temperatures, day_offset=0):
    """Return the hour index of the warmest 2 m temperature on the target day.

    `forecast_times` are the local ISO timestamps and `temperatures` the matching
    2 m temperatures; `day_offset` picks the day (0 = today, 1 = tomorrow). Returns
    None if the target day is absent from the forecast.
    """
    first_day = date.fromisoformat(forecast_times[0][:10])
    target_day = (first_day + timedelta(days=day_offset)).isoformat()
    day_indices = [i for i, time in enumerate(forecast_times) if time.startswith(target_day)]
    if not day_indices:
        return None
    return max(day_indices, key=lambda i: temperatures[i])
