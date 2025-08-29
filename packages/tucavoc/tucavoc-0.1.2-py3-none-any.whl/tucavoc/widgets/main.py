"""Contains the main tucavoc widget."""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from avoca.bindings.gcwerks import read_gcwerks
from avoca.utils import compounds_from_df
from PySide6.QtCore import QSettings
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tucavoc import parameters, uncertainties
from tucavoc.abstract_uncertainty import (
    _ALL_PARAMETERS,
    BoolParameter,
    FloatParamter,
    Selection,
    Uncertainty,
)
from tucavoc.additional_data import AdditionalData, StartEndOffsets
from tucavoc.additional_data.empa import BRM_meteo, NABEL_Data
from tucavoc.additional_data.station import StationInformation
from tucavoc.additional_data.widget import AdditonalDataDialog
from tucavoc.calculations import check_data_for_calculations, get_groups_dict, main
from tucavoc.equations import (
    CALIBRATION_FACTOR,
    CARBON_RESPONSE_FACTOR_EQUATION,
    CONCENTRATION_USING_CRF,
    MAIN_CALCULATION,
)
from tucavoc.exports import EXPORT_REQUIRES, EXPORTS_DICT
from tucavoc.exports.excel import TableType, export_to_table
from tucavoc.parameters import (
    BLANK_CONC_PRESET,
    EXPORT_NAME,
    IN_CALIB,
)
from tucavoc.plots import plot_calibration_areas, plot_group_conc, plot_uncertainties
from tucavoc.utils import guess_calib_substances
from tucavoc.widgets.parameters import ParametersSelector
from tucavoc.widgets.qsettings_selector import QSettingsSelector
from tucavoc.widgets.substances import SubstancesSelector
from tucavoc.widgets.uncertainties import UncertaintiesWidget
from tucavoc.widgets.utils import (
    CheckableComboBox,
    CheckBoxWithSettings,
    FileShowerLabel,
)


class TucavocWidget(QWidget):
    """Select which substances are used and their parameters and which ones can be used.

    Can decide the following:
    * Whether the substance are selected for the output.
    * The value of the carbon number for substances.
    * Whether the substance is a NPL substance.
    """

    settings: QSettings

    runtypes: list[str]

    settings_selector: QSettingsSelector
    substances_selector: SubstancesSelector
    parameters_selector: ParametersSelector
    uncertainties_widget: UncertaintiesWidget

    export_formats_combobox: CheckableComboBox

    additional_data_dialog: AdditonalDataDialog

    def __init__(
        self,
        settings: QSettings = None,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        with open(Path(__file__).parent / "style_sheet.qss", "r") as fh:
            self.setStyleSheet(fh.read())
        if settings is None:
            settings = QSettings("tucavoc", "TucavocWidget", parent=self)
        self.settings = settings
        self.logger = logging.getLogger("tucavoc.TucavocWidget")

        main_layout = QVBoxLayout(self)
        title_layout = QVBoxLayout()

        # Add a title
        title = QLabel("TUCAVOC", self)
        title.setStyleSheet("font-size: 18pt;")
        title.setAlignment(Qt.AlignHCenter)
        title_layout.addWidget(title)
        # Link to the docu
        link = QLabel(
            (
                '<a href="https://tucavoc.readthedocs.io/"> See the full'
                " documentation !</a>"
            ),
            self,
        )
        link.setTextFormat(Qt.RichText)
        link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        link.setAlignment(Qt.AlignHCenter)
        link.setOpenExternalLinks(True)
        title_layout.addWidget(link)

        top_layout = QHBoxLayout()

        main_layout.addLayout(top_layout)
        input_group = QGroupBox("Input Files", self)
        input_layout = QVBoxLayout(input_group)
        top_layout.addWidget(input_group)
        top_layout.addLayout(title_layout)

        # Settings selection
        settings_group = QGroupBox("Settings Loading", self)
        settings_layout = QVBoxLayout(settings_group)
        self.settings_selector = QSettingsSelector(self.settings)
        settings_layout.addWidget(self.settings_selector)
        self.settings_selector.settings_changed.connect(self._reload_settings)
        top_layout.addWidget(settings_group)

        # Add a file loader
        self.button_select_file = QPushButton("Select File", self)
        previous_file = self.settings.value("previous_file", "")
        self.label_selected_file = FileShowerLabel(previous_file, self)
        layout_file = QHBoxLayout()
        layout_file.addWidget(self.button_select_file)
        layout_file.addWidget(self.label_selected_file)
        input_layout.addLayout(layout_file)
        self.button_select_file.clicked.connect(self.change_file)

        # Add runtype selection for calibration and blanks
        layout_runtype = QGridLayout()
        layout_runtype.addWidget(QLabel("Calibration RunType", self), 1, 0)
        layout_runtype.addWidget(QLabel("Blanks RunType", self), 2, 0)
        self.combobox_calibration = QComboBox(self)
        self.combobox_blanks = QComboBox(self)
        self.checkbox_fromdata_blanks = CheckBoxWithSettings(
            "read_blanks_from_data",
            self.settings,
            self,
            default_initial_state=False,
            check_box_name="Set value Manually",
        )
        layout_runtype.addWidget(self.combobox_calibration, 1, 1)
        layout_runtype.addWidget(self.combobox_blanks, 2, 1)
        layout_runtype.addWidget(self.checkbox_fromdata_blanks, 2, 2)
        input_layout.addLayout(layout_runtype)
        self.checkbox_fromdata_blanks.stateChanged.connect(
            self._changed_blank_manual_selection
        )

        # Adds a button that guesses when a sub is in the calibration
        guess_calib = QPushButton("Guess substance in calibration from data", self)
        guess_calib.setToolTip(
            "Will compare calib and blank values to set automatically which"
            " substances are in the calibration."
        )
        guess_calib.clicked.connect(self._guess_calib_substances)
        input_layout.addWidget(guess_calib)

        # Add a checkbox for choosing interpolation in the calibration
        self.checkbox_interpolation = CheckBoxWithSettings(
            "interpolate_calibration",
            self.settings,
            self,
            default_initial_state=True,
            check_box_name="Interpolate calibration",
        )
        self.checkbox_interpolation.setToolTip(
            "If check the calibration value used will be interpolated from"
            " the neighboring calibration runs. If not checked the value"
            " will be taken from the previous calibration run."
        )
        input_layout.addWidget(self.checkbox_interpolation)

        # Extract params for Parameters selector
        parameters = [
            p
            for p in _ALL_PARAMETERS
            if isinstance(p, (FloatParamter, BoolParameter)) and p not in [IN_CALIB]
        ]
        self.per_substance_parameters = [EXPORT_NAME] + [
            p for p in parameters if p.selectable == Selection.PER_SUBSTANCE
        ]
        self.global_parameters = [
            p for p in parameters if p.selectable == Selection.GLOBAL
        ]
        # Add the parameters selection
        layout_all_params = QGridLayout()
        self.parameters_selector = ParametersSelector(
            self.global_parameters, self.settings, self
        )
        layout_all_params.addWidget(self.parameters_selector, 0, 0)

        # Add the substance selector
        self.substances_selector = SubstancesSelector(
            [], self.per_substance_parameters, self.settings, self
        )
        layout_all_params.addWidget(self.substances_selector, 1, 0, 1, 3)

        # Uncertainties
        self.uncertainties_widget = UncertaintiesWidget(
            [
                uncertainties.PRECISION,
                uncertainties.CALIBRATION,
                uncertainties.PEAKINTEGRATION,
                uncertainties.VOLUME,
                uncertainties.FURTHERINSTRUMENTALPROBLEMS,
                uncertainties.LINEARITY,
                uncertainties.SAMPLING,
            ],
            self,
            self.settings,
        )
        layout_all_params.addWidget(self.uncertainties_widget, 0, 1)
        self.uncertainties_widget.uncertainty_checked.connect(
            self._on_uncertainty_checked
        )

        main_layout.addLayout(layout_all_params)

        # Group box for the output widgets
        output_group = QGroupBox("Outputs", self)
        layout_all_params.addWidget(output_group, 0, 2)
        output_layout = QFormLayout(output_group)

        # Output directory
        self.button_select_outdir = QPushButton("Change", output_group)
        self.label_selected_outdir = FileShowerLabel(
            self.settings.value("output_dir", ""), output_group
        )
        layout_outdir = QHBoxLayout()
        layout_outdir.addWidget(self.label_selected_outdir)
        layout_outdir.addWidget(self.button_select_outdir)
        output_layout.addRow("Output Directory", layout_outdir)
        self.button_select_outdir.clicked.connect(self.change_outdir)

        # Select export formats
        self.export_formats_combobox = CheckableComboBox()
        for idx, k in enumerate(EXPORTS_DICT.keys()):
            # Adapt the enum str to have only the name of the enum
            name = "".join(str(k).split(".")[1:])

            self.export_formats_combobox.addItem(name)

        # Save to settings when something is changed
        self.export_formats_combobox.element_checked.connect(
            lambda name, state: self.settings.setValue(
                "export_formats/" + name, state == Qt.Checked
            )
        )

        output_layout.addRow("Export Formats ", self.export_formats_combobox)

        # Select output run types
        self.combobox_out_runtypes = CheckableComboBox()
        output_layout.addRow("Output Runtypes ", self.combobox_out_runtypes)
        # Save to settings when something is changed
        self.combobox_out_runtypes.element_checked.connect(
            lambda name, state: self.settings.setValue(
                "output_runtypes/" + name, state == Qt.Checked
            )
        )

        # Select additional data
        self.add_additional_data_button = QPushButton("Choose", self)
        self.add_additional_data_button.clicked.connect(self._open_additional_data)
        output_layout.addRow("Additional Data", self.add_additional_data_button)
        self.additional_data_dialog = AdditonalDataDialog(
            [
                data(settings=self.settings)
                for data in [
                    StartEndOffsets,
                    NABEL_Data,
                    BRM_meteo,
                    StationInformation,
                ]
            ],
            self,
            settings=self.settings,
        )
        self.additional_data_dialog.setWindowTitle("Select additional data")
        self.additional_data_dialog.setWindowModality(Qt.WindowModal)

        # Add a plot button
        self.plot_subs_combobox = QComboBox(self)
        output_layout.addRow("Plot a substance", self.plot_subs_combobox)
        self.plot_subs_combobox.activated.connect(lambda ind: self._plot())

        # Add the calculate button
        self.button_start = QPushButton("Start Calculations", output_group)
        output_layout.addWidget(self.button_start)
        self.button_start.clicked.connect(self.start_calculations)

        self._change_file(self.label_selected_file.text())

    def change_file(self):
        """Change the currently selected file."""
        file, _filter = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select input file",
            dir=".",
            filter="dat *.dat",
        )

        if file:
            self._change_file(file)

    def _change_file(self, file):
        # Read the input data file
        path = Path(file)
        if not path.exists():
            print(f"{path} does not exist.")
            return
        if not path.is_file():
            print(f"{path} is not a file.")
            return
        self.label_selected_file.setText(file)
        try:
            self.df = read_gcwerks(path, keep_ordering_from_file=True)
            self.label_selected_file.setStyleSheet("background-color : lightgreen")
        except Exception as exp:
            print(f"Error while reading the data from {path}.")
            print(f"{exp}.")
            self.label_selected_file.setStyleSheet("background-color : red")
            return
        # Check few things in the file
        columns_mandatory = [
            ("-", "type"),
        ]
        for col in columns_mandatory:
            if col not in self.df.columns:
                print(f"Column {col} is missing in the input file: {path}.")
                self.label_selected_file.setStyleSheet("background-color : red")
                return
        self.settings.setValue("previous_file", file)
        self._recreate_substances()
        self._set_runtypes()
        # Calling that will update the parameters needed for the selected uncertainties
        self.uncertainties_widget.set_selected_uncertainties_from_settings()

        self._initialize_export_formats()

    def _initialize_export_formats(self):
        for idx, k in enumerate(EXPORTS_DICT.keys()):
            # Adapt the enum str to have only the name of the enum
            name = "".join(str(k).split(".")[1:])
            # Load the initial state from the settings
            settings_key = "export_formats/" + name
            initial_state = self.settings.value(settings_key, False, bool)
            self.export_formats_combobox.setItemChecked(idx, initial_state)

    def _open_additional_data(self):
        """Sould open an additional data dialog with the widget."""

        self.additional_data_dialog.show()

    def _reload_settings(self):
        """Called when the settings are changed to update widgets with new settings."""
        # Dont change the file when reloading the settings
        self._change_file(self.label_selected_file.text())
        self.uncertainties_widget.set_selected_uncertainties_from_settings()

    def _recreate_substances(self):
        #  Remove, Create, Replace the substances widget
        self.substances_selector.close()
        # exctract the substances
        substances = compounds_from_df(self.df)
        new_substances_selector = SubstancesSelector(
            substances,
            self.per_substance_parameters,
            settings=self.settings,
            parent=self,
        )
        self.layout().replaceWidget(self.substances_selector, new_substances_selector)
        self.substances_selector = new_substances_selector

        # self.layout().addWidget(self.substances_selector)
        # self.layout().update()

    def _guess_calib_substances(self):
        """This will set the calib substance widgets based on the data."""

        mask_blank = self.df[("-", "type")] == self.combobox_blanks.currentText()
        mask_calib = self.df[("-", "type")] == self.combobox_calibration.currentText()

        for (
            substance,
            wid_dic,
        ) in self.substances_selector.widgets_dict.items():
            wid_dic["in_calib_checkbox"].setChecked(
                guess_calib_substances(
                    self.df.loc[mask_calib, (substance, "area")],
                    self.df.loc[mask_blank, (substance, "area")],
                )
            )

    def _on_uncertainty_checked(self, u: Uncertainty, state: bool):
        """Update the parameters that are necassary."""
        self.logger.debug(f"_on_uncertainty_checked({u=}, {state=})")
        required_params = (
            self.uncertainties_widget.get_required_parameters()
            + CALIBRATION_FACTOR.variables
            + CARBON_RESPONSE_FACTOR_EQUATION.variables
            + MAIN_CALCULATION.variables
            + CONCENTRATION_USING_CRF.variables
        )
        for param in u.parameters:
            is_required = param in required_params
            # Set in the parameter selector
            if param in self.parameters_selector.parameters:
                self.parameters_selector.widgets[
                    self.parameters_selector.parameters.index(param)
                ].setEnabled(is_required)
            elif param in self.substances_selector.parameters:
                # Set columns hidden or not
                if param.name in self.substances_selector.column_of_parameters:
                    self.substances_selector.table.setColumnHidden(
                        self.substances_selector.column_of_parameters[param.name],
                        not is_required,
                    )
                for widget_dict in self.substances_selector.widgets_dict.values():
                    widget_dict[param.name].setEnabled(is_required)
            else:
                # Parameter is something calculated or not there
                pass

    def _set_runtypes(self):
        # Add the new widgets
        self.runtypes = np.unique(self.df["-", "type"].astype(str))

        self.combobox_out_runtypes.clear()
        for i, runtype in enumerate(self.runtypes):
            self.combobox_out_runtypes.addItem(runtype)
            initial_state = self.settings.value(
                f"output_runtypes/{runtype}", True, bool
            )
            self.combobox_out_runtypes.setItemChecked(i, initial_state)

        self.combobox_calibration.clear()
        self.combobox_blanks.clear()

        self.combobox_calibration.addItems(self.runtypes)
        self.combobox_blanks.addItems(self.runtypes)

        if "std" in self.runtypes:
            self.combobox_calibration.setCurrentText("std")
        if "blank" in self.runtypes:
            self.combobox_blanks.setCurrentText("blank")

        self._changed_blank_manual_selection(
            bool(self.checkbox_fromdata_blanks.checkState())
        )

    def _selected_output_types(self) -> list[str]:
        return [
            runtype
            for i, runtype in enumerate(self.runtypes)
            if self.combobox_out_runtypes.itemChecked(i)
        ]

    def _changed_blank_manual_selection(self, manual_selection: bool):
        """When the user selects whether he want to manually choose the blank values."""
        col = self.substances_selector.column_of_parameters[BLANK_CONC_PRESET.name]
        rel_err_widget = self.parameters_selector.get_widget_of_param(
            parameters.REL_ERROR_CONC_BLANK
        )
        if manual_selection:
            self.substances_selector.table.showColumn(col)
            rel_err_widget.setEnabled(True)
        else:
            self.substances_selector.table.hideColumn(col)
            rel_err_widget.setDisabled(True)

    def change_outdir(self):
        """Change the currently selected directory for the outputs"""
        dir = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select directory where the output will be written.",
            dir=".",
        )

        if dir:
            self.label_selected_outdir.setText(dir)
            self.settings.setValue("output_dir", dir)

    def start_calculations(self):
        """Start the calculations.

        This function is called when the user clicks the start calculations button.
        It performs all the calculations and saves the results.

        """
        out_dir = Path(self.label_selected_outdir.text())

        if not out_dir.exists():
            QMessageBox.warning(
                self,
                "Output directory does not exist",
                (
                    f"The output directory {out_dir} does not exist. Please"
                    " create it or select a valid directory."
                ),
            )
            return

        N_STEPS = 10
        progress_dialog = QProgressDialog(
            "tucavoc calculations", "cancel", 0, N_STEPS, self
        )
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(1)

        def update_progress(text: str):
            progress_dialog.setValue(progress_dialog.value() + 1)
            progress_dialog.setLabelText(text)

        update_progress("Preparing the data")

        self.df_subs = self.substances_selector.get_substances_df()
        df_calc = self.df.copy()

        for p, val in self.parameters_selector.get_parameters_dict().items():
            # Assign the value to all the parameters
            self.df_subs[p] = val

        update_progress("Checking the data")

        problems = check_data_for_calculations(df_calc, self.df_subs)
        problems.extend(self._check_data_for_exports())
        if problems:
            msg_box = QMessageBox(
                QMessageBox.Critical,
                "Calculations cannot be done",
                "\n".join(problems),
                parent=self,
            )
            progress_dialog.close()
            msg_box.exec()
            return

        # Save the substances
        self.df_subs.to_csv(out_dir / "df_subs.csv")
        self.df_subs.to_excel(out_dir / "df_subs.xlsx")

        # Add the substance to the plot combobox
        groups_dict = get_groups_dict(self.df_subs)
        self.plot_subs_combobox.addItems(
            self.df_subs.index.to_list() + list(groups_dict.keys())
        )

        uncertainties = self.uncertainties_widget.get_selected_uncertainties()

        update_progress("Calculating the concentrations")

        df_calc, _ = main(
            df_calc,
            self.df_subs,
            uncertainties,
            calib_type=self.combobox_calibration.currentText(),
            blank_type=self.combobox_blanks.currentText(),
            blanks_in_df_subs=bool(self.checkbox_fromdata_blanks.checkState()),
            ignore_n_first_blanks=self.parameters_selector.get_param(
                parameters.IGNORE_N_FIRST_BLANKS
            ),
            ignore_n_first_calibs=self.parameters_selector.get_param(
                parameters.IGNORE_N_FIRST_CALIBS
            ),
            interpolate=self.checkbox_interpolation.isChecked(),
        )
        self.df_calc = df_calc

        update_progress("Adding the flags")

        update_progress("Saving the output")
        saved = False
        while not saved:
            try:
                self.export(out_dir, df_calc, groups_dict)
                saved = True
            except PermissionError as pe:
                # This happens when an excel file is opened
                msg_box = QMessageBox(
                    QMessageBox.Critical,
                    f"Cannot export the files",
                    f"A file of the export is open : Close it: {pe.filename}",
                    parent=self,
                )
                msg_box.exec()
            except Exception as e:
                # This happens when an excel file is opened
                msg_box = QMessageBox(
                    QMessageBox.Critical,
                    f"Could not export the files.",
                    f"Internal Error. Please check terminal.",
                    parent=self,
                )
                msg_box.show()
                raise e

        update_progress("Finished")

        progress_dialog.close()

        msg_box = QMessageBox(self)
        msg_box.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        msg_box.setText(
            "Calculation was sucessful. See the output files in <strong> <a"
            f' href="file:///{str(out_dir.resolve()) }">'
            f" {out_dir.resolve()} </a>  </strong> "
        )
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction)

        msg_box.exec()

    def check_requirement(self, requirement: Uncertainty | AdditionalData) -> bool:
        """Check if the requirment is met.

        :return: True if the requirement is met, False if the requirement is missing.
        """
        if isinstance(requirement, Uncertainty):
            return requirement in self.uncertainties_widget.get_selected_uncertainties()

        elif isinstance(requirement, AdditionalData):
            for (
                additional_data,
                check,
            ) in self.additional_data_dialog.additional_data_checked.items():
                if check and isinstance(additional_data, type(requirement)):
                    return True
            return False
        else:
            raise TypeError(f"Invalid requirement type {type(requirement)}")

    def _check_data_for_exports(self) -> list[str]:
        problems = []
        for idx, export_type in enumerate(EXPORTS_DICT.keys()):
            if self.export_formats_combobox.itemChecked(idx):
                # Check the dependencies
                for requirement in EXPORT_REQUIRES[export_type]:
                    if not self.check_requirement(requirement):
                        # If the object is instantiated, str should be the name
                        if isinstance(requirement, AdditionalData):
                            req_str = (
                                "Additional Data:" f" {type(requirement).__name__}"
                            )
                        else:
                            req_str = f"Uncertainty: {requirement}"
                        problems.append(f"{export_type} requires {req_str}")

        return problems

    def export(self, out_dir, df_calc, groups_dict):
        """Export the files."""
        exported_substances = self.substances_selector.get_exported_substances()
        # Select types for the output
        mask_output = df_calc[("-", "type")].isin(self._selected_output_types())

        # Find out which columns should be exported
        df_calc_cols = [
            col_name
            for col_name in df_calc.columns
            if (col_name[0] in exported_substances + ["-"] + list(groups_dict.keys()))
            and not col_name[0] == ""
        ]

        # Selects only required columns and rows
        df_output: pd.DataFrame = df_calc.loc[
            mask_output,
            df_calc_cols,
        ]

        # Add the additional data
        additional_datas = {}
        for (
            additional_data,
            checked,
        ) in self.additional_data_dialog.additional_data_checked.items():
            if not checked:
                continue
            additional_datas[type(additional_data)] = additional_data

            df_additonal = additional_data.get_data(df_calc[("-", "datetime")])
            if df_additonal is None:
                # No data to add in the dataframe
                continue

            data_name = type(additional_data).__name__
            # Make it a 2 levels index so we know the source of the data
            df_additonal.columns = pd.MultiIndex.from_product(
                [[data_name], df_additonal.columns]
            )
            # add to the output
            df_output = df_output.join(df_additonal)

            # add the date time before saving for
            df_additonal.insert(0, ("-", "datetime"), df_calc[("-", "datetime")])
            df_additonal.to_csv(
                out_dir / f"additional_data_{data_name}.csv", index=False
            )

        df_output.to_csv(out_dir / "results.csv", index=False)

        # Merge the groups and the substance for the export
        group_names = [k for k in groups_dict.keys() if k]
        df_subs_to_export = pd.concat(
            [
                self.df_subs.loc[
                    [
                        sub
                        for sub in exported_substances
                        if sub not in list(groups_dict.keys())
                    ]
                ],
                pd.DataFrame(index=group_names, columns=self.df_subs.columns),
            ]
        )
        df_subs_to_export.loc[group_names, "export_name"] = group_names
        df_subs_to_export = df_subs_to_export.loc[exported_substances]

        # Save always the concentrations as csv
        export_to_table(
            df_output,
            df_subs_to_export,
            export_path=out_dir,
            table_type=TableType.CSV,
        )
        # Export to the selected formats
        for idx, (export_name, export_func) in enumerate(EXPORTS_DICT.items()):
            if self.export_formats_combobox.itemChecked(idx):
                try:
                    export_func(
                        df_output,
                        df_subs_to_export,
                        out_dir,
                        additional_data=additional_datas,
                    )
                except PermissionError as pe:
                    # Permission error occur when file is opened,
                    # This is already handled by the main function
                    raise pe
                except Exception as e:
                    raise RuntimeError(f"Could not export to {export_name}") from e

    def _plot(self):
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 1, sharex=True)
        uncertainties = self.uncertainties_widget.get_selected_uncertainties()
        # name = "ethane"
        name = self.plot_subs_combobox.currentText()

        # Extract the calibration and blanks
        df_to_plot = self.df_calc.copy()
        df_to_plot.loc[
            ~self.df_calc[("-", "type")].isin(self._selected_output_types()),
            ("-", "datetime"),
        ] = np.nan
        if name in get_groups_dict(self.df_subs).keys():
            plot_group_conc(
                axes[0],
                name,
                df_to_plot,
                self.df_subs,
            )
        else:
            # On the calibration plot we want to see the whole data
            plot_calibration_areas(axes[0], name, self.df_calc, self.df_subs)
        plot_uncertainties(
            axes[1],
            name,
            uncertainties,
            df_to_plot,
            self.df_subs,
        )
        # Also show x ticks on ax 0
        axes[0].tick_params(axis="x", which="both", labelbottom=True)
        fig.set_tight_layout(True)
        plt.show(block=True)


if __name__ == "__main__":
    app = QApplication([])

    import logging

    logging.basicConfig(level=logging.INFO)
    # logging.getLogger("tucavoc").setLevel(logging.DEBUG)

    widget = TucavocWidget()
    widget.show()

    sys.exit(app.exec())
