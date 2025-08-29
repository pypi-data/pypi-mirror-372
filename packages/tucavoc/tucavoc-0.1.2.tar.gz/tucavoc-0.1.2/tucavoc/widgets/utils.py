"""Widgets useful for all."""

from pathlib import Path
import sys
from PySide6.QtCore import QSettings, Signal, QEvent
from PySide6.QtWidgets import (
    QWidget,
    QLineEdit,
    QCheckBox,
    QLabel,
    QApplication,
    QWidget,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QHBoxLayout,
    QStyledItemDelegate,
)
from PySide6.QtGui import (
    QDoubleValidator,
    QPalette,
    QStandardItem,
    QFontMetrics,
)
from PySide6.QtGui import Qt


from tucavoc.abstract_uncertainty import (
    BoolParameter,
    FloatParamter,
    OptionalFloatParameter,
    StrParameter,
)


class LineEditWithSetttings(QLineEdit):
    """A special line edit that save to settings."""

    def __init__(
        self,
        settings_name: str,
        settings: QSettings,
        parent: QWidget = ...,
        initial_value: str = "",
    ) -> None:
        self.settings_name = settings_name
        self.settings = settings
        # Set the line edit start value
        initial_text = str(self.settings.value(settings_name, initial_value))

        # Initalize the QLineEdit
        super().__init__(initial_text, parent)

        def set_value(text: str):
            self.settings.setValue(self.settings_name, text)

        self.textChanged.connect(set_value)

        # Ensure that the settings are written
        set_value(initial_text)


class ValueEditWithSettings(QLineEdit):
    """A special line edit that handle float values and save to settings."""

    def __init__(
        self,
        settings_name: str,
        settings: QSettings,
        parent: QWidget = ...,
        initial_value: float = 1.0,
    ) -> None:
        self.settings_name = settings_name
        self.settings = settings
        # Set the line edit start value
        initial_text = str(self.settings.value(settings_name, initial_value))

        # Initalize the QLineEdit
        super().__init__(initial_text, parent)
        # Make sure only double are given
        self.setValidator(QDoubleValidator(self))

        def set_value(text: str):
            self.settings.setValue(self.settings_name, text)

        self.textChanged.connect(set_value)

        # Ensure that the settings are written
        set_value(initial_text)


class CheckBoxWithSettings(QCheckBox):
    """A checkbox that  save to settings."""

    def __init__(
        self,
        settings_name: str,
        settings: QSettings,
        parent: QWidget = ...,
        default_initial_state: bool = True,
        check_box_name: str = "",
    ) -> None:
        self.settings_name = settings_name
        self.settings = settings
        # Setup the checkbox
        super().__init__(check_box_name, parent)
        # Read the settings to know the state or use default
        initial_state = self.settings.value(
            settings_name, default_initial_state, bool
        )
        self.setChecked(initial_state)

        def set_value(state: bool):
            self.settings.setValue(self.settings_name, bool(state))

        self.stateChanged.connect(set_value)

        # Ensure that the settings are written
        set_value(initial_state)


def create_parameter_widget(
    param,
    settings: QSettings,
    parent: QWidget,
    substance: str = "-",
):
    if isinstance(param, FloatParamter):
        widget = ValueEditWithSettings(
            f"{substance}.{param.name}",
            settings,
            parent,
            param.val,
        )
        widget.setValidator(
            QDoubleValidator(
                bottom=param.min_val,
                top=param.max_val,
                decimals=param.decimals,
                parent=parent,
            )
        )
        widget.setAlignment(Qt.AlignRight)
        if type(param) == OptionalFloatParameter:
            # Add a check box that makes is possible to choose or not
            # to set the data manually
            main_widget = QWidget(parent)
            layout = QHBoxLayout()
            main_widget.setLayout(layout)
            layout.addWidget(widget)
            from_data_checkbox = CheckBoxWithSettings(
                f"{substance}.{param.name}.from_data",
                settings,
                parent,
                check_box_name="From Data",
            )
            layout.addWidget(from_data_checkbox)

            # connect the checkbox to deactivate the value edit
            def set_value(checked: bool, rel_value_edit: QLineEdit = widget):
                rel_value_edit.setDisabled(checked)

            # Set the intial condition
            widget.setDisabled(
                from_data_checkbox.checkState() == Qt.CheckState.Checked
            )
            from_data_checkbox.stateChanged.connect(set_value)
            # Override the function to make some features available later
            main_widget.setText = lambda txt, w=widget: w.setText(txt)
            # Make it smaller
            main_widget.setStyleSheet("border-width:0px;")
            from_data_checkbox.setStyleSheet("border-width:0px;")
            widget = main_widget

    elif type(param) == BoolParameter:
        widget = CheckBoxWithSettings(
            f"{substance}.{param.name}", settings, parent
        )
        widget.setStyleSheet("margin-left:50%; margin-right:50%;")
    elif type(param) == StrParameter:
        widget = LineEditWithSetttings(
            f"{substance}.{param.name}",
            settings,
            parent,
            initial_value=param.val,
        )
    else:
        raise TypeError(param)

    return widget


class FileShowerLabel(QLabel):
    """Special label for showing file paths."""

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)


class FileSelector(QWidget):
    """Allows to select a file and show the path.

    Also works for directory if is_dir is selected
    """

    file_changed: Signal = Signal(Path)
    current_file: Path

    def __init__(
        self,
        label: str,
        parent: QWidget = None,
        settings: QSettings = None,
        is_dir: bool = False,
    ) -> None:
        super().__init__(parent)
        self.label = label

        self.is_dir = is_dir

        if settings is None:
            self.settings = QSettings(self)
        else:
            self.settings = settings

        self.current_file = Path(
            self.settings.value(f"FileSelector.previous_file_{label}", ".")
        )
        layout = QHBoxLayout(self)

        self.setLayout(layout)

        layout.addWidget(QLabel(label))
        self.label_selected_file = FileShowerLabel(
            str(self.current_file), self
        )
        layout.addWidget(self.label_selected_file)
        self.button_select_file = QPushButton(
            "Select " + ("Directory" if self.is_dir else "File"), self
        )
        layout.addWidget(self.button_select_file)

        self.button_select_file.clicked.connect(self.change_file)

    def change_file(self):
        """Change the currently selected file."""
        if self.is_dir:
            file = QFileDialog.getExistingDirectory(
                self, caption=f"Select dir for {self.label}", dir="."
            )
        else:
            file, _filter = QFileDialog.getOpenFileName(
                parent=self,
                caption=f"Select file for {self.label}",
                dir=".",
            )

        if file:
            self.set_file(file)

    def set_file(self, file: str | Path):
        self.settings.setValue(
            f"FileSelector.previous_file_{self.label}", str(file)
        )
        self.current_file = Path(file)
        self.label_selected_file.setText(str(file))
        self.file_changed.emit(Path(file))


class CheckableComboBox(QComboBox):
    element_checked: Signal = Signal(str, Qt.CheckState)

    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # Make the lineedit the same color as QPushButton
        palette = qApp.palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object, event: QEvent):
        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.scenePosition().toPoint())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    new_state = Qt.Unchecked
                else:
                    new_state = Qt.Checked
                item.setCheckState(new_state)
                self.element_checked.emit(item.text(), new_state)

                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(
            text, Qt.ElideRight, self.lineEdit().width()
        )
        self.lineEdit().setText(elidedText)

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def setItemChecked(self, index, checked: bool = False):
        item = self.model().item(index, self.modelColumn())
        if checked:
            state = Qt.Checked
        else:
            state = Qt.Unchecked
        item.setCheckState(state)

    def itemChecked(self, index):
        item = self.model().item(index, self.modelColumn())
        return item.checkState() == Qt.Checked

    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).data())
        return res


class CheckableComboBoxApp(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 150)

        mainLayout = QVBoxLayout()

        self.combo = CheckableComboBox()
        mainLayout.addWidget(self.combo)

        for i in range(6):
            self.combo.addItem("Item {0}".format(str(i)))
            self.combo.setItemChecked(i, i % 2 == 0)

        btn = QPushButton("Print Values")
        btn.clicked.connect(self.getValue)
        mainLayout.addWidget(btn)

        self.setLayout(mainLayout)

    def getValue(self):
        for i in range(self.combo.count()):
            print(
                "Index: {0} is checked {1}".format(
                    i, self.combo.itemChecked(i)
                )
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # myApp = FileSelector("test", is_dir=False)
    myApp = CheckableComboBoxApp()
    myApp.show()

    sys.exit(app.exec())
