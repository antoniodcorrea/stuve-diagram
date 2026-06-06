from datetime import datetime

from src.rendering.build_subtitle import build_subtitle


def test_formats_location_and_metar_times():
    generated_at = datetime(2026, 6, 6, 7, 30)
    subtitle = build_subtitle(
        "Aeródromo de Fuentemilanos", "2026-06-06T12:00", generated_at)
    assert subtitle == "AERÓDROMO DE FUENTEMILANOS\n061200LT (060730LT)"


def test_uppercases_the_location():
    subtitle = build_subtitle("madrid", "2026-06-06T08:00", datetime(2026, 6, 6, 8, 0))
    assert subtitle.startswith("MADRID\n")


def test_valid_time_comes_from_forecast_time():
    subtitle = build_subtitle("x", "2026-06-15T18:00", datetime(2026, 6, 6, 6, 0))
    assert "151800LT" in subtitle
