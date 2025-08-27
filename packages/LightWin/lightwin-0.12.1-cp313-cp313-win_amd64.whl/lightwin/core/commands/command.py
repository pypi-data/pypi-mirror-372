"""Define the base class from which all commands will inherit."""

from abc import abstractmethod
from collections.abc import Iterable, Sequence
from typing import override

from lightwin.core.instruction import Instruction
from lightwin.tracewin_utils.line import DatLine


class Command(Instruction):
    """A generic Command class.

    Parameters
    ----------
    idx :
        Dictionary holding useful indexes. Keys are ``'dat_idx'`` (position in
        the ``DAT`` file) and ``'influenced_elements'`` (position in the
        ``DAT`` file of the elements concerned by current command).
    line :
        Line in the ``DAT`` file corresponding to current command.

    See Also
    --------
    :meth:`.ListOfElementsFactory.subset_list_run`
    :func:`.dat_filecontent_from_smaller_list_of_elements`

    """

    def __init__(
        self, line: DatLine, dat_idx: int | None = None, **kwargs
    ) -> None:
        """Instantiate mandatory attributes."""
        super().__init__(line, dat_idx, **kwargs)
        self.influenced = slice(0, 1)

    def set_influenced_elements(
        self, instructions: list[Instruction], **kwargs: float
    ) -> None:
        """Determine the index of the elements concerned by :func:`apply`."""
        start = self.idx["dat_idx"] + 1
        influenced = self._indexes_between_this_command_and(
            instructions[start:], type(self)
        )
        self.influenced = influenced
        return

    @abstractmethod
    def apply(
        self, instructions: list[Instruction], **kwargs: float
    ) -> list[Instruction]:
        """Apply the command."""
        return instructions

    def concerns_one_of(self, dat_indexes: Iterable[int]) -> bool:
        """Tell if ``self`` concerns an element, which ``dat_idx`` is given.

        Internally, we convert the ``self.influenced`` from a :class:`set` to
        a :class:`list` object and check intersections with ``dat_indexes``.

        Parameters
        ----------
        dat_indexes :
            Indexes in the ``DAT`` file of the sub-list of elements under
            creation.

        """
        idx_influenced = range(self.influenced.start, self.influenced.stop)
        idx_influenced = [i for i in idx_influenced]

        intersect = list(set(idx_influenced).intersection(dat_indexes))
        return len(intersect) > 0

    def _indexes_between_this_command_and(
        self,
        instructions_after_self: Sequence[Instruction],
        *stop_types: type,
    ) -> slice:
        """
        Determine the indexes of the instructions affected by an instruction.

        We return the indexes of instructions between the first of
        ``instructions`` and the first instruction which type is in
        ``stop_types``.

        Parameters
        ----------
        instructions_after_self :
            All instructions after ``self`` (``self`` not included).
        stop_types :
            Type(s) of commands after which ``self`` has no influence. If not
            provided, we set it to the type of ``self``. In other words, a
            ``FREQ`` influences every element up to the following ``FREQ``.

        Returns
        -------
            All the indexes of the instrutions that will be affected by self.

        """
        if len(stop_types) == 0:
            stop_types = (type(self),)
        start = self.idx["dat_idx"] + 1
        i = 0
        for i, instruction in enumerate(instructions_after_self):
            if isinstance(instruction, stop_types):
                break
        influenced = slice(start, start + i)
        return influenced

    @override
    def increment_dat_position(self, increment: int = 1) -> None:
        """Increment dat_index and indexes of elements concerned by command."""
        self.influenced = slice(
            self.influenced.start + increment, self.influenced.stop + increment
        )
        return super().increment_dat_position(increment)
