import contextlib
import io
import json
import urllib.parse

from src.sounding import fetch_open_meteo as fetch_module
from src.sounding.fetch_open_meteo import fetch_open_meteo


def _patch_urlopen(monkeypatch, payload, captured):
    @contextlib.contextmanager
    def fake(url, timeout=None):
        captured["url"] = url
        yield io.BytesIO(json.dumps(payload).encode())

    monkeypatch.setattr(fetch_module.urllib.request, "urlopen", fake)


def test_returns_parsed_json(monkeypatch):
    captured = {}
    _patch_urlopen(monkeypatch, {"hourly": {"time": []}}, captured)
    assert fetch_open_meteo(40.0, -3.0) == {"hourly": {"time": []}}


def test_request_includes_coordinates_and_surface_variables(monkeypatch):
    captured = {}
    _patch_urlopen(monkeypatch, {}, captured)
    fetch_open_meteo(40.0, -3.0)
    query = urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)
    assert query["latitude"] == ["40.0"]
    assert query["longitude"] == ["-3.0"]
    assert "surface_pressure" in query["hourly"][0]


def test_request_pairs_each_variable_with_each_level(monkeypatch):
    captured = {}
    _patch_urlopen(monkeypatch, {}, captured)
    fetch_open_meteo(40.0, -3.0)
    query = urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)
    assert "temperature_850hPa" in query["hourly"][0]
    assert "wind_direction_500hPa" in query["hourly"][0]


def test_request_includes_the_daily_max_temperature(monkeypatch):
    captured = {}
    _patch_urlopen(monkeypatch, {}, captured)
    fetch_open_meteo(40.0, -3.0)
    query = urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)
    assert "temperature_2m_max" in query["daily"][0]
