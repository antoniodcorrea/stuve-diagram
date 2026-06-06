"""Resolve a free-form location query to coordinates via Nominatim (OSM)."""

import json
import urllib.parse
import urllib.request

from src.sounding.constants import (
    GEOCODER_TIMEOUT_SECONDS,
    GEOCODER_URL,
    GEOCODER_USER_AGENT,
)


def geocode(location_query):
    """Return (latitude, longitude) for a free-form place query."""
    query = urllib.parse.urlencode({"q": location_query, "format": "json", "limit": 1})
    request = urllib.request.Request(f"{GEOCODER_URL}?{query}",
                                     headers={"User-Agent": GEOCODER_USER_AGENT})
    with urllib.request.urlopen(request, timeout=GEOCODER_TIMEOUT_SECONDS) as response:
        results = json.load(response)
    if not results:
        raise ValueError(f"No geocoding result for {location_query!r}")
    return float(results[0]["lat"]), float(results[0]["lon"])
