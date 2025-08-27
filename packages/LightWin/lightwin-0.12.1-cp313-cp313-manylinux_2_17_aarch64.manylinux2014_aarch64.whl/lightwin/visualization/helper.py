"""Define types and helpers for the visualization library."""

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure, SubFigure

X_AXIS_T = Literal["z_abs", "elt_idx"]


def create_fig_if_not_exists(
    axnum: int | list[int] | range,
    sharex: bool = False,
    num: int = 1,
    clean_fig: bool = False,
    **kwargs,
) -> tuple[Figure, list[Axes]]:
    """
    Check if figures were already created, create it if not.

    Parameters
    ----------
    axnum :
        Axes indexes as understood by ``Figure.add_subplot``, or number of
        desired axes.
    sharex :
        If x axis should be shared.
    num :
        Fig number.
    clean_fig :
        If the previous plot should be erased from Figure.

    """
    if isinstance(axnum, int):
        # We make a one-column, `axnum` rows figure
        axnum = range(100 * axnum + 11, 101 * axnum + 11)

    if plt.fignum_exists(num):
        fig = plt.figure(num)
        axlist = fig.get_axes()
        if clean_fig:
            clean_figures([num])
        return fig, axlist

    fig = plt.figure(num)
    axlist = [fig.add_subplot(axnum[0])]
    shared_ax = None
    if sharex:
        shared_ax = axlist[0]
    axlist += [fig.add_subplot(num, sharex=shared_ax) for num in axnum[1:]]
    return fig, axlist


def clean_figures(fig_ids: Sequence[int | str | Figure | SubFigure]) -> None:
    """Clean axis of Figs in fignumlist."""
    for fig_id in fig_ids:
        fig = plt.figure(fig_id)
        clean_axes(fig.get_axes())


def clean_axes(ax_ids: Sequence[Axes]) -> None:
    """Clean given axis."""
    for ax in ax_ids:
        ax.cla()


def remove_artists(axe: Axes) -> None:
    """Remove lines and plots, but keep labels and grids."""
    for artist in axe.lines:
        artist.remove()
    axe.set_prop_cycle(None)  # type: ignore


def savefig(fig: Figure, filepath: Path) -> None:
    """Save the figure."""
    fig.set_size_inches(25.6, 13.64)
    fig.tight_layout()
    fig.savefig(filepath)
    logging.debug(f"Fig. saved in {filepath}")
