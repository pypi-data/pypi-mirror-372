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
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import QSettings


import pandas as pd

from tucavoc.widgets.utils import (
    ValueEditWithSettings,
    create_parameter_widget,
)
from tucavoc.abstract_uncertainty import (
    BoolParameter,
    FloatParamter,
    OptionalFloatParameter,
    Parameter,
    StrParameter,
)
from tucavoc.calculations import get_groups_dict
from tucavoc.parameters import (
    LOD,
    ERROR_SYSTEMATIC_INSTR,
    CONC_CALIB,
    USE_FOR_GENERAL_CRF,
)


class SubstancesSelector(QGroupBox):
    """Select which substances are used and their parameters and which ones can be used.

    Can decide the following:
    * Whether the substance are selected for the output.
    * The value of the carbon number for substances.
    * Whether the substance is a NPL substance.

    :arg use_table: Whether to show on a table or on a gridlayout
    """

    settings: QSettings

    npl_lineedits: dict[str, QLineEdit]
    parameters: list[Parameter]
    column_of_parameters: dict[str, int]
    table: QTableWidget

    widgets_dict: dict[
        # Substance name
        str,
        dict[
            # Parameter name
            str,
            QWidget,
        ],
    ]

    def __init__(
        self,
        substances: list[str],
        parameters: list[Parameter],
        settings: QSettings = None,
        parent: QWidget = None,
        use_table: bool = True,
    ) -> None:
        super().__init__("Substances", parent)
        if settings is None:
            settings = QSettings(
                "./settings.ini", QSettings.IniFormat, parent=self
            )
        self.settings = settings
        self.parameters = parameters
        self.column_of_parameters = {}

        main_layout = QVBoxLayout(self)

        if len(set(substances)) != len(substances):
            raise ValueError(f"Duplicate substances received: {substances}")
        row_offset = 1 if use_table else 3
        col_offset = 3

        if use_table:
            table = QTableWidget(
                len(substances) + row_offset,
                len(parameters) + col_offset,
                self,
            )
            main_layout.addWidget(table)
        else:
            internal_widget = QWidget(self)
            layout = QGridLayout(internal_widget)
            main_layout.addWidget(internal_widget)

            scroll_area = QScrollArea()
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(internal_widget)
            main_layout.addWidget(scroll_area)

        lab = "Include Substance \n in output file"
        if use_table:
            table.setHorizontalHeaderItem(0, QTableWidgetItem(lab))
        else:
            layout.addWidget(QLabel(lab, self), 0, 0)

        # Adds a button with add group for creating new group
        add_group_button = QPushButton("+", self)
        if use_table:
            table.setHorizontalHeaderItem(1, QTableWidgetItem("Groups"))
            table.setCellWidget(0, 1, add_group_button)
        else:
            group_layout = QHBoxLayout()
            group_layout.addWidget(QLabel("Group", self))
            group_layout.addWidget(add_group_button)
            layout.addLayout(group_layout, 0, 1)

        if use_table:
            table.setVerticalHeaderItem(0, QTableWidgetItem("Substances"))
        # table.setVerticalHeaderItem(1, QTableWidgetItem(""))
        if use_table:
            table.setHorizontalHeaderItem(2, QTableWidgetItem("In Calib"))
        else:
            layout.addWidget(QLabel("In Calib", self), 0, 2)
        # Add the parameters
        for i, param in enumerate(parameters):
            col = i + col_offset
            # Add column labels
            if not use_table:
                layout.addWidget(
                    QLabel(f"{param.name}"), 0, col, Qt.AlignRight
                )
                layout.addWidget(
                    QLabel(f"[{param.unit}]"), 1, col, Qt.AlignRight
                )

            if isinstance(param, FloatParamter):
                set_all_button = QPushButton(f"Set to All")
                set_all_button.clicked.connect(
                    lambda *args, param=param: self.open_set_all_dialog(param)
                )
            else:
                set_all_button = QLabel("")
            table.setCellWidget(0, col, set_all_button)

            if use_table:
                sub_widget = QTableWidgetItem(
                    "Use in the \n General CRF"
                    if param == USE_FOR_GENERAL_CRF
                    else f"{param.full_name}\n[{param.unit}]"
                )

                table.setHorizontalHeaderItem(col, sub_widget)

                self.column_of_parameters[param.name] = col

            else:
                layout.addWidget(set_all_button, 2, col)

        self.widgets_dict = {}
        self.npl_lineedits = {}

        for i, substance in enumerate(substances):
            # Add the line
            # For each column we do:
            # 1. create the widget
            # 2. set the start state of the widget from settings
            # 3. define the function to change the settings
            # 4. assign the callback
            # Record all the widgets of that substance
            row = i + row_offset
            sub_dict = {}
            self.widgets_dict[substance] = sub_dict
            # Add the parameters
            for j, param in enumerate(parameters):
                col = j + col_offset

                # The widget that will allow the change that parameter value
                widget = create_parameter_widget(
                    param,
                    settings=self.settings,
                    parent=self,
                    substance=substance,
                )
                if use_table:
                    table.setCellWidget(row, j + col_offset, widget)
                else:
                    layout.addWidget(widget, row, j + col_offset)

                sub_dict[param.name] = widget

            if use_table:
                table.setVerticalHeaderItem(row, QTableWidgetItem(substance))

            selected_checkbox = QCheckBox(
                *([] if use_table else [substance]), self
            )
            selected_checkbox.setChecked(
                self.settings.value(f"{substance}.include_sub", True, bool)
            )

            def set_value(state, substance=substance):
                setting = "{}.include_sub".format(substance)
                self.settings.setValue(setting, state)

            selected_checkbox.stateChanged.connect(set_value)
            if use_table:
                selected_checkbox.setStyleSheet(
                    "margin-left:50%; margin-right:50%;"
                )
                table.setCellWidget(row, 0, selected_checkbox)
            else:
                layout.addWidget(selected_checkbox, row, 0)

            # A combo box taht allows for selecting a group
            # to which the substance belong
            group_combobox = QComboBox(self)

            # Make sure the wheel event will not update the combobox but the table
            def wheelEvent(*args, **kwargs):
                return table.wheelEvent(*args, **kwargs)

            group_combobox.wheelEvent = wheelEvent
            group_combobox.addItems(
                # Finds all the existing groups in the settings
                {self.settings.value(f"{sub}.group", "") for sub in substances}
            )
            group_combobox.setCurrentText(
                self.settings.value(f"{substance}.group", "", str),
            )

            def set_group_text(text, setting="{}.group".format(substance)):
                self.settings.setValue(setting, text)

            group_combobox.currentTextChanged.connect(set_group_text)

            if use_table:
                table.setCellWidget(row, 1, group_combobox)
            else:
                layout.addWidget(group_combobox, row, 1)

            in_calib_checkbox = QCheckBox(self)

            def set_value(state, substance=substance):
                setting = "{}.in_calib".format(substance)
                state = bool(state) 
                self.settings.setValue(setting, state)
                self.widgets_dict[substance]["conc_calib"].setEnabled(state)
                self.widgets_dict[substance]["use_for_general_crf"].setEnabled(
                    state
                )
                if not state:
                    self.widgets_dict[substance][
                        "use_for_general_crf"
                    ].setChecked(state)

            in_calib_checkbox.stateChanged.connect(set_value)

            # Set the intial values and config
            checked = self.settings.value(f"{substance}.in_calib", True, bool)
            in_calib_checkbox.setChecked(checked)
            set_value(checked)
            if use_table:
                in_calib_checkbox.setStyleSheet(
                    "margin-left:50%; margin-right:50%;"
                )
                table.setCellWidget(row, 2, in_calib_checkbox)
            else:
                layout.addWidget(in_calib_checkbox, row, 2)

            group_combobox.currentText

            sub_dict["selected_checkbox"] = selected_checkbox
            sub_dict["in_calib_checkbox"] = in_calib_checkbox

            sub_dict["group_combobox"] = group_combobox

            self.table = table

        def popup_new_group():
            # Create a new group when the users presses
            new_group, worked = QInputDialog.getText(
                self,
                "Enter a new group name",
                "new group : ",
            )
            if worked:
                if new_group in substances:
                    msg_box = QMessageBox(self)
                    msg_box.setText(
                        f"Cannot add group: '{new_group}'.\n"
                        f"'{new_group}' is already the name of a substance."
                    )
                    msg_box.exec()
                    return
                # Add the group to all comboboxes
                for sub_dict in self.widgets_dict.values():
                    sub_dict["group_combobox"].addItem(new_group)

        add_group_button.clicked.connect(popup_new_group)

        if use_table:
            table.resizeColumnsToContents()
            table.resizeRowsToContents()
        else:
            self.setLayout(layout)

    def open_set_all_dialog(self, parameter: Parameter):
        """Open the dialog to set all the parameter values."""
        match parameter:
            case FloatParamter():
                new_val, success = QInputDialog.getDouble(
                    self,
                    "Set value to all substances",
                    (
                        "Set value for <b><i> "
                        f"{parameter.full_name} [{parameter.unit}] </i></b> "
                        "to all the substances."
                    ),
                    parameter.val,
                    parameter.min_val,
                    parameter.max_val,
                    parameter.decimals,
                )
                if success:
                    # Set the value to all
                    for sub_dict in self.widgets_dict.values():
                        line_edit: QLineEdit = sub_dict[parameter.name]
                        line_edit.setText(str(new_val))
            case _:
                raise NotImplementedError(type(parameter))

    def get_selected_substances(self) -> list[str]:
        """Find out the substances that are selected.


        This will remove substance the user did not select or that are not part
        of any group fo rthe calculations.
        """
        return [
            substance
            for substance, sub_dict in self.widgets_dict.items()
            if sub_dict["selected_checkbox"].checkState()
            == Qt.CheckState.Checked
            or sub_dict["group_combobox"].currentText()
        ]

    def get_all_substances(self) -> list[str]:
        """Read all the substances."""
        return list(self.widgets_dict.keys())

    def get_exported_substances(self) -> list[str]:
        """Find out the substances that are selected for export.

        The substances are sorted in a desired order for being exported.
        """
        exported_substances = []

        # Add the groups where they should be
        df_subs = self.get_substances_df()
        groups_dict = get_groups_dict(df_subs)

        # We will visit all the groups one by one and remove the ones that are out
        for sub in df_subs.index.to_list():
            if df_subs.loc[sub, "include_sub"]:
                exported_substances.append(sub)
            group = df_subs.loc[sub, "group"]
            if group:
                groups_dict[group].remove(sub)
                if not groups_dict[group]:
                    # Empty
                    exported_substances.append(group)

        return exported_substances

    def get_calib_substances(self) -> list[str]:
        """Find out the substances that are used for calibration.


        This will remove substance the user did not select or that are not part
        of any group fo rthe calculations.
        """
        return [
            substance
            for substance, sub_dict in self.widgets_dict.items()
            if sub_dict["in_calib_checkbox"].checkState()
            == Qt.CheckState.Checked
        ]

    def get_substances_df(self) -> pd.DataFrame:
        """Return a dataframe with the attributes of different substances."""

        # Create a dictornary of the substance values
        substances = self.get_all_substances()

        # Reserved key in the df for non parameter specific columns in substance df
        other_keys = ["group", "include_sub", "in_calib"]
        parameter_names = [param.name for param in self.parameters]

        intersectable_parameters = [
            p for p in other_keys if p in parameter_names
        ]
        if intersectable_parameters:
            raise RuntimeError(
                "Some Parameters have the same name as "
                f"a default widget: {intersectable_parameters}. "
                "Please change the name of the parameters."
            )

        # Create the dataframe
        df = pd.DataFrame(index=substances)
        columns = parameter_names + other_keys

        for param in self.parameters:
            if type(param) in [BoolParameter, FloatParamter, StrParameter]:
                # Read the values for each substance from the settings
                df[param.name] = [
                    self.settings.value(
                        f"{sub}.{param.name}", param.val, param.type
                    )
                    for sub in substances
                ]
            elif type(param) in [OptionalFloatParameter]:
                # Set nan when the value has to be read from the data
                df[param.name] = [
                    self.settings.value(
                        f"{sub}.{param.name}", param.val, param.type
                    )
                    if not self.settings.value(
                        f"{sub}.{param.name}.from_data", True, bool
                    )
                    else None
                    for sub in substances
                ]
            else:
                raise TypeError(param)

        # Process the "other_keys"
        df["group"] = [
            self.settings.value(f"{sub}.group", "", str) for sub in substances
        ]
        df["include_sub"] = [
            self.settings.value(f"{sub}.include_sub", True, bool)
            for sub in substances
        ]
        df["in_calib"] = [
            self.settings.value(f"{sub}.in_calib", True, bool)
            for sub in substances
        ]

        if 'export_name' not in df.columns:
            df['export_name'] = df.index
        # Set the index name when the export_name is nan or empty
        mask = df['export_name'].isna() | df['export_name'].eq('')
        df.loc[mask, 'export_name'] = df.index[mask]

        return df


if __name__ == "__main__":
    app = QApplication([])

    widget = SubstancesSelector(
        set(["TestA", "B", "C12", *[i for i in "asdhflewnfjwnejfkjkj"]]),
        [LOD, ERROR_SYSTEMATIC_INSTR, CONC_CALIB, USE_FOR_GENERAL_CRF],
        # use_table=False,
    )
    widget.show()
    print(widget.get_substances_df())
    print(widget.get_selected_substances())
    print(widget.get_calib_substances())

    sys.exit(app.exec())
