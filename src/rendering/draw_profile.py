"""Draw the temperature and dew-point profiles plus the ground-level line."""

from src.thermodynamics.pressure_coordinate import pressure_to_axis


def draw_profile(ax, sounding):
    ax.plot(sounding.temperature, pressure_to_axis(sounding.pressure),
            color="black", lw=1.0, label="Temperature", zorder=5)
    ax.plot(sounding.dew_point, pressure_to_axis(sounding.pressure),
            color="black", lw=1.0, ls=":", label="Dew point", zorder=5)

    # Ground level: the highest measured pressure
    ground_pressure = sounding.pressure.max()
    ax.axhline(pressure_to_axis(ground_pressure), color="black", lw=0.3, zorder=4)
