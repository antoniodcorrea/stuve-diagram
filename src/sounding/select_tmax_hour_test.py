from src.sounding.select_tmax_hour import select_tmax_hour


def _day(date, temperatures):
    times = [f"{date}T{hour:02d}:00" for hour in range(24)]
    return times, temperatures


def test_returns_the_hour_of_the_daily_maximum():
    temps = [10 + (h if h <= 15 else 30 - h) for h in range(24)]  # peaks at 15:00
    times, temperatures = _day("2026-06-06", temps)
    assert select_tmax_hour(times, temperatures) == 15


def test_restricts_to_the_target_day():
    day0 = [f"2026-06-06T{h:02d}:00" for h in range(24)]
    day1 = [f"2026-06-07T{h:02d}:00" for h in range(24)]
    times = day0 + day1
    temperatures = [0] * 24 + [h if h != 17 else 99 for h in range(24)]  # day1 peaks at 17:00
    assert select_tmax_hour(times, temperatures, day_offset=1) == 24 + 17


def test_returns_none_when_the_day_is_absent():
    times = [f"2026-06-06T{h:02d}:00" for h in range(24)]
    assert select_tmax_hour(times, list(range(24)), day_offset=1) is None
