"""Shared presentation settings for GPAP² analytical figures."""

from __future__ import annotations

from collections.abc import Mapping

import matplotlib as mpl

PROFILE_COLOURS: Mapping[int, str] = {
    1: "#0072B2",
    2: "#E69F00",
    3: "#009E73",
}

SUPPORT_COLOURS: Mapping[str, str] = {
    "DESCRIPTIVELY_SUPPORTED": "#0072B2",
    "ASSOCIATIVELY_EXAMINABLE": "#009E73",
    "PARTIALLY_SUPPORTABLE_WITH_MAJOR_QUALIFICATION": "#E69F00",
    "NOT_SUPPORTABLE_WITH_CURRENT_PUBLIC_DATA": "#767676",
}

INK = "#202124"
MUTED = "#5F6368"
GRID = "#D9D9D9"


def apply_figure_style() -> None:
    """Apply restrained, accessible defaults without changing analytical values."""

    mpl.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": GRID,
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "axes.titlesize": 13,
            "axes.titleweight": "normal",
            "axes.grid": False,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "legend.frameon": False,
            "savefig.facecolor": "white",
            "text.color": INK,
            "xtick.color": INK,
            "ytick.color": INK,
        }
    )


def finish_axis(axis: mpl.axes.Axes, *, grid_axis: str | None = None) -> None:
    """Remove visual clutter and optionally add a light reference grid."""

    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color(GRID)
    if grid_axis:
        axis.grid(axis=grid_axis, color=GRID, linewidth=0.7, alpha=0.8)
        axis.set_axisbelow(True)
