"""Apply the clean sans-serif font style used by the Stüve diagram."""

import matplotlib as mpl


def apply_font_style():
    # Futura everywhere, for a 1960s NASA look (with fallbacks).
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = ["Futura", "Futura Std", "Helvetica Neue", "DejaVu Sans"]
    mpl.rcParams["mathtext.fontset"] = "dejavusans"
    mpl.rcParams["axes.formatter.use_mathtext"] = True
