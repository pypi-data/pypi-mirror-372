"""Calculation of chromatography amount fraction and uncertainties.

This package aims at processing data for 
calculating the uncertainty of the measurements.

.. note::
    TUCAVOC python code uses 
    *concentration* instead of *amount fraction*.
    As one single small word is easier most of the function use the abbreviation *conc*.


"""
from os import PathLike
from pathlib import Path
import pandas as pd


def read_concs(file: PathLike) -> pd.DataFrame:
    """Read the concentration of substances from a TUCAVOC file.

    Concentration files are usually the output of the calculations.

    :return concs_df: The :py:class:`pandas.DataFrame` with the concentrations.
        This is a dataframe with the metadata columns first and then
        each substance concentration in one column.
    """
    df_full_concs = pd.read_csv(file, header=[0, 1])
    # Extract only the columns we need
    columns = [
        (a, b) for a, b in df_full_concs.columns if a == "-" or b == "conc"
    ]
    return pd.DataFrame(
        {c[1] if c[0] == "-" else c[0]: df_full_concs[c] for c in columns}
    )


def read_output(file: PathLike) -> pd.DataFrame:
    """Read an output file from TUCAVOC.

    Concentration files are usually the output of the calculations.

    :return concs_df: The :py:class:`pandas.DataFrame` with the concnetrations.
        This is a dataframe with 2-Levels columns.
        The first level of the column is the substance and the second is
        the variable corresponding to that substance.
        For example to access the concentration of methane you can do :
        `df[('methane', 'conc')]`.
        The metadata common to all substances is acessed using a '-'
        instead of the substance name:
        `df[('-', 'type')]` .
    """

    return pd.read_csv(file, header=[0, 1])



if __name__ == "__main__":
    print(read_concs(Path(".") / "concs.csv"))
