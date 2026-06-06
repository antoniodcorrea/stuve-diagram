import contextlib
import io
import json

import pytest

from src.sounding import geocode as geocode_module
from src.sounding.geocode import geocode


def _patch_urlopen(monkeypatch, payload):
    @contextlib.contextmanager
    def fake(request, timeout=None):
        yield io.BytesIO(json.dumps(payload).encode())

    monkeypatch.setattr(geocode_module.urllib.request, "urlopen", fake)


def test_returns_lat_lon_as_floats(monkeypatch):
    _patch_urlopen(monkeypatch, [{"lat": "40.4168", "lon": "-3.7038"}])
    assert geocode("Madrid") == (40.4168, -3.7038)


def test_raises_when_no_results(monkeypatch):
    _patch_urlopen(monkeypatch, [])
    with pytest.raises(ValueError):
        geocode("Nowhere at all")


def test_uses_first_result(monkeypatch):
    _patch_urlopen(monkeypatch, [
        {"lat": "1.0", "lon": "2.0"},
        {"lat": "9.0", "lon": "9.0"},
    ])
    assert geocode("Anywhere") == (1.0, 2.0)
