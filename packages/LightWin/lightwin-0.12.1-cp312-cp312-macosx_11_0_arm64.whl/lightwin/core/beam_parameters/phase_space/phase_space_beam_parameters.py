"""Handle the beam parameters of a single phase space.

For a list of the units associated with every parameter, see
:ref:`units-label`.

.. note::
    In this module, angles are stored in deg, not in rad!

"""

from dataclasses import dataclass
from typing import Self

import numpy as np
from numpy.typing import NDArray

from lightwin.core.beam_parameters.helper import (
    mismatch_from_arrays,
    resample_twiss_on_fix,
    sigma_from_transfer_matrices,
)
from lightwin.core.beam_parameters.phase_space.i_phase_space_beam_parameters import (
    IPhaseSpaceBeamParameters,
)
from lightwin.util.typing import BeamKwargs


@dataclass
class PhaseSpaceBeamParameters(IPhaseSpaceBeamParameters):
    """Hold Twiss, emittance, envelopes of a single phase-space."""

    # Override some types from mother class
    eps_no_normalization: NDArray[np.float64]
    eps_normalized: NDArray[np.float64]
    mismatch_factor: NDArray[np.float64] | None = None

    # Already with proper type in mother class:
    # envelopes: NDArray[np.float64] | None = None
    # twiss: NDArray[np.float64] | None = None
    # tm_cumul: NDArray[np.float64] | None = None
    # sigma: NDArray[np.float64] | None = None

    @classmethod
    def from_cumulated_transfer_matrices(
        cls,
        phase_space_name: str,
        sigma_in: NDArray[np.float64],
        tm_cumul: NDArray[np.float64],
        gamma_kin: NDArray[np.float64],
        beta_kin: NDArray[np.float64],
        beam_kwargs: BeamKwargs,
    ) -> Self:
        r"""Compute :math:`\sigma` matrix, and everything from it."""
        sigma = sigma_from_transfer_matrices(sigma_in, tm_cumul)
        phase_space = cls.from_sigma(
            phase_space_name,
            sigma,
            gamma_kin,
            beta_kin,
            tm_cumul=tm_cumul,
            beam_kwargs=beam_kwargs,
        )
        return phase_space

    @classmethod
    def from_sigma(
        cls,
        phase_space_name: str,
        sigma: NDArray[np.float64],
        gamma_kin: NDArray[np.float64],
        beta_kin: NDArray[np.float64],
        beam_kwargs: BeamKwargs,
        **kwargs: NDArray[np.float64],  # tm_cumul
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
        phase_space_name: str,
        gamma_kin: NDArray[np.float64],
        beta_kin: NDArray[np.float64],
        beam_kwargs: BeamKwargs,
        **kwargs: NDArray[np.float64],  # sigma, tm_cumul
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

    @classmethod
    def from_averaging_x_and_y(
        cls, phase_space_name: str, x_space: Self, y_space: Self
    ) -> Self:
        """Create average transverse phase space from [xx'] and [yy'].

        ``eps`` is always initialized. ``mismatch_factor`` is calculated if it
        was already calculated in ``x_space`` and ``y_space``.

        """
        assert phase_space_name == "t"
        eps_normalized = 0.5 * (
            x_space.eps_normalized + y_space.eps_normalized
        )
        eps_no_normalization = 0.5 * (
            x_space.eps_no_normalization + y_space.eps_no_normalization
        )
        envelopes = 0.5 * (x_space.envelopes + y_space.envelopes)

        mismatch_factor = None
        if (
            x_space.mismatch_factor is not None
            and y_space.mismatch_factor is not None
        ):
            mismatch_factor = 0.5 * (
                x_space.mismatch_factor + y_space.mismatch_factor
            )

        phase_space = cls(
            phase_space_name=phase_space_name,
            eps_no_normalization=eps_no_normalization,
            eps_normalized=eps_normalized,
            envelopes=envelopes,
            mismatch_factor=mismatch_factor,
        )
        return phase_space

    @property
    def alpha(self) -> NDArray[np.float64] | None:
        """Get first column of ``self.twiss``."""
        if self.twiss is None:
            return None
        return self.twiss[:, 0]

    @alpha.setter
    def alpha(self, value: NDArray[np.float64]) -> None:
        """Set first column of ``self.twiss``."""
        assert self.twiss is not None
        self.twiss[:, 0] = value

    @property
    def beta(self) -> NDArray[np.float64] | None:
        """Get second column of ``self.twiss``."""
        if self.twiss is None:
            return None
        return self.twiss[:, 1]

    @beta.setter
    def beta(self, value: NDArray[np.float64]) -> None:
        """Set second column of ``self.twiss``."""
        assert self.twiss is not None
        self.twiss[:, 1] = value

    @property
    def gamma(self) -> NDArray[np.float64] | None:
        """Get third column of ``self.twiss``."""
        if self.twiss is None:
            return None
        return self.twiss[:, 2]

    @gamma.setter
    def gamma(self, value: NDArray[np.float64]) -> None:
        """Set third column of ``self.twiss``."""
        assert self.twiss is not None
        self.twiss[:, 2] = value

    @property
    def envelope_pos(self) -> NDArray[np.float64] | None:
        """Get first column of ``self.envelopes``."""
        if self.envelopes is None:
            return None
        return self.envelopes[:, 0]

    @envelope_pos.setter
    def envelope_pos(self, value: NDArray[np.float64]) -> None:
        """Set first column of ``self.envelopes``."""
        assert self.envelopes is not None
        self.envelopes[:, 0] = value

    @property
    def envelope_energy(self) -> NDArray[np.float64] | None:
        """Get second column of ``self.envelopes``."""
        if self.envelopes is None:
            return None
        return self.envelopes[:, 1]

    @envelope_energy.setter
    def envelope_energy(self, value: NDArray[np.float64]) -> None:
        """Set second column of ``self.envelopes``."""
        assert self.envelopes is not None
        self.envelopes[:, 1] = value

    @property
    def eps(self) -> NDArray[np.float64]:
        """Return the normalized emittance."""
        return self.eps_normalized

    @property
    def non_norm_eps(self) -> NDArray[np.float64]:
        """Return the non-normalized emittance."""
        return self.eps_no_normalization

    @property
    def sigma_in(self) -> NDArray[np.float64]:
        r"""Return the first :math:`\sigma` beam matrix."""
        assert self.sigma is not None
        return self.sigma[0]

    def set_mismatch(
        self,
        reference_phase_space: Self,
        reference_z_abs: NDArray[np.float64],
        z_abs: NDArray[np.float64],
        raise_missing_twiss_error: bool = True,
        **mismatch_kw: bool,
    ) -> None:
        """Compute and set the mismatch with ``reference_phase_space``.

        Parameters
        ----------
        reference_phase_space :
            Beam parameters in the same phase space, corresponding to the
            reference linac.
        reference_z_abs :
            Positions corresponding to ``reference_phase_space``.
        z_abs :
            Positions in the linac under study.
        raise_missing_twiss_error :
            If set to True and the Twiss parameters were not calculated in
            current phase space, raise an error.
        mismatch_kw :
            Keyword arguments passed to the function computing mismatch factor.

        """
        assert self.phase_space_name == reference_phase_space.phase_space_name

        if self.twiss is None:
            if not raise_missing_twiss_error:
                return None
            raise RuntimeError(
                "Fixed linac Twiss not calculated in phase space"
                f" {self.phase_space_name}. Cannot compute mismatch."
            )

        reference_twiss = reference_phase_space.twiss
        if reference_twiss is None:
            if not raise_missing_twiss_error:
                return None
            raise RuntimeError(
                "Reference Twiss not calculated in phase space "
                f"{self.phase_space_name}. Cannot compute mismatch."
            )

        assert reference_twiss is not None and self.twiss is not None

        if reference_twiss.shape != self.twiss.shape:
            reference_twiss = resample_twiss_on_fix(
                reference_z_abs, reference_twiss, z_abs
            )

        self.mismatch_factor = mismatch_from_arrays(
            reference_twiss, self.twiss, transp=True
        )
