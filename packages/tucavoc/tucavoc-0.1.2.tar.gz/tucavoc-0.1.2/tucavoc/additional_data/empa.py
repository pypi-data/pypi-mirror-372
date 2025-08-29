"""Different Additonal data of EMPA."""
from __future__ import annotations
import datetime
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from tucavoc.additional_data import AdditionalData

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class NABEL_Data(AdditionalData):
    """This can be used to read a nabel file.

    Nabel files contain additional substances that we can
    add to an export.
    Each column is a different substance and they can be selected by
    the user.
    """

    file: Path

    def get_data(self, time_serie: pd.Series) -> pd.DataFrame:
        """Load file from nabel and extract the data corresponding to the run."""

        indexes = np.searchsorted(
            # TODO: add the real start time to the df and use it
            self.df["datetime"],
            time_serie,
            side="right",
        )
        if 0 in indexes:
            raise ValueError(
                f"NABEL data starts at {self.df['datetime'].iloc[0]} "
                f"but tucavoc measurements start at {time_serie.iloc[0]}"
            )
        if len(self.df) in indexes:
            raise ValueError(
                f"NABEL data end at {self.df['datetime'].iloc[-1]} "
                f"but tucavoc measurements end at {time_serie.iloc[-1]}"
            )
        return pd.DataFrame(
            {
                col: (
                    self.df[col].to_numpy()[indexes]
                    + self.df[col].to_numpy()[np.clip(indexes - 1, 0, len(self.df) - 1)]
                )
                / 2
                for col in self.columns
                if not hasattr(self, "substances_layout")
                or self.columns_checkboxes[col].isChecked()
            }
        )

    def _read_file(self, file: Path):

        from PySide6.QtWidgets import QCheckBox

        file = Path(file)
        if not file.is_file():
            raise FileNotFoundError(f"Cannot find nabel file at {file}.")

        df = pd.read_csv(file, encoding="ANSI", sep=";", header=1, skiprows=[2, 3])
        # Fist column is called Kanal: and is for datetime
        # Last column is empty
        self.columns = list(df.columns[1:-1])

        # Convert to py datetime
        df["datetime"] = pd.to_datetime(df["Kanal:"], dayfirst=True)

        self.df = df
        self.columns_checkboxes: dict[str, QCheckBox] = {}
        if hasattr(self, "substances_layout"):
            # Clear the layout
            for i in reversed(range(self.substances_layout.count())):
                self.substances_layout.itemAt(i).widget().deleteLater()

            for col in self.columns:
                col_checkbox = QCheckBox(col)
                self.substances_layout.addWidget(col_checkbox)
                self.columns_checkboxes[col] = col_checkbox
                # Link to the settings
                settings_name = f"tucavoc.NABEL_Data.{col}"
                is_checked = self.settings.value(settings_name, True, bool)
                col_checkbox.setChecked(is_checked)

                def change_value(checked, settings_name=settings_name):
                    self.settings.setValue(settings_name, checked)

                col_checkbox.stateChanged.connect(change_value)

    @cached_property
    def widget(self) -> QWidget:

        from PySide6.QtWidgets import (
            QHBoxLayout,
            QVBoxLayout,
            QWidget,
        )
        from tucavoc.widgets.utils import FileSelector

        widget = QWidget()

        self.substances_layout = QHBoxLayout()

        nabel_file_selector = FileSelector(
            "NABEL_data", parent=widget, settings=self.settings
        )

        nabel_file_selector.file_changed.connect(self._read_file)

        if nabel_file_selector.current_file.is_file():
            self._read_file(nabel_file_selector.current_file)

        layout = QVBoxLayout()
        layout.addWidget(nabel_file_selector)
        layout.addLayout(self.substances_layout)

        widget.setLayout(layout)
        return widget


class BRM_meteo(AdditionalData):
    """The meteorology for BRM."""

    meteo_dir: Path

    def get_data(self, time_serie: pd.Series) -> pd.DataFrame:
        """Read the Bermouster meteo files."""
        if hasattr(self, "meteo_dir"):
            path = self.meteo_dir
        else:
            # Read settings from the file selector
            path = Path(
                self.settings.value(
                    f"FileSelector.previous_file_BRM meteo directory", "."
                )
            )
        if not path.is_dir():
            raise FileNotFoundError(f"{path} for meteo data is not a dir")
        # list the files
        fmt = "Beromuenster-*-10min.csv"
        # read them into pandas
        df_list = [
            pd.read_csv(
                file,
                usecols=["timed", "windspeed_12", "winddirection_12"],
            )
            for file in path.rglob(fmt)
        ]
        if not df_list:
            raise FileNotFoundError(
                f"No files of format {fmt} for brm meteo where found in {path}"
            )
        # concatenate them together
        df_meteo_full = pd.concat(df_list)

        # We need to convert from utc to winter time
        zurich_info = ZoneInfo("Europe/Zurich")
        timedelta_offset = zurich_info.utcoffset(datetime.datetime(2022, 1, 1, 1))
        # Convert timed to winter time
        df_meteo_full["datetime [WZ]"] = (
            pd.to_datetime(df_meteo_full["timed"]) + timedelta_offset
        )

        indexes = np.searchsorted(
            # TODO: add the real start time to the df and use it
            df_meteo_full["datetime [WZ]"],
            time_serie,
            side="right",
        )

        if 0 in indexes:
            raise ValueError(
                f"BRM_meteo data starts at WZ {df_meteo_full['datetime [WZ]'].iloc[0]} "
                f"but tucavoc measurements start at {time_serie.iloc[0]}"
            )
        if len(df_meteo_full) in indexes:
            raise ValueError(
                f"BRM_meteo data ends at WZ {df_meteo_full['datetime [WZ]'].iloc[-1]} "
                f"but tucavoc measurements end at {time_serie.iloc[-1]}"
            )

        return pd.DataFrame(
            # Average between the two brm times
            # Make sure the indexes don't go to far
            {
                col: (
                    df_meteo_full[col].to_numpy()[indexes]
                    + df_meteo_full[col].to_numpy()[
                        np.clip(indexes + 1, 0, len(df_meteo_full) - 1)
                    ]
                )
                / 2
                for col in ["windspeed_12", "winddirection_12"]
            }
        )

    @cached_property
    def widget(self) -> QWidget:
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QVBoxLayout,
            QWidget,
        )
        from tucavoc.widgets.utils import FileSelector

        widget = QWidget()

        self.substances_layout = QHBoxLayout()

        meteo_folder_selector = FileSelector(
            "BRM meteo directory",
            parent=widget,
            settings=self.settings,
            is_dir=True,
        )

        def set_meteo_dir(dir):
            self.meteo_dir = Path(dir)

        meteo_folder_selector.file_changed.connect(set_meteo_dir)

        layout = QVBoxLayout()
        layout.addWidget(meteo_folder_selector)
        layout.addLayout(self.substances_layout)

        widget.setLayout(layout)
        return widget


if __name__ == "__main__":
    # Here I just test our data for some times
    data = NABEL_Data()
    path = r"C:\Users\coli\Documents\ovoc-calculations\data\ZUE_für_GC_10Min.csv"
    data._read_file(path)

    print(
        data.get_data(
            pd.Series(
                [
                    datetime.datetime(2022, 7, 1, 4, 36),
                    datetime.datetime(2022, 7, 1, 8, 21),
                ]
            )
        )
    )

    data = BRM_meteo()
    path = r"C:\Users\coli\Documents\ovoc-calculations\meteo_files"
    data.meteo_dir = Path(path)

    print(
        data.get_data(
            pd.Series(
                [
                    datetime.datetime(2022, 4, 1, 4, 36),
                    datetime.datetime(2022, 4, 1, 8, 21),
                ]
            )
        )
    )
