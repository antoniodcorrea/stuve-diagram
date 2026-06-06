<p align="center">
  <img src="./img/logo.png" alt="Stüve diagram logo" width="200">
</p>

# Stüve diagram

Generates [Stüve diagrams](https://en.wikipedia.org/wiki/St%C3%BCve_diagram) for a given location using [Open-Meteo](https://open-meteo.com/)
pressure-level forecast. 
Aimed at soaring flight planning.

## Example

![Stüve diagram](./examples/stuve-flugplatz-speck-fehraltorf-2026-06-06-0800LT.png)

## What it does

For a given location, on each run it:

- Geocodes the location name (Nominatim / OpenStreetMap) into coordinates.
- Fetches the Open-Meteo GFS forecast (temperature, humidity, geopotential height and wind at every pressure level, plus the surface).
- Renders one diagram per target hour (08, 10, 12, 14, 16, 18, 20 local time) of the chosen day — today by default, or tomorrow with `--tomorrow` — each with temperature and dew-point profiles, wind barbs (with speeds in kt and m/s), altitude scales in metres and feet, and the adiabat / mixing-ratio background.

Diagrams are written to `./output/` as `stuve-<location>-<date>-<HHMM>LT.png`.

## Requirements

- Python 3.7+
- `matplotlib`, `pandas`, `numpy`
- Internet access (Nominatim + Open-Meteo)

```bash
pip install matplotlib pandas numpy
```

## Usage

```bash
make LOCATION="Flugplatz Speck-Fehraltorf" today
make LOCATION="Flugplatz Speck-Fehraltorf" tomorrow
```

## Configuration

The location is required and passed on the command line:

```bash
python -m src.stuve --location "Flugplatz Speck-Fehraltorf"
```

Other settings live in `src/config/constants.py` (plot bounds, figure size,
output directory).

Other domain constants:

- `src/sounding/constants.py` — `TARGET_HOURS_LOCAL`, Open-Meteo model/levels, geocoder.
- `src/rendering/constants.py` — styling (fonts, barbs, labels, title).
- `src/thermodynamics/constants.py` — physical constants and grid sampling.

## Project structure

```
src/
  stuve.py                Entry point: orchestrates the pipeline
  config/                 Shared diagram bounds, app configuration, font style
  sounding/               Data sources: geocode, fetch Open-Meteo, build sounding,
                          select target hours
  thermodynamics/         Pressure coordinate, dew point, adiabatic field grid
  rendering/              Background, profiles, altitude labels, wind barbs,
                          axes, subtitle, and the diagram compositor
  helpers/                Cross-cutting utilities (e.g. filename-safe slugs)
```

Pipeline: `geocode → fetch → select target hours → build sounding → render`
(the adiabatic field grid is computed inside the background drawing).

## Testing

Co-located unit tests (`*_test.py`) next to the code they cover:

```bash
make test
```
