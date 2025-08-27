"""Define a variation of :class:`.LeastSquares`.

It is not intended to be used with ``phi_s fit``. Approach is here to make the
residuals grow when the constraints are not respected.

"""

import logging

import numpy as np

from lightwin.optimisation.algorithms.algorithm import ComputeConstraintsT
from lightwin.optimisation.algorithms.least_squares import LeastSquares


class LeastSquaresPenalty(LeastSquares):
    """A least-squares method, with a penalty function to consider constraints.

    Everything is inherited from :class:`.LeastSquares`.

    """

    supports_constraints = True

    def __init__(
        self, *args, history_kwargs: dict | None = None, **kwargs
    ) -> None:
        """Set additional information."""
        if history_kwargs is not None:
            logging.warning(
                "History recording not implemented for DownhillSimplexPenalty."
            )
        super().__init__(*args, history_kwargs=history_kwargs, **kwargs)
        self.compute_constraints: ComputeConstraintsT

        if "phi_s" in self.variable_names:
            logging.error(
                "This algorithm is not intended to work with synch phase as "
                "variables, but rather as constraint."
            )

    def _norm_wrapper_residuals(self, var: np.ndarray) -> float:
        """Give residuals with a penalty."""
        cav_settings = self._create_set_of_cavity_settings(var)
        simulation_output = self.compute_beam_propagation(cav_settings)
        residuals = self.compute_residuals(simulation_output)
        constraints_evaluations = self.compute_constraints(simulation_output)
        penalty = self._penalty(constraints_evaluations)
        return float(np.linalg.norm(residuals)) * penalty

    def _penalty(self, constraints_evaluations: np.ndarray) -> float:
        """Compute appropriate penalty."""
        violated_constraints = constraints_evaluations[
            np.where(constraints_evaluations > 0.0)
        ]
        n_violated = violated_constraints.shape[0]
        if n_violated == 0:
            return 1.0
        return 1.0 + np.sum(n_violated) * 10.0
