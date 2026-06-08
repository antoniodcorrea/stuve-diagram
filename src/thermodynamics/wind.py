"""Wind derivatives for soaring: the boundary-layer mean wind (thermal drift)
and the bulk shear through the lower troposphere.

Direction is the bearing the wind comes from (meteorological), so the u/v
components point where it blows toward, matching the wind-barb drawing.
"""

import numpy as np

BULK_SHEAR_DEPTH_M = 6000.0


def wind_components(direction_degrees, speed):
    """u, v (eastward, northward) for a meteorological direction and speed."""
    direction_radians = np.deg2rad(np.asarray(direction_degrees, dtype=float))
    speed = np.asarray(speed, dtype=float)
    return -speed * np.sin(direction_radians), -speed * np.cos(direction_radians)


def _direction_and_speed(u, v):
    direction = (np.degrees(np.arctan2(-u, -v)) + 360.0) % 360.0
    return float(direction), float(np.hypot(u, v))


def mean_layer_wind(sounding, top_pressure):
    """Mean wind (direction °, speed) over the surface-to-`top_pressure` layer."""
    surface_pressure = sounding.pressure.max()
    layer = sounding[(sounding.pressure <= surface_pressure) & (sounding.pressure >= top_pressure)]
    u, v = wind_components(layer.wind_direction.to_numpy(), layer.wind_speed.to_numpy())
    return _direction_and_speed(u.mean(), v.mean())


def bulk_shear(sounding, depth_m=BULK_SHEAR_DEPTH_M):
    """Magnitude (m/s) of the wind difference across `depth_m` above the surface."""
    altitude = sounding.altitude.to_numpy()
    u, v = wind_components(sounding.wind_direction.to_numpy(), sounding.wind_speed.to_numpy())
    order = np.argsort(altitude)
    bottom_altitude = altitude.min()
    top_altitude = bottom_altitude + depth_m
    u_shear = np.interp(top_altitude, altitude[order], u[order]) - u[order][0]
    v_shear = np.interp(top_altitude, altitude[order], v[order]) - v[order][0]
    return float(np.hypot(u_shear, v_shear))
