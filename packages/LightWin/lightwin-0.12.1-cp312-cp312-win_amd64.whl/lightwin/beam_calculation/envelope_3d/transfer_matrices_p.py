"""Define every element transfer matrix.

Units are taken exactly as in TraceWin, i.e. fifth line is ``z (m)`` and
sixth line is ``dp/p``.

.. todo::
    3D field maps?

.. todo::
    Maybe it would be clearer to compose r_xx, r_yy, r_zz. As an example, the
    zz_drift is used in several places.

.. todo::
    Will be necessary to separate this module into several sub-packages

.. todo::
    more math, less numpy. look at envelope 1d version

"""

import math
from typing import Callable

import numpy as np

from lightwin.beam_calculation.integrators.rk4 import rk4
from lightwin.constants import c


# =============================================================================
# Electric field functions
# =============================================================================
def e_func(
    z: float, e_spat: Callable[[float], float], phi: float, phi_0: float
) -> float:
    """Give the electric field at position z and phase phi.

    The field is normalized and should be multiplied by k_e.

    """
    return e_spat(z) * math.cos(phi + phi_0)


# =============================================================================
# Transfer matrices
# =============================================================================
def drift(
    gamma_in: float,
    delta_s: float,
    omega_0_bunch: float,
    n_steps: int = 1,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, None]:
    """Calculate the transfer matrix of a drift.

    Parameters
    ----------
    gamma_in :
        Lorentz gamma at entry of drift.
    delta_s :
        Size of the drift in :unit:`mm`.
    omega_0_bunch :
        Pulsation of the beam.
    n_steps :
        Number of integration steps. The number of integration steps has no
        influence on the results. The default is one. It is different from
        unity when crossing a failed field map, as it allows to keep the same
        size of ``transfer_matrix`` and ``gamma_phi`` between nominal and fixed
        linacs.

    Returns
    -------
    transfer_matrix :
        (n_steps, 6, 6) array containing the transfer matrices.
    gamma_phi :
        (n_steps, 2) with Lorentz gamma in first column and relative phase in
        second column.
    itg_field :
        Dummy variable for consistency with the field map function.

    """
    gamma_in_min2 = gamma_in**-2
    transfer_matrix = np.full(
        (n_steps, 6, 6),
        np.array(
            [
                [1.0, delta_s, 0.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, delta_s, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 1.0, delta_s * gamma_in_min2],
                [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            ]
        ),
    )
    beta_in = np.sqrt(1.0 - gamma_in_min2)
    delta_phi = omega_0_bunch * delta_s / (beta_in * c)

    gamma_phi = np.empty((n_steps, 2))
    gamma_phi[:, 0] = gamma_in
    gamma_phi[:, 1] = np.arange(0.0, n_steps) * delta_phi + delta_phi
    return transfer_matrix, gamma_phi, None


def quad(
    gamma_in: float,
    delta_s: float,
    gradient: float,
    omega_0_bunch: float,
    q_adim: float,
    e_rest_mev: float,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, None]:
    """Calculate the transfer matrix of a quadrupole.

    Parameters
    ----------
    delta_s :
        Size of the drift in :unit:`m`.
    gamma_in :
        Lorentz gamma at entry of drift.
    n_steps :
        Number of integration steps. The number of integration steps has no
        influence on the results. The default is one. It is different from
        unity when crossing a failed field map, as it allows to keep the same
        size of ``transfer_matrix`` and ``gamma_phi`` between nominal and fixed
        linacs.
    gradient :
        Quadrupole gradient in :unit:`T/m`.
    omega_0_bunch :
        Pulsation of the beam.
    q_adim :
        Adimensioned charge of accelerated particle.
    e_rest_mev :
        Rest energy of the accelerated particle.

    Returns
    -------
    transfer_matrix :
        (1, 6, 6) array containing the transfer matrices.
    gamma_phi :
        (1, 2) with Lorentz gamma in first column and relative phase in
        second column.
    itg_field :
        Dummy variable for consistency with the field map function.

    """
    gamma_in_min2 = gamma_in**-2
    beta_in = np.sqrt(1.0 - gamma_in_min2)

    delta_phi = omega_0_bunch * delta_s / (beta_in * c)
    gamma_phi = np.empty((1, 2))
    gamma_phi[:, 0] = gamma_in
    gamma_phi[:, 1] = np.arange(0.0, 1) * delta_phi + delta_phi

    magnetic_rigidity = _magnetic_rigidity(
        beta_in, gamma_in, e_rest_mev=e_rest_mev
    )
    focusing_strength = _focusing_strength(gradient, magnetic_rigidity)

    if q_adim * gradient > 0.0:
        transfer_matrix = _horizontal_focusing_quadrupole(
            focusing_strength, delta_s, gamma_in_min2
        )
        return transfer_matrix, gamma_phi, None

    transfer_matrix = _horizontal_defocusing_quadrupole(
        focusing_strength, delta_s, gamma_in_min2
    )
    return transfer_matrix, gamma_phi, None


def _horizontal_focusing_quadrupole(
    focusing_strength: float, delta_s: float, gamma_in_min2: float
) -> np.ndarray:
    """Transfer matrix of a quadrupole focusing in horizontal plane."""
    _cos, _cosh, _sin, _sinh = _quadrupole_trigo_hyperbolic(
        focusing_strength, delta_s
    )
    transfer_matrix = np.full(
        (1, 6, 6),
        np.array(
            [
                [_cos, _sin / focusing_strength, 0.0, 0.0, 0.0, 0.0],
                [-focusing_strength * _sin, _cos, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, _cosh, _sinh / focusing_strength, 0.0, 0.0],
                [0.0, 0.0, focusing_strength * _sinh, _cosh, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 1.0, delta_s * gamma_in_min2],
                [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            ]
        ),
    )
    return transfer_matrix


def _horizontal_defocusing_quadrupole(
    focusing_strength: float, delta_s: float, gamma_in_min2: float
) -> np.ndarray:
    """Transfer matrix of a quadrupole defocusing in horizontal plane."""
    _cos, _cosh, _sin, _sinh = _quadrupole_trigo_hyperbolic(
        focusing_strength, delta_s
    )
    transfer_matrix = np.full(
        (1, 6, 6),
        np.array(
            [
                [_cosh, _sinh / focusing_strength, 0.0, 0.0, 0.0, 0.0],
                [focusing_strength * _sinh, _cosh, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, _cos, _sin / focusing_strength, 0.0, 0.0],
                [0.0, 0.0, -focusing_strength * _sin, _cos, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 1.0, delta_s * gamma_in_min2],
                [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            ]
        ),
    )
    return transfer_matrix


def field_map_rk4(
    gamma_in: float,
    d_z: float,
    n_steps: int,
    omega0_rf: float,
    k_e: float,
    phi_0_rel: float,
    e_spat: Callable[[float], float],
    q_adim: float,
    inv_e_rest_mev: float,
    omega_0_bunch: float,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Calculate the transfer matrix of a FIELD_MAP using Runge-Kutta."""
    z_rel = 0.0
    itg_field = 0.0
    half_dz = 0.5 * d_z

    # Constants to speed up calculation
    delta_phi_norm = omega0_rf * d_z / c
    delta_gamma_norm = q_adim * d_z * inv_e_rest_mev
    k_k = delta_gamma_norm * k_e

    transfer_matrix = np.empty((n_steps, 6, 6))
    gamma_phi = np.empty((n_steps + 1, 2))
    gamma_phi[0, 0] = gamma_in
    gamma_phi[0, 1] = 0.0

    # Define the motion function to integrate
    def du(z: float, u: np.ndarray) -> np.ndarray:
        r"""Compute variation of energy and phase.

        Parameters
        ----------
        z :
            Position where variation is calculated.
        u :
            First component is gamma. Second is phase in :unit:`rad`.

        Return
        ------
            First component is :math:`\delta gamma / \delta z` in :unit:`MeV/m`.
            Second is :math:`\delta \phi / \delta z` in :unit:`rad/m`.

        """
        v0 = k_k * e_func(z, e_spat, u[1], phi_0_rel)
        beta = np.sqrt(1.0 - u[0] ** -2)
        v1 = delta_phi_norm / beta
        return np.array([v0, v1])

    for i in range(n_steps):
        # Compute gamma and phase changes
        delta_gamma_phi = rk4(u=gamma_phi[i, :], du=du, x=z_rel, dx=d_z)

        # Update
        gamma_phi[i + 1, :] = gamma_phi[i, :] + delta_gamma_phi

        # Update itg_field. Used to compute V_cav and phi_s.
        itg_field += (
            k_e
            * e_func(z_rel, e_spat, gamma_phi[i, 1], phi_0_rel)
            * (1.0 + 1j * np.tan(gamma_phi[i, 1] + phi_0_rel))
            * d_z
        )

        # Compute gamma and phi at the middle of the thin lense
        gamma_phi_middle = gamma_phi[i, :] + 0.5 * delta_gamma_phi

        # To speed up (corresponds to the gamma_variation at the middle of the
        # thin lense at cos(phi + phi_0) = 1
        delta_gamma_middle_max = k_k * e_spat(z_rel + half_dz)

        e_spat1 = e_spat
        delta_e_max = (
            k_k * (e_spat(z_rel + 0.9999998 * d_z) - e_spat1(z_rel)) / d_z
        )
        # The term 0.9999998 to ensure the final step in inside the range for
        # the interpolation

        # Compute thin lense transfer matrix
        transfer_matrix[i, :, :] = thin_lense(
            gamma_phi[i, 0],
            gamma_phi[i + 1, 0],
            gamma_phi_middle,
            half_dz,
            delta_gamma_middle_max,
            phi_0_rel,
            omega0_rf,
            delta_e_max,
            omega_0_bunch=omega_0_bunch,
        )

        z_rel += d_z

    return transfer_matrix, gamma_phi[1:, :], itg_field


def thin_lense(
    gamma_in: float,
    gamma_out: float,
    gamma_phi_m: np.ndarray,
    half_dz: float,
    delta_gamma_m_max: float,
    phi_0: float,
    omega0_rf: float,
    delta_e_max: float,
    omega_0_bunch: float,
) -> np.ndarray:
    """Thin lense approximation: drift-acceleration-drift.

    Parameters
    ----------
    gamma_in :
        gamma at entrance of first drift.
    gamma_out :
        gamma at exit of first drift.
    gamma_phi_m :
        gamma and phase at the thin acceleration drift.
    half_dz :
        Half a spatial step in :unit:`m`.
    delta_gamma_m_max :
        Max gamma increase if the cos(phi + phi_0) of the acc. field is 1.
    phi_0 :
        Input phase of the cavity.
    omega0_rf :
        Pulsation of the cavity.
    delta_e_max :
        Derivative of the electric field.
    omega_0_bunch :
        Pulsation of the beam.

    Return
    ------
        Transfer matrix of the thin lense.

    """
    # Used for tm components
    beta_m = np.sqrt(1.0 - gamma_phi_m[0] ** -2)
    k_speed1 = delta_gamma_m_max / (gamma_phi_m[0] * beta_m**2)
    k_speed2 = k_speed1 * np.cos(gamma_phi_m[1] + phi_0)

    # Thin lense transfer matrices components
    k_1 = k_speed1 * omega0_rf / (beta_m * c) * np.sin(gamma_phi_m[1] + phi_0)
    k_2 = 1.0 - (2.0 - beta_m**2) * k_speed2
    k_3 = (1.0 - k_speed2) / k_2

    # New terms
    k_1a = (
        delta_e_max
        * np.cos(gamma_phi_m[1] + phi_0)
        / (gamma_phi_m[0] * beta_m**2)
    )
    k_1xy = -0.5 * k_1a + k_speed1 * beta_m * omega0_rf / (2 * c) * np.sin(
        gamma_phi_m[1] + phi_0
    )
    k_2xy = 1.0 - k_speed2
    k_3xy = (1.0 - k_speed2) / k_2xy

    transfer_matrix = drift(
        gamma_in=gamma_out, delta_s=half_dz, omega_0_bunch=omega_0_bunch
    )[0][0] @ (
        np.array(
            (
                [k_3xy, 0.0, 0.0, 0.0, 0.0, 0.0],
                [k_1xy, k_2xy, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, k_3xy, 0.0, 0.0, 0.0],
                [0.0, 0.0, k_1xy, k_2xy, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, k_3, 0.0],
                [0.0, 0.0, 0.0, 0.0, k_1, k_2],
            )
        )
        @ drift(
            gamma_in=gamma_in, delta_s=half_dz, omega_0_bunch=omega_0_bunch
        )[0][0]
    )
    return transfer_matrix


# =============================================================================
# Helpers
# =============================================================================
def _magnetic_rigidity(
    beta: float, gamma: float, e_rest_mev: float, **kwargs
) -> float:
    """Compute magnetic rigidity of particle."""
    return 1e6 * e_rest_mev * beta * gamma / c


def _focusing_strength(gradient: float, magnetic_rigidity: float) -> float:
    """Compute focusing strength of the quadrupole."""
    return np.sqrt(abs(gradient / magnetic_rigidity))


def _quadrupole_trigo_hyperbolic(
    focusing_strength: float, delta_s: float
) -> tuple[float, float, float, float]:
    """
    Pre-compute some parameters for the quadrupole transfer matrix.

    .. todo::
        As I am working on floats and not on np arrays, maybe the functions
        from the cmath package would be more adapted?
    """
    kdelta_s = focusing_strength * delta_s

    _cos = np.cos(kdelta_s)
    _cosh = np.cosh(kdelta_s)

    _sin = np.sin(kdelta_s)
    _sinh = np.sinh(kdelta_s)

    return _cos, _cosh, _sin, _sinh
