"""Define an object to create :class:`.ListOfElements`.

Its main goal is to initialize :class:`.ListOfElements` with the proper input
synchronous particle and beam properties.
:meth:`.whole_list_run` is called within the :class:`.Accelerator` and generate
a full :class:`.ListOfElements` from scratch.

:meth:`.subset_list_run` is called within :class:`.Fault` and generates a
:class:`.ListOfElements` that contains only a fraction of the linac.

.. todo::
    Also handle ``DST`` file in :meth:`.subset_list_run`.

.. todo::
    Maybe it will be necessary to handle cases where the synch particle is not
    perfectly on the axis?

.. todo::
    Find a smart way to sublass :class:`.ListOfElementsFactory` according to
    the :class:`.BeamCalculator`... Loading field maps not necessary with
    :class:`.TraceWin` for example.

.. todo::
    The ``elements_to_dump`` key should be in the configuration file

"""

import logging
import shutil
from abc import ABCMeta
from collections.abc import Collection
from pathlib import Path
from typing import Any

import numpy as np

from lightwin.beam_calculation.simulation_output.simulation_output import (
    SimulationOutput,
)
from lightwin.core.beam_parameters.factory import InitialBeamParametersFactory
from lightwin.core.elements.element import Element
from lightwin.core.elements.field_maps.field_map import FieldMap
from lightwin.core.instruction import Instruction
from lightwin.core.instructions_factory import InstructionsFactory
from lightwin.core.list_of_elements.list_of_elements import (
    FilesInfo,
    ListOfElements,
)
from lightwin.core.particle import ParticleInitialState
from lightwin.tracewin_utils.dat_files import (
    dat_filecontent_from_file,
    dat_filecontent_from_smaller_list_of_elements,
    export_dat_filecontent,
)
from lightwin.tracewin_utils.line import DatLine
from lightwin.util.typing import BeamKwargs


class ListOfElementsFactory:
    """Factory class to create list of elements from different contexts."""

    def __init__(
        self,
        is_3d: bool,
        is_multipart: bool,
        default_field_map_folder: Path,
        beam_kwargs: BeamKwargs,
        load_field_maps: bool = True,
        field_maps_in_3d: bool = False,
        load_cython_field_maps: bool = False,
        elements_to_dump: ABCMeta | tuple[ABCMeta, ...] = (),
    ):
        """Declare and create some mandatory factories.

        .. note::
            For now, we have only one ``input_beam`` parameters, we create only
            one :class:`.ListOfElements`. Hence we create in the most general
            way possible.
            We instantiate :class:`.InitialBeamParametersFactory` with
            ``is_3d=True`` and ``is_multipart=True`` because it will work with
            all the :class:`.BeamCalculator` objects -- some phase-spaces may
            be created but never used though.

        Parameters
        ----------
        phi_s_definition :
            Definition for the synchronous phases that will be used. Allowed
            values are in :data:`.PHI_S_MODELS`. The default is
            ``'historical'``.

        """
        freq_bunch_mhz = beam_kwargs["f_bunch_mhz"]
        assert isinstance(freq_bunch_mhz, float)

        self.initial_beam_factory = InitialBeamParametersFactory(
            # Useless with Envelope1D
            is_3d=True,
            # Useless with Envelope1D, Envelope3D, TraceWin if partran = 0
            is_multipart=True,
            beam_kwargs=beam_kwargs,
        )

        self.instructions_factory = InstructionsFactory(
            freq_bunch_mhz,
            default_field_map_folder,
            load_field_maps,
            field_maps_in_3d,
            load_cython_field_maps,
            elements_to_dump=elements_to_dump,
        )

    def whole_list_run(
        self,
        dat_file: Path,
        accelerator_path: Path,
        instructions_to_insert: Collection[Instruction | DatLine] = (),
        **kwargs: Any,
    ) -> ListOfElements:
        """Create a new :class:`.ListOfElements`, encompassing a full linac.

        Factory function called from within the :class:`.Accelerator` object.

        Parameters
        ----------
        dat_file :
            Absolute path to the ``DAT`` file.
        accelerator_path :
            Absolute path where results for each :class:`.BeamCalculator` will
            be stored.
        instructions_to_insert :
            Some elements or commands that are not present in the ``DAT`` file
            but that you want to add. The default is an empty tuple.
        kwargs :
            Arguments to instantiate the input particle and beam properties.

        Returns
        -------
            Contains all the :class:`.Element` of the linac, as well as the
            proper particle and beam properties at its entry.

        """
        logging.info(
            "First initialisation of ListOfElements, ecompassing all linac. "
            f"Created with {dat_file = }"
        )

        dat_filecontent = dat_filecontent_from_file(
            dat_file, keep="all", instructions_to_insert=instructions_to_insert
        )
        instructions = self.instructions_factory.run(dat_filecontent)
        elts = [x for x in instructions if isinstance(x, Element)]

        files: FilesInfo = {
            "dat_file": dat_file,
            "dat_filecontent": dat_filecontent,
            "accelerator_path": accelerator_path,
            "elts_n_cmds": instructions,
        }

        input_particle = self._whole_list_input_particle(**kwargs)
        input_beam = self.initial_beam_factory.factory_new(
            sigma_in=kwargs["sigma_in"], w_kin=kwargs["w_kin"]
        )

        tm_cumul_in = np.eye(6)
        list_of_elements = ListOfElements(
            elts=elts,
            input_particle=input_particle,
            input_beam=input_beam,
            tm_cumul_in=tm_cumul_in,
            files=files,
            first_init=True,
        )
        return list_of_elements

    def _whole_list_input_particle(
        self, w_kin: float, phi_abs: float, z_in: float, **kwargs: np.ndarray
    ) -> ParticleInitialState:
        """Create a :class:`.ParticleInitialState` for full list of elts."""
        input_particle = ParticleInitialState(
            w_kin=w_kin,
            phi_abs=phi_abs,
            z_in=z_in,
            synchronous=True,
        )
        return input_particle

    def subset_list_run(
        self,
        elts: list[Element],
        simulation_output: SimulationOutput,
        files_from_full_list_of_elements: FilesInfo,
    ) -> ListOfElements:
        """Create a :class:`.ListOfElements` as subset of a previous one.

        Factory function used during the fitting process, called by a
        :class:`.Fault` object. During this optimisation process, we compute
        the propagation of the beam only on the smallest possible subset of the
        linac.

        It creates the proper :class:`.ParticleInitialState` and
        :class:`.BeamParameters` objects. In contrary to
        :meth:`whole_list_run`, the :class:`.BeamParameters` must contain
        information on the transverse plane if beam propagation is performed
        with :class:`.TraceWin`.

        Parameters
        ----------
        elts :
            A plain list containing the elements objects that the object should
            contain.
        simulation_output :
            Holds the results of the pre-existing list of elements.
        files_from_full_list_of_elements :
            The `files` attribute of :class:`.ListOfElements` from the full
            :class:`.ListOfElements`.

        Returns
        -------
            Contains all the elements that will be recomputed during the
            optimisation, as well as the proper particle and beam properties at
            its entry.

        """
        logging.info(
            "Initalisation of ListOfElements from already initialized"
            f" elements: {elts[0]} to {elts[-1]}."
        )

        input_elt, input_pos = self._get_initial_element(
            elts, simulation_output
        )
        get_kw = {
            "elt": input_elt,
            "pos": input_pos,
            "to_numpy": False,
        }
        input_particle = self._subset_input_particle(
            simulation_output, **get_kw
        )
        input_beam = self.initial_beam_factory.factory_subset(
            simulation_output, get_kw
        )

        files = self._subset_files_dictionary(
            elts,
            files_from_full_list_of_elements,
        )

        transfer_matrix = simulation_output.transfer_matrix
        assert transfer_matrix is not None
        tm_cumul_in = transfer_matrix.cumulated[0]

        list_of_elements = ListOfElements(
            elts=elts,
            input_particle=input_particle,
            input_beam=input_beam,
            tm_cumul_in=tm_cumul_in,
            files=files,
            first_init=False,
        )

        return list_of_elements

    def _shift_entry_phase(
        self, cavities: list[FieldMap], delta_phi: float
    ) -> None:
        """Shift the entry phase in the given cavities.

        This is mandatory for TraceWin solver, as the absolute phase at the
        entrance of the first element is always 0.0.

        """
        pass

    def _subset_files_dictionary(
        self,
        elts: list[Element],
        files_from_full_list_of_elements: FilesInfo,
        folder: Path | str = Path("tmp"),
        dat_name: Path | str = Path("tmp.dat"),
    ) -> FilesInfo:
        """Set the new ``DAT`` file containing only elements of ``elts``."""
        accelerator_path = files_from_full_list_of_elements["accelerator_path"]
        out = accelerator_path / folder
        out.mkdir(exist_ok=True)
        dat_file = out / dat_name

        dat_filecontent, instructions = (
            dat_filecontent_from_smaller_list_of_elements(
                files_from_full_list_of_elements["elts_n_cmds"],
                elts,
            )
        )

        files: FilesInfo = {
            "dat_file": dat_file,
            "dat_filecontent": dat_filecontent,
            "accelerator_path": accelerator_path / folder,
            "elts_n_cmds": instructions,
        }

        export_dat_filecontent(dat_filecontent, dat_file)
        return files

    def _delta_phi_for_tracewin(
        self, phi_at_entry_of_compensation_zone: float
    ) -> float:
        """Give new absolute phases for :class:`.TraceWin`.

        In TraceWin, the absolute phase at the entrance of the compensation
        zone is 0, while it is not in the rest of the code. Hence we must
        rephase the cavities in the subset.

        """
        phi_at_linac_entry = 0.0
        delta_phi_bunch = (
            phi_at_entry_of_compensation_zone - phi_at_linac_entry
        )
        return delta_phi_bunch

    def _get_initial_element(
        self, elts: list[Element], simulation_output: SimulationOutput
    ) -> tuple[Element | str, str]:
        """Set the element from which we should take energy, phase, etc."""
        input_elt, input_pos = elts[0], "in"
        try:
            _ = simulation_output.get("w_kin", elt=input_elt)
        except AttributeError:
            logging.warning(
                "First element of new ListOfElements is not in the given "
                "SimulationOutput. I will consider that the last element of "
                "the SimulationOutput is the first of the new ListOfElements."
            )
            input_elt, input_pos = "last", "out"
        return input_elt, input_pos

    def _subset_input_particle(
        self, simulation_output: SimulationOutput, **kwargs: Any
    ) -> ParticleInitialState:
        """Create input particle for subset of list of elements."""
        w_kin, phi_abs, z_abs = simulation_output.get(
            "w_kin", "phi_abs", "z_abs", **kwargs
        )
        input_particle = ParticleInitialState(
            w_kin, phi_abs, z_abs, synchronous=True
        )
        return input_particle

    def from_existing_list(
        self,
        elts: ListOfElements,
        *,
        instructions_to_insert: Collection[Instruction] = (),
        append_stem: str = "",
        which_phase: str = "phi_0_rel",
    ) -> ListOfElements:
        """Create new list of elements, based on an exising one.

        This method is used for beauty pass: we already have fixed the linac,
        but we want to add DIAG/ADJUST TraceWin commands to perform a second
        optimisation.

        .. todo::
            Maybe gather some things with the subset?

        """
        logging.info("Creating ListOfElements from pre-existing.")

        original_dat = elts.files["dat_file"]
        assert isinstance(original_dat, Path)
        new_dat = original_dat
        if append_stem:
            new_dat = new_dat.with_stem(new_dat.stem + "_" + append_stem)
        shutil.copy(original_dat, new_dat)

        accelerator_path = elts.files["accelerator_path"]
        assert isinstance(accelerator_path, Path)

        kwargs = {
            "w_kin": elts.input_particle.w_kin,
            "phi_abs": elts.input_particle.phi_abs,
            "z_in": elts.input_particle.z_in,
            "sigma_in": elts.input_beam.sigma,
        }

        new_elts = self.whole_list_run(
            dat_file=new_dat,
            accelerator_path=accelerator_path,
            instructions_to_insert=instructions_to_insert,
            **kwargs,
        )
        export_dat_filecontent(new_elts.files["dat_filecontent"], new_dat)
        return new_elts
