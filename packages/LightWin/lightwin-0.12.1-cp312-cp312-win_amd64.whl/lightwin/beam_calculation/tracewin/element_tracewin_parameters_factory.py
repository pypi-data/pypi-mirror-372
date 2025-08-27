"""Create the solver parameters for :class:`.TraceWin`."""

from typing import Any

import numpy as np

from lightwin.beam_calculation.parameters.factory import (
    ElementBeamCalculatorParametersFactory,
)
from lightwin.beam_calculation.tracewin.element_tracewin_parameters import (
    ElementTraceWinParameters,
)
from lightwin.core.elements.element import Element


class ElementTraceWinParametersFactory(ElementBeamCalculatorParametersFactory):
    """Define a method to easily create the solver parameters."""

    def __init__(self) -> None:
        """Instantiate the class."""

    def run(
        self, elt: Element, z_element: np.ndarray, s_in: int, s_out: int
    ) -> ElementTraceWinParameters:
        """Create the parameters for every element.

        .. note::
            In contrary to :class:`.Envelope1D` and :class:`.Envelope3D`, this
            method is called *after* a simulation. As a matter of fact,
            TraceWin does not need our solver parameters to run. However, we
            need to link TraceWin's array of results with our
            :class:`.ListOfElements`.

        See Also
        --------
        :meth:`.SimulationOutputFactoryTraceWin._save_tracewin_meshing_in_elements`

        """
        constructor = self._parameters_constructor(elt)
        single_element_tracewin_parameters = constructor(
            elt.length_m, z_element, s_in, s_out
        )
        return single_element_tracewin_parameters

    def _parameters_constructor(self, *args: Any, **kwargs: Any) -> type:
        """Return the same class for every element."""
        return ElementTraceWinParameters
