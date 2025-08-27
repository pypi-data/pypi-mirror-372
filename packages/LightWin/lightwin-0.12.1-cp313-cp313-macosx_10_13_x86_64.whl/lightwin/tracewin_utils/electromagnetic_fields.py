"""Define functions to handle TraceWin electromagnetic fields.

.. note::
    Last compatibility check: TraceWin v2.22.1.0

.. todo::
    some functions are not used anymore I guess...

.. todo::
    Better handling of the module import

"""

import logging
import os.path
from collections.abc import Collection
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from lightwin.beam_calculation.cy_envelope_1d.electromagnetic_fields import (
    load_electromagnetic_fields_for_cython,
)
from lightwin.core.elements.field_maps.field_map import FieldMap
from lightwin.core.elements.field_maps.superposed_field_map import (
    SuperposedFieldMap,
)
from lightwin.core.em_fields.helper import (
    FieldFuncComponent1D,
    create_1d_field_func,
)
from lightwin.tracewin_utils.field_map_loaders import FIELD_MAP_LOADERS

FIELD_GEOMETRIES = {
    0: "no field",
    1: "1D: F(z)",
    2: "not available",
    3: "not available",
    4: "2D cylindrical static or RF electric field",
    5: "2D cylindrical static or RF magnetic field",
    6: "2D cartesian field",
    7: "3D cartesian field",
    8: "3D cylindrical field",
    9: "1D: G(z)",
}  #:

FIELD_TYPES = (
    "static electric field",
    "static magnetic field",
    "RF electric field",
    "RF magnetic field",
    "3D aperture map",
)  #:
LOADABLE = (".edz",)  #:


def load_electromagnetic_fields(
    field_maps: Collection[FieldMap],
    cython: bool,
    loadable: Collection[str] = LOADABLE,
) -> None:
    """Load field map files into the :class:`.FieldMap` objects.

    As for now, only 1D RF electric field are handled by :class:`.Envelope1D`.
    With :class:`.TraceWin`, every field is supported.

    .. todo::
        I think that this should be a method right? Different FieldMap objects
        -> different loading func?

    """
    for field_map in field_maps:
        if isinstance(superposed := field_map, SuperposedFieldMap):
            load_electromagnetic_fields(
                superposed.field_maps, cython, loadable
            )
            for rf_field in superposed.rf_fields:
                rf_field.shift()
            continue

        field_map_types = _geom_to_field_map_type(field_map.geometry)
        extensions = _get_filemaps_extensions(field_map_types)

        field_map.set_full_path(extensions)

        args = load_field_map_file(field_map, loadable)
        if args is None:
            continue

        field_map.rf_field.set_e_spat(args[0], args[2])
        field_map.rf_field.n_z = args[1]

    if cython:
        load_electromagnetic_fields_for_cython(field_maps, loadable)


def _geom_to_field_map_type(geom: int) -> dict[str, str]:
    """
    Determine the field map type from TraceWin's ``geom`` parameter.

    Examples
    --------
    ``geom == 100`` will lead to ``{'RF electric field': '1D: F(z)', 'static \
magnetic field': 'no field', 'static electric field': 'no field'}``

    ``geom == 7700`` will lead to ``{'RF magnetic field': '3D cartesian field'\
, 'RF electric field': '3D cartesian field', 'static magnetic field': 'no \
field', 'static electric field': 'no field'}``

    Note that every key associated with a ``'no field'`` or ``'not available'``
    value will be removed from the dictionary before returning.

    Notes
    -----
    Last compatibility check: TraceWin v2.22.1.0

    """
    figures = (int(i) for i in f"{abs(geom):0>5}")
    out = {
        field_type: FIELD_GEOMETRIES[figure]
        for figure, field_type in zip(figures, FIELD_TYPES)
    }

    if "not available" in out.values():
        logging.error(
            "At least one invalid field geometry was given in the " ".dat."
        )

    for key in list(out):
        if out[key] in ("no field", "not available"):
            del out[key]

    return out


def _get_filemaps_extensions(
    field_map_type: dict[str, str],
) -> dict[str, list[str]]:
    """
    Get the proper file extensions for every field map.

    Parameters
    ----------
    field_map_type :
        Dictionary which keys are in :data:`FIELD_TYPES` and values are values
        of :data:`.FIELD_GEOMETRIES`.

    Returns
    -------
        Dictionary with the same keys as input. The values are lists containing
        all the extensions of the files to load, without a '.'.

    """
    all_extensions = {
        field_type: _get_filemap_extensions(field_type, field_geometry)
        for field_type, field_geometry in field_map_type.items()
        if field_geometry != "not available"
    }
    return all_extensions


def _get_filemap_extensions(field_type: str, field_geometry: str) -> list[str]:
    """
    Get the proper file extensions for the file map under study.

    Parameters
    ----------
    field_type :
        Type of the field/aperture. Allowed values are in :data:`FIELD_TYPES`.
    field_geometry :
        Name of the geometry of the field, as in TraceWin. Allowed values are
        values of :data:`FIELD_GEOMETRIES`.

    Returns
    -------
        Extension without '.' of every file to load.

    """
    if field_type == "3D aperture map":
        return ["ouv"]

    first_word_field_type, second_word_field_type, _ = field_type.split(" ")
    first_character = _get_field_nature(second_word_field_type)
    second_character = _get_type(first_word_field_type)

    first_words_field_geometry = field_geometry.split()[0]
    if first_words_field_geometry != "1D:":
        first_words_field_geometry = " ".join(field_geometry.split()[:2])
    third_characters = _get_field_components(first_words_field_geometry)

    extensions = [
        first_character + second_character + third_character
        for third_character in third_characters
    ]
    return extensions


def _get_field_nature(second_word_field_type: str) -> Literal["e", "b"]:
    """Give first letter of the file extension.

    Parameters
    ----------
    second_word_field_type :
        This is the second word in a :data:`FIELD_TYPES` entry.

    Returns
    -------
        First character in the file extension.

    """
    if second_word_field_type == "electric":
        return "e"
    if second_word_field_type == "magnetic":
        return "b"
    raise OSError(
        f"{second_word_field_type = } while it must be in "
        "('electric', 'magnetic')"
    )


def _get_type(first_word_field_type: str) -> Literal["s", "d"]:
    """Give second letter of the file extension.

    Parameters
    ----------
    first_word_field_type :
        The first word in a :data:`FIELD_TYPES` entry.

    Returns
    -------
        Second character in the file extension.

    """
    if first_word_field_type == "static":
        return "s"
    if first_word_field_type == "RF":
        return "d"
    raise OSError(
        f"{first_word_field_type = } while it must be in ('static', 'RF')"
    )


def _get_field_components(first_words_field_geometry: str) -> list[str]:
    """Give last letter of the extension of every file to load.

    Parameters
    ----------
    first_words_field_geometry :
        Beginning of a :data:`FIELD_GEOMETRIES` value.

    Returns
    -------
        Last extension character of every file to load.

    """
    selectioner = {
        "1D:": ["z"],
        "2D cylindrical": ["r", "z", "q"],
        "2D cartesian": ["x", "y"],
        "3D cartesian": ["x", "y", "z"],
        "3D cylindrical": ["r", "q", "z"],
    }
    if first_words_field_geometry not in selectioner:
        raise OSError(
            f"{first_words_field_geometry = } while it should be in "
            f"{tuple(selectioner.keys())}."
        )
    third_characters = selectioner[first_words_field_geometry]
    return third_characters


def load_field_map_file(
    field_map: FieldMap, loadable: Collection[str]
) -> tuple[FieldFuncComponent1D, int, int] | None:
    """Go across the field map file names and load the first recognized.

    For now, only ``EDZ`` files (1D electric RF) are implemented. This will be
    a problem with :class:`.Envelope1D`, but :class:`.TraceWin` does not care.

    """
    files = field_map.field_map_file_name
    if isinstance(files, Path):
        files = (files,)
    loadable_files = list(filter(lambda x: x.suffix in loadable, files))
    if len(loadable_files) > 1:
        logging.info("Loading of several field_maps not handled")
        return None

    for file_name in loadable_files:
        _, extension = os.path.splitext(file_name)

        if extension not in FIELD_MAP_LOADERS:
            logging.debug("Field map extension not handled.")
            continue

        import_function = FIELD_MAP_LOADERS[extension]

        # this will require an update if I want to implement new field map
        # extensions
        n_z, zmax, norm, f_z, n_cell = import_function(file_name)

        assert is_a_valid_1d_electric_field(
            n_z, zmax, f_z, field_map.length_m
        ), f"Error loading {field_map}'s field map."
        f_z = rescale(f_z, norm)
        z_cavity_array = np.linspace(0.0, zmax, n_z + 1)

        e_spat = create_1d_field_func(
            field_values=f_z, corresponding_positions=z_cavity_array
        )

        # Patch to keep one filepath per FieldMap. Will require an update in
        # the future...
        field_map.field_map_file_name = file_name

        return e_spat, n_z, n_cell
    logging.error(
        "Reached end of _load_field_map_file without loading anything."
    )
    return None


def is_a_valid_1d_electric_field(
    n_z: int,
    zmax: float,
    f_z: np.ndarray,
    cavity_length: float,
    tol: float = 1e-6,
    **validity_check_kwargs,
) -> bool:
    """Assert that the electric field that we loaded is valid."""
    if f_z.shape[0] != n_z + 1:
        logging.error(
            f"The electric field file should have {n_z + 1} lines, but it is "
            f"{f_z.shape[0]} lines long. "
        )
        return False

    if abs(zmax - cavity_length) > tol:
        logging.error(
            f"Mismatch between the length of the field map {zmax = } and "
            f"{cavity_length = }."
        )
        return False

    return True


def rescale(f_z: np.ndarray, norm: float, tol: float = 1e-6) -> np.ndarray:
    """Rescale the array if it was given scaled."""
    if abs(norm - 1.0) < tol:
        return f_z
    return f_z / norm


# FIXME Cannot import Accelerator type (circular import)
# Maybe this routine would be better in Accelerator?
# |-> more SimulationOutput


def output_data_in_tw_fashion(linac) -> pd.DataFrame:
    """Mimick TW's Data tab."""
    larousse = {
        "#": lambda lin, elt: elt.get("elt_idx", to_numpy=False),
        "Name": lambda lin, elt: elt.name,
        "Type": lambda lin, elt: elt.get("nature", to_numpy=False),
        "Length (mm)": lambda lin, elt: elt.length_m * 1e3,
        "Grad/Field/Amp": lambda lin, elt: (
            elt.grad
            if (elt.get("nature", to_numpy=False) == "QUAD")
            else np.nan
        ),
        "EoT (MV/m)": lambda lin, elt: None,
        "EoTLc (MV)": lambda lin, elt: elt.get("v_cav_mv"),
        "Input_Phase (deg)": lambda lin, elt: elt.get(
            "phi_0_rel", to_deg=True
        ),
        "Sync_Phase (deg)": lambda lin, elt: elt.get("phi_s", to_deg=True),
        "Energy (MeV)": lambda lin, elt: lin.get("w_kin", elt=elt, pos="out"),
        "Beta Synch.": lambda lin, elt: lin.get("beta", elt=elt, pos="out"),
        "Full length (mm)": lambda lin, elt: lin.get(
            "z_abs", elt=elt, pos="out"
        )
        * 1e3,
        "Abs. phase (deg)": lambda lin, elt: lin.get(
            "phi_abs", to_deg=True, elt=elt, pos="out"
        ),
    }

    data = []
    n_latt = 1
    i = 0
    for lattice in linac.elts.by_lattice:
        lattice_n = "--------M" + str(n_latt)
        data.append(
            [
                np.nan,
                lattice_n,
                "",
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            ]
        )
        n_latt += 1
        for elt in lattice:
            row = []
            for value in larousse.values():
                row.append(value(linac, elt))
                data.append(row)
                i += 1

    data = pd.DataFrame(data, columns=larousse.keys())
    return data
