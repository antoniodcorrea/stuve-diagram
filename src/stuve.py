"""Render Stüve diagrams from the Open-Meteo forecast.

A Stüve diagram plots temperature on a linear x-axis and pressure on the
y-axis scaled as p**(R/cp). That scaling makes the dry adiabats straight
lines, which is the defining feature of the diagram.

One diagram is produced per target hour of the current day (skipping any
already past at run time).

Usage:
    python -m src.stuve --location "Place name" [--today | --tomorrow]
"""

import argparse
import os
from datetime import datetime, timedelta, timezone

from src.config.constants import OUTPUT_DIR
from src.config.matplotlib_style import apply_font_style
from src.rendering.build_subtitle import build_subtitle
from src.rendering.render_diagram import render_diagram
from src.sounding.fetch_open_meteo import fetch_open_meteo
from src.sounding.geocode import geocode
from src.sounding.select_target_hours import select_target_hours
from src.helpers.slugify import slugify
from src.sounding.sounding_from_forecast import sounding_from_forecast


def parse_args():
    parser = argparse.ArgumentParser(description="Render Stüve diagrams.")
    parser.add_argument("--location", required=True,
                        help="place to forecast, resolved by the geocoder")
    day = parser.add_mutually_exclusive_group()
    day.add_argument("--today", dest="day_offset", action="store_const", const=0,
                     default=0, help="render today's diagrams (default)")
    day.add_argument("--tomorrow", dest="day_offset", action="store_const", const=1,
                     help="render tomorrow's diagrams")
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    apply_font_style()
    latitude, longitude = geocode(args.location)
    forecast = fetch_open_meteo(latitude, longitude)
    hourly = forecast["hourly"]
    target_hours = select_target_hours(hourly["time"], args.day_offset)

    if not target_hours:
        print("No target hours available for the requested day.")
        return

    location_timezone = timezone(timedelta(seconds=forecast["utc_offset_seconds"]))
    generated_at_local = datetime.now(location_timezone)
    location_slug = slugify(args.location)

    for hour_index, forecast_time in target_hours:
        sounding = sounding_from_forecast(forecast, hour_index)
        date = forecast_time[:10]
        metar_time = forecast_time[11:16].replace(":", "")
        subtitle = build_subtitle(args.location, forecast_time, generated_at_local)
        output_path = os.path.join(
            OUTPUT_DIR, f"stuve-{location_slug}-{date}-{metar_time}LT.png")
        render_diagram(sounding, subtitle, output_path)
        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
