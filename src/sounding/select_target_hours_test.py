from src.sounding.constants import TARGET_HOURS_LOCAL
from src.sounding.select_target_hours import select_target_hours


def _full_day(date):
    return [f"{date}T{hour:02d}:00" for hour in range(24)]


def _two_days(first, second):
    return _full_day(first) + _full_day(second)


def test_selects_all_target_hours_when_present():
    times = _full_day("2026-06-06")
    selected = select_target_hours(times)
    assert [hour for _, hour in selected] == [
        f"2026-06-06T{h:02d}:00" for h in TARGET_HOURS_LOCAL]


def test_indices_point_back_into_the_time_array():
    times = _full_day("2026-06-06")
    for index, forecast_time in select_target_hours(times):
        assert times[index] == forecast_time


def test_skips_hours_missing_from_the_forecast():
    # Drop everything from 14:00 onward so only the earlier targets remain.
    times = [f"2026-06-06T{hour:02d}:00" for hour in range(14)]
    selected = [hour for _, hour in select_target_hours(times)]
    assert selected == [
        f"2026-06-06T{h:02d}:00" for h in TARGET_HOURS_LOCAL if h < 14]


def test_uses_the_first_entry_as_today():
    # First entry's date is the day used to build the target timestamps.
    times = _full_day("2026-12-31")
    selected = [hour for _, hour in select_target_hours(times)]
    assert all(hour.startswith("2026-12-31") for hour in selected)


def test_default_offset_selects_the_first_day():
    times = _two_days("2026-06-06", "2026-06-07")
    selected = [hour for _, hour in select_target_hours(times)]
    assert all(hour.startswith("2026-06-06") for hour in selected)


def test_offset_one_selects_the_next_day():
    times = _two_days("2026-06-06", "2026-06-07")
    selected = [hour for _, hour in select_target_hours(times, day_offset=1)]
    assert [hour for hour in selected] == [
        f"2026-06-07T{h:02d}:00" for h in TARGET_HOURS_LOCAL]


def test_offset_crosses_month_boundary():
    times = _two_days("2026-06-30", "2026-07-01")
    selected = [hour for _, hour in select_target_hours(times, day_offset=1)]
    assert all(hour.startswith("2026-07-01") for hour in selected)


def test_indices_point_into_the_array_for_tomorrow():
    times = _two_days("2026-06-06", "2026-06-07")
    for index, forecast_time in select_target_hours(times, day_offset=1):
        assert times[index] == forecast_time
