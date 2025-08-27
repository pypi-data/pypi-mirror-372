"""Create the solver parameters for :class:`.Envelope3D`."""

import logging

from lightwin.beam_calculation.envelope_3d.element_envelope3d_parameters import (
    BendEnvelope3DParameters,
    DriftEnvelope3DParameters,
    ElementEnvelope3DParameters,
    FieldMapEnvelope3DParameters,
    QuadEnvelope3DParameters,
    SolenoidEnvelope3DParameters,
)
from lightwin.beam_calculation.envelope_3d.util import ENVELOPE3D_METHODS_T
from lightwin.beam_calculation.parameters.factory import (
    ElementBeamCalculatorParametersFactory,
)
from lightwin.core.elements.bend import Bend
from lightwin.core.elements.diagnostic import Diagnostic
from lightwin.core.elements.drift import Drift
from lightwin.core.elements.element import Element
from lightwin.core.elements.field_maps.field_map import FieldMap
from lightwin.core.elements.field_maps.field_map_70 import FieldMap70
from lightwin.core.elements.field_maps.field_map_7700 import FieldMap7700
from lightwin.core.elements.quad import Quad
from lightwin.core.elements.solenoid import Solenoid
from lightwin.physics.synchronous_phases import PHI_S_MODELS
from lightwin.util.typing import BeamKwargs

#: Implemented elements; a non-implemented element will be replaced by a Drift.
#: A warning will be raised.
PARAMETERS_3D = {
    Bend: BendEnvelope3DParameters,
    Diagnostic: DriftEnvelope3DParameters,
    Drift: DriftEnvelope3DParameters,
    FieldMap: FieldMapEnvelope3DParameters,
    Quad: QuadEnvelope3DParameters,
    Solenoid: SolenoidEnvelope3DParameters,
}


class ElementEnvelope3DParametersFactory(
    ElementBeamCalculatorParametersFactory
):
    """Define a method to easily create the solver parameters."""

    def __init__(
        self,
        method: ENVELOPE3D_METHODS_T,
        n_steps_per_cell: int,
        solver_id: str,
        beam_kwargs: BeamKwargs,
        phi_s_definition: PHI_S_MODELS = "historical",
    ) -> None:
        """Prepare import of proper functions."""
        self.method = method
        self.n_steps_per_cell = n_steps_per_cell
        self.solver_id = solver_id
        self.beam_kwargs = beam_kwargs
        self.phi_s_definition = phi_s_definition

    def run(self, elt: Element) -> ElementEnvelope3DParameters:
        """Create the proper subclass of solver parameters, instantiate it.

        Parameters
        ----------
        elt :
            Element under study.

        Returns
        -------
        ElementEnvelope3DParameters
            Proper instantiated subclass of
            :class:`.ElementEnvelope3DParameters`.

        """
        subclass = self._parameters_constructor(elt)
        kwargs = {
            "method": self.method,
            "n_steps_per_cell": self.n_steps_per_cell,
            "solver_id": self.solver_id,
            "phi_s_definition": self.phi_s_definition,
        }

        single_element_envelope_3d_parameters = subclass(
            elt=elt, beam_kwargs=self.beam_kwargs, **kwargs
        )

        return single_element_envelope_3d_parameters

    def _parameters_constructor(
        self, elt: Element, default: type = PARAMETERS_3D[Drift]
    ) -> type:
        """Get the proper object constructor.

        Examples
        --------
        >>> self._parameters_constructor(Drift())
        DriftEnvelope3DParameters

        >>> self._parameters_constructor(Quad())
        QuadEnvelope3DParameters

        As DiagPosition is not in PARAMETERS_3D, we look for the mother
        class Diagnostic.

        >>> self._parameters_constructor(DiagPosition())
        DriftEnvelope3DParameters

        To avoid wasting computation time, non-accelerating field maps are
        treated as drifts.

        >>> self._parameters_constructor(FieldMap100(is_accelerating=False))
        DriftEnvelope3DParameters

        """
        element_class = type(elt)
        if isinstance(elt, (FieldMap70, FieldMap7700)):
            logging.error(
                f"{elt = } of type {element_class} transverse dynamics not "
                "implemented yet."
            )
        if isinstance(elt, FieldMap) and not elt.is_accelerating:
            return default

        constructor = PARAMETERS_3D.get(element_class, None)
        if constructor is not None:
            return constructor

        super_class = element_class.__base__
        constructor = PARAMETERS_3D.get(super_class, None)
        if constructor is not None:
            return constructor

        logging.error(
            f"Element {elt} of {element_class = } not added to the Envelope3D "
            "dict linking every Element class to its specific parameters"
            "(transfer matrix in particular). Neither was found its "
            f"{super_class = }. "
            "Note that you can use the elements_to_dump key in the "
            "Envelope3D.ListOfElementFactory class."
        )
        return default
