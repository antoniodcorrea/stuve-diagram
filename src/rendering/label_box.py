"""The shared translucent label box: a white, rounded-corner background, wider
horizontally than it is tall, used behind every on-diagram text label."""

from matplotlib.patches import BoxStyle
from matplotlib.path import Path

from src.rendering.constants import (
    LABEL_BOX_HORIZONTAL_PAD,
    LABEL_BOX_ROUNDING,
    PARCEL_LABEL_BOX_ALPHA,
    PARCEL_LABEL_BOX_PAD,
)


class _RoundedHorizontallyPadded(BoxStyle.Square):
    """A rounded box whose horizontal padding is wider than its vertical padding."""

    def __init__(self, pad=PARCEL_LABEL_BOX_PAD, horizontal_pad=LABEL_BOX_HORIZONTAL_PAD,
                 rounding=LABEL_BOX_ROUNDING):
        super().__init__(pad)
        self.horizontal_pad = horizontal_pad
        self.rounding = rounding

    def __call__(self, x0, y0, width, height, mutation_size):
        vertical = mutation_size * self.pad
        horizontal = mutation_size * self.horizontal_pad
        x0, y0 = x0 - horizontal, y0 - vertical
        x1, y1 = x0 + width + 2 * horizontal, y0 + height + 2 * vertical
        radius = min(mutation_size * self.rounding, (x1 - x0) / 2, (y1 - y0) / 2)

        vertices = [
            (x0 + radius, y0),
            (x1 - radius, y0), (x1, y0), (x1, y0 + radius),
            (x1, y1 - radius), (x1, y1), (x1 - radius, y1),
            (x0 + radius, y1), (x0, y1), (x0, y1 - radius),
            (x0, y0 + radius), (x0, y0), (x0 + radius, y0),
            (x0 + radius, y0),
        ]
        codes = [Path.MOVETO,
                 Path.LINETO, Path.CURVE3, Path.CURVE3,
                 Path.LINETO, Path.CURVE3, Path.CURVE3,
                 Path.LINETO, Path.CURVE3, Path.CURVE3,
                 Path.LINETO, Path.CURVE3, Path.CURVE3,
                 Path.CLOSEPOLY]
        return Path(vertices, codes)


def translucent_label_bbox():
    """bbox dict for an on-diagram label: white, translucent, rounded, h-padded."""
    return dict(boxstyle=_RoundedHorizontallyPadded(), facecolor="white",
                edgecolor="none", alpha=PARCEL_LABEL_BOX_ALPHA)
