"""A widget for selecting the q settings group."""

import json
from os import PathLike
import sys
from typing import Any
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QApplication,
    QLineEdit,
    QPushButton,
    QInputDialog,
    QFileDialog,
    QStyle,
)
from PySide6.QtCore import QSettings, Signal


class QSettingsSelector(QWidget):

    settings_changed = Signal()
    _last_file: None | PathLike

    def __init__(
        self, settings: QSettings = None, parent: QWidget = None
    ) -> None:
        super().__init__(parent)

        self._last_file = None

        layout = QVBoxLayout(self)
        layout_buttons = QHBoxLayout()
        layout.addLayout(layout_buttons)

        # Create default settings if was not given
        if settings is None:
            settings = QSettings("QSettingsSelector", "Default", self)
        self.settings = settings

        # Settings selection
        self.settings_selector = QComboBox(self)
        keys = self.settings.childGroups() or ["Default"]
        self.settings_selector.addItems(keys)
        layout.addWidget(self.settings_selector)
        self.settings_selector.currentTextChanged.connect(self._change_group)

        # Load the group from the last time
        settings_name = self.settings.value("last_group", "Default", str)
        self.settings.beginGroup(settings_name)
        self.settings_selector.setCurrentText(settings_name)

        # Add new group
        icon = self.style().standardIcon(QStyle.SP_FileDialogNewFolder)
        new_button = QPushButton(icon, "New", self)
        new_button.clicked.connect(self._open_new_group_dialog)
        layout_buttons.addWidget(new_button)

        # Add Save button
        icon = self.style().standardIcon(QStyle.SP_DialogSaveButton)
        new_button = QPushButton(icon, "", self)
        new_button.clicked.connect(self._quick_save)
        layout_buttons.addWidget(new_button)

        # Add SaveAs button
        icon = self.style().standardIcon(QStyle.SP_DialogSaveButton)
        new_button = QPushButton(icon, "Save", self)
        new_button.clicked.connect(self._save)
        layout_buttons.addWidget(new_button)

        # Add load button
        icon = self.style().standardIcon(QStyle.SP_DialogOpenButton)
        new_button = QPushButton(icon, "Load", self)
        new_button.clicked.connect(self._load)
        layout_buttons.addWidget(new_button)

    def _change_group(self, new_group: str):
        self._last_file = None
        # Save in the 'general group' what the last group was
        self.settings.endGroup()
        # self.settings.beginGroup("General")
        self.settings.setValue("last_group", new_group)

        # When the group is changed, settins are loaded
        self.settings.beginGroup(new_group)
        self.settings_changed.emit()

    def _open_new_group_dialog(self):
        text, success = QInputDialog.getText(
            self,
            "New Settings Configuration",
            "Choose a name for the new settings.",
            text="new_config",
        )
        if success and self.settings_selector.findText(text) == -1:
            self.settings_selector.addItem(text)
            # Add the current vlues to the new settings
            current_key_values = self._all_key_values()
            # Now that is is changed, set the new default
            self._change_group(text)
            for key, value in current_key_values.items():
                self.settings.setValue(key, value)

            self.settings_selector.setCurrentText(text)

    def _all_key_values(self) -> dict[str, Any]:
        """Current keys and values of the group that is now."""

        return {
            key: self.settings.value(key) for key in self.settings.allKeys()
        }

    def _quick_save(self):
        """Save to the lastly selected file."""
        if self._last_file is None:
            self._save()
        else:
            self._save_to_file(self._last_file)

    def _save(self):
        """Save the settings.

        Opens a dialog that let the user choose different parameters.
        """

        fileName, selectedFilter = QFileDialog.getSaveFileName(
            self,
            f"Save current settings '{self.settings.group()}' to file",
            filter="Settings (*.json)",
        )
        if selectedFilter == "Settings (*.json)":
            self._save_to_file(fileName)

    def _save_to_file(self, file: PathLike):
        settings_mapping = self._all_key_values()
        self._last_file = file
        with open(file, "w") as f:
            json.dump(settings_mapping, f, indent=2)

    def _load(self):
        """Load the settings.

        Opens a dialog that let the user choose different parameters.
        """
        fileName, selectedFilter = QFileDialog.getOpenFileName(
            self,
            f"Load settings for '{self.settings.group()}' from file.",
            filter="Settings (*.json)",
        )
        if selectedFilter == "Settings (*.json)":
            group_stem = Path(fileName).stem
            self._change_group(group_stem)
            self.settings_selector.setCurrentText(group_stem)
            with open(fileName, "r") as f:
                settings_mapping = dict(json.load(f))
            for key, value in settings_mapping.items():
                self.settings.setValue(key, value)
            self._last_file = fileName
            self.settings_changed.emit()


if __name__ == "__main__":
    app = QApplication([])

    widget = QWidget()
    layout = QVBoxLayout(widget)

    # settings = QSettings("./data/settings_test.ini", QSettings.IniFormat)
    settings_widget = QSettingsSelector()
    edit = QLineEdit(
        settings_widget.settings.value("swag", "default_value", str)
    )

    settings_widget.settings_changed.connect(
        lambda: edit.setText(
            settings_widget.settings.value("swag", "default_value", str)
        )
    )
    edit.editingFinished.connect(
        lambda: settings_widget.settings.setValue("swag", edit.text())
    )
    layout.addWidget(settings_widget)
    layout.addWidget(edit)

    widget.show()

    sys.exit(app.exec())
