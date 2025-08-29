"""Additional data can be added to TUCAVOC exports.

If you want to create your custom additonal data, you need to follow 
these steps:

* Inherit from :py:class:`tucavoc.additional_data.AdditionalData`
* Implement :py:meth:`tucavoc.additional_data.AdditionalData.get_data` 

If you want to include your additional data in the TUCAVOC widget:

* Also implement the :py:attr:`widget` property. See existing examples.
* In the main widget find where the additional data is defined and add it.
"""

from __future__ import annotations
from datetime import timedelta
from functools import cached_property
from typing import TYPE_CHECKING
import pandas as pd


if TYPE_CHECKING:
    from PySide6 import QtWidgets
    from PySide6.QtCore import QSettings


try:
    from PySide6.QtCore import QSettings
except ImportError:
    class QSettings:
        """Emulate QSettings if PySide6 is not available.
        
        Return always the default values.
        """
        def __init__(self):
            pass

        def value(self, key, default, type):
            return default

        def setValue(self, key, value):
            pass



class AdditionalData:
    """Represent an additonal data in tucavoc.

    :param settings: Settings to use for the additional data.
        Some additional data might need to save user settings if some
        parameters can be selected.
    :param widget: Qt Widget to be displayed in the main widget.

    """

    widget: QtWidgets.QWidget

    settings: QSettings

    def __init__(self, settings: QSettings = None) -> None:
        super().__init__()

        if settings is None:
            self.settings = QSettings()
        else:
            self.settings = settings

    def get_data(self, time_serie: pd.Series) -> pd.DataFrame | None:
        """Get the additional data for the requested times.

        This method must be implemented when creating a new type
        of additional data.

        :param time_serie: Times for which
            the additional data should be returned.

        :return: Dataframe with the additional data. Can be many columns,
            but they have to provide a value for each time in the
            time_serie.
        """
        pass

    def add_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add data to the dataframe.

        :param df: Dataframe to which the data should be added.
            Should not be changed inplace.

        :return: Dataframe with additional data.
        """

        additional_data = self.get_data(df[("-", "datetime")])
        additional_data.columns = pd.MultiIndex.from_product(
            [[type(self).__name__], additional_data.columns]
        )

        return df.join(additional_data)


class StartEndOffsets(AdditionalData):
    def get_data(self, time_serie: pd.Series) -> pd.DataFrame:
        offset_start = timedelta(
            minutes=self.settings.value(
                "AdditionalData.StartEndOffsets.start_time_offset", 0, int
            )
        )
        offset_end = timedelta(
            minutes=self.settings.value(
                "AdditionalData.StartEndOffsets.end_time_offset", 0, int
            )
        )
        return pd.DataFrame(
            {
                "datetime_start": time_serie + offset_start,
                "datetime_end": time_serie + offset_end,
            }
        )

    @cached_property
    def widget(self) -> QtWidgets.QWidget:

            
        from PySide6.QtGui import QIntValidator
        from PySide6 import QtWidgets

        
        widget = QtWidgets.QWidget()

        layout = QtWidgets.QFormLayout()

        start_time = self.settings.value(
            "AdditionalData.StartEndOffsets.start_time_offset", 0, int
        )
        end_time = self.settings.value(
            "AdditionalData.StartEndOffsets.end_time_offset", 0, int
        )

        self.start_time_edit = QtWidgets.QLineEdit(str(start_time), widget)
        layout.addRow("Offset to start [minutes]", self.start_time_edit)
        self.end_time_edit = QtWidgets.QLineEdit(str(end_time), widget)
        layout.addRow("Offset to end [minutes]", self.end_time_edit)

        self.start_time_edit.setValidator(QIntValidator(-20000, 20000, widget))
        self.end_time_edit.setValidator(QIntValidator(-20000, 20000, widget))
        self.start_time_edit.textChanged.connect(
            lambda val: self.settings.setValue(
                "AdditionalData.StartEndOffsets.start_time_offset", val
            )
        )
        self.end_time_edit.textChanged.connect(
            lambda val: self.settings.setValue(
                "AdditionalData.StartEndOffsets.end_time_offset", val
            )
        )

        widget.setLayout(layout)
        return widget
