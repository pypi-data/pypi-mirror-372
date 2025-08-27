"""Define a :class:`.BeamCalculator` that will call TraceWin from cmd line.

It inherits from :class:`.BeamCalculator` base class.  It solves the motion of
the particles in envelope or multipart, in 3D. In contrary to
:class:`.Envelope1D` solver, it is not a real solver but an interface with
``TraceWin`` which must be installed on your machine.

"""

import logging
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from lightwin.beam_calculation.beam_calculator import BeamCalculator
from lightwin.beam_calculation.simulation_output.simulation_output import (
    SimulationOutput,
)
from lightwin.beam_calculation.tracewin.element_tracewin_parameters_factory import (
    ElementTraceWinParametersFactory,
)
from lightwin.beam_calculation.tracewin.simulation_output_factory import (
    SimulationOutputFactoryTraceWin,
)
from lightwin.core.accelerator.accelerator import Accelerator
from lightwin.core.elements.field_maps.field_map import FieldMap
from lightwin.core.list_of_elements.list_of_elements import ListOfElements
from lightwin.failures.set_of_cavity_settings import SetOfCavitySettings
from lightwin.tracewin_utils.interface import (
    beam_calculator_to_command,
    failed_cavities_to_command,
    set_of_cavity_settings_to_command,
)
from lightwin.util.typing import REFERENCE_PHASE_POLICY_T, BeamKwargs


class TraceWin(BeamCalculator):
    """Hold a TraceWin beam calculator.

    Parameters
    ----------
    executable :
        Path to the TraceWin executable.
    ini_path :
        Path to the ``INI`` TraceWin file.
    base_kwargs :
        TraceWin optional arguments. Override what is defined in ``INI``, but
        overriden by arguments from :class:`.ListOfElements` and
        :class:`.SimulationOutput`.
    _tracewin_command :
        Attribute to hold the value of the base command to call TraceWin.
    out_folder :
        Name of the results folder (not a complete path, just a folder name).
    path_cal :
        Name of the results folder. Updated at every call of the
        :func:`init_solver_parameters` method, using
        ``Accelerator.accelerator_path`` and ``self.out_folder`` attributes.
    dat_file :
        Base name for the ``DAT`` file. ??

    """

    def __init__(
        self,
        executable: Path,
        ini_path: Path,
        base_kwargs: dict[str, str | int | float | bool | None],
        out_folder: Path | str,
        default_field_map_folder: Path | str,
        beam_kwargs: BeamKwargs,
        reference_phase_policy: REFERENCE_PHASE_POLICY_T = "phi_0_rel",
        cal_file: Path | None = None,
        **kwargs: Any,
    ) -> None:
        """Define some other useful methods, init variables."""
        self.executable = executable
        self.ini_path = ini_path.resolve().absolute()
        self.base_kwargs = base_kwargs
        self.cal_file = cal_file
        self._beam_kwargs = beam_kwargs

        filename = Path("tracewin.out")
        if self.is_a_multiparticle_simulation:
            filename = Path("partran1.out")
        self._filename = filename
        super().__init__(
            reference_phase_policy=reference_phase_policy,
            out_folder=out_folder,
            default_field_map_folder=default_field_map_folder,
            beam_kwargs=beam_kwargs,
            **kwargs,
        )

        self.path_cal: Path
        self.dat_file: Path
        self._tracewin_command: list[str] | None = None

    def _set_up_specific_factories(self) -> None:
        """Set up the factories specific to the :class:`.BeamCalculator`.

        This method is called in the :meth:`.BeamCalculator.__init__`, hence it
        appears only in the base :class:`.BeamCalculator`.

        """
        self.beam_calc_parameters_factory = ElementTraceWinParametersFactory()

        self.simulation_output_factory = SimulationOutputFactoryTraceWin(
            _is_3d=self.is_a_3d_simulation,
            _is_multipart=self.is_a_multiparticle_simulation,
            _solver_id=self.id,
            _beam_kwargs=self._beam_kwargs,
            out_folder=self.out_folder,
            _filename=self._filename,
            beam_calc_parameters_factory=self.beam_calc_parameters_factory,
        )

    def _tracewin_base_command(
        self, accelerator_path: Path, **kwargs
    ) -> tuple[list[str], Path]:
        """Define the 'base' command for TraceWin.

        This part of the command is the same for every :class:`.ListOfElements`
        and every :class:`.Fault`. It sets the TraceWin executable, the
        ``INI`` file.  It also defines ``base_kwargs``, which should be the
        same for every calculation. Finally, it sets ``path_cal``.
        But this path is more :class:`.ListOfElements` dependent...
        ``Accelerator.accelerator_path`` + ``out_folder``
        (+ ``fault_optimisation_tmp_folder``)

        """
        kwargs = kwargs.copy()
        for key, val in self.base_kwargs.items():
            if key not in kwargs:
                kwargs[key] = val

        path_cal = accelerator_path / self.out_folder
        if not path_cal.is_dir():
            path_cal.mkdir()

        _tracewin_command = beam_calculator_to_command(
            self.executable,
            self.ini_path,
            path_cal,
            **kwargs,
        )
        return _tracewin_command, path_cal

    def _tracewin_full_command(
        self,
        elts: ListOfElements,
        set_of_cavity_settings: SetOfCavitySettings | None,
        **kwargs,
    ) -> tuple[list[str], Path]:
        """Set the full TraceWin command.

        It contains the 'base' command, which includes every argument that is
        common to every calculation with this :class:`.BeamCalculator`: path to
        ``INI`` file, to executable...

        It contains the :class:`.ListOfElements` command: path to the ``DAT``
        file, initial energy and beam properties.

        It can contain some :class:`.SetOfCavitySettings` commands: ``ele``
        arguments to modify some cavities tuning.

        """
        accelerator_path = elts.files_info["accelerator_path"]
        command, path_cal = self._tracewin_base_command(
            accelerator_path, **kwargs
        )
        command.extend(elts.tracewin_command)
        if set_of_cavity_settings is None:
            return command, path_cal

        command.extend(
            set_of_cavity_settings_to_command(
                set_of_cavity_settings,
                phi_bunch_first_element=elts.input_particle.phi_abs,
                idx_first_element=elts[0].idx["elt_idx"],
            )
        )
        command.extend(
            failed_cavities_to_command(
                elts.l_cav,
                idx_first_element=elts[0].idx["elt_idx"],
            )
        )
        return command, path_cal

    # TODO what is specific_kwargs for? I should just have a function
    # set_of_cavity_settings_to_kwargs
    def run(
        self,
        elts: ListOfElements,
        update_reference_phase: bool = False,
        **specific_kwargs,
    ) -> SimulationOutput:
        """Run TraceWin.

        Parameters
        ----------
        elts :
            List of elements in which the beam must be propagated.
        update_reference_phase :
            To change the reference phase of cavities when it is different from
            the one asked in the ``TOML``. To use after the first calculation,
            if :attr:`.BeamCalculator.reference_phase_policy` does not align
            with :attr:`.CavitySettings.reference`.
        specific_kwargs :
            ``TraceWin`` optional arguments. Overrides what is defined in
            ``base_kwargs`` and ``INI``.

        Returns
        -------
            Holds energy, phase, transfer matrices (among others) packed into a
            single object.

        """
        return super().run(elts, update_reference_phase, **specific_kwargs)

    def run_with_this(
        self,
        set_of_cavity_settings: SetOfCavitySettings | None,
        elts: ListOfElements,
        use_a_copy_for_nominal_settings: bool = True,
        **specific_kwargs,
    ) -> SimulationOutput:
        """Perform a simulation with new cavity settings.

        Calling it with ``set_of_cavity_settings = None`` is the same as
        calling the plain :func:`run` method.

        Parameters
        ----------
        set_of_cavity_settings :
            The new cavity settings to try. If it is None, then the cavity
            settings are taken from the FieldMap objects.
        elts :
            List of elements in which the beam should be propagated.
        use_a_copy_for_nominal_settings :
            To copy the nominal :class:`.CavitySettings` and avoid altering
            their nominal counterpart. Set it to True during optimisation, to
            False when you want to keep the current settings. The default is
            True.

        Returns
        -------
            Holds energy, phase, transfer matrices (among others) packed into a
            single object.

        """
        if specific_kwargs not in (None, {}):
            logging.critical(f"{specific_kwargs = }: deprecated.")

        if specific_kwargs is None:
            specific_kwargs = {}

        set_of_cavity_settings = SetOfCavitySettings.from_incomplete_set(
            set_of_cavity_settings,
            elts.l_cav,
            use_a_copy_for_nominal_settings=use_a_copy_for_nominal_settings,
        )

        command, path_cal = self._tracewin_full_command(
            elts, set_of_cavity_settings, **specific_kwargs
        )
        is_a_fit = use_a_copy_for_nominal_settings
        exception = _run_in_bash(command, output_command=not is_a_fit)

        # check in which order those two methods should be called
        simulation_output = self._generate_simulation_output(
            elts,
            path_cal,
            exception,
            set_of_cavity_settings=set_of_cavity_settings,
        )
        self._post_treat_cavity_setttings(
            set_of_cavity_settings, elts.l_cav, simulation_output
        )
        return simulation_output

    def post_optimisation_run_with_this(
        self,
        optimized_cavity_settings: SetOfCavitySettings,
        full_elts: ListOfElements,
        **specific_kwargs,
    ) -> SimulationOutput:
        """Run TraceWin with optimized cavity settings.

        After the optimisation, we want to re-run TraceWin with the new
        settings. However, we need to tell it that the linac is bigger than
        during the optimisation. Concretely, it means:

        * Rephasing the cavities in the compensation zone.
        * Updating the ``index`` ``n`` of the cavities in the ``ele[n][v]``
          command.

        Note that at this point, the ``DAT`` has not been updated yet.

        Parameters
        ----------
        optimized_cavity_settings :
            Optimized parameters.
        full_elts :
            Contains the full linac.

        Returns
        -------
            Necessary information on the run.

        """
        optimized_cavity_settings.re_set_elements_index_to_absolute_value()

        # patch: to have the new settings saved in the .dat, we incorporate
        # new cavity settings now
        # for cavity in full_elts.l_cav:
        #     if cavity not in optimized_cavity_settings:
        #         continue
        #     cavity.cavity_settings = optimized_cavity_settings[cavity]

        # full_elts.store_settings_in_dat(
        #     full_elts.files_info["dat_file"], which_phase=self.reference_phase
        # )

        simulation_output = self.run_with_this(
            optimized_cavity_settings, full_elts, **specific_kwargs
        )
        return simulation_output

    def init_solver_parameters(self, accelerator: Accelerator) -> None:
        """Set the ``path_cal`` variable.

        We also set the ``_tracewin_command`` attribute to None, as it must be
        updated when ``path_cal`` changes.

        .. note::
            In contrary to :class:`.Envelope1D` and :class:`.Envelope3D`, this
            routine does not set parameters for the :class:`.BeamCalculator`.
            As a matter of a fact, TraceWin is a standalone code and does not
            need out solver parameters.
            However, if we want to save the meshing used by TraceWin, we will
            have to use the :class:`.ElementTraceWinParametersFactory` later.

        """
        self.path_cal = Path(
            accelerator.get("accelerator_path"), self.out_folder
        )
        if not self.path_cal.is_dir():
            self.path_cal.mkdir()

        self._tracewin_command = None

        if self.cal_file is None:
            return
        assert self.cal_file.is_file()
        shutil.copy(self.cal_file, self.path_cal)
        logging.debug(f"Copied {self.cal_file = } in {self.path_cal = }.")

    @property
    def is_a_multiparticle_simulation(self) -> bool:
        """Tell if you should buy Bitcoins now or wait a few months."""
        if "partran" in self.base_kwargs:
            return self.base_kwargs["partran"] == 1
        return Path(self.path_cal, "partran1.out").is_file()

    @property
    def is_a_3d_simulation(self) -> bool:
        """Tell if the simulation is in 3D."""
        return True

    def _post_treat_cavity_setttings(
        self,
        set_of_cavity_settings: SetOfCavitySettings | None,
        cavities: Sequence[FieldMap],
        simulation_output: SimulationOutput,
    ) -> None:
        """Store cavity settings in the appropriate :class:`.CavitySettings`.

        .. note::
           When we are under a fitting process, *i.e.* when
           ``set_of_cavity_settings`` is not ``None``, we update the
           :class:`.CavitySettings` in the ``set_of_cavity_settings``, not the
           ones in :attr:`.FieldMap.cavity_settings`.

        """
        for cavity in cavities:
            phi_abs, v_cav_mv, phi_s = simulation_output.get(
                "phi_abs",
                "v_cav_mv",
                "phi_s",
                elt=cavity,
                pos="in",
                to_deg=False,
                to_numpy=False,
            )
            if set_of_cavity_settings is None:
                # Any cavity during a "normal" run
                settings = cavity.cavity_settings
            elif cavity in set_of_cavity_settings:
                # Compensating cavity during a fit
                settings = set_of_cavity_settings[cavity]
            else:
                # Non-compensating cavity during a fit
                continue

            settings.phi_bunch = phi_abs
            settings.phi_s = phi_s
            settings.v_cav_mv = v_cav_mv
        return


# =============================================================================
# Bash
# =============================================================================
def _run_in_bash(
    command: list[str], output_command: bool = True, output_error: bool = False
) -> bool:
    """Run given command in bash."""
    output = "\n\t".join(command)
    if output_command:
        logging.info(f"Running command:\n\t{output}")

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    exception = process.wait()

    # exception = False
    # for line in process.stdout:
    # if output_error:
    # print(line)
    # exception = True

    if exception != 0 and output_error:
        logging.warning(
            "A message was returned when executing following "
            f"command:\n\t{stderr}"
        )
    return exception != 0
