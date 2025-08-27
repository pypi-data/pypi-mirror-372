"""Set initial values/limits in :class:`.DesignSpaceFactory`."""

import math
from typing import overload

import numpy as np

from lightwin.core.elements.element import Element
from lightwin.core.elements.field_maps.field_map import FieldMap
from lightwin.util.typing import GETTABLE_ELT_T, GETTABLE_FIELD_MAP_T


@overload
def same_value_as_nominal(
    variable: GETTABLE_ELT_T, reference_element: Element, **kwargs
) -> float: ...


@overload
def same_value_as_nominal(
    variable: GETTABLE_FIELD_MAP_T, reference_element: FieldMap, **kwargs
) -> float: ...


def same_value_as_nominal(
    variable: GETTABLE_ELT_T | GETTABLE_FIELD_MAP_T,
    reference_element: Element | FieldMap,
    **kwargs,
) -> float:
    """Return ``variable`` value in ``reference_element``.

    This is generally a good initial value for optimisation.

    """
    reference_value = reference_element.get(variable, to_numpy=False)
    return reference_value


def phi_s_limits(
    reference_element: FieldMap,
    max_increase_sync_phase_in_percent: float,
    max_absolute_sync_phase_in_deg: float = 0.0,
    min_absolute_sync_phase_in_deg: float = -90.0,
    **kwargs,
) -> tuple[float, float]:
    r"""Return classic limits for the synchronous phase.

    Minimum is ``min_absolute_sync_phase_in_deg``, which is -90 degrees by
    default. Maximum is nominal synchronous phase +
    ``max_increase_in_percent``, or ``max_absolute_sync_phase_in_deg`` which is
    0 degrees by default.

    Parameters
    ----------
    reference_element :
        Element in its nominal tuning.
    max_increase_in_percent :
        Maximum increase of the synchronous phase in percent.
    max_absolute_sync_phase_in_deg :
        Maximum absolute synchronous phase in radians. The default is 0.
    min_absolute_sync_phase_in_deg :
        Minimum absolute synchronous phase in radians. The default is
        :math:`-\pi / 2`.

    Returns
    -------
        Lower and upper limits for the synchronous phase.

    """
    reference_phi_s = same_value_as_nominal("phi_s", reference_element)
    phi_s_min = math.radians(min_absolute_sync_phase_in_deg)
    phi_s_max = min(
        math.radians(max_absolute_sync_phase_in_deg),
        reference_phi_s * (1.0 - 1e-2 * max_increase_sync_phase_in_percent),
    )
    return (phi_s_min, phi_s_max)


def phi_0_limits(**kwargs) -> tuple[float, float]:
    r"""Return classic limits for the absolute or relative rf phase.

    Returns
    -------
        Always :math:`(-2\pi, 2\pi)`.

    """
    return (-2.0 * math.pi, 2.0 * math.pi)


def k_e_limits(
    reference_element: FieldMap,
    max_decrease_k_e_in_percent: float,
    max_increase_k_e_in_percent: float,
    maximum_k_e_is_calculated_wrt_maximum_k_e_of_section: bool = False,
    reference_elements: list[Element] | None = None,
    **kwargs,
) -> tuple[float, float]:
    r"""Get classic limits for ``k_e``.

    Parameters
    ----------
    reference_element :
        The nominal element.
    max_decrease_in_percent :
        Allowed decrease in percent with respect to the nominal ``k_e``.
    max_increase_in_percent :
        Allowed increase in percent with respect to the nominal ``k_e``.
    maximum_k_e_is_calculated_wrt_maximum_k_e_of_section :
        Use this flag to compute allowed increase of ``k_e`` with respect to
        the maximum ``k_e`` of the section, instead of the ``k_e`` of the
        nominal cavity. This is what we used in :cite:`Placais2022a`.
    reference_elements :
        List of the nominal elements. Must be provided if
        ``maximum_k_e_is_calculated_wrt_maximum_k_e_of_section`` is True.

    Returns
    -------
        Lower and upper bounds for ``k_e``.

    """
    reference_k_e = same_value_as_nominal("k_e", reference_element)
    min_k_e = reference_k_e * (1.0 - 1e-2 * max_decrease_k_e_in_percent)
    max_k_e = reference_k_e * (1.0 + 1e-2 * max_increase_k_e_in_percent)

    if not maximum_k_e_is_calculated_wrt_maximum_k_e_of_section:
        return (min_k_e, max_k_e)

    section_idx = reference_element.idx["section"]
    assert reference_elements is not None
    max_k_e_of_section = _get_maximum_k_e_of_section(
        section_idx, reference_elements
    )
    max_k_e = max_k_e_of_section * (1.0 + 1e-2 * max_increase_k_e_in_percent)
    return (min_k_e, max_k_e)


def _get_maximum_k_e_of_section(
    section_idx: int,
    reference_elements: list[Element],
) -> float:
    """Get the maximum ``k_e`` of section."""
    elements_in_current_section = list(
        filter(
            lambda element: element.idx["section"] == section_idx,
            reference_elements,
        )
    )
    k_e_in_current_section = [
        (
            element.get("k_e", to_numpy=False)
            if isinstance(element, FieldMap)
            else np.nan
        )
        for element in elements_in_current_section
    ]
    maximum_k_e = np.nanmax(k_e_in_current_section)
    return maximum_k_e


LIMITS_CALCULATORS = {
    "phi_s": phi_s_limits,
    "phi_0_abs": phi_0_limits,
    "phi_0_rel": phi_0_limits,
    "k_e": k_e_limits,
}
