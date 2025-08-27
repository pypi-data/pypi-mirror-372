"""Define the REPEAT_ELE command."""

import logging
from collections.abc import Sequence
from copy import deepcopy

from lightwin.core.commands.command import Command
from lightwin.core.commands.lattice import Lattice, LatticeEnd
from lightwin.core.commands.set_adv import SetAdv
from lightwin.core.instruction import Comment, Instruction
from lightwin.tracewin_utils.line import DatLine


class RepeatEle(Command):
    """Repeat the ``n`` following elements ``k`` times."""

    is_implemented = True
    n_attributes = 2

    def __init__(
        self, line: DatLine, dat_idx: int | None = None, **kwargs: str
    ) -> None:
        """Instantiate object."""
        logging.warning(
            "REPEAT_ELE under implementation. Behavior not tested w.r.t "
            "lattice number."
        )
        super().__init__(line, dat_idx)
        self.k_times = int(line.splitted[1])
        self.n_following = int(line.splitted[2])

    def set_influenced_elements(
        self, instructions: Sequence[Instruction], **kwargs: float
    ) -> None:
        """Capture ``n`` following elements, as well as their commands."""
        start = self.idx["dat_idx"] + 1

        number_of_elements = 0
        stop = start
        for instruction in instructions[start:]:

            if number_of_elements == self.n_following:
                self.influenced = slice(start, stop)
                return

            stop += 1
            if isinstance(instruction, RepeatEle):
                raise OSError("I think nested REPEAT_ELE are not allowed.")

            if isinstance(instruction, (Lattice, LatticeEnd)):
                logging.info(
                    "Lattice indexes should be OK, but section number may bug."
                )

            if isinstance(instruction, SetAdv):
                logging.error(
                    "According to doc, SET_ADV commands should not be "
                    "duplicated. Still unsure about how I will treat that."
                )
                continue

            if isinstance(instruction, (Command, Comment)):
                continue

            number_of_elements += 1
        raise OSError("Reached end of file without completing REPEAT_ELE.")

    def apply(
        self, instructions: list[Instruction], **kwargs: float
    ) -> list[Instruction]:
        """Copy the ``n`` elements ``k`` times."""
        repeated_instructions = instructions[self.influenced]
        period_length = len(repeated_instructions)
        for _ in range(self.k_times - 1):
            for instruction in repeated_instructions:
                copied_instruction = deepcopy(instruction)
                copied_instruction.increment_dat_position(
                    increment=period_length
                )
                copied_instruction.insert_object(instructions)
        return instructions
