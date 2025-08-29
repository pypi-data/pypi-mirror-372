"""Flagging in TUCAVOC.

TUCAVOC add a flag value for each measurement of each substance.

"""
from enum import IntEnum
import pandas as pd

from avoca.flags import QA_Flag



def set_flags(df: pd.DataFrame, df_substances: pd.DataFrame):
    """Set automatic flags to the dataframe.

    This will add a sub column to all the substances based on
    automatic recognition of the data.
    
    Uses flags from avoca:  avoca.rtfd.io
        
    * `VALID` by default for any measurement
    * `MISSING_MEASUREMENT_UNSPECIFED_REASON` if
        the amount fraction value is nan.
        This is the case when the base value was nan.
    * `BELOW_DETECTION_LIMIT` if :term:`conc` is
        below the :term:`detection_limit` or is smaller than
        :term:`u_precision` / 3

    """


    for sub in df_substances.index:
        if (sub, "flag") not in df:
            # Valid flag
            df[(sub, "flag")] = int(0)

        # Value samller than detection limit or not precise enough,
        # = below detection limit
        if (sub, "detection_limit") in df:
            df.loc[
                (df[(sub, "conc")] < df[(sub, "detection_limit")]),
                (sub, "flag"),
            ] |= QA_Flag.BELOW_DETECTION_LIMIT.value

        if (sub, "u_precision") in df:
            df.loc[
                (df[(sub, "conc")] < 3 * df[(sub, "u_precision")]),
                (sub, "flag"),
            ] |= QA_Flag.BELOW_DETECTION_LIMIT.value

        # Invalid when is nan
        df.loc[
            pd.isna(df[(sub, "conc")]),
            (sub, "flag"),
        ] |= QA_Flag.MISSING.value


def set_group_flags(
    df: pd.DataFrame,
    df_substances: pd.DataFrame,
    group_dict: dict[str, list[str]],
):
    """Set flags for the groups.

    Similar to :py:func:`set_flags` but adapted for groups.

    * `VALID` by default for any measurement
    * `MISSING_MEASUREMENT_UNSPECIFED_REASON` if
        the amount fraction value is nan.
        This is the case when the base value was nan.

    """

    for group in group_dict.keys():
        if (group, "flag") not in df:
            # Valid flag
            df[(group, "flag")] = int(0)

        # Invalid when is nan
        df.loc[
            pd.isna(df[(group, "conc")]),
            (group, "flag"),
        ] = QA_Flag.MISSING.value
