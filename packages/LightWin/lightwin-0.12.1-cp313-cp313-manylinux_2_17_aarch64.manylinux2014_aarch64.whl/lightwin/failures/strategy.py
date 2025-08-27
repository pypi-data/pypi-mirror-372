"""Define the function related to the ``strategy`` key of ``wtf``.

In particular, it answers the question:
**Given this set of faults, which compensating cavities will be used?**

.. note::
    In order to add a compensation strategy, you must add it to the
    :data:`COMPENSATING_SELECTOR` dict, and also to the list of supported
    strategies in :mod:`.optimisation.wtf_specs` module.

"""

from collections.abc import Sequence
from functools import partial
from typing import Any, Literal

from lightwin.core.elements.field_maps.field_map import FieldMap
from lightwin.core.list_of_elements.helper import (
    group_elements_by_lattice,
    is_list_of_list_of_field_maps,
)
from lightwin.core.list_of_elements.list_of_elements import ListOfElements
from lightwin.failures.helper import (
    gather,
    nested_containing_desired,
    sort_by_position,
)
from lightwin.util.helper import flatten

cavities_id = Sequence[int] | Sequence[str]
nested_cavities_id = Sequence[Sequence[int]] | Sequence[Sequence[str]]


def failed_and_compensating(
    elts: ListOfElements,
    failed: cavities_id | nested_cavities_id,
    id_nature: Literal["cavity", "element", "name"],
    strategy: str,
    compensating_manual: nested_cavities_id | None = None,
    **wtf: Any,
) -> tuple[list[list[FieldMap]], list[list[FieldMap]]]:
    """Determine the compensating cavities for every failure."""
    failed_cavities = elts.take(failed, id_nature=id_nature)
    assert [cavity.can_be_retuned for cavity in flatten(failed_cavities)]
    elements = elts.tunable_cavities

    if strategy == "manual":
        assert (
            compensating_manual is not None
        ), f"With {strategy = } you must provide the compensating cavities."
        compensating_cavities = elts.take(
            compensating_manual, id_nature=id_nature
        )
        return manual(failed_cavities, compensating_cavities)

    fun_sort = partial(
        COMPENSATING_SELECTOR[strategy],
        elements=elements,
        elements_gathered_by_lattice=group_elements_by_lattice(elements),
        remove_failed=False,
        **wtf,
    )
    failed_gathered, compensating_gathered = gather(
        failed_elements=failed_cavities, fun_sort=fun_sort
    )
    return failed_gathered, compensating_gathered


def k_out_of_n[T](
    elements: Sequence[T],
    failed_elements: Sequence[T],
    *,
    k: int,
    tie_politics: str = "upstream first",
    shift: int = 0,
    remove_failed: bool = True,
    **kwargs,
) -> Sequence[T]:
    """Return ``k`` compensating cavities per failed in ``elts_of_interest``.

    Compensate the :math:`n` failed cavities with :math:`k\times n` closest
    cavities :cite:`saini_assessment_2021,Yee-Rendon2022a`.

    .. note::
        ``T`` can represent a :class:`.Element`, or a list of
        :class:`.Element`. Returned type/data structure will be the same as
        what was given in arguments. This function is hereby also used by
        :func:`l_neighboring_lattices` which gives in lattices.

    Parameters
    ----------
    elements :
        All the tunable elements/lattices/sections.
    failed_elements :
        Failed cavities/lattice.
    k :
        Number of compensating cavity per failure.
    tie_politics :
        When two elements have the same position, will you want to have the
        upstream or the downstream first?
    shift :
        Distance increase for downstream elements (``shift < 0``) or upstream
        elements (``shift > 0``). Used to have a window of compensating
        cavities which is not centered around the failed elements.

    Returns
    -------
        Contains all the altered elements/lattices. The ``n`` first are failed,
        the ``k * n`` following are compensating.

    """
    sorted_by_position = sort_by_position(
        elements,
        failed_elements,
        tie_politics,
        shift,
    )
    n = len(failed_elements)
    altered = sorted_by_position[: n + k * n]
    if remove_failed:
        return altered[n:]
    return altered


def l_neighboring_lattices[T](
    elements_gathered_by_lattice: Sequence[Sequence[T]],
    failed_elements: Sequence[T],
    *,
    l: int,
    tie_politics: str = "upstream first",
    shift: int = 0,
    remove_failed: bool = True,
    min_number_of_cavities_in_lattice: int = 1,
    **kwargs,
) -> Sequence[T]:
    """Select full lattices neighboring the failed cavities.

    Every fault will be compensated by ``l`` full lattices, direct neighbors of
    the errors :cite:`Bouly2014,Placais2022a`. You must provide ``l``.
    Non-failed cavities in the same lattice as the failure are also used.

    Parameters
    ----------
    elements_by_lattice :
        Tunable elements sorted by lattice.
    failed_elements :
        Failed cavities/lattice.
    l :
        Number of compensating lattice per failure.
    tie_politics :
        When two elements have the same position, will you want to have the
        upstream or the downstream first?
    shift :
        Distance increase for downstream elements (``shift < 0``) or upstream
        elements (``shift > 0``). Used to have a window of compensating
        cavities which is not centered around the failed elements.
    remove_failed :
        To remove the failed lattices from the output.
    min_number_of_cavities_in_lattice :
        If a lattice has less than this number of functional cavities, we
        look for another lattice. This is designed to removed lattices which
        have no cavities. Note that lattices that have some functional cavities
        but not enough will be used for compensation anyway.

    Returns
    -------
        Contains all the altered cavities.

    """
    lattices_with_a_fault = nested_containing_desired(
        elements_gathered_by_lattice, failed_elements
    )

    elements_gathered_by_lattice = [
        x
        for x in elements_gathered_by_lattice
        if len(x) >= min_number_of_cavities_in_lattice
        or x in lattices_with_a_fault
    ]

    compensating_lattices = k_out_of_n(
        elements_gathered_by_lattice,
        lattices_with_a_fault,
        k=l,
        tie_politics=tie_politics,
        shift=shift,
        remove_failed=True,
    )
    for lattice in compensating_lattices:
        if len(lattice) >= min_number_of_cavities_in_lattice:
            continue
        elements_gathered_by_lattice.remove(lattice)

    altered_lattices = k_out_of_n(
        elements_gathered_by_lattice,
        lattices_with_a_fault,
        k=l,
        tie_politics=tie_politics,
        shift=shift,
        remove_failed=False,
    )

    altered_cavities = [x for x in flatten(altered_lattices)]
    if remove_failed:
        altered_cavities = [
            x for x in altered_cavities if x not in failed_elements
        ]

    return altered_cavities


def manual(
    failed_cavities: Sequence[list[FieldMap]],
    compensating_cavities: list[list[FieldMap]] | Any,
) -> tuple[list[list[FieldMap]], list[list[FieldMap]]]:
    """Associate failed with compensating cavities."""
    assert is_list_of_list_of_field_maps(
        failed_cavities
    ), f"{failed_cavities = } is not a nested list of cavities."
    assert is_list_of_list_of_field_maps(
        compensating_cavities
    ), f"{compensating_cavities = } is not a nested list of cavities."
    assert len(failed_cavities) == len(compensating_cavities), (
        f"Mismatch between {len(failed_cavities) = } and "
        f"{len(compensating_cavities) = }"
    )
    return failed_cavities, compensating_cavities


def global_compensation[T](
    elements: Sequence[T],
    failed_elements: Sequence[T],
    *,
    remove_failed: bool = True,
    **kwargs,
) -> Sequence[T]:
    """Give all the cavities of the linac.

    Parameters
    ----------
    elements :
        All the tunable elements.
    failed_elements :
        Failed cavities.

    Returns
    -------
        Contains all the altered elements.

    """
    if not remove_failed:
        return elements
    altered = [x for x in elements if x not in failed_elements]
    return altered


def global_downstream[T](
    elements: Sequence[T],
    failed_elements: Sequence[T],
    *,
    remove_failed: bool = True,
    **kwargs,
) -> Sequence[T]:
    """Give all the cavities after failure of the linac.

    Parameters
    ----------
    elements :
        All tunable the elements.
    failed_elements :
        Failed cavities.

    Returns
    -------
        Contains all the altered elements.

    """
    indexes = [elements.index(cavity) for cavity in failed_elements]
    first_index = min(indexes)
    altered = elements[first_index:]
    if not remove_failed:
        return altered
    altered = [x for x in altered if x not in failed_elements]
    return altered


COMPENSATING_SELECTOR = {
    "k out of n": k_out_of_n,
    "l neighboring lattices": l_neighboring_lattices,
    "global": global_compensation,
    "global_downstream": global_downstream,
    "manual": manual,
}  #:
