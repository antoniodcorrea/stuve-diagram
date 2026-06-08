"""Render Stüve diagrams from the Open-Meteo forecast.

A Stüve diagram plots temperature on a linear x-axis and pressure on the
y-axis scaled as p**(R/cp). That scaling makes the dry adiabats straight
lines, which is the defining feature of the diagram.

One diagram is produced for the morning sounding hour, overlaid with the Tmax
parcel ascent (thermal top and cloud base) for soaring flight planning.

Usage:
    python -m src.stuve --location "Place name" [--today | --tomorrow]
"""

import argparse
import os
from datetime import datetime, timedelta, timezone

from src.config.constants import OUTPUT_DIR
from src.config.matplotlib_style import apply_font_style
from src.rendering.build_subtitle import build_subtitle
from src.rendering.projection import PROJECTIONS
from src.rendering.render_diagram import render_diagram
from src.sounding.fetch_open_meteo import fetch_open_meteo
from src.sounding.geocode import geocode
from src.sounding.select_target_hour import select_target_hour
from src.sounding.select_tmax_hour import select_tmax_hour
from src.helpers.slugify import slugify
from src.sounding.sounding_from_forecast import sounding_from_forecast
from src.thermodynamics.indices import compute_indices
from src.thermodynamics.parcel import parcel_ascent
from src.thermodynamics.wind import bulk_shear, mean_layer_wind


def parse_args():
    parser = argparse.ArgumentParser(description="Render Stüve diagrams.")
    parser.add_argument("--location", required=True,
                        help="place to forecast, resolved by the geocoder")
    day = parser.add_mutually_exclusive_group()
    day.add_argument("--today", dest="day_offset", action="store_const", const=0,
                     default=0, help="render today's diagram (default)")
    day.add_argument("--tomorrow", dest="day_offset", action="store_const", const=1,
                     help="render tomorrow's diagram")
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    apply_font_style()
    latitude, longitude = geocode(args.location)
    forecast = fetch_open_meteo(latitude, longitude)
    hourly = forecast["hourly"]
    target = select_target_hour(hourly["time"], args.day_offset)

    if target is None:
        print("Target hour not available for the requested day.")
        return
    hour_index, forecast_time = target

    location_timezone = timezone(timedelta(seconds=forecast["utc_offset_seconds"]))
    generated_at_local = datetime.now(location_timezone)
    location_slug = slugify(args.location)

    sounding = sounding_from_forecast(forecast, hour_index)
    surface = sounding.iloc[0]
    max_temperature = forecast["daily"]["temperature_2m_max"][args.day_offset]
    parcel = parcel_ascent(surface.pressure, max_temperature, surface.dew_point,
                           sounding.pressure.values, sounding.temperature.values)

    indices = compute_indices(sounding, parcel, max_temperature)
    thermal_top = parcel["thermal_top_pressure"] or sounding.pressure.min()
    indices["mean_wind_direction"], indices["mean_wind_speed"] = mean_layer_wind(
        sounding, thermal_top)
    indices["bulk_shear"] = bulk_shear(sounding)

    # Overlay the temperature line at the hour of Tmax (peak heating), unless that
    # is the hour already being rendered.
    tmax_index = select_tmax_hour(hourly["time"], hourly["temperature_2m"], args.day_offset)
    overlay_sounding = (sounding_from_forecast(forecast, tmax_index)
                        if tmax_index is not None and tmax_index != hour_index else None)

    date = forecast_time[:10]
    metar_time = forecast_time[11:16].replace(":", "")
    subtitle = build_subtitle(args.location, forecast_time, generated_at_local)

    for projection in PROJECTIONS:
        output_path = os.path.join(
            OUTPUT_DIR, f"{location_slug}-{date}-{metar_time}LT-{projection.slug}.png")
        render_diagram(sounding, parcel, indices, overlay_sounding, subtitle,
                       output_path, projection)
        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
