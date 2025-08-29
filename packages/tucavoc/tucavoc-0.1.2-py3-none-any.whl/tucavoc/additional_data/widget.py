from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QVBoxLayout,
    QCheckBox,
    QDialog,
)
import sys
from tucavoc.additional_data import AdditionalData, StartEndOffsets
from tucavoc.additional_data.empa import NABEL_Data
from PySide6.QtCore import QSettings


class AdditonalDataDialog(QDialog):

    # Store whethere the additional data is activatedc
    additional_data_checked: dict[AdditionalData, bool]

    def __init__(
        self,
        additional_data: list[AdditionalData],
        parent: QWidget = None,
        settings: QSettings = None,
    ) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        if settings is None:
            self.settings = QSettings()
        else:
            self.settings = settings

        self.additional_data_checked = {}
        for data in additional_data:
            checkbox = QCheckBox(type(data).__name__, self)
            layout.addWidget(checkbox)
            layout.addWidget(data.widget)

            settings_name = (
                f"tucavoc.AdditonalDataDialog.activated.{type(data).__name__}"
            )
            activated = self.settings.value(settings_name, False, bool)
            checkbox.setChecked(activated)

            def state_changed(
                activated,
                widget=data.widget,
                settings_name=settings_name,
                data=data,
            ):
                if activated:
                    widget.show()
                else:
                    widget.hide()
                self.additional_data_checked[data] = activated
                self.settings.setValue(settings_name, activated)

            checkbox.stateChanged.connect(state_changed)

            state_changed(activated)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])

    settings = QSettings("EMPA", "test")
    widget = AdditonalDataDialog(
        [NABEL_Data(settings=settings), StartEndOffsets(settings=settings)],
        settings=settings,
    )
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
