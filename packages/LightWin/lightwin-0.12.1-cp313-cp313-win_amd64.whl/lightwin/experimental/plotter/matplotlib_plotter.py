"""Define a plotter that rely on the matplotlib library."""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pandas as pd
from matplotlib.axes import Axes

from lightwin.core.list_of_elements.list_of_elements import ListOfElements
from lightwin.experimental.plotter.i_plotter import IPlotter
from lightwin.experimental.plotter.matplotlib_helper import (
    create_fig_if_not_exists,
    plot_section,
    plot_structure,
)
from lightwin.util.dicts_output import markdown


class MatplotlibPlotter(IPlotter):
    """A plotter that takes in numpy arrays."""

    def __init__(self, elts: ListOfElements | None = None) -> None:
        """Instantiate some common attributes."""
        super().__init__(elts)

    def _setup_fig(self, fignum: int, title: str, **kwargs) -> list[Axes]:
        """Setup the figure and axes."""
        axnum = 2
        if not self._structure:
            axnum = 1
        return create_fig_if_not_exists(
            axnum,
            title=title,
            sharex=self._sharex,
            num=fignum,
            clean_fig=True,
            **kwargs,
        )

    def _actual_plot(
        self,
        data: pd.DataFrame,
        ylabel: str,
        axes: Sequence[Axes],
        axes_index: int,
        xlabel: str = markdown["z_abs"],
        **plot_kwargs: Any,
    ) -> Sequence[Axes]:
        """Create the plot itself."""
        data.plot(
            ax=axes[axes_index],
            sharex=self._sharex,
            grid=self._grid,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=self._legend,
            **plot_kwargs,
        )
        return axes

    def save_figure(
        self, axes: Axes | Sequence[Axes], save_path: Path
    ) -> None:
        if isinstance(axes, Sequence):
            axes = axes[0]
        figure = axes.get_figure()
        assert figure is not None
        return figure.savefig(save_path)

    def _plot_structure(
        self,
        axes: Sequence[Axes],
        elts: ListOfElements | None = None,
        x_axis: str = "z_abs",
    ) -> None:
        """Add a plot to show the structure of the linac."""
        if elts is None:
            elts = self._elts
            assert hasattr(self, "_elts"), (
                "Please provide at least a defaut ListOfElements for structure"
                " plots."
            )
        plot_structure(axes[-1], elts, x_axis)

        if not self._sections:
            return
        return self._plot_sections(axes[-1], elts, x_axis)

    def _plot_sections(
        self, axes: Any, elts: ListOfElements, x_axis: str
    ) -> None:
        """Add the sections on the structure plot."""
        return plot_section(axes, elts, x_axis)

    def _actual_constant_plot(
        self,
        axes: Axes | Sequence[Axes],
        constant: float,
        color: str,
        ls: str,
        **kwargs,
    ) -> None:
        """Add one constant plot."""
        if not isinstance(axes, Sequence):
            axes = (axes,)
        for axe in axes:
            axe.axhline(constant, xmin=0, xmax=1, color=color, ls=ls, **kwargs)
