#!/usr/bin/env python
# coding=utf-8
# https://git.nilu.no/ebas/ebas-io
"""
Copy from ebas_genfile.py 1630 2017-05-23 16:10:23Z pe $

Submission for the EMPA lab on Climate Gases.

https://www.empa.ch/web/s503//climate-gases

Laboratory for Air Pollution / Environmental Technology 
Swiss Federal Laboratories for Materials Science and Technology

"""
from pathlib import Path
from ebas.io.file import nasa_ames
from nilutility.datatypes import DataObject
from ebas.domain.basic_domain_logic.time_period import (
    estimate_period_code,
    estimate_resolution_code,
    estimate_sample_duration_code,
)
import datetime
import numpy as np

import pandas as pd
from tucavoc.additional_data import AdditionalData
from tucavoc.flags import QA_Flag as Flags

from ebas.io.file import SUPPRESS_METADATA_OCCURRENCE, FLAGS_AS_IS

__version__ = "EMPA.ABT503.2022.0"

empa_organisation = DataObject(
    OR_CODE="CH01L",
    OR_NAME="Swiss Federal Laboratories for Materials Science and Technology",
    OR_ACRONYM="EMPA",
    OR_UNIT="Laboratory for Air Pollution",
    OR_ADDR_LINE1="Ueberlandstrasse 129",
    OR_ADDR_LINE2="",
    OR_ADDR_ZIP="8600",
    OR_ADDR_CITY="Duebendorf",
    OR_ADDR_COUNTRY="Switzerland",
)


def empa_person(first_name: str, last_name: str, email: str):
    """Create a data object with an person from EMPA Dübendorf."""
    return DataObject(
        PS_LAST_NAME=last_name,
        PS_FIRST_NAME=first_name,
        PS_EMAIL=email,
        PS_ORG_NAME=(
            "Swiss Federal Laboratories for Materials Science and Technology"
        ),
        PS_ORG_ACR="EMPA",
        PS_ORG_UNIT="Laboratory for Air Pollution",
        PS_ADDR_LINE1="Ueberlandstrasse 129",
        PS_ADDR_LINE2="",
        PS_ADDR_ZIP="8600",
        PS_ADDR_CITY="Duebendorf",
        PS_ADDR_COUNTRY="Switzerland",
        PS_ORCID=None,
    )


lionel = empa_person(
    "Lionel",
    "Constantin",
    "lionel.constantin@empa.ch",
)
matz = empa_person(
    "Matz",
    "Hill",
    "matthias.hill@empa.ch",
)
stefan = empa_person(
    "Stefan",
    "Reimann",
    "stefan.reimann@empa.ch",
)


def set_fileglobal_metadata(nas):
    """
    Set file global metadata for the EbasNasaAmes file object

    Parameters:
        nas    EbasNasaAmes file object
    Returns:
        None
    """
    # All times reported to EBAS need to be in UTC!
    # Setting the timezone here explicitly should remind you to check your data
    nas.metadata.timezone = "UTC"

    # Revision information
    nas.metadata.revdate = datetime.datetime.now(tz=datetime.timezone.utc)
    nas.metadata.revision = "1"
    nas.metadata.revdesc = (
        "automatically generated with python ovoc-calculations"
    )

    # Data Originator Organisation
    nas.metadata.org = empa_organisation

    # Projects the data are associated to
    nas.metadata.projects = ["ACTRIS", "EMEP", "GAW-WDCRG"]

    # Data Originators (PIs)
    nas.metadata.originator = []
    nas.metadata.originator.append(matz)
    nas.metadata.originator.append(stefan)
    nas.metadata.originator.append(lionel)

    # Data Submitters (contact for data technical issues)
    nas.metadata.submitter = []
    nas.metadata.submitter.append(matz)

    nas.metadata.rescode_sample = "15mn"

    # Station metadata BRM
    nas.metadata.station_code = "CH0053R"
    nas.metadata.platform_code = "CH0053S"
    nas.metadata.station_name = "Beromuenster"

    nas.metadata.station_wdca_id = "GAWACH__BRM"
    nas.metadata.station_gaw_id = "BRM"
    nas.metadata.station_gaw_name = "Beromuenster"
    # nas.metadata.station_airs_id =    # N/A
    # nas.metadata.station_other_ids = "721 (NILUDB)"
    # nas.metadata.station_state_code =  # N/A
    nas.metadata.station_landuse = "Other"
    nas.metadata.station_setting = "Rural"
    nas.metadata.station_gaw_type = "R"
    nas.metadata.station_wmo_region = 6
    nas.metadata.station_latitude = 47.189594
    nas.metadata.station_longitude = 8.175465
    nas.metadata.station_altitude = 797.0

    # Added by EMPA
    nas.metadata.mea_altitude = 802.0
    nas.metadata.mea_height = 5.0
    nas.metadata.comp_name = "NMHC"

    nas.metadata.matrix = "air"
    nas.metadata.instr_type = "online_gc"
    nas.metadata.lab_code = "CH01L"
    nas.metadata.instr_name = "Agilent_MARKES-GC-FID_cn13283047_BRM"
    nas.metadata.instr_manufacturer = "MARKES+MARKES+Agilent"
    nas.metadata.instr_model = "Air Server+UNITY2+7890A GC/FID"
    nas.metadata.instr_serialno = "cn13283047"

    nas.metadata.method = "CH01L_MARES_GC_FID_VOCAIR_BRM"
    nas.metadata.std_method = "SOP=ACTRIS_VOC_2014"

    nas.metadata.cal_scale = "NPL"
    nas.metadata.cal_std_id = "D386648"
    nas.metadata.sec_std_id = "Duebendorf air; RIX-filling; D641650"
    nas.metadata.inlet_type = "Hat or hood"
    nas.metadata.inlet_desc = (
        "ambient air is brought into the cabin through a main inlet line at a"
        " flow rate of 300 lpm. From the main inlet line short stainless steel"
        " tubes are used to bring the air samples to the instruments."
    )

    nas.metadata.detection_limit_desc = (
        "Determined by integration of a baseline signal multiplied by a factor"
        " of 3"
    )
    nas.metadata.uncertainty_desc = (
        "Includes reproducibility (precision) + systematic errors (accuracy)"
    )
    nas.metadata.zero_negative = "Zero possible"
    nas.metadata.zero_negative_desc = (
        "Zero values may appear due to statistical variations at very low"
        " concentrations"
    )

    nas.metadata.acknowledgements = (
        "Request acknowledgement details from data originator"
    )
    nas.metadata.comment = (
        "For OVOCs, terpenes and acetoniotril the calibration factor is"
        " calculated with the effective carbon number"
        " (https://doi.org/10.1093/chromsci/23.8.333). These factors were"
        " verified in the round robin test in Hohenpeissenberg (2018)."
    )

    # More file global metadata, but those can be overridden per variable
    # See set_variables for examples
    # nas.metadata.instr_type = "passive_puf"
    # nas.metadata.lab_code = "CH01L"
    # nas.metadata.instr_name = "puf_42"
    # nas.metadata.method = "NO01L_gc_ms"
    # nas.metadata.regime = "IMG"
    # nas.metadata.comp_name   will be set on variable level
    # nas.metadata.unit        will be set on variable level
    nas.metadata.statistics = "arithmetic mean"
    nas.metadata.datalevel = "2"
    # To view all possible metadata
    # http://htmlpreview.github.io/?https://git.nilu.no/ebas/ebas-io/raw/master/Examples/Doc/Notebooks/html/EbasMetadata.html


def set_time_axes(nas, sample_times: list[tuple[datetime.datetime]]):
    """
    Set the time axes and related metadata for the EbasNasaAmes file object.

    Parameters:
        nas    EbasNasaAmes file object
    Returns:
        None
    """
    # define start and end times for all samples
    nas.sample_times = sample_times

    #
    # Generate metadata that are related to the time axes:
    #

    # period code is an estimate of the current submissions period, so it should
    # always be calculated from the actual time axes, like this:
    nas.metadata.period = estimate_period_code(
        nas.sample_times[0][0], nas.sample_times[-1][1]
    )

    # Sample duration can be set automatically
    nas.metadata.duration = estimate_sample_duration_code(nas.sample_times)
    # or set it hardcoded:
    # nas.metadata.duration = '3mo'

    # Resolution code can be set automatically
    # But be aware that resolution code is an identifying metadata element.
    # That means, several submissions of data (multiple years) will
    # only be stored as the same dataset if the resolution code is the same
    # for all submissions!
    # That might be a problem for time series with varying resolution code
    # (sometimes 2 months, sometimes 3 months, sometimes 9 weeks, ...). You
    # might consider using a fixed resolution code for those time series.
    # Automatic calculation (will work from ebas.io V.3.0.7):
    nas.metadata.resolution = estimate_resolution_code(nas.sample_times)
    # or set it hardcoded:
    # nas.metadata.resolution = '3mo'

    # It's a good practice to use Jan 1st of the year of the first sample
    # endtime as the file reference date (zero point of time axes).
    nas.metadata.reference_date = datetime.datetime(
        nas.sample_times[0][1].year, 1, 1
    )


def set_variables(nas, df: pd.DataFrame, df_substances: pd.DataFrame):
    """
    Set metadata and data for all variables for the EbasNasaAmes file object.

    The df_substances must have all the substances
    The df is the dataframe of calculations.
    It must have the following columns:
    for each substance, it has a measure value

    Parameters:
        nas    EbasNasaAmes file object
    Returns:
        None
    """
    UNIT = "pmol/mol"  # = ppt
    for sub in df_substances.index.to_list():
        # variable 1: examples for missing values and flagging
        # values = [1.22, 2.33, None, 4.55]  # missing value is None!
        values = [
            round(val, 2)
            if flag != Flags.MISSING_MEASUREMENT_UNSPECIFED_REASON
            and np.isfinite(val)
            else None
            for val, flag in zip(df[(sub, "conc")], df[(sub, "flag")])
        ]
        flags = [
            [] if flag == Flags.VALID else [int(flag)]
            for flag in df[(sub, "flag")]
        ]

        export_name = df_substances.loc[sub, "export_name"]

        # [] means no flags for this measurement
        # [999] missing or invalid flag needed because of missing value (None)
        # [632, 665] multiple flags per measurement possible
        metadata = DataObject()
        metadata.comp_name = export_name
        metadata.title = f"{export_name}"
        metadata.unit = UNIT  # "pg/m3" ?
        metadata.detection_limit = [
            # Add a .0 after the value
            f"{df_substances.loc[sub, 'detection_limit']:.1f}",
            UNIT,
        ]
        # alternatively, you could set all metadata at once:
        # metadata = DataObject(comp_name='HCB', unit = 'pg/m3')
        nas.variables.append(
            DataObject(
                values_=values,
                flags=flags,
                metadata=metadata,
                flagcol=False,
            )
        )

        # Following are other examplles which we could read
        # They are useful for dealing with the uncertainties

        ## variable 2: examples for overridden metadata, uncertainty and detection
        ## limit
        # values = [1.22, 2.33, 3.44, 4.55]
        # flags = [[], [], [], []]
        # metadata = DataObject()
        # metadata.comp_name = "benz_a_anthracene"
        # metadata.unit = "ng/m3"
        ## matrix is different for this variable. Generally, you can override most
        ## elements of nas.metadata on a per-variable basis by just setting the
        ## according nas.variables[i].metadata element.
        # metadata.matrix = "air+aerosol"
        ## additionally, we also specify uncertainty and detection limit for this
        ## variable:
        # metadata.detection_limit = [0.10, "ng/m3"]
        ## detection limit unit must always be the same as the variable's unit!
        # metadata.uncertainty = [0.12, "ng/m3"]
        ## uncertainty unit is either the same as the variable's unit, ot '%' for
        ## relative uncertainty:
        ## metadata.uncertainty = [10.0, '%']
        # nas.variables.append(
        #    DataObject(
        #        values_=values, flags=flags, flagcol=True, metadata=metadata
        #    )
        # )

        #
        ## variable 3: uncertainty will be specified for each sample (see variable 4)
        # values = [1.22, 2.33, 3.44, 4.55]
        # flags = [[], [], [], []]
        # metadata = DataObject()
        # metadata.comp_name = "PCB_101"
        # metadata.unit = "pg/m3"
        # nas.variables.append(
        #    DataObject(
        #        values_=values, flags=flags, flagcol=True, metadata=metadata
        #    )
        # )
        #
        # variable 4: this variable contains the uncertainties for varable 3

        metadata = DataObject()
        metadata.comp_name = export_name
        metadata.title = f"{export_name}_exp_unc"
        metadata.unit = UNIT
        # this is what makes this variable the uncetainty time series:
        metadata.statistics = "expanded uncertainty 2sigma"
        values = [
            round(val, 2)
            if flag != Flags.MISSING_MEASUREMENT_UNSPECIFED_REASON
            and np.isfinite(val)
            else None
            for val, flag in zip(df[(sub, "u_expanded")], df[(sub, "flag")])
        ]
        nas.variables.append(
            DataObject(
                values_=values,
                flags=flags,
                metadata=metadata,
                flagcol=False,
            )
        )

        metadata = DataObject()
        metadata.comp_name = export_name
        metadata.title = f"{export_name}_pr"
        metadata.unit = UNIT
        # this is what makes this variable the uncetainty time series:
        metadata.statistics = "precision"
        values = [
            round(val, 2)
            if flag != Flags.MISSING_MEASUREMENT_UNSPECIFED_REASON
            and np.isfinite(val)
            else None
            for val, flag in zip(df[(sub, "u_precision")], df[(sub, "flag")])
        ]
        nas.variables.append(
            DataObject(
                values_=values,
                flags=flags,
                metadata=metadata,
                flagcol=True,
            )
        )


def export_EBAS(
    df: pd.DataFrame,
    df_substances: pd.DataFrame,
    export_dir: Path,
    additional_data: dict[type, AdditionalData] = {},
):
    """Export data to the EBAS database."""

    substances = df_substances.index.to_list()
    # Ensure export dir was created
    if not export_dir.is_dir():
        export_dir.mkdir()

    # Create an EbasNasaAmes file object
    nas = nasa_ames.EbasNasaAmes()

    # Set file global metadata
    set_fileglobal_metadata(nas)

    # Our data is in winter time, one hour before the UTC
    start = df[("StartEndOffsets", "datetime_start")] - datetime.timedelta(
        hours=1
    )
    end = df[("StartEndOffsets", "datetime_end")] - datetime.timedelta(hours=1)
    sample_times = [(s, e) for s, e in zip(start, end)]
    # Set the time axes and related metadata
    set_time_axes(nas, sample_times)

    # Set metadata and data for all variables
    set_variables(nas, df, df_substances)

    # write the file:
    SUPPRESS_SORT_VARIABLES = 1
    nas.metadata.comp_name = "NMHC"
    nas.write(
        createfiles=True,
        destdir=export_dir,
        flags=FLAGS_AS_IS,
        # Note on the flag:
        # We have a special way of specifying the flag, and it is easier
        # to consider is as a variable and not let the ebas io module to the
        # flagging
        suppress=SUPPRESS_METADATA_OCCURRENCE | SUPPRESS_SORT_VARIABLES,
    )
    # createfiles=True
    #     Actually creates output files, else the output would go to STDOUT.
    # You can also specify:
    #     destdir='path/to/directory'
    #         Specify a specific relative or absolute path to a directory the
    #         files should be written to
    #     flags=FLAGS_COMPRESS
    #         Compresses the file size by reducing flag columns.
    #         Flag columns will be less explicit and thus less intuitive for
    #         humans to read.
    #     flags=FLAGS_ALL
    #         Always generate one flag column per variable. Very intuitive to
    #         read, but increases filesize.
    #     The default for flags is: Generate one flag column per file if the
    #     flags are the same for all variables in the file. Else generate one
    #     flag column per variable.
    #     This is a trade-off between the advantages and disadvantages of the
    #     above mentioned approaches.


if __name__ == "__main__":
    # A small test set for the export
    hour = datetime.timedelta(hours=1)
    df = pd.DataFrame(
        {
            ("StartEndOffsets", "datetime_start"): [
                datetime.datetime.now() - 1 * hour,
                datetime.datetime.now() - 2 * hour,
            ],
            ("StartEndOffsets", "datetime_end"): [
                datetime.datetime.now(),
                datetime.datetime.now() - 1 * hour,
            ],
            ("methane", "conc"): [1, 2],
            ("methane", "u_expanded"): [1, 2],
            ("methane", "u_precision"): [1, 2],
            ("methane", "flag"): [
                Flags.UNSPECIFIED_LOCAL_CONTAMINATION,
                Flags.BELOW_DETECTION_LIMIT,
            ],
            ("propane", "conc"): [1, 3],
            ("propane", "u_expanded"): [1, 3],
            ("propane", "u_precision"): [1, 3],
            ("propane", "flag"): [
                Flags.VALID,
                Flags.MISSING_MEASUREMENT_UNSPECIFED_REASON,
            ],
        }
    )
    df_substances = pd.DataFrame(
        {"detection_limit": [0.1, 0.2]}, index=["methane", "propane"]
    )
    export_EBAS(
        df,
        df_substances,
        export_dir=Path(
            r"C:\Users\coli\Documents\ovoc-calculations\data\test_ebas"
        ),
    )
