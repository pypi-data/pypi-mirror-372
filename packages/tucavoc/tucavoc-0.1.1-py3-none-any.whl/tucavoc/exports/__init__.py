"""Exports format available in tucavoc.

Adding an export format can be done the following way:

    * implement a function for the export following the function format of
        :py:func:`~tucavoc.exports.template_export_function` 
    * add your function in the `EXPORTS_DICT` in the file
        `tucavoc.exports.__init__.py` .

This will ensure compatibility with the tucavoc API and tucavoc widget.

.. note::

    If your export format also require additonal data,
    might also need to implement an Additional data. 
"""
import enum
from pathlib import Path
import pandas as pd
from tucavoc.abstract_uncertainty import Uncertainty

from tucavoc.additional_data import AdditionalData, StartEndOffsets
from tucavoc.additional_data.station import StationInformation
from tucavoc import uncertainties
    
from .empa_qa_tools import export_EmpaQATool
from .excel import export_to_table
try:
    from .ebas_genfile import export_EBAS
except ImportError:
    # Dependency to ebas_genfile not installed
    def export_EBAS(*args, **kwargs):
        raise ImportError(
            "ebas-io package not installed. See https://git.nilu.no/ebas/ebas-io "
        )


class ExportFormat(enum.Enum):
    """The different export formats from tucavoc."""

    excel = enum.auto()
    EmpaQATool_csv = enum.auto()
    EBAS_nas = enum.auto()


EXPORTS_DICT = {
    ExportFormat.excel: export_to_table,
    ExportFormat.EmpaQATool_csv: export_EmpaQATool,
    ExportFormat.EBAS_nas: export_EBAS,
}

# Required additonal data
EXPORT_REQUIRES: dict[ExportFormat, list[Uncertainty | AdditionalData]] = {
    ExportFormat.excel: [],
    ExportFormat.EmpaQATool_csv: [
        StartEndOffsets(),
        uncertainties.PRECISION,
        StationInformation(),
    ],
    ExportFormat.EBAS_nas: [StartEndOffsets(), uncertainties.PRECISION],
}


def template_export_function(
    df_calc: pd.DataFrame,
    df_substances: pd.DataFrame,
    export_path: Path,
    additional_data: dict[type, AdditionalData] = {},
):
    """A template function for the export.

    :arg df_calc: The dataframe with the calculation.
    :arg substances: A list containing the name of the substances to export.
    :arg export_path: the file/dir in which the export should be done
        (the suffix should be added in the export function)
    :arg additional_data: A dictionary containing the additional data
        required for the export. The keys are the type of the additional data
        and the values are the additional data.
    """
    ...
