"""Define every element longitudinal transfer matrix.

Units are taken exactly as in TraceWin, i.e. first line is ``z (m)`` and second
line is ``dp/p``.

.. todo::
    Possible to use only lists here. May speed up the code, especially in _c.
    But numpy is fast, no?

.. todo::
    send beta as argument to avoid recomputing it each time

.. todo::
    Use :func:`e_func_complex` in :func:`z_field_map_rk4`?

.. todo::
    electric field interpolated twice: a first time for acceleration, and a
    second time to iterate itg_field. Maybe this could be done only once.

"""

import math
from collections.abc import Collection
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


# Could be faster I think
# Not used in field_map_rk4 for now
def e_func_complex(
    z: float, e_spat: Callable[[float], float], phi: float, phi_0: float
) -> complex:
    """Give the complex electric field at position z and phase phi.

    The field is normalized and should be multiplied by k_e.

    """
    return (
        e_spat(z) * math.cos(phi + phi_0) * (1.0 + 1j * math.tan(phi + phi_0))
    )


def e_funcs_scaled(
    z: float,
    e_spats: Collection[Callable[[float], float]],
    phi: float,
    phi_0s: Collection[float],
    scaling_factors: Collection[float],
) -> float:
    """Give the electric field at position z and phase phi w/ several maps.

    .. note::
        In contrary to :func:`e_func`, it is mandatory to give the
        field maps scaling factors here.

    """
    fields = [
        scaling * e_func(z, e_spat, phi, phi_0)
        for scaling, e_spat, phi_0 in zip(
            scaling_factors, e_spats, phi_0s, strict=True
        )
    ]

    return sum(fields)


def e_funcs_scaled_complex(
    z: float,
    e_spats: Collection[Callable[[float], float]],
    phi: float,
    phi_0s: Collection[float],
    scaling_factors: Collection[float],
) -> complex:
    """Give complex electric field at position z and phase phi w/ several maps.

    .. note::
        In contrary to :func:`e_func`, it is mandatory to give the
        field maps scaling factors here.

    """
    fields = [
        scaling * e_func_complex(z, e_spat, phi, phi_0)
        for scaling, e_spat, phi_0 in zip(
            scaling_factors, e_spats, phi_0s, strict=True
        )
    ]
    return sum(fields)


# =============================================================================
# Transfer matrices
# =============================================================================
def z_drift(
    gamma_in: float,
    delta_s: float,
    omega_0_bunch: float,
    n_steps: int = 1,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, None]:
    """Calculate the transfer matrix of a drift."""
    gamma_in_min2 = gamma_in**-2
    r_zz = np.full(
        (n_steps, 2, 2), np.array([[1.0, delta_s * gamma_in_min2], [0.0, 1.0]])
    )
    beta_in = math.sqrt(1.0 - gamma_in_min2)
    delta_phi = omega_0_bunch * delta_s / (beta_in * c)

    # Two possibilites: second one is faster
    # l_gamman = [gamma for i in range(n_steps)]
    # l_phi_rel = [(i+1)*delta_phi for i in range(n_steps)]
    # gamma_phi = np.empty((n_steps, 2))
    # gamma_phi[:, 0] = l_W_kin
    # gamma_phi[:, 1] = l_phi_rel
    gamma_phi = np.empty((n_steps, 2))
    gamma_phi[:, 0] = gamma_in
    gamma_phi[:, 1] = np.arange(0.0, n_steps) * delta_phi + delta_phi
    return r_zz, gamma_phi, None


def z_field_map_rk4(
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
) -> tuple[np.ndarray, np.ndarray, complex]:
    """Calculate the transfer matrix of a FIELD_MAP using Runge-Kutta."""
    z_rel = 0.0
    itg_field = 0.0
    half_dz = 0.5 * d_z

    # Constants to speed up calculation
    delta_phi_norm = omega0_rf * d_z / c
    delta_gamma_norm = q_adim * d_z * inv_e_rest_mev
    k_k = delta_gamma_norm * k_e

    r_zz = np.empty((n_steps, 2, 2))
    gamma_phi = np.empty((n_steps + 1, 2))
    gamma_phi[0, 0] = gamma_in
    gamma_phi[0, 1] = 0.0

    # Define the motion function to integrate
    def du(z: float, u: np.ndarray) -> np.ndarray:
        r"""
        Compute variation of energy and phase.

        Parameters
        ----------
        z :
            Position where variation is calculated.
        u :
            First component is gamma. Second is phase in rad.

        Return
        ------
            First component is :math:`\Delta \gamma / \Delta z` in
            :unit:`MeV/m`. Second is :math:`\Delta \phi / \Delta z` in
            :unit:`rad/m`.

        """
        v0 = k_k * e_func(z, e_spat, u[1], phi_0_rel)
        beta = np.sqrt(1.0 - u[0] ** -2)
        v1 = delta_phi_norm / beta
        return np.array([v0, v1])

    for i in range(n_steps):
        # Compute gamma and phase changes
        delta_gamma_phi = rk4(u=gamma_phi[i, :], du=du, x=z_rel, dx=d_z)

        gamma_phi[i + 1, :] = gamma_phi[i, :] + delta_gamma_phi

        itg_field += (
            k_e
            * e_func(z_rel, e_spat, gamma_phi[i, 1], phi_0_rel)
            * (1.0 + 1j * math.tan(gamma_phi[i, 1] + phi_0_rel))
            * d_z
        )

        # Compute gamma and phi at the middle of the thin lense
        gamma_phi_middle = gamma_phi[i, :] + 0.5 * delta_gamma_phi

        # To speed up (corresponds to the gamma_variation at the middle of the
        # thin lense at cos(phi + phi_0) = 1
        delta_gamma_middle_max = k_k * e_spat(z_rel + half_dz)

        # Compute thin lense transfer matrix
        r_zz[i, :, :] = z_thin_lense(
            gamma_phi[i, 0],
            gamma_phi[i + 1, 0],
            gamma_phi_middle,
            half_dz,
            delta_gamma_middle_max,
            phi_0_rel,
            omega0_rf,
            omega_0_bunch=omega_0_bunch,
        )

        z_rel += d_z

    return r_zz, gamma_phi[1:, :], itg_field


def z_superposed_field_maps_rk4(
    gamma_in: float,
    d_z: float,
    n_steps: int,
    omega0_rf: float,
    k_es: Collection[float],
    phi_0_rels: Collection[float],
    e_spats: Collection[Callable[[float], float]],
    omega_0_bunch: float,
    q_adim: float,
    inv_e_rest_mev: float,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, complex]:
    """Calculate the transfer matrix of superposed FIELD_MAP using RK."""
    z_rel = 0.0
    itg_field = 0.0
    half_dz = 0.5 * d_z

    # Constants to speed up calculation
    delta_phi_norm = omega0_rf * d_z / c
    delta_gamma_norm = q_adim * d_z * inv_e_rest_mev
    # k_k = delta_gamma_norm * k_e
    k_ks = [delta_gamma_norm * k_e for k_e in k_es]

    r_zz = np.empty((n_steps, 2, 2))
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
        v :
            First component is :math:`\Delta \gamma / \Delta z` in
            :unit:`MeV / m`.
            Second is :math:`\Delta \phi / \Delta z` in :unit:`rad / m`.

        """
        # v0 = k_k * e_func(z, e_spat, u[1], phi_0_rel)
        v0 = e_funcs_scaled(z, e_spats, u[1], phi_0_rels, k_ks)
        beta = np.sqrt(1.0 - u[0] ** -2)
        v1 = delta_phi_norm / beta
        return np.array([v0, v1])

    for i in range(n_steps):
        # Compute gamma and phase changes
        delta_gamma_phi = rk4(u=gamma_phi[i, :], du=du, x=z_rel, dx=d_z)

        gamma_phi[i + 1, :] = gamma_phi[i, :] + delta_gamma_phi

        # itg_field += (
        #     k_e
        #     * e_func(z_rel, e_spat, gamma_phi[i, 1], phi_0_rel)
        #     * (1.0 + 1j * math.tan(gamma_phi[i, 1] + phi_0_rel))
        #     * d_z
        # )
        itg_field += (
            e_funcs_scaled_complex(
                z_rel, e_spats, gamma_phi[i, 1], phi_0_rels, k_es
            )
            * d_z
        )

        # Compute gamma and phi at the middle of the thin lense
        gamma_phi_middle = gamma_phi[i, :] + 0.5 * delta_gamma_phi

        # To speed up (corresponds to the gamma_variation at the middle of the
        # thin lense at cos(phi + phi_0) = 1
        # delta_gamma_middle_max = k_k * e_spat(z_rel + half_dz)
        delta_gamma_middle_maxs = [
            k_k * e_spat(z_rel + half_dz) for k_k, e_spat in zip(k_ks, e_spats)
        ]

        # Compute thin lense transfer matrix
        r_zz[i, :, :] = z_thin_lense_superposed(
            gamma_phi[i, 0],
            gamma_phi[i + 1, 0],
            gamma_phi_middle,
            half_dz,
            delta_gamma_middle_maxs,
            phi_0_rels,
            omega0_rf,
            omega_0_bunch=omega_0_bunch,
            **kwargs,
        )

        z_rel += d_z

    return r_zz, gamma_phi[1:, :], itg_field


def z_field_map_leapfrog(
    d_z: float,
    gamma_in: float,
    n_steps: int,
    omega0_rf: float,
    k_e: float,
    phi_0_rel: float,
    e_spat: Callable[[float], float],
    q_adim: float,
    inv_e_rest_mev: float,
    gamma_init: float,
    omega_0_bunch: float,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, float]:
    """
    Calculate the transfer matrix of a ``FIELD_MAP`` using leapfrog.

    .. todo::
        clean, fix, separate leapfrog integration in dedicated module

    This method is less precise than RK4. However, it is much faster.

    Classic leapfrog method:
    speed(i+0.5) = speed(i-0.5) + accel(i) * dt
    pos(i+1)     = pos(i)       + speed(i+0.5) * dt

    Here, dt is not fixed but dz.
    z(i+1) += dz
    t(i+1) = t(i) + dz / (c beta(i+1/2))
    (time and space variables are on whole steps)
    beta calculated from W(i+1/2) = W(i-1/2) + qE(i)dz
    (speed/energy is on half steps)

    """
    z_rel = 0.0
    itg_field = 0.0
    half_dz = 0.5 * d_z

    # Constants to speed up calculation
    delta_phi_norm = omega0_rf * d_z / c
    delta_gamma_norm = q_adim * d_z * inv_e_rest_mev
    k_k = delta_gamma_norm * k_e

    r_zz = np.empty((n_steps, 2, 2))
    gamma_phi = np.empty((n_steps + 1, 2))
    gamma_phi[0, 1] = 0.0
    # Rewind energy from i=0 to i=-0.5 if we are at the first cavity:
    # FIXME must be cleaner
    if gamma_in == gamma_init:
        gamma_phi[0, 0] = gamma_in - 0.5 * k_k * e_func(
            z_rel, e_spat, gamma_phi[0, 1], phi_0_rel
        )
    else:
        gamma_phi[0, 0] = gamma_in

    for i in range(n_steps):
        # Compute gamma change
        delta_gamma = k_k * e_func(z_rel, e_spat, gamma_phi[i, 1], phi_0_rel)

        # New gamma at i+0.5
        gamma_phi[i + 1, 0] = gamma_phi[i, 0] + delta_gamma
        beta = np.sqrt(1.0 - gamma_phi[i + 1, 0] ** -2)

        # Compute phase at step i + 1
        delta_phi = delta_phi_norm / beta
        gamma_phi[i + 1, 1] = gamma_phi[i, 1] + delta_phi

        # Update itg_field. Used to compute V_cav and phi_s.
        itg_field += (
            k_e
            * e_func(z_rel, e_spat, gamma_phi[i, 1], phi_0_rel)
            * (1.0 + 1j * np.tan(gamma_phi[i, 1] + phi_0_rel))
            * d_z
        )

        # Compute gamma and phi at the middle of the thin lense
        gamma_phi_middle = np.array(
            [gamma_phi[i, 0], gamma_phi[i, 1] + 0.5 * delta_phi]
        )
        # We already are at the step i + 0.5, so gamma_middle and beta_middle
        # are the same as gamma and beta

        # To speed up (corresponds to the gamma_variation at the middle of the
        # thin lense at cos(phi + phi_0) = 1
        delta_gamma_middle_max = k_k * e_spat(z_rel + half_dz)

        # Compute thin lense transfer matrix
        r_zz[i, :, :] = z_thin_lense(
            gamma_phi[i, 0],
            gamma_phi[i + 1, 0],
            gamma_phi_middle,
            half_dz,
            delta_gamma_middle_max,
            phi_0_rel,
            omega0_rf,
            omega_0_bunch=omega_0_bunch,
        )

        z_rel += d_z

    return r_zz, gamma_phi[1:, :], itg_field


def z_thin_lense_new(
    scaled_e_middle: complex,
    gamma_in: float,
    gamma_out: float,
    gamma_middle: float,
    half_dz: float,
    omega0_rf: float,
    omega_0_bunch: float,
    **kwargs,
) -> np.ndarray:
    """
    Thin lense approximation: drift-acceleration-drift.

    Parameters
    ----------
    gamma_in :
        gamma at entrance of first drift.
    gamma_out :
        gamma at exit of first drift.
    gamma_middle :
        gamma at the thin acceleration drift.
    half_dz :
        Half a spatial step in :unit:`m`.
    omega0_rf :
        Pulsation of the cavity.

    Return
    ------
        Transfer matrix of the thin lense.

    """
    beta_m = math.sqrt(1.0 - gamma_middle**-2)
    scaled_e_middle /= gamma_middle * beta_m**2
    k_1 = scaled_e_middle.imag * omega0_rf / (beta_m * c)
    k_2 = 1.0 - (2.0 - beta_m**2) * scaled_e_middle.real
    k_3 = (1.0 - scaled_e_middle.real) / k_2

    # Faster than matmul or matprod_22
    r_zz_array = z_drift(gamma_out, half_dz, omega_0_bunch=omega_0_bunch)[0][
        0
    ] @ (
        np.array(([k_3, 0.0], [k_1, k_2]))
        @ z_drift(gamma_in, half_dz, omega_0_bunch=omega_0_bunch)[0][0]
    )
    return r_zz_array


def z_thin_lense(
    gamma_in: float,
    gamma_out: float,
    gamma_phi_m: np.ndarray,
    half_dz: float,
    delta_gamma_m_max: float,
    phi_0: float,
    omega0_rf: float,
    omega_0_bunch: float,
    **kwargs,
) -> np.ndarray:
    """
    Thin lense approximation: drift-acceleration-drift.

    Parameters
    ----------
    gamma_in :
        gamma at entrance of first drift.
    gamma_out :
        gamma at exit of first drift.
    gamma_phi_m :
        gamma and phase at the thin acceleration drift.
    half_dz :
        Half a spatial step in m.
    delta_gamma_m_max :
        Max gamma increase if the cos(phi + phi_0) of the acc. field is 1.
    phi_0 :
        Input phase of the cavity.
    omega0_rf :
        Pulsation of the cavity.
    omega_0_bunch :
        Pulsation of the beam.

    Return
    ------
        Transfer matrix of the thin lense.

    """
    # Used for tm components
    beta_m = math.sqrt(1.0 - gamma_phi_m[0] ** -2)
    k_speed1 = delta_gamma_m_max / (gamma_phi_m[0] * beta_m**2)
    k_speed2 = k_speed1 * math.cos(gamma_phi_m[1] + phi_0)

    # Thin lense transfer matrices components
    k_1 = (
        k_speed1 * omega0_rf / (beta_m * c) * math.sin(gamma_phi_m[1] + phi_0)
    )
    k_2 = 1.0 - (2.0 - beta_m**2) * k_speed2
    k_3 = (1.0 - k_speed2) / k_2

    # Faster than matmul or matprod_22
    r_zz_array = z_drift(gamma_out, half_dz, omega_0_bunch=omega_0_bunch)[0][
        0
    ] @ (
        np.array(([k_3, 0.0], [k_1, k_2]))
        @ z_drift(gamma_in, half_dz, omega_0_bunch=omega_0_bunch)[0][0]
    )
    return r_zz_array


def z_thin_lense_superposed(
    gamma_in: float,
    gamma_out: float,
    gamma_phi_m: np.ndarray,
    half_dz: float,
    delta_gamma_m_maxs: Collection[float],
    phi_0s: Collection[float],
    omega0_rf: float,
    omega_0_bunch: float,
    **kwargs,
) -> np.ndarray:
    """
    Compute trajectory with thin lense approximation: drift-acceleration-drift.

    Parameters
    ----------
    gamma_in :
        gamma at entrance of first drift.
    gamma_out :
        gamma at exit of first drift.
    gamma_phi_m :
        gamma and phase at the thin acceleration drift.
    half_dz :
        Half a spatial step in m.
    delta_gamma_m_maxs :
        Max gamma increase if the cos(phi + phi_0) of the acc. field is 1.
    phi_0s :
        Input phases of the elements.
    omega0_rf :
        Pulsation of the elements.
    omega_0_bunch :
        Bunch pulsation.

    Return
    ------
        Transfer matrix of the thin lense.

    """
    # Used for tm components
    beta_m = math.sqrt(1.0 - gamma_phi_m[0] ** -2)
    # k_speed1 = delta_gamma_m_max / (gamma_phi_m[0] * beta_m**2)
    # k_speed2 = k_speed1 * math.cos(gamma_phi_m[1] + phi_0)
    k_speed1s = [
        delta_gamma_m_max / (gamma_phi_m[0] * beta_m**2)
        for delta_gamma_m_max in delta_gamma_m_maxs
    ]
    k_speed2s = [
        k_speed1 * math.cos(gamma_phi_m[1] + phi_0)
        for k_speed1, phi_0 in zip(k_speed1s, phi_0s)
    ]

    # Thin lense transfer matrices components
    # k_1 = (
    #     k_speed1 * omega0_rf / (beta_m * c) * math.sin(gamma_phi_m[1] + phi_0)
    # )
    # k_2 = 1.0 - (2.0 - beta_m**2) * k_speed2
    # k_3 = (1.0 - k_speed2) / k_2
    k_1 = sum(
        [
            k_speed1
            * omega0_rf
            / (beta_m * c)
            * math.sin(gamma_phi_m[1] + phi_0)
            for k_speed1, phi_0 in zip(k_speed1s, phi_0s)
        ]
    )
    k_2 = sum([1.0 - (2.0 - beta_m**2) * k_speed2 for k_speed2 in k_speed2s])
    k_3 = sum([(1.0 - k_speed2) / k_2 for k_speed2 in k_speed2s])

    # Faster than matmul or matprod_22
    r_zz_array = z_drift(gamma_out, half_dz, omega_0_bunch=omega_0_bunch)[0][
        0
    ] @ (
        np.array(([k_3, 0.0], [k_1, k_2]))
        @ z_drift(gamma_in, half_dz, omega_0_bunch=omega_0_bunch)[0][0]
    )
    return r_zz_array


def z_bend(
    gamma_in: float,
    delta_s: float,
    factor_1: float,
    factor_2: float,
    factor_3: float,
    omega_0_bunch: float,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, None]:
    r"""Compute the longitudinal transfer matrix of a bend.

    ``factor_1`` is:

    .. math::
        \frac{-h^2\Delta s}{k_x^2}

    ``factor_2`` is:

    .. math::
        \frac{h^2 \sin{(k_x\Delta s)}}{k_x^3}

    ``factor_3`` is:

    .. math::
        \Delta s \left(1 - \frac{h^2}{k_x^2}\right)

    """
    gamma_in_min2 = gamma_in**-2
    beta_in_squared = 1.0 - gamma_in_min2

    topright = factor_1 * beta_in_squared + factor_2 + factor_3 * gamma_in_min2
    r_zz = np.eye(2)
    r_zz[0, 1] = topright

    delta_phi = omega_0_bunch * delta_s / (math.sqrt(beta_in_squared) * c)
    gamma_phi = np.array([gamma_in, delta_phi])
    return r_zz[np.newaxis, :], gamma_phi[np.newaxis, :], None
