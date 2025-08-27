"""Define an objective that is a quantity must be within some bounds.

.. todo::
    Implement loss functions.

"""

import logging
from typing import Any, Self

from lightwin.beam_calculation.simulation_output.simulation_output import (
    SimulationOutput,
)
from lightwin.optimisation.objective.objective import Objective
from lightwin.util.typing import GETTABLE_SIMULATION_OUTPUT_T


class QuantityIsBetween(Objective):
    """Quantity must be within some bounds."""

    def __init__(
        self,
        name: str,
        weight: float,
        get_key: GETTABLE_SIMULATION_OUTPUT_T,
        get_kwargs: dict[str, Any],
        limits: tuple[float, float],
        descriptor: str | None = None,
        loss_function: str | None = None,
    ) -> None:
        """
        Set complementary :meth:`.SimulationOutput.get` flags, reference value.

        Parameters
        ----------
        name :
            A short string to describe the objective and access to it.
        weight :
            A scaling constant to set the weight of current objective.
        get_key :
            Name of the quantity to get.
        get_kwargs :
            Keyword arguments for the :meth:`.SimulationOutput.get` method. We
            do not check its validity, but in general you will want to define
            the keys ``elt`` and ``pos``. If objective concerns a phase, you
            may want to precise the ``to_deg`` key. You also should explicit
            the ``to_numpy`` key.
        limits :
            Lower and upper bound for the value.
        loss_function :
            Indicates how the residuals are handled when the quantity is
            outside the limits. Currently not implemented.

        """
        self._check_get_arguments(get_key, get_kwargs)
        self.get_key: GETTABLE_SIMULATION_OUTPUT_T = get_key
        self.get_kwargs = get_kwargs
        self.ideal_value: tuple[float, float]
        super().__init__(
            name, weight, descriptor=descriptor, ideal_value=limits
        )
        if loss_function is not None:
            logging.warning("Loss functions not implemented.")

    @classmethod
    def relative_to_reference(
        cls,
        name: str,
        weight: float,
        get_key: GETTABLE_SIMULATION_OUTPUT_T,
        get_kwargs: dict[str, Any],
        relative_limits: tuple[float, float],
        reference_value: float,
        descriptor: str | None = None,
        loss_function: str | None = None,
    ) -> Self:
        r"""
        Set complementary :meth:`.SimulationOutput.get` flags, reference value.

        Parameters
        ----------
        name :
            A short string to describe the objective and access to it.
        weight :
            A scaling constant to set the weight of current objective.
        get_key :
            Name of the quantity to get.
        get_kwargs :
            Keyword arguments for the :meth:`.SimulationOutput.get` method. We
            do not check its validity, but in general you will want to define
            the keys ``elt`` and ``pos``. If objective concerns a phase, you
            may want to precise the ``to_deg`` key. You also should explicit
            the ``to_numpy`` key.
        relative_limits :
            Lower and upper bound for the value, in :unit:`\%` wrt
            ``reference_value``. First value should be lower than
            :math:`100\%`, second value higher than :math:`100\%`.
        reference_value :
            Ideal value.
        loss_function :
            Indicates how the residuals are handled when the quantity is
            outside the limits. Currently not implemented.

        """
        assert relative_limits[0] <= 100.0 and relative_limits[1] >= 100.0, (
            f"{relative_limits = } but should look like `(80, 135)` (which "
            "means: objective must be 80% and 135% of reference value."
        )
        limits: tuple[float, float]
        limits = (
            reference_value * 1e-2 * relative_limits[0],
            reference_value * 1e-2 * relative_limits[1],
        )
        if reference_value <= 0.0:
            logging.info(
                f"{reference_value = } is negative. Inverting bounds to keep "
                "limits[0] < limits[1]."
            )
            limits = (limits[1], limits[0])
        return cls(
            name=name,
            weight=weight,
            get_key=get_key,
            get_kwargs=get_kwargs,
            limits=limits,
            descriptor=descriptor,
            loss_function=loss_function,
        )

    def base_str(self) -> str:
        """Tell nature and position of objective."""
        message = f"{self.get_key:>23}"

        elt = str(self.get_kwargs.get("elt", "NA"))
        message += f" @elt {elt:>5}"

        pos = str(self.get_kwargs.get("pos", "NA"))
        message += f" ({pos:>3}) | {self.weight:>5} | "
        return message

    def __str__(self) -> str:
        """Give objective information value."""
        message = self.base_str()
        message += f"{self.ideal_value[0]:+.2e} ~ {self.ideal_value[1]:+.2e}"  # type: ignore
        return message

    def _value_getter(self, simulation_output: SimulationOutput) -> float:
        """Get desired value using :meth:`.SimulationOutput.get` method."""
        return simulation_output.get(self.get_key, **self.get_kwargs)

    def evaluate(self, simulation_output: SimulationOutput) -> float:
        assert isinstance(simulation_output, SimulationOutput)
        value = self._value_getter(simulation_output)
        return self._compute_residuals(value)

    def _compute_residuals(self, value: float) -> float:
        """Compute residual for ``value`` with respect to the ideal interval.

        This method applies a quadratic penalty if the value lies outside the
        target interval defined by ``self.ideal_value``. No penalty is applied
        when the value is within the interval.

        The loss function is:

        - 0 if ``ideal_value[0] <= value <= ideal_value[1]``
        - ``weight * (value - bound)^2`` otherwise, where bound is the violated
          boundary.

        Parameters
        ----------
        value :
            The value to evaluate.

        Returns
        -------
            The computed residual (loss).

        """
        if value < self.ideal_value[0]:
            return self.weight * (value - self.ideal_value[0]) ** 2
        if value > self.ideal_value[1]:
            return self.weight * (value - self.ideal_value[1]) ** 2
        return 0.0
