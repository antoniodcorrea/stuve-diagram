"""A concise glossary of the panel acronyms and entries, drawn below the diagram
in the panel's monospace font, laid out in three columns."""

from src.rendering.constants import (
    GLOSSARY_COLUMN_X,
    GLOSSARY_TERM_WIDTH,
    GLOSSARY_TOP_GAP_POINTS,
    PANEL_FONT_SIZE,
    PANEL_LINESPACING,
)

# [(term, definition), ...] per column.
_GLOSSARY = [
    [
        ("Trigger T", "Temp that triggers thermals"),
        ("Working bd", "Usable thermal-layer depth"),
        ("Lapse rate", "Mixed-layer gradient °C/km"),
        ("Max Th Str", "Est. peak climb rate"),
        ("Cloud base", "Cumulus base height"),
        ("Cloud top", "Cumulus top height"),
    ],
    [
        ("EL", "Equilibrium level"),
        ("Freezing", "0 °C isotherm"),
        ("LFC", "Level of free convection"),
        ("CCL", "Convective condensation level"),
        ("LCL", "Lifting condensation level"),
        ("TI 850/700", "Thermal index at 850/700"),
    ],
    [
        ("CAPE", "Avail. potential energy"),
        ("CIN", "Convective inhibition"),
        ("Lifted idx", "Lifted index (neg unstable)"),
        ("Showalter", "Showalter index"),
        ("K-index", "K index"),
        ("Total Tot.", "Total Totals index"),
    ],
]


def _column_text(entries):
    return "\n".join(f"{term:<{GLOSSARY_TERM_WIDTH}}{definition}" for term, definition in entries)


def draw_glossary(ax):
    for x, entries in zip(GLOSSARY_COLUMN_X, _GLOSSARY):
        ax.annotate(_column_text(entries), xy=(x, 0), xycoords="axes fraction",
                    xytext=(0, -GLOSSARY_TOP_GAP_POINTS), textcoords="offset points",
                    ha="left", va="top", family="monospace", fontsize=PANEL_FONT_SIZE,
                    linespacing=PANEL_LINESPACING, annotation_clip=False, color="black")
