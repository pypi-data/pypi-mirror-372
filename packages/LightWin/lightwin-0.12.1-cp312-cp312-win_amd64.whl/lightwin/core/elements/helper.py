"""Define helper functions applying on elements."""

import logging
from collections.abc import Sequence
from pprint import pformat

from lightwin.core.elements.element import Element


def give_name_to_elements(
    elts: Sequence[Element], warn_default_element_names: bool = True
) -> None:
    """Give to every :class:`.Element` the name TraceWin would give it."""
    civil_register: dict[str, int] = {}
    elements_with_a_default_name = []
    for elt in elts:
        if name := elt._personalized_name:
            if name not in civil_register:
                civil_register[name] = 1
                continue
            nth = civil_register[name] + 1
            elt._personalized_name = f"{name}_{nth}"
            logging.info(
                f"Duplicate personalized name found: {name}. Renaming to "
                f"{elt._personalized_name}."
            )
            civil_register[name] = nth
            continue

        nth = civil_register.get(name := elt.base_name, 0) + 1
        elt._default_name = f"{name}{nth}"
        civil_register[name] = nth
        if name == "ELT":
            elements_with_a_default_name.append(elt)

    if not warn_default_element_names:
        return

    if (fallback_name := Element.base_name) not in civil_register:
        return
    logging.warning(
        f"Used a fallback name for {civil_register[fallback_name]} elements. "
        "Check that every subclass of Element that you use overrides the "
        f"default Element.base_name = {fallback_name}. Faulty elements:\n"
        f"{pformat(elements_with_a_default_name, width=120)}"
    )


def force_a_section_for_every_element(elts: Sequence[Element]) -> None:
    """Give a section index to every element."""
    idx_section = 0
    for elt in elts:
        idx = elt.idx["section"]
        if idx < 0:
            elt.idx["section"] = idx_section
            continue
        idx_section = idx
    return


def force_a_lattice_for_every_element(elts: Sequence[Element]) -> None:
    """Give a lattice index to every element.

    Elements before the first LATTICE command will be in the same lattice as
    the elements after the first LATTICE command.

    Elements after the first LATTICE command will be in the previous lattice.

    Example
    -------
    .. list-table ::
        :widths: 10 10 10
        :header-rows: 1

        * - Element/Command
          - Lattice before
          - Lattice after
        * - ``QP1``
          - None
          - 0
        * - ``DR1``
          - None
          - 0
        * - ``LATTICE``
          -
          -
        * - ``QP2``
          - 0
          - 0
        * - ``DR2``
          - 0
          - 0
        * - ``END LATTICE``
          -
          -
        * - ``QP3``
          - None
          - 0
        * - ``LATTICE``
          -
          -
        * - ``DR3``
          - 1
          - 1
        * - ``END LATTICE``
          -
          -
        * - ``QP4``
          - None
          - 1
    """
    idx_lattice = 0
    for elt in elts:
        idx = elt.idx["lattice"]
        if idx < 0:
            elt.idx["lattice"] = idx_lattice
            continue
        idx_lattice = idx
