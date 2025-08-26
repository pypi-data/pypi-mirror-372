"""Few modules for importing and exporting from https://voc-qc.nilu.no/

Note that the export and import functions are the opposite of the
import/export feature from the website.
(We export data from this programm, which is imported to the site.)
(We import data into this programm, which was exported from the site.)
"""

from datetime import datetime
import logging
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import pandas.errors


from tucavoc.additional_data import AdditionalData
from tucavoc.additional_data.station import StationInformation

from tucavoc.flags import QA_Flag


def number_of_digits_required(serie: pd.Series) -> int:
    """Return the number of digits required for the calculation"""
    # TODO: need to check if we need the actual int  value, we can put a .9 at the end
    if all(pd.isna(serie) | (serie == 0)):
        # Only 2 will be required
        return 2
    else:
        number_of_digits = np.log10(serie[serie > 0])
        max_digits = number_of_digits[number_of_digits != np.inf]
        if len(max_digits) == 0:
            return 2
        return int(max(np.max(max_digits), 0) + 2)


def export_EmpaQATool(
    df: pd.DataFrame,
    df_substances: pd.DataFrame,
    export_path: Path,
    additional_data: dict[type, AdditionalData] = {},
    substances: list[str] = [],
    rounding_decimals: int = 4,
):
    """Export to the EmpaQATool format.

    The exported file from the program can then be imported to
    the tool on https://voc-qc.nilu.no/Import
    The specs fro that file can be found in
    https://voc-qc.nilu.no/doc/CSVImport_FormatSpecifications.pdf

    This will add the additional data from the dataframe.

    :arg df: Calculation dataframe
    :arg df_substances: Substances dataframe
    :arg export_path: Path to export the file
    :arg additional_data: Additional data to add to the export
    :arg substances: List of substances to export. You can also specify group names.
        If not specified, this will use the substances from `df_substances`.

    """

    logger = logging.getLogger(__name__)

    warnings.filterwarnings(
        action="ignore",
        category=pandas.errors.PerformanceWarning,
        module="pandas",
    )

    df_out = pd.DataFrame()
    # fmt = "%Y-%m-%d %H:%M:%S"
    fmt = "%d.%m.%Y %H:%M:%S"
    df_out["start"] = df[("StartEndOffsets", "datetime_start")].dt.strftime(fmt)
    df_out["end"] = df[("StartEndOffsets", "datetime_end")].dt.strftime(fmt)

    if not substances:
        substances = df_substances.index.to_list()

    if "export_name" not in df_substances.columns:
        df_substances["export_name"] = df_substances.index

    remove_infs = lambda x: x.replace([np.inf, -np.inf], np.nan)
    clean_col = lambda x: remove_infs(x).round(rounding_decimals).astype(str)

    for substance in substances:

        if substance in df_substances.index:
            export_name = df_substances.loc[substance, "export_name"]
            if not export_name or pd.isna(export_name):
                export_name = substance
        else:
            export_name = substance

        mask_invalid = (
            (
                df[(substance, "flag")]
                & (QA_Flag.MISSING.value + QA_Flag.INVALIDATED_EXT.value)
            ).astype(bool)
            | pd.isna(df[(substance, "conc")])
            | pd.isna(df[(substance, "u_expanded")])
            | pd.isna(df[(substance, "u_precision")])
            | (~np.isfinite(df[(substance, "conc")]))
        )

        below_detection_limit = (
            df[(substance, "flag")] & QA_Flag.BELOW_DETECTION_LIMIT.value
        ).astype(bool)

        # Convert to str so we can control the formatting
        df_out[f"{export_name}-Value"] = clean_col(df[(substance, "conc")])

        # Input the missing values as 9. see issue #7 gitlab.empa.ch
        df_out.loc[mask_invalid, f"{export_name}-Value"] = (
            "9" * number_of_digits_required(df[(substance, "conc")])
        )

        # Convert to str so we can control the formatting
        df_out[f"{export_name}-Accuracy"] = clean_col(df[(substance, "u_expanded")])
        # Input the missing values as 9. see issue #7 gitlab.empa.ch
        df_out.loc[mask_invalid, f"{export_name}-Accuracy"] = (
            "9" * number_of_digits_required(df[(substance, "u_expanded")])
        )

        # Convert to str so we can control the formatting
        df_out[f"{export_name}-Precision"] = clean_col(df[(substance, "u_precision")])

        # Input the missing values as 9. see issue #7 gitlab.empa.ch
        df_out.loc[mask_invalid, f"{export_name}-Precision"] = (
            "9" * number_of_digits_required(df[(substance, "u_precision")])
        )


        df_out[f"{export_name}-Flag"] = 0.0
        df_out.loc[below_detection_limit, f"{export_name}-Flag"] = 0.147
        df_out.loc[mask_invalid, f"{export_name}-Flag"] = 0.999

    export_path.mkdir(exist_ok=True)

    if StationInformation in additional_data:
        station_info: StationInformation = additional_data[StationInformation]
        station = station_info.get_station()

        abbreviation = station.abbreviation

    elif "station_abbreviation" in additional_data:
        abbreviation = additional_data["station_abbreviation"]

    else:
        logger.warning(
            "No station information found, using default values. "
            "This might not be correct."
        )
        abbreviation = "XXX"
    # [station]_[dataset]_[revision]
    file_name = f"{abbreviation}_{df[('StartEndOffsets', 'datetime_start')].iloc[0]:%Y%m%d}_{datetime.now():%Y%m%d}"

    out_filepath = Path(export_path, file_name).with_suffix(".csv")
    df_out.to_csv(
        out_filepath,
        sep=";",
        index=False,
        encoding="utf-8",
    )
    print(f"Exported to `{out_filepath}`")
