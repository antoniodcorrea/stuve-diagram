from src.sounding.constants import TARGET_HOUR_LOCAL
from src.sounding.select_target_hour import select_target_hour


def _full_day(date):
    return [f"{date}T{hour:02d}:00" for hour in range(24)]


def _two_days(first, second):
    return _full_day(first) + _full_day(second)


def test_selects_the_target_hour_when_present():
    times = _full_day("2026-06-06")
    index, forecast_time = select_target_hour(times)
    assert forecast_time == f"2026-06-06T{TARGET_HOUR_LOCAL:02d}:00"
    assert times[index] == forecast_time


def test_returns_none_when_the_target_hour_is_missing():
    times = [f"2026-06-06T{hour:02d}:00" for hour in range(TARGET_HOUR_LOCAL)]
    assert select_target_hour(times) is None


def test_uses_the_first_entry_as_today():
    times = _full_day("2026-12-31")
    _index, forecast_time = select_target_hour(times)
    assert forecast_time.startswith("2026-12-31")


def test_default_offset_selects_the_first_day():
    times = _two_days("2026-06-06", "2026-06-07")
    _index, forecast_time = select_target_hour(times)
    assert forecast_time.startswith("2026-06-06")


def test_offset_one_selects_the_next_day():
    times = _two_days("2026-06-06", "2026-06-07")
    index, forecast_time = select_target_hour(times, day_offset=1)
    assert forecast_time == f"2026-06-07T{TARGET_HOUR_LOCAL:02d}:00"
    assert times[index] == forecast_time


def test_offset_crosses_month_boundary():
    times = _two_days("2026-06-30", "2026-07-01")
    _index, forecast_time = select_target_hour(times, day_offset=1)
    assert forecast_time.startswith("2026-07-01")
