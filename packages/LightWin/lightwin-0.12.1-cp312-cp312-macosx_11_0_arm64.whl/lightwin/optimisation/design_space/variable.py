"""Define :class:`Variable`, which stores an optimisation variable.

It keeps it's name, bounds, initial value, etc.

"""

import logging
from dataclasses import dataclass
from typing import Self

import numpy as np
import pandas as pd

from lightwin.optimisation.design_space.design_space_parameter import (
    DesignSpaceParameter,
)

IMPLEMENTED_VARIABLES = ("k_e", "phi_0_abs", "phi_0_rel", "phi_s")  #:


@dataclass
class Variable(DesignSpaceParameter):
    """A single variable.

    It can be a cavity amplitude, absolute phase, relative phase or synchronous
    phase with an initial value and limits.

    Parameters
    ----------
    name :
        Name of the parameter. Must be compatible with the
        :meth:`.SimulationOutput.get` method, and be in
        :data:`.IMPLEMENTED_VARIABLES`.
    element_name :
        Name of the element concerned by the parameter.
    limits :
        Lower and upper bound for the variable. ``np.nan`` deactivates a bound.
    x_0 :
        Initial value.

    """

    x_0: float

    @classmethod
    def from_floats(
        cls,
        name: str,
        element_name: str,
        x_min: float,
        x_max: float,
        x_0: float = np.nan,
    ) -> Self:
        """Initialize object with ``x_min``, ``x_max`` instead of ``limits``.

        Parameters
        ----------
        name :
            Name of the parameter. Must be compatible with the
            :meth:`.SimulationOutput.get` method, and be in
            :data:`.IMPLEMENTED_VARIABLES`.
        element_name :
            Name of the element concerned by the parameter.
        x_min :
            Lower limit. ``np.nan`` to deactivate lower bound.
        x_max :
            Upper limit. ``np.nan`` to deactivate lower bound.
        x_0: float
            Initial value.

        Returns
        -------
            A Variable with limits = (x_min, x_max).

        """
        return cls(name, element_name, (x_min, x_max), x_0)

    @classmethod
    def from_pd_series(
        cls, name: str, element_name: str, pd_series: pd.Series
    ) -> Self:
        """Init object from a pd series (file import)."""
        x_min = pd_series.loc[f"{name}: x_min"]
        x_max = pd_series.loc[f"{name}: x_max"]
        x_0 = pd_series.loc[f"{name}: x_0"]
        return cls.from_floats(name, element_name, x_min, x_max, x_0)

    def __post_init__(self):
        """Convert values in deg for output if it is angle."""
        if self.name not in IMPLEMENTED_VARIABLES:
            logging.warning(f"Variable {self.name} not tested.")
        super().__post_init__()
