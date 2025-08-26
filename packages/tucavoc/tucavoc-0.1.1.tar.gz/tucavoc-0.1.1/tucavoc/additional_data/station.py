from __future__ import annotations
from functools import cached_property
from typing import TYPE_CHECKING

from tucavoc.additional_data import AdditionalData
from tucavoc.station import Station

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget, QComboBox


class StationInformation(AdditionalData):
    """Widget allowing to select which station is used and open editting of station."""

    ids_combobox: QComboBox

    settings_str = "AdditionalData.StationInformation"

    @property
    def current_station(self) -> str:
        """Return the current station."""
        return self.settings.value(f"{self.settings_str}.current_station", "XXX", str)

    @current_station.setter
    def current_station(self, station_id: str):
        """Set the current station."""
        self.settings.setValue(f"{self.settings_str}.current_station", station_id)

    @property
    def all_stations(self) -> list[str]:
        """Return all the stations."""
        return self.settings.value(f"{self.settings_str}.all_stations", "", str).split(
            ","
        )

    @cached_property
    def widget(self) -> QWidget:

        from PySide6 import QtWidgets

        

        widget = QtWidgets.QWidget()

        ids_combobox = QtWidgets.QComboBox()
        self.ids_combobox = ids_combobox

        layout = QtWidgets.QHBoxLayout()

        ids_combobox.addItems(self.all_stations)
        ids_combobox.setCurrentText(self.current_station)

        def change_station(station_id):
            self.current_station = station_id

        ids_combobox.currentTextChanged.connect(change_station)

        layout.addWidget(ids_combobox)

        # Button to open the station editor
        edit_button = QtWidgets.QPushButton("Edit station")
        edit_button.clicked.connect(self.open_station_editor)
        layout.addWidget(edit_button)

        # Button to create a new station
        new_button = QtWidgets.QPushButton("New station")
        new_button.clicked.connect(self.create_new_station)
        layout.addWidget(new_button)

        widget.setLayout(layout)
        self.widget = widget
        return widget

    def open_station_editor(self):
        """Open the station editor."""
        from tucavoc.widgets.station import StationEditWidget
        self.station_editor = StationEditWidget(
            station_id=self.current_station,
            settings=self.settings,
            settings_name=self.settings_str,
        )

        # Show the dialog until the user closes it
        self.station_editor.exec()

    def create_new_station(self):
        """Create a new station."""
        from PySide6 import QtWidgets

        # First ask for a station ID
        station_id, ok = QtWidgets.QInputDialog.getText(
            self.widget, "New station", "Station ID"
        )
        if not ok:
            return

        # Check the name of the station is okay
        if len(station_id) != 3:
            QtWidgets.QMessageBox.critical(
                self.widget,
                "Station ID",
                "Station ID must be 3 letters long",
            )
            return
        if not station_id.isupper():
            QtWidgets.QMessageBox.critical(
                self.widget,
                "Station ID",
                "Station ID must be upper case",
            )
            return
        # Must be letters only
        if not station_id.isalpha():
            QtWidgets.QMessageBox.critical(
                self.widget,
                "Station ID",
                "Station ID must be letters only",
            )
            return

        # Check the station does not already exists
        all_stations = self.all_stations
        if station_id in all_stations:
            QtWidgets.QMessageBox.critical(
                self.widget,
                "Station ID",
                "Station ID already exists",
            )
            return

        # Create the station
        all_stations.append(station_id)
        self.settings.setValue(
            f"{self.settings_str}.all_stations", ",".join(all_stations)
        )
        self.settings.setValue(f"{self.settings_str}.current_station", station_id)
        self.ids_combobox.addItem(station_id)
        self.ids_combobox.setCurrentText(station_id)

        # Open the station editor
        self.open_station_editor()

    def get_station(self) -> Station:
        """Create a station from the settings.

        :return: Station created from the settings.
        """

        station_id = self.current_station

        station_settings_str = f"{self.settings_str}.{station_id}"

        station = Station(
            station_id,
            name=self.settings.value(f"{station_settings_str}.name", ""),
        )

        return station


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from PySide6 import QtCore

    app = QApplication([])

    settings = QtCore.QSettings("test", "test")
    widget = StationInformation(settings)
    widget.widget.show()

    app.exec()
