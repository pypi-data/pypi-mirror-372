import logging
import sys
from typing import Any
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
    QCheckBox,
    QLabel,
    QGridLayout,
    QLayout,
)
from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
    QCheckBox,
    QLabel,
    QGridLayout,
    QLineEdit,
    QGroupBox,
)
from PySide6.QtGui import QDoubleValidator

from tucavoc.abstract_uncertainty import FloatParamter, Parameter, Uncertainty
from tucavoc.uncertainties import (
    Calibration,
    FurtherInstrumentalProblems,
    PeakIntegration,
    Linearity,
    Precision,
    Sampling,
    Volume,
)


def build_uncertainty_layout(uncertainty: Uncertainty) -> QGridLayout:
    settings = QSettings("EMPA", f"TUCAVOC.{uncertainty.name}")
    layout = QGridLayout()


class UncertaintiesWidget(QGroupBox):
    """Widget making the user able to select the different uncertainties he wants to use."""

    uncertainties: list[Uncertainty]
    check_boxes: dict[Uncertainty, QCheckBox]
    settings: QSettings

    uncertainty_checked = Signal(Uncertainty, bool)

    SETTING_STR_NAME: str = "uncertainty_activated"

    def __init__(
        self,
        uncertainties: list[Uncertainty],
        parent: QWidget = None,
        settings: QSettings = None,
    ) -> None:
        super().__init__("Uncertainties Selection", parent)
        if settings is None:
            settings = QSettings(
                "./settings.ini", QSettings.IniFormat, parent=self
            )
        self.settings = settings
        self.logger = logging.getLogger("tucavoc.UncertaintiesWidget")

        self.uncertainties = uncertainties
        layout = QVBoxLayout(self)

        self.check_boxes = {}

        for uncertainty in self.uncertainties:
            check_box = QCheckBox(uncertainty.name, self)
            setting_str = f"{self.SETTING_STR_NAME}.{uncertainty.name}"
            # Read the name in the settings
            initial_state = self.settings.value(setting_str, True, bool)
            check_box.setChecked(initial_state)
            check_box.setToolTip(uncertainty.explanation)

            def on_changed(
                new_state: bool,
                uncertainty=uncertainty,
                setting_str=setting_str,
            ):
                self.settings.setValue(setting_str, new_state)
                self.uncertainty_checked.emit(uncertainty, new_state)

            # Will change the settings
            check_box.stateChanged.connect(on_changed)

            layout.addWidget(check_box)

            self.check_boxes[uncertainty] = check_box

        self.setLayout(layout)

    def get_selected_uncertainties(self) -> list[Uncertainty]:
        """Return the uncertainty values that have been selected by the user."""

        return [
            uncertainty
            for uncertainty, check_box in self.check_boxes.items()
            if check_box.checkState() == Qt.CheckState.Checked
        ]

    def get_required_parameters(self) -> list[Parameter]:
        """Return the parameters required for the selected uncertainties."""
        return sum(
            [u.parameters for u in self.get_selected_uncertainties()], []
        )

    def set_selected_uncertainties_from_settings(self) -> None:
        """Set the unertainties that should be selected."""

        for uncertainty, check_box in self.check_boxes.items():
            setting_str = f"{self.SETTING_STR_NAME}.{uncertainty.name}"
            new_state = self.settings.value(setting_str, True, bool)
            check_box.setChecked(new_state)
            # Also emit the signal for widgets listening to this
            self.uncertainty_checked.emit(uncertainty, new_state)


if __name__ == "__main__":
    app = QApplication([])

    widget = UncertaintiesWidget(
        [
            Precision(),
            Calibration(),
            PeakIntegration(),
            Volume(),
            FurtherInstrumentalProblems(),
            Linearity(),
            Sampling(),
        ]
    )
    widget.uncertainty_checked.connect(lambda *args: print(*args))
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
