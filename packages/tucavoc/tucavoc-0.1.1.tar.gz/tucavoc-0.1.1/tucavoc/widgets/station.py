"""Widget for setting parameters of a station."""

from PySide6 import QtWidgets


from PySide6.QtCore import QSettings
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator



from tucavoc.widgets.utils import LineEditWithSetttings





class StationEditWidget(QtWidgets.QDialog):
    """Widget for setting parameters of a station."""

    def __init__(
        self,
        station_id: str = "XXX",
        settings: QSettings = None,
        settings_name: str = "",
    ) -> None:
        super().__init__()

        self.station_id = station_id

        self.settings_name = f"{settings_name}.{station_id}"

        if settings is None:
            self.settings = QSettings()
        else:
            self.settings = settings

        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the user interface."""

        self.setWindowTitle("Station parameters")

        self.layout = QtWidgets.QFormLayout(self)

        self.layout.addRow("Station ID", QtWidgets.QLabel(self.station_id))

        self.name = LineEditWithSetttings(
            f"{self.settings_name}.name", self.settings, self
        )
        self.layout.addRow("Name", self.name)

        self.setLayout(self.layout)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    widget = StationEditWidget()
    widget.show()

    sys.exit(app.exec())
