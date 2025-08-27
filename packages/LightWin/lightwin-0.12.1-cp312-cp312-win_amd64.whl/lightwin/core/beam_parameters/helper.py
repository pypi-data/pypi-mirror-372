"""Define functions useful for beam parameters calculations.

For more information on the units that are used in this module, see
:ref:`units-label`.

"""

import logging
from typing import overload

import numpy as np
from numpy.typing import NDArray

from lightwin.physics import converters
from lightwin.util.typing import PHASE_SPACE_T, PHASE_SPACES, BeamKwargs


# =============================================================================
# Compute quantities from the sigma beam matrix
# =============================================================================
def reconstruct_sigma(
    phase_space_name: str,
    sigma_00: NDArray,
    sigma_01: NDArray,
    eps: NDArray,
    tol: float = 1e-8,
    eps_is_normalized: bool = False,
    gamma_kin: NDArray | None = None,
    beta_kin: NDArray | None = None,
    **beam,
) -> NDArray:
    r"""
    Set :math:`\sigma` matrix from the two top components and emittance.

    Inputs are in :unit:`mm` and :unit:`mrad`, but the :math:`\sigma` matrix is
    in SI units (:unit:`m` and :unit:`rad`).

    See Also
    --------
    :ref:`units-label`.

    Parameters
    ----------
    phase_space_name :
        Name of the phase space.
    sigma_00 :
        ``(n, )`` array of top-left sigma matrix components.
    sigma_01 :
        ``(n, )`` array of top-right (bottom-left) sigma matrix components.
    eps :
        ``(n, )`` un-normalized emittance array, in units consistent with
        ``sigma_00`` and ``sigma_01``.
    tol :
        ``sigma_00`` is set to np.nan where it is under ``tol`` to avoid
        ``RuntimeWarning``. The default is ``1e-8``.
    eps_is_normalized :
        To tell if the given emittance is already normalized. The default is
        True. In this case, it is de-normalized and ``gamma_kin`` must be
        provided.
    gamma_kin :
        Lorentz gamma factor. The default is None. It is mandatory to give it
        if the emittance is given unnormalized.
    beta_kin :
        Lorentz beta factor. The default is None. In this case, we compute it
        from ``gamma_kin``.
    beam :
        Configuration dictionary holding the beam parameters.

    Returns
    -------
        ``(n, 2, 2)`` full sigma matrix along the linac.

    """
    if phase_space_name not in ("zdelta", "x", "y", "x99", "y99"):
        logging.warning(
            "sigma reconstruction in this phase space not tested. "
            "You'd better check the units of the output."
        )

    if eps_is_normalized:
        assert gamma_kin is not None
        if beta_kin is None:
            beta_kin = converters.energy(
                energy_in=gamma_kin, key="gamma to beta", **beam
            )
            assert isinstance(beta_kin, np.ndarray)
        eps /= beta_kin * gamma_kin

    sigma = np.zeros((sigma_00.shape[0], 2, 2))
    sigma_00[np.where(np.abs(sigma_00) < tol)] = np.nan
    sigma[:, 0, 0] = sigma_00
    sigma[:, 0, 1] = sigma_01
    sigma[:, 1, 0] = sigma_01
    sigma[:, 1, 1] = (eps**2 + sigma_01**2) / sigma_00

    if phase_space_name in ("zdelta", "x", "y", "x99", "y99"):
        sigma *= 1e-6
    assert isinstance(sigma, np.ndarray)
    return sigma


@overload
def eps_from_sigma(
    phase_space_name: str,
    sigma: NDArray,
    gamma_kin: NDArray,
    beta_kin: NDArray,
    beam_kwargs: BeamKwargs,
) -> tuple[NDArray, NDArray]: ...


@overload
def eps_from_sigma(
    phase_space_name: str,
    sigma: NDArray,
    gamma_kin: float,
    beta_kin: float,
    beam_kwargs: BeamKwargs,
) -> tuple[float, float]: ...


def eps_from_sigma(
    phase_space_name: str,
    sigma: NDArray,
    gamma_kin: NDArray | float,
    beta_kin: NDArray | float,
    beam_kwargs: BeamKwargs,
) -> tuple[NDArray | float, NDArray | float]:
    r"""Compute emittance from :math:`\sigma` beam matrix.

    In the :math:`[z-\delta]` phase space, emittance is in :unit:`\\pi.mm.\\%`.
    In the transverse phase spaces, emittance is in :unit:`\\pi.mm.mrad`.
    :math:`\sigma` is always in SI units.

    Parameters
    ----------
    phase_space_name :
        Name of the phase space, used to apply proper normalization factor.
    sigma :
        ``(n, 2, 2)`` (or ``(2, 2)``) :math:`\sigma` beam matrix in SI units.
    gamma_kin :
        ``(n, )`` (or float) Lorentz gamma factor.
    beta_kin :
        ``(n, )`` (or float) Lorentz beta factor.
    beam_kwargs :
        Configuration dictionary holding the initial beam parameters.

    Returns
    -------
    eps_no_normalization
        ``(n, )`` array (or float) of emittance, not normalized.
    eps_normalized
        ``(n, )`` array (or float) of emittance, normalized.

    """
    allowed = ("zdelta", "x", "y", "x99", "y99")
    assert (
        phase_space_name in allowed
    ), f"Phase-space {phase_space_name} not in {allowed = }."

    is_initials = False
    if isinstance(gamma_kin, float):
        is_initials = True
        sigma = sigma[np.newaxis, :, :]

    dets = np.linalg.det(sigma)
    invalid_idx = np.where(dets < 0.0)
    dets[invalid_idx] = np.nan
    eps_no_normalization = np.sqrt(dets)

    if phase_space_name in ("zdelta",):
        eps_no_normalization *= 1e5
    elif phase_space_name in ("x", "y", "x99", "y99"):
        eps_no_normalization *= 1e6

    eps_normalized = converters.emittance(
        eps_no_normalization,
        f"normalize {phase_space_name}",
        gamma_kin=gamma_kin,
        beta_kin=beta_kin,
        **beam_kwargs,
    )
    if is_initials:
        return eps_no_normalization[0], eps_normalized[0]

    assert isinstance(eps_normalized, np.ndarray)
    return eps_no_normalization, eps_normalized


def twiss_from_sigma(
    phase_space_name: str,
    sigma: NDArray,
    eps_no_normalization: NDArray | float,
    tol: float = 1e-8,
) -> NDArray:
    r"""Compute the Twiss parameters using the :math:`\sigma` matrix.

    In the :math:`[z-\delta]` phase space, emittance and Twiss are in
    :unit:`mm` and :unit:`\\%`.
    In the transverse phase spaces, emittance and Twiss are in :unit:`mm` and
    :unit:`mrad`.
    :math:`\sigma` is always in SI units.

    .. todo::
        Would be better if all emittances had the same units? Check
        consistency with rest of the code...

    Parameters
    ----------
    phase_space_name :
        Name of the phase space, used to set the proper normalization.
    sigma :
        ``(n, 2, 2)`` array (or ``(2, 2)``) holding :math:`\sigma` beam matrix.
    eps_no_normalization :
        ``(n, )`` array (or float) of unnormalized emittance.
    tol :
        ``eps_no_normalization`` is set to np.nan where it is under ``tol``
        to avoid ``RuntimeWarning``. The default is ``1e-8``.

    Returns
    -------
        ``(n, 3)`` (or ``(3, )``) array of Twiss parameters.

    """
    assert phase_space_name in ("zdelta", "x", "y", "x99", "y99")

    is_initial = False
    if isinstance(eps_no_normalization, float):
        is_initial = True
        sigma = sigma[np.newaxis, :, :]

    n_points = sigma.shape[0]
    twiss = np.full((n_points, 3), np.nan)

    for i in range(n_points):
        divisor = np.atleast_1d(eps_no_normalization)[i]
        if np.abs(divisor) < tol:
            divisor = np.nan

        twiss[i, :] = (
            np.array([-sigma[i, 1, 0], sigma[i, 0, 0], sigma[i, 1, 1]])
            / divisor
            * 1e6
        )

    if phase_space_name == "zdelta":
        twiss[:, 0] *= 1e-1
        twiss[:, 2] *= 1e-2

    if is_initial:
        return twiss[0]
    return twiss


# TODO would be possible to skip this with TW, where envelope_pos is
# already known
def envelopes_from_sigma(
    phase_space_name: str,
    sigma: NDArray,
) -> NDArray:
    r"""Compute the envelopes.

    Units are :unit:`mm` for the position envelope in :math:`[z-\delta]`,
    :math:`[x-x']`, :math:`[y-y']`. Units are :unit:`\\%` for the energy
    envelope in :math:`[z-\delta]`, and :unit:`mrad` for :math:`[x-x']` and
    :math:`[y-y']`.

    Parameters
    ----------
    phase_space_name :
        Name of the phase space, used to set the proper normalization.
    sigma :
        ``(n, 2, 2)`` (or ``(2, 2)``) array holding :math:`\sigma` beam matrix.

    Returns
    -------
        ``(n, 2)`` (or ``(2, )``) array with position envelope in first column,
        energy envelope in second.

    """
    is_initial = False
    if sigma.ndim == 2:
        is_initial = True
        sigma = sigma[np.newaxis, :, :]

    envelope_pos = np.array([np.sqrt(sigm[0, 0]) for sigm in sigma]) * 1e3
    envelope_energy = np.array([np.sqrt(sigm[1, 1]) for sigm in sigma]) * 1e3

    if phase_space_name == "zdelta":
        envelope_energy /= 10.0

    if is_initial:
        return np.array([envelope_pos[0], envelope_energy[0]])
    envelopes = np.column_stack((envelope_pos, envelope_energy))
    return envelopes


# =============================================================================
# Compute quantities from the transfer matrix
# =============================================================================
def sigma_from_transfer_matrices(
    sigma_in: NDArray,
    tm_cumul: NDArray,
) -> NDArray:
    r"""
    Compute the :math:`\sigma` beam matrices over the linac.

    ``sigma_in`` and transfer matrices shall have same units, in the same phase
    space.

    Parameters
    ----------
    tm_cumul :
        ``(n, 2, 2)`` cumulated transfer matrices along the linac.
    sigma_in :
        ``(2, 2)`` :math:`\sigma` beam matrix at the linac entrance.

    Returns
    -------
        ``(n, 2, 2)`` :math:`\sigma` beam matrix along the linac.

    """
    sigma = []
    if tm_cumul.ndim == 2:
        tm_cumul = tm_cumul[np.newaxis]
    n_points = tm_cumul.shape[0]

    for i in range(n_points):
        sigma.append(tm_cumul[i] @ sigma_in @ tm_cumul[i].transpose())
    return np.array(sigma)


# =============================================================================
# Compute quantities from Twiss and emittance
# =============================================================================
def envelopes_from_twiss_eps(twiss: NDArray, eps: NDArray | float) -> NDArray:
    r"""
    Compute the envelopes from the Twiss parameters and emittance.

    Parameters
    ----------
    twiss :
        ``(n, 3)`` (or ``(3, )``) array of Twiss parameters.
    eps :
        ``(n, )`` array of emittance. If the phase space is :math:`[\phi-W]`,
        the emittance should be normalized. Else, it should be un-normalized.

    Returns
    -------
        ``(n, 2)`` (or ``(2, )``) array with position envelope in first column,
        energy envelope in second.

    """
    if isinstance(eps, float):
        envelopes = np.sqrt(twiss[1:] * eps)
        return envelopes

    envelopes = np.sqrt(twiss[:, 1:] * eps[:, np.newaxis])
    assert envelopes.shape != (2,)
    return envelopes


# =============================================================================
# Compute quantities from another phase space
# =============================================================================
@overload
def eps_from_other_phase_space(
    other_phase_space_name: str,
    phase_space_name: str,
    eps_other: NDArray,
    gamma_kin: NDArray,
    beta_kin: NDArray,
    **beam_kwargs,
) -> tuple[NDArray, NDArray]: ...


@overload
def eps_from_other_phase_space(
    other_phase_space_name: str,
    phase_space_name: str,
    eps_other: float,
    gamma_kin: float,
    beta_kin: float,
    **beam_kwargs,
) -> tuple[float, float]: ...


def eps_from_other_phase_space(
    other_phase_space_name: str,
    phase_space_name: str,
    eps_other: NDArray | float,
    gamma_kin: NDArray | float,
    beta_kin: NDArray | float,
    **beam_kwargs,
) -> tuple[NDArray | float, NDArray | float]:
    """Convert emittance from another phase space.

    Output emittance is normalized if input is, and is un-normalized if the
    input emittance is not normalized.

    .. warning::
        old funct returned eps with same normalisation state as given eps_other

    Parameters
    ----------
    other_phase_space_name :
        Name of the original phase space.
    phase_space_name :
        Name of the phase space, used to ensure correct
        normalization/denormalization.
    eps_other :
        ``(n, )`` array (or float) of emittance of starting phase-space.
    gamma_kin :
        ``(n, )`` array (or float) of Lorentz gamma.
    beta_kin :
        ``(n, )`` array (or float) of Lorentz beta
    beam_kwargs :
        Configuration dictionary holding the initial beam parameters.

    Returns
    -------
    eps_no_normalization :
        ``(n, )`` array (or float) of emittance, not normalized.
    eps_normalized :
        ``(n, )`` array (or float) of emittance, normalized.

    """
    convert_key = f"{other_phase_space_name} to {phase_space_name}"
    eps_normalized = converters.emittance(
        eps_other,
        convert_key,
        gamma_kin=gamma_kin,
        beta_kin=beta_kin,
        **beam_kwargs,
    )

    eps_no_normalization = converters.emittance(
        eps_normalized,
        f"de-normalize {phase_space_name}",
        gamma_kin,
        beta_kin,
        **beam_kwargs,
    )
    return eps_no_normalization, eps_normalized


def twiss_from_other_phase_space(
    other_phase_space_name: str,
    phase_space_name: str,
    twiss_other: NDArray,
    gamma_kin: NDArray | float,
    beta_kin: NDArray | float,
    **beam,
) -> NDArray:
    """Compute Twiss parameters from Twiss parameters in another plane.

    Parameters
    ----------
    other_phase_space_name :
        Name of the original phase space.
    phase_space_name :
        Name of the phase space.
    twiss_other :
        ``(n, 3)`` Twiss array from original phase space.
    gamma_kin :
        ``(n, )`` array (or float) of Lorentz gamma.
    beta_kin :
        ``(n, )`` array (or float) of Lorentz beta
    beam :
        Configuration dictionary holding the initial beam parameters.

    Returns
    -------
        ``(n, 3)`` array of Twiss parameters.

    """
    convert_key = f"{other_phase_space_name} to {phase_space_name}"

    is_initial = False
    if isinstance(gamma_kin, float):
        is_initial = True
        twiss_other = twiss_other[np.newaxis, :]

    twiss = converters.twiss(
        twiss_other, gamma_kin, convert_key, beta_kin=beta_kin, **beam
    )
    if is_initial:
        return twiss[0, :]
    return twiss


# =============================================================================
# Utility
# =============================================================================
def mismatch_from_arrays(
    ref: NDArray, fix: NDArray, transp: bool = False
) -> NDArray:
    """Compute the mismatch factor between two ellipses."""
    assert isinstance(ref, np.ndarray)
    assert isinstance(fix, np.ndarray)
    # Transposition needed when computing the mismatch factor at more than one
    # position, as shape of twiss arrays is (n, 3).
    if transp:
        ref = ref.transpose()
        fix = fix.transpose()

    if ref.shape != fix.shape:
        return fix[0] * np.nan

    # R in TW doc
    __r = ref[1] * fix[2] + ref[2] * fix[1]
    __r -= 2.0 * ref[0] * fix[0]

    # Forbid R values lower than 2 (numerical error)
    __r = np.atleast_1d(__r)
    __r[np.where(__r < 2.0)] = 2.0

    mismatch = np.sqrt(0.5 * (__r + np.sqrt(__r**2 - 4.0))) - 1.0
    return mismatch


def resample_twiss_on_fix(
    reference_z_abs: NDArray, reference_twiss: NDArray, z_abs: NDArray
) -> NDArray:
    """Interpolate ref Twiss on fix Twiss to compute mismatch afterwards."""
    n_points = z_abs.shape[0]
    out_shape = (n_points, 3)
    out = np.empty(out_shape)

    if reference_z_abs.shape[0] != reference_twiss.shape[0]:
        logging.critical(
            f"Mismatch between the shapes of the reference arrays, returnin "
            f"NaN.\n{reference_z_abs.shape = }\n{reference_twiss.shape = }\n"
            f"{z_abs.shape = }"
        )
        return np.full(out_shape, np.nan)

    for axis in range(out.shape[1]):
        out[:, axis] = np.interp(
            z_abs, reference_z_abs, reference_twiss[:, axis]
        )
    return out


def phase_space_name_hidden_in_key(key: str) -> bool:
    """Tell if the name of a phase-space is present in ``key``."""
    if "_" not in key:
        return False

    to_test = key.split("_")
    if to_test[-1] in PHASE_SPACES:
        return True
    return False


def separate_var_from_phase_space(key: str) -> tuple[str, PHASE_SPACE_T]:
    """Separate variable name from phase space name."""
    splitted = key.split("_")
    key = "_".join(splitted[:-1])
    phase_space = splitted[-1]
    assert phase_space in PHASE_SPACES
    return key, phase_space
