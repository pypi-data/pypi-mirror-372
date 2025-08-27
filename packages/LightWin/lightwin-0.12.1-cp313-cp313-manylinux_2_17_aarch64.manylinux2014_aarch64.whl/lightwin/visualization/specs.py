"""Define parameters to set the plots."""

from lightwin.config.key_val_conf_spec import KeyValConfSpec

PLOTS_CONFIG = (
    KeyValConfSpec(
        key="add_objectives",
        types=(bool,),
        description="Add objectives position to plots?",
        default_value=False,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="energy",
        types=(bool,),
        description="Plot evolution of kinetic energy?",
        default_value=False,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="phase",
        types=(bool,),
        description="Plot evolution of absolute phase?",
        default_value=False,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="cav",
        types=(bool,),
        description="Plot cavity parameters?",
        default_value=False,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="emittance",
        types=(bool,),
        description="Plot evolution of emittance?",
        default_value=False,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="twiss",
        types=(bool,),
        description="Plot Twiss parameters?",
        default_value=False,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="envelopes",
        types=(bool,),
        description="Plot envelopes?",
        default_value=False,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="transfer_matrices",
        types=(bool,),
        description="Plot transfer matrix components?",
        default_value=False,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="acceptance",
        types=(bool,),
        description="Plot acceptances?",
        default_value=False,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="kwargs",
        types=(dict,),
        description="kwargs passed to |axplot|.",
        default_value={},
        is_mandatory=False,
    ),
)
