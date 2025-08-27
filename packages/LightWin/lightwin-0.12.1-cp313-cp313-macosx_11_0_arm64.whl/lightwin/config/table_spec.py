"""Define the base objects constraining values/types of config parameters."""

import logging
from collections.abc import Callable, Collection
from pathlib import Path
from typing import Any, Literal

from lightwin.config.helper import find_path
from lightwin.config.key_val_conf_spec import KeyValConfSpec

CONFIGURABLE_OBJECTS = (
    "beam",
    "beam_calculator",
    "beam_calculator_post",
    "design_space",
    "evaluators",
    "files",
    "plots",
    "wtf",
)


class TableConfSpec:
    """Set specifications for a table, which holds several key-value pairs.

    .. note::
        This object can be subclassed for specific configuration needs, eg
        :class:`.BeamTableConfSpec`.

    """

    def __init__(
        self,
        configured_object: Literal[
            "beam",
            "beam_calculator",
            "beam_calculator_post",
            "design_space",
            "evaluators",
            "files",
            "plots",
            "wtf",
        ],
        table_entry: str,
        specs: (
            Collection[KeyValConfSpec]
            | dict[str, Collection[KeyValConfSpec]]
            | dict[bool, Collection[KeyValConfSpec]]
        ),
        is_mandatory: bool = True,
        can_have_untested_keys: bool = False,
        selectkey_n_default: tuple[str, str | bool] | None = None,
        monkey_patches: (
            dict[str, dict[str, Callable]]
            | dict[bool, dict[str, Callable]]
            | None
        ) = None,
    ) -> None:
        """Set a table of properties. Correspond to a [table] in the ``TOML``.

        Parameters
        ----------
        configured_object :
            Name of the object that will receive associated parameters.
        table_entry :
            Name of the table in the ``TOML`` file, without brackets.
        specs :
            The :class:`.KeyValConfSpec` objects in the current table. When the
            format of the table depends on the value of a key, provide a
            dictionary linking every possible table with the corresponding
            value.
        is_mandatory :
            If the current table must be provided. The default is True.
        can_have_untested_keys :
            If LightWin should remain calm when some keys are provided in the
            ``TOML`` but do not correspond to any :class:`.KeyValConfSpec`.
            The default is False.
        selectkey_n_default :
            Must be given if ``specs`` is a dict. First value is name of the
            spec, second value is default value. We will look for this spec in
            the configuration file and select the proper ``Collection`` of
            ``KeyValConfSpec`` accordingly.
        monkey_patches :
            Same keys as ``specs``, to override some default methods. The
            default is None.

        """
        self.configured_object = configured_object
        self.table_entry = table_entry

        self._specs = specs
        self._monkey_patches = monkey_patches
        self._selectkey_n_default = selectkey_n_default
        self.specs_as_dict: dict[str, KeyValConfSpec]
        self._set_specs_as_dict()

        self.is_mandatory = is_mandatory
        self.can_have_untested_keys = can_have_untested_keys
        logging.info(f".toml table [{table_entry}] loaded!")

    def __repr__(self) -> str:
        """Print how the object was created."""
        info = (
            "TableConfSpec:",
            f"{self.configured_object:>16s} -> [{self.table_entry}]",
        )
        return " ".join(info)

    def _get_specs(
        self, toml_subdict: dict[str, Any] | None = None
    ) -> list[KeyValConfSpec]:
        """Get the proper list of :class:`.KeyValConfSpec`.

        Used when we need to read the value of ``_selectkey_n_default``
        in the ``TOML`` to choose precisely which configuration we should
        match.

        Parameters
        ----------
        toml_subdict :
            The content of the toml file. We use it only if ``self._specs`` is
            not already a Collection. We look for the value of
            ``self._selectkey_n_default[0]`` and use it to select the
            proper table. If not provided, we fall back on a default value.

        """
        if not isinstance(self._specs, dict):
            assert self._selectkey_n_default is None, (
                f"You provided {self._selectkey_n_default = }, but the"
                f" table will always be {self._specs} as you did not give a "
                "dictionary."
            )
            return list(self._specs)

        assert self._selectkey_n_default is not None, (
            "You must provide the name of the key that will allow to select "
            f"proper table among {self._specs.keys()}"
        )
        value = self._selectkey_n_default[1]
        if toml_subdict is not None:
            value = toml_subdict.get(self._selectkey_n_default[0])
        assert isinstance(value, (str, bool))

        specs = self._specs[value]
        assert specs is not None

        if self._monkey_patches is not None:
            monkey_patches = self._monkey_patches[value]
            self._apply_monkey_patches(monkey_patches)
        return list(specs)

    def _set_specs_as_dict(
        self, toml_subdict: dict[str, Any] | None = None
    ) -> None:
        """Set the dict of specifications.

        Used when we need to read the value of ``_selectkey_n_default``
        in the ``TOML`` to choose precisely which configuration we should
        match.
        If ``toml_subdict`` is not provided, we use a default value.

        """
        specs = self._get_specs(toml_subdict)
        specs = _remove_overriden_keys(specs)
        self.specs_as_dict = {spec.key: spec for spec in specs}

    def _get_proper_spec(self, spec_name: str) -> KeyValConfSpec | None:
        """Get the specification for the property named ``spec_name``."""
        spec = self.specs_as_dict.get(spec_name, None)
        if spec is not None:
            return spec
        if self.can_have_untested_keys:
            return
        msg = (
            f"The table {self.table_entry} has no specs for property "
            f"{spec_name}"
        )
        logging.error(msg)
        raise OSError(msg)

    def to_toml_strings(
        self,
        toml_subdict: dict[str, Any],
        original_toml_folder: Path | None = None,
        **kwargs,
    ) -> list[str]:
        """Convert the given dict in string that can be put in a ``TOML``.

        Parameters
        ----------
        toml_subdict :
            A dictionary corresponding to a ``TOML`` table.
        original_toml_folder :
            Where the original ``TOML`` was; this is used to resolve paths
            relative to this location.

        Returns
        -------
        list[str]
            All the ``TOML`` lines corresponding to the table under study.

        """
        strings = [f"[{self.table_entry}]"]
        for key, val in toml_subdict.items():
            spec = self._get_proper_spec(key)
            if spec is None:
                continue
            strings.append(
                spec.to_toml_string(
                    val, original_toml_folder=original_toml_folder, **kwargs
                )
            )

        return strings

    def _pre_treat(self, toml_subdict: dict[str, Any], **kwargs) -> None:
        """Edit some values, create new ones. To call before validation.

        .. note::
            In general, the edited values will undergo the validation process.

        """
        pass

    def prepare(self, toml_subdict: dict[str, Any], **kwargs) -> bool:
        """Validate the config dict and edit some values."""
        self._set_specs_as_dict(toml_subdict)
        self._pre_treat(toml_subdict, **kwargs)
        validations = self._validate(toml_subdict, **kwargs)
        self._post_treat(toml_subdict, **kwargs)
        self._set_specs_as_dict(toml_subdict)
        return validations

    def _validate(self, toml_subdict: dict[str, Any], **kwargs) -> bool:
        """Check that key-values in ``toml_subdict`` are valid.

        This method is defined to keep an implementation of the original method
        even when ``validate`` is overriden by a monkey patch.

        """
        validations = [self._mandatory_keys_are_present(toml_subdict.keys())]
        for key, val in toml_subdict.items():
            spec = self._get_proper_spec(key)
            if spec is None:
                continue
            validations.append(spec.validate(val, **kwargs))

        all_is_validated = all(validations)
        if not all_is_validated:
            logging.error(
                f"At least one error was raised treating {self.table_entry}"
            )

        return all_is_validated

    def _post_treat(self, toml_subdict: dict[str, Any], **kwargs) -> None:
        """Edit some values, create new ones. To call after validation.

        .. note::
            In general, the edited values will not be validated. To handle with
            care.

        """
        self._make_paths_absolute(toml_subdict, **kwargs)

    def _make_paths_absolute(
        self,
        toml_subdict: dict[str, Any],
        toml_folder: Path | None = None,
        **kwargs,
    ) -> None:
        """Transform the paths to their absolute resolved version."""
        for key, val in toml_subdict.items():
            spec = self._get_proper_spec(key)
            if spec is None:
                continue
            if Path not in spec.types:
                continue

            try:
                new_val = find_path(toml_folder, val)
                toml_subdict[key] = new_val
            except FileNotFoundError:
                continue

    def _mandatory_keys_are_present(self, toml_keys: Collection[str]) -> bool:
        """Ensure that all the mandatory parameters are defined."""
        they_are_all_present = True

        for key, spec in self.specs_as_dict.items():
            if not spec.is_mandatory:
                continue
            if key in toml_keys:
                continue
            they_are_all_present = False
            logging.error(f"The key {key} should be given but was not found.")

        return they_are_all_present

    def generate_dummy_dict(
        self, only_mandatory: bool = True
    ) -> dict[str, Any]:
        """Generate a default dummy dict that should let LightWin work."""
        dummy_conf = {
            spec.key: spec.default_value
            for spec in self.specs_as_dict.values()
            if spec.is_mandatory or not only_mandatory
        }
        return dummy_conf

    def _apply_monkey_patches(
        self, monkey_patches: dict[str, Callable]
    ) -> None:
        """Override the base methods."""
        for method_name, method in monkey_patches.items():
            setattr(self, method_name, method.__get__(self, self.__class__))


def _remove_overriden_keys(
    specs: Collection[KeyValConfSpec],
) -> list[KeyValConfSpec]:
    """Remove the :class:`.KeyValConfSpec` objects to override.

    .. todo::
        Not Pythonic at all.

    """
    cleaned_specs = []
    keys = []
    for spec in specs:
        if key := spec.key not in keys:
            cleaned_specs.append(spec)
            keys.append(key)
            continue

        assert spec.overrides_previously_defined, (
            f"The key {spec} is defined twice, but it was not declared that it"
            " can override."
        )
        idx_to_del = keys.index(key)
        del cleaned_specs[idx_to_del]
        del keys[idx_to_del]
        cleaned_specs.append(spec)
        keys.append(key)

    return list(specs)
