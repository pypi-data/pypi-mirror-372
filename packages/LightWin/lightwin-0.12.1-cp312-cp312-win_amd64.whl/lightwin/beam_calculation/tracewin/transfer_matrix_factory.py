"""Provide an easy way to generate :class:`.TransferMatrix`."""

import logging
import os

import numpy as np

from lightwin.core.elements.element import ELEMENT_TO_INDEX_T
from lightwin.core.transfer_matrix.factory import TransferMatrixFactory
from lightwin.core.transfer_matrix.transfer_matrix import TransferMatrix
from lightwin.tracewin_utils import load


class TransferMatrixFactoryTraceWin(TransferMatrixFactory):
    """Provide a method for easy creation of :class:`.TransferMatrix`."""

    def _load_transfer_matrices(
        self,
        path_cal: str,
        filename: str = "Transfer_matrix1.dat",
        high_def: bool = False,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get the full transfer matrices calculated by TraceWin.

        Parameters
        ----------
        filename :
            The name of the transfer matrix file produced by TraceWin. The
            default is ``"Transfer_matrix1.dat"``.
        high_def :
            To get the transfer matrices at all the solver step, instead at the
            elements exit only. The default is False. Currently not
            implemented.

        Returns
        -------
        element_numbers :
            Number of the elements.
        position_in_m :
            Position of the elements.
        transfer_matrices :
            Cumulated transfer matrices of the elements.

        """
        if high_def:
            logging.error(
                "High definition not implemented. Can only import transfer "
                "matrices @ element positions."
            )
            high_def = False

        path = os.path.join(path_cal, filename)
        elements_numbers, position_in_m, transfer_matrices = (
            load.transfer_matrices(path)
        )
        logging.debug(f"successfully loaded {path}")
        return elements_numbers, position_in_m, transfer_matrices

    def run(
        self,
        tm_cumul_in: np.ndarray,
        path_cal: str,
        element_to_index: ELEMENT_TO_INDEX_T,
    ) -> TransferMatrix:
        r"""Load the TraceWin transfer matrix file and create the object.

        Parameters
        ----------
        tm_cumul_in :
            Cumulated transfer matrix at entrance of linac or linac subset.
        path_cal :
            Full path to transfer matrix file.
        element_to_index :
            to doc

        Returns
        -------
            The various transfer matrices in the :math:`[x-x']`, :math:`[y-y']`
            and :math:`[z-\delta]` planes.

        """
        _, _, cumulated = self._load_transfer_matrices(path_cal)
        transfer_matrix = TransferMatrix(
            self.is_3d,
            first_cumulated_transfer_matrix=tm_cumul_in,
            cumulated=cumulated,
            element_to_index=element_to_index,
        )
        return transfer_matrix
