#!/usr/bin/env python

import datetime
from ebas.io.file.nasa_ames import EbasNasaAmes
from ebas.io.file import SUPPRESS_METADATA_OCCURRENCE, FLAGS_AS_IS
from nilutility.datatypes import DataObject
from nilutility.datetime_helper import DatetimeInterval

from tucavoc.exports.ebas_genfile import set_fileglobal_metadata, set_time_axes

nas = EbasNasaAmes()
# sample times: just one sample for demo
nas.sample_times.append(
    DatetimeInterval(
        datetime.datetime(2022, 1, 1), datetime.datetime(2022, 1, 1, 1)
    )
)

# Add var 1
flags = [[], []]
metadata = DataObject()
metadata.comp_name = "methanol"
metadata.unit = "pmol/mol"
metadata.statistics = "arithmetic mean"
metadata.detection_limit = (25, "pmol/mol")
nas.variables.append(
    DataObject(
        values_=[3.2, 1.3],
        flags=flags,
        metadata=metadata,
        flagcol=False,
    )
)

# Add var 2
metadata = metadata.copy()
metadata.statistics = "expanded uncertainty 2sigma"
del metadata["detection_limit"]
nas.variables.append(
    DataObject(
        values_=[2.2, 1.3],
        flags=flags,
        metadata=metadata,
        flagcol=False,
    )
)

# Add var 3
metadata = metadata.copy()
metadata.statistics = "precision"
nas.variables.append(
    DataObject(
        values_=[1.2, 1.3],
        flags=flags,
        metadata=metadata,
        flagcol=True,
    )
)
# Add second sub
flags = [[], [999]]
metadata = DataObject()
metadata.comp_name = "ethanol"
metadata.unit = "pmol/mol"
metadata.statistics = "arithmetic mean"
metadata.detection_limit = (25, "pmol/mol")
nas.variables.append(
    DataObject(
        values_=[5.2, 1.1],
        flags=flags,
        metadata=metadata,
        flagcol=False,
    )
)

# Add var 2
metadata = metadata.copy()
metadata.statistics = "expanded uncertainty 2sigma"
del metadata["detection_limit"]
nas.variables.append(
    DataObject(
        values_=[3.2, 1.3],
        flags=flags,
        metadata=metadata,
        flagcol=False,
    )
)

# Add var 3
metadata = metadata.copy()
metadata.statistics = "precision"
nas.variables.append(
    DataObject(
        values_=[1.2, 2.3],
        flags=flags,
        metadata=metadata,
        flagcol=True,
    )
)

# Set file global metadata
nas.metadata.comp_name = "NMHC"

set_fileglobal_metadata(nas)
set_time_axes(
    nas,
    [
        (datetime.datetime(2022, 1, 1), datetime.datetime(2022, 1, 1, 3)),
        (datetime.datetime(2022, 1, 2), datetime.datetime(2022, 1, 1, 4)),
    ],
)
# use suppress=SUPPRESS_METADATA_OCCURRENCE:
# ebas-io will not move any metadata between variable metadata and file global
# metadata
nas.write(
    createfiles=True,
    flags=FLAGS_AS_IS,
    destdir=r"C:\Users\coli\Documents\ovoc-calculations\data\test_ebas",
    suppress=SUPPRESS_METADATA_OCCURRENCE,
)
