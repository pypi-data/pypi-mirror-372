"""Helpers for settings."""

import logging
from os import PathLike
from pathlib import Path

from typing import Any

import pandas as pd

from tucavoc import parameters
from tucavoc.abstract_uncertainty import Parameter, PARAMETERS_BY_NAME

# Global settings are settings that should be set for all compounds (same value for all compounds)
GLOBAL_SETTINGS = [
    parameters.CALIB_VOLUME,
    parameters.SAMPLE_VOLUME,
]

# Mandatory parameters that will be set by default if they are not in the settings file
MANDATORY_PARAMS: list[Parameter] = [
    parameters.GROUP,
    parameters.USE_FOR_GENERAL_CRF,
    parameters.CN,
    parameters.ECN_CONTRIB,
    parameters.CRF,
    parameters.BLANK_CONC_PRESET,
    parameters.IN_CALIB,
]


def settings_to_df_compounds(
    settings: dict[str, Any], compounds: list[str]
) -> pd.DataFrame:
    """Convert the settings to a dataframe."""

    logger = logging.getLogger(__name__)

    # Create a temporary storage for settings we want
    settins_dict: dict[str, dict[str, Any]] = {cmp: {} for cmp in compounds}

    # Fill the dataframe
    for setting_key, setting_value in settings.items():
        # Try to check if the format correspond to cmp.setting_name

        splitted = setting_key.split(".")
        if len(splitted) != 2:
            continue
        cmp, setting_name = splitted
        if cmp not in compounds:
            continue

        settins_dict[cmp][setting_name] = setting_value

    df = pd.DataFrame(settins_dict).T

    # Set some additional global settings to the compounds
    for param in GLOBAL_SETTINGS:
        # This is how tucavoc writes the settings
        key_tuavoc = f"-.{param.name}"
        if param.name in settings:
            key = param.name
            if key_tuavoc in settings:
                raise ValueError(
                    f"Both {param.name} and {key_tuavoc} are set in the settings. Please set only one."
                )
        elif key_tuavoc in settings:
            key = key_tuavoc
        else:
            raise ValueError(
                f"Missing global setting for {param}. Please set it in the settings as {param.name}"
            )
        df[param.name] = settings[key]

    # Set default values to the mandatory varialbes
    for param in MANDATORY_PARAMS:
        if param.name not in df.columns:
            df[param.name] = param.val
    

    for column in df.columns:
        if column not in PARAMETERS_BY_NAME:
            logger.warning(f"Unknown parameter '{column}' in the settings.")
            continue 
        param_type = PARAMETERS_BY_NAME[column].type
        if param_type is None:
            continue
        if param_type == str:
            df[column] = df[column].fillna("")
        elif param_type == bool:
            df[column] = df[column].astype(str).str.lower().map({'true': True, 'false': False})
        df[column] = df[column].astype(PARAMETERS_BY_NAME[column].type)

    return df


if __name__ == "__main__":
    test_file = Path("test.json")

    import json

    with open(test_file, "r") as f:
        settings = json.load(f)

    compounds = ["A", "B", "C"]
    df = settings_to_df_compounds(settings, compounds)

    print(df)
