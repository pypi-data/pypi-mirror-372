"""Define :class:`Aperture`. It does nothing."""

from lightwin.core.elements.element import Element
from lightwin.tracewin_utils.line import DatLine


class Aperture(Element):
    """A dummy object."""

    base_name = "AP"
    increment_lattice_idx = False
    is_implemented = False

    def __init__(
        self,
        line: DatLine,
        dat_idx: int | None = None,
        **kwargs: str,
    ) -> None:
        """Force an element with null-length."""
        super().__init__(line, dat_idx, **kwargs)
        self.length_m = 0.0
