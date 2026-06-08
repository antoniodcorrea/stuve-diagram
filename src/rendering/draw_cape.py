"""Shade the CAPE area: the positive-buoyancy region between the level of free
convection and the equilibrium level, where the Tmax parcel is warmer than the
environment. Drawn as hatching behind the temperature and parcel curves."""

import numpy as np
import matplotlib as mpl

from src.rendering.constants import (
    CAPE_FILL,
    CAPE_HATCH,
    CAPE_HATCH_COLOR,
    CAPE_HATCH_LINEWIDTH,
)


def draw_cape(ax, indices, sounding, projection):
    lfc = indices["lfc_pressure"]
    el = indices["el_pressure"]
    if lfc is None or el is None:
        return

    profile = indices["parcel_profile"]
    pressures = profile["pressures"]
    band = (pressures <= lfc) & (pressures >= el)
    if not band.any():
        return

    band_pressures = pressures[band]
    parcel_temperature = profile["temperature"][band]
    order = sounding.pressure.argsort()
    environment_temperature = np.interp(
        band_pressures, sounding.pressure.values[order], sounding.temperature.values[order])

    parcel_x, parcel_y = projection.to_xy(parcel_temperature, band_pressures)
    environment_x, environment_y = projection.to_xy(environment_temperature, band_pressures)
    polygon_x = np.concatenate([parcel_x, environment_x[::-1]])
    polygon_y = np.concatenate([parcel_y, environment_y[::-1]])

    # Hatch colour follows the edge colour in matplotlib; draw no visible outline.
    with mpl.rc_context({"hatch.color": CAPE_HATCH_COLOR,
                         "hatch.linewidth": CAPE_HATCH_LINEWIDTH}):
        ax.fill(polygon_x, polygon_y, facecolor=CAPE_FILL, edgecolor="none",
                hatch=CAPE_HATCH, zorder=2)
