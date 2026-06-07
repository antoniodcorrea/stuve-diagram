"""Draw the temperature and dew-point profiles plus the ground-level line."""


def draw_profile(ax, sounding, projection):
    temperature_x, temperature_y = projection.to_xy(sounding.temperature, sounding.pressure)
    ax.plot(temperature_x, temperature_y,
            color="black", lw=1.0, label="Temperature", zorder=5)
    dew_point_x, dew_point_y = projection.to_xy(sounding.dew_point, sounding.pressure)
    ax.plot(dew_point_x, dew_point_y,
            color="black", lw=1.0, ls=":", label="Dew point", zorder=5)

    # Ground level: the highest measured pressure
    ground_pressure = sounding.pressure.max()
    ax.axhline(projection.pressure_to_y(ground_pressure), color="black", lw=0.3, zorder=4)
