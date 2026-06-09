"""Convective and stability indices derived from the sounding.

Everything here builds on the Tmax convective parcel (the forecast-max-temperature
ascent the whole diagram is about): CAPE/CIN and the level of free convection,
equilibrium level and cloud top come from lifting that parcel; the classic fixed-
level indices (K, Total Totals, Showalter, Lifted Index) and the soaring numbers
(convective temperature, thermal index, working band) come from the same sounding.

`compute_indices` is the single entry point: it returns a flat dict of scalars
for the panel plus the saturated parcel profile and key pressures for drawing.
"""

import numpy as np

from src.thermodynamics.column import first_crossing, interp_at
from src.thermodynamics.constants import (
    DRY_AIR_TO_WATER_VAPOUR_RATIO,
    GAS_CONSTANT_DRY_AIR,
    GRAVITY,
    KAPPA,
    THERMAL_UPDRAFT_EFFICIENCY,
    ZERO_CELSIUS_IN_KELVIN,
)
from src.thermodynamics.moist_parcel import moist_parcel_profile
from src.thermodynamics.saturation import (
    dew_point_from_vapour_pressure,
    mixing_ratio,
    saturation_vapour_pressure,
)

# Fixed levels (hPa) the classic stability indices are defined on.
LEVEL_850, LEVEL_700, LEVEL_500 = 850.0, 700.0, 500.0

# The column helpers, under the (pressures, values, target) argument order this
# module reads naturally; see src/thermodynamics/column.py for the implementation.
_at = interp_at
_first_crossing = first_crossing


def cape_cin(profile, environment_pressure, environment_temperature):
    """CAPE and CIN (J/kg) for the parcel, with the LFC and EL pressures.

    CAPE is the positive-buoyancy area between the level of free convection and
    the equilibrium level; CIN is the negative area below the LFC. Buoyancy uses
    plain temperature (no virtual-temperature correction).
    """
    pressures = profile["pressures"]
    buoyancy = profile["temperature"] - _at(environment_pressure, environment_temperature, pressures)

    log_pressure = np.log(pressures)
    layer_thickness = log_pressure[:-1] - log_pressure[1:]            # d(ln p) > 0 going up
    layer_buoyancy = (buoyancy[:-1] + buoyancy[1:]) / 2.0
    layer_energy = GAS_CONSTANT_DRY_AIR * layer_buoyancy * layer_thickness

    lcl = profile["lcl_pressure"]
    start = 0 if lcl is None else int(np.flatnonzero(pressures <= lcl)[0])
    positive = np.flatnonzero((buoyancy > 0) & (np.arange(pressures.size) >= start))
    if positive.size == 0:
        return {"cape": 0.0, "cin": 0.0, "lfc_pressure": None, "el_pressure": None}

    lfc_index = int(positive[0])
    after = np.flatnonzero((buoyancy <= 0) & (np.arange(pressures.size) > lfc_index))
    el_index = int(after[0]) if after.size else pressures.size - 1

    cape = float(layer_energy[lfc_index:el_index].clip(min=0).sum())
    cin = float(layer_energy[:lfc_index].clip(max=0).sum())
    return {"cape": cape, "cin": cin,
            "lfc_pressure": float(pressures[lfc_index]),
            "el_pressure": float(pressures[el_index])}


def lifted_index(profile, environment_pressure, environment_temperature):
    """Lifted Index (°C): environment minus the parcel temperature at 500 hPa."""
    if environment_pressure[0] <= LEVEL_500:
        return None
    parcel_500 = _at(profile["pressures"], profile["temperature"], LEVEL_500)
    return float(_at(environment_pressure, environment_temperature, LEVEL_500) - parcel_500)


def showalter_index(environment_pressure, environment_temperature, environment_dew_point):
    """Showalter Index (°C): a parcel lifted from 850 hPa, evaluated at 500 hPa."""
    if environment_pressure[0] <= LEVEL_850:
        return None
    temperature_850 = float(_at(environment_pressure, environment_temperature, LEVEL_850))
    dew_point_850 = float(_at(environment_pressure, environment_dew_point, LEVEL_850))
    lifted = moist_parcel_profile(LEVEL_850, temperature_850, dew_point_850)
    parcel_500 = _at(lifted["pressures"], lifted["temperature"], LEVEL_500)
    return float(_at(environment_pressure, environment_temperature, LEVEL_500) - parcel_500)


def k_index(environment_pressure, environment_temperature, environment_dew_point):
    """K-Index (°C): mid-level lapse plus low-level moisture and 700 hPa dryness."""
    if environment_pressure[0] <= LEVEL_850:
        return None
    t850, t700, t500 = _at(environment_pressure, environment_temperature,
                           [LEVEL_850, LEVEL_700, LEVEL_500])
    td850, td700 = _at(environment_pressure, environment_dew_point, [LEVEL_850, LEVEL_700])
    return float((t850 - t500) + td850 - (t700 - td700))


def total_totals(environment_pressure, environment_temperature, environment_dew_point):
    """Total Totals Index (°C): vertical totals plus cross totals."""
    if environment_pressure[0] <= LEVEL_850:
        return None
    t850, t500 = _at(environment_pressure, environment_temperature, [LEVEL_850, LEVEL_500])
    td850 = float(_at(environment_pressure, environment_dew_point, LEVEL_850))
    return float((t850 - t500) + (td850 - t500))


def convective_temperature(surface_pressure, surface_dew_point,
                           environment_pressure, environment_temperature):
    """Convective (trigger) temperature (°C) and its condensation level (CCL hPa).

    The CCL is where the surface mixing-ratio line meets the environment
    temperature; the trigger temperature is the dry adiabat from the CCL brought
    back down to the surface. Returns (temperature, ccl_pressure), both None if
    the surface air never reaches saturation within the column.
    """
    pressures = np.asarray(environment_pressure, dtype=float)
    surface_ratio = mixing_ratio(saturation_vapour_pressure(surface_dew_point), surface_pressure)
    vapour_pressure = surface_ratio * pressures / (DRY_AIR_TO_WATER_VAPOUR_RATIO + surface_ratio)
    mixing_line_dew_point = dew_point_from_vapour_pressure(vapour_pressure)

    ccl_pressure = _first_crossing(pressures,
                                   np.asarray(environment_temperature) - mixing_line_dew_point)
    if ccl_pressure is None:
        return None, None

    ccl_temperature = float(_at(pressures, environment_temperature, ccl_pressure))
    trigger_kelvin = ((ccl_temperature + ZERO_CELSIUS_IN_KELVIN)
                      * (surface_pressure / ccl_pressure) ** KAPPA)
    return trigger_kelvin - ZERO_CELSIUS_IN_KELVIN, ccl_pressure


def thermal_index(profile, environment_pressure, environment_temperature, level):
    """Thermal Index (°C) at a pressure level: environment minus Tmax parcel.

    Negative means the parcel is warmer than its surroundings there: usable lift.
    Returns None if the level is below ground.
    """
    if environment_pressure[0] <= level:
        return None
    parcel = _at(profile["pressures"], profile["temperature"], level)
    return float(_at(environment_pressure, environment_temperature, level) - parcel)


def isotherm_level(environment_pressure, environment_temperature, environment_altitude,
                   isotherm_celsius):
    """Pressure (hPa) and altitude (m) where the environment first reaches
    `isotherm_celsius` going up, or (None, None) if it never does."""
    difference = np.asarray(environment_temperature, dtype=float) - isotherm_celsius
    pressure = _first_crossing(environment_pressure, difference)
    if pressure is None:
        return None, None
    return pressure, float(_at(environment_pressure, environment_altitude, pressure))


def freezing_level(environment_pressure, environment_temperature, environment_altitude):
    """Pressure (hPa) and altitude (m) of the 0 °C isotherm, or (None, None)."""
    return isotherm_level(environment_pressure, environment_temperature, environment_altitude, 0.0)


def mixing_layer_lapse_rate(environment_pressure, environment_temperature,
                            environment_altitude, thermal_top_pressure):
    """Real environment lapse rate (°C/km) over the mixed layer, surface to the
    thermal top. The stronger this is, the more buoyant the dry thermals."""
    if thermal_top_pressure is None:
        return None
    surface_temperature = float(np.asarray(environment_temperature, dtype=float)[0])
    surface_altitude = float(np.asarray(environment_altitude, dtype=float)[0])
    top_temperature = float(_at(environment_pressure, environment_temperature, thermal_top_pressure))
    top_altitude = float(_at(environment_pressure, environment_altitude, thermal_top_pressure))
    depth = top_altitude - surface_altitude
    if depth <= 0:
        return None
    return (surface_temperature - top_temperature) / depth * 1000.0


def thermal_strength(parcel, environment_pressure, environment_temperature, environment_altitude):
    """Estimated thermal climb rate (m/s) and the parcel's peak temperature excess
    (°C) over the environment within the working band.

    Integrates the dry buoyant energy the Tmax parcel releases between the surface
    and the thermal top, then converts it to a climb speed with the efficiency
    factor. Returns (None, None) when there is no thermal top (no working band).
    """
    pressures = parcel.get("pressures")
    thermal_top = parcel.get("thermal_top_pressure")
    if pressures is None or thermal_top is None:
        return None, None
    band = pressures >= thermal_top
    if band.sum() < 2:
        return None, None

    band_pressures = pressures[band]
    parcel_temperature = parcel["temperature"][band]
    environment_at_band = _at(environment_pressure, environment_temperature, band_pressures)
    altitude_at_band = _at(environment_pressure, environment_altitude, band_pressures)

    excess = parcel_temperature - environment_at_band
    buoyancy = GRAVITY * np.clip(excess, 0.0, None) / (environment_at_band + ZERO_CELSIUS_IN_KELVIN)
    order = np.argsort(altitude_at_band)
    energy = float(np.trapezoid(buoyancy[order], altitude_at_band[order]))
    speed = THERMAL_UPDRAFT_EFFICIENCY * float(np.sqrt(2.0 * max(energy, 0.0)))
    return speed, float(np.max(excess))


def compute_indices(sounding, parcel, max_temperature, tmax_sounding=None):
    """All the panel scalars plus the saturated Tmax parcel and its key levels.

    `parcel` is the dry Tmax ascent from `parcel_ascent` (reused for the thermal
    top and cloud base so the panel matches the drawn lines). `tmax_sounding` is
    the temperature profile at the hour of peak heating; the thermal strength is
    measured against it (the air the thermals actually rise through), falling back
    to the morning sounding when it is not available.
    """
    surface = sounding.iloc[0]
    pressure = sounding.pressure.values
    temperature = sounding.temperature.values
    dew_point = sounding.dew_point.values
    altitude = sounding.altitude.values

    profile = moist_parcel_profile(surface.pressure, max_temperature, surface.dew_point)
    energy = cape_cin(profile, pressure, temperature)
    trigger, ccl_pressure = convective_temperature(
        surface.pressure, surface.dew_point, pressure, temperature)
    freezing_pressure, freezing_altitude = freezing_level(pressure, temperature, altitude)

    thermal_top = parcel["thermal_top_pressure"]
    cloud_base = parcel["cloud_base_pressure"]
    surface_altitude = float(altitude[0])

    strength_sounding = sounding if tmax_sounding is None else tmax_sounding
    strength, excess = thermal_strength(parcel, strength_sounding.pressure.values,
                                        strength_sounding.temperature.values,
                                        strength_sounding.altitude.values)
    ccl_temperature = None if ccl_pressure is None else float(_at(pressure, temperature, ccl_pressure))

    def altitude_or_none(level_pressure):
        return None if level_pressure is None else _altitude_at(level_pressure, pressure, altitude)

    # Blue day: the condensation level sits above the thermal top, so the thermals
    # die before any cumulus form. Match the drawn diagram and report no cloud base.
    effective_thermal_top = thermal_top or profile["pressures"][-1]
    blue_day = cloud_base is None or cloud_base < effective_thermal_top

    return {
        "parcel_profile": profile,
        "cape": energy["cape"],
        "cin": energy["cin"],
        "lfc_pressure": energy["lfc_pressure"],
        "el_pressure": energy["el_pressure"],
        "lifted_index": lifted_index(profile, pressure, temperature),
        "showalter_index": showalter_index(pressure, temperature, dew_point),
        "k_index": k_index(pressure, temperature, dew_point),
        "total_totals": total_totals(pressure, temperature, dew_point),
        "trigger_temperature": trigger,
        "ccl_pressure": ccl_pressure,
        "ccl_temperature": ccl_temperature,
        "ccl_altitude": altitude_or_none(ccl_pressure),
        "lcl_pressure": profile["lcl_pressure"],
        "lcl_altitude": altitude_or_none(profile["lcl_pressure"]),
        "lfc_altitude": altitude_or_none(energy["lfc_pressure"]),
        "el_altitude": altitude_or_none(energy["el_pressure"]),
        "thermal_index_850": thermal_index(profile, pressure, temperature, LEVEL_850),
        "thermal_index_700": thermal_index(profile, pressure, temperature, LEVEL_700),
        "freezing_pressure": freezing_pressure,
        "freezing_altitude": freezing_altitude,
        "working_band_m": (_altitude_at(thermal_top, pressure, altitude) - surface_altitude
                           if thermal_top else None),
        "mixing_layer_lapse_rate": mixing_layer_lapse_rate(pressure, temperature, altitude, thermal_top),
        "thermal_strength_ms": strength,
        "thermal_excess_max": excess,
        "cloud_base_m": None if blue_day else _altitude_at(cloud_base, pressure, altitude),
        "cloud_top_m": None if blue_day or energy["el_pressure"] is None
        else _altitude_at(energy["el_pressure"], pressure, altitude),
    }


def _altitude_at(pressure, environment_pressure, environment_altitude):
    return float(_at(environment_pressure, environment_altitude, pressure))
