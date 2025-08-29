from pathlib import Path
import sys
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QButtonGroup,
    QRadioButton,
    QGroupBox,
    QLineEdit,
    QCheckBox,
    QGridLayout,
    QScrollArea,
    QComboBox,
    QMessageBox,
    QInputDialog,
    QFormLayout,
)
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import QSettings


import pandas as pd
from tucavoc import parameters

from tucavoc.widgets.utils import (
    ValueEditWithSettings,
    create_parameter_widget,
)
from tucavoc.abstract_uncertainty import (
    BoolParameter,
    FloatParamter,
    Parameter,
)
from tucavoc.parameters import LOD, ERROR_SYSTEMATIC_INSTR


class ParametersSelector(QGroupBox):
    parameters: list[Parameter]
    widgets: list[QWidget]

    def __init__(
        self,
        parameters: list[Parameter],
        settings: QSettings = None,
        parent: QWidget = None,
    ) -> None:
        super().__init__("Global Parameters", parent)
        self.parameters = parameters

        if settings is None:
            settings = QSettings(
                "./settings.ini", QSettings.IniFormat, parent=self
            )
        self.settings = settings

        layout = QGridLayout()

        self.widgets = []

        for row, parameter in enumerate(parameters):
            widget = create_parameter_widget(parameter, self.settings, self)

            layout.addWidget(QLabel(parameter.full_name, self), row, 0)
            layout.addWidget(QLabel(f"[{parameter.unit}]", self), row, 1)
            layout.addWidget(widget, row, 2)
            self.widgets.append(widget)

        self.setLayout(layout)

    def get_param(self, param: Parameter) -> float | int:
        """Return the value for the requested parameter."""
        return self.settings.value(f"-.{param.name}", param.val, param.type)

    def get_parameters_dict(self) -> dict[str, int]:
        """Return a dictionary mapping parameter names to their values."""
        return {param.name: self.get_param(param) for param in self.parameters}

    def get_widget_of_param(self, param: Parameter) -> QWidget:
        if param not in self.parameters:
            raise IndexError(f"{param} not in {self}")
        index = self.parameters.index(param)
        return self.widgets[index]


if __name__ == "__main__":
    app = QApplication([])

    widget = ParametersSelector([LOD, ERROR_SYSTEMATIC_INSTR])
    widget.show()

    sys.exit(app.exec())
