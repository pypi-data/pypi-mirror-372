"""Handle the initial beam parameters of a single phase space.

For a list of the units associated with every parameter, see
:ref:`units-label`.

.. note::
    In this module, angles are stored in deg, not in rad!

"""

from dataclasses import dataclass
from typing import Self

import numpy as np
from numpy.typing import NDArray

from lightwin.core.beam_parameters.phase_space.i_phase_space_beam_parameters import (
    IPhaseSpaceBeamParameters,
)
from lightwin.util.typing import PHASE_SPACE_T, BeamKwargs


@dataclass
class InitialPhaseSpaceBeamParameters(IPhaseSpaceBeamParameters):
    """Hold Twiss, emittance, envelopes of single phase-space @ single pos."""

    # Override some types from mother class
    eps_no_normalization: float
    eps_normalized: float
    mismatch_factor: float | None = None

    # Already with proper type in mother class:
    # envelopes: NDArray | None = None
    # twiss: NDArray | None = None
    # tm_cumul: NDArray | None = None
    # sigma: NDArray | None = None

    def __post_init__(self) -> None:
        """Ensure that the phase space exists."""
        if self.tm_cumul is None:
            self.tm_cumul = np.eye(2)
        super().__post_init__()

    @classmethod
    def from_sigma(
        cls,
        phase_space_name: PHASE_SPACE_T,
        sigma: NDArray,
        gamma_kin: float,
        beta_kin: float,
        beam_kwargs: BeamKwargs,
        **kwargs: NDArray,  # tm_cumul
    ) -> Self:
        """Compute Twiss, eps, envelopes just from sigma matrix."""
        return super().from_sigma(
            phase_space_name,
            sigma,
            gamma_kin,
            beta_kin,
            beam_kwargs=beam_kwargs,
            **kwargs,
        )

    @classmethod
    def from_other_phase_space(
        cls,
        other_phase_space: Self,
        phase_space_name: PHASE_SPACE_T,
        gamma_kin: float,
        beta_kin: float,
        beam_kwargs: BeamKwargs,
        **kwargs: NDArray,  # sigma, tm_cumul
    ) -> Self:
        """Fully initialize from another phase space."""
        return super().from_other_phase_space(
            other_phase_space,
            phase_space_name,
            gamma_kin,
            beta_kin,
            beam_kwargs=beam_kwargs,
            **kwargs,
        )

    @property
    def alpha(self) -> float | None:
        """Get first element of ``self.twiss``."""
        if self.twiss is None:
            return None
        return self.twiss[0]

    @alpha.setter
    def alpha(self, value: float) -> None:
        """Set first element of ``self.twiss``."""
        assert self.twiss is not None
        self.twiss[0] = value

    @property
    def beta(self) -> float | None:
        """Get second element of ``self.twiss``."""
        if self.twiss is None:
            return None
        return self.twiss[1]

    @beta.setter
    def beta(self, value: float) -> None:
        """Set second element of ``self.twiss``."""
        assert self.twiss is not None
        self.twiss[1] = value

    @property
    def gamma(self) -> float | None:
        """Get third element of ``self.twiss``."""
        if self.twiss is None:
            return None
        return self.twiss[2]

    @gamma.setter
    def gamma(self, value: float) -> None:
        """Set third element of ``self.twiss``."""
        assert self.twiss is not None
        self.twiss[2] = value

    @property
    def envelope_pos(self) -> float | None:
        """Get first element of ``self.envelopes``."""
        if self.envelopes is None:
            return None
        return self.envelopes[0]

    @envelope_pos.setter
    def envelope_pos(self, value: float) -> None:
        """Set first element of ``self.envelopes``."""
        assert self.envelopes is not None
        self.envelopes[0] = value

    @property
    def envelope_energy(self) -> float | None:
        """Get second element of ``self.envelopes``."""
        if self.envelopes is None:
            return None
        return self.envelopes[1]

    @envelope_energy.setter
    def envelope_energy(self, value: float) -> None:
        """Set second element of ``self.envelopes``."""
        assert self.envelopes is not None
        self.envelopes[1] = value

    @property
    def eps(self) -> float:
        """Return the normalized emittance."""
        return self.eps_normalized

    @property
    def non_norm_eps(self) -> float:
        """Return the normalized emittance."""
        return self.eps_no_normalization
