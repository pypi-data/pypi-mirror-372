from tucavoc import tex
from tucavoc.abstract_uncertainty import (
    CalculatedVariable,
    DataVariable,
    OptionalDataVariable,
    OptionalFloatParameter,
    FloatParamter,
    StrParameter,
    OptionalDataVariableOrCalculated,
    Selection,
    BoolParameter,
)


SAMPLE_AREA = DataVariable(
    "area_sample",
    full_name="Peak area of sample measurement",
    unit="area",
    tex_name=tex.area_sample,
)
CALIB_AREA = CalculatedVariable(
    "area_calib",
    full_name="Peak area of calibration gas measurement",
    unit="area",
    tex_name=tex.area_calib,
)

BLANK_AREA = OptionalDataVariableOrCalculated(
    "area_blank",
    full_name="Possible blank area value determined in zero gas measurements",
    explanation=(
        "In few cases, the blank values obtained in zero gas measurements can"
        " be significantly higher than the determined peak areas yielding"
        " negative amount fractions according to "
        " :math:numref:`calculationofamountfractionsforlineardetectionsystems`"
        " and :math:numref:`amountfractionusingcrf`. Then the zero gas"
        " procedure and further potential sources of blank values have to be"
        " checked and appropriate uncertainties of the blank values have to be"
        " estimated. See also :term:`blank_conc_preset` . "
    ),
    unit="area",
    val=0.0,
    tex_name=tex.area_blank,
)

BLANK_CONC_PRESET = OptionalFloatParameter(
    "blank_conc_preset",
    full_name="Blank amount fraction",
    explanation=(
        "Amount fraction of the blank. A constant value that can be assigned."
        " TUCAVOC will then retrieve the blank area value using Equations"
        " :math:numref:`retrievalofblankareafromamountfraction` or"
        " :math:numref:`retrievalofblankareafromamountfractionforsubstancesnotinthecalibrationgas`."
        " This helps when the value of the blank is known but was not measured"
        " in the sample."
    ),
    unit="pmol/mol",
    val=0.0,
    tex_name=tex.conc_blank,
    selectable=Selection.PER_SUBSTANCE,
)

IGNORE_N_FIRST_BLANKS = FloatParamter(
    "ignore_n_first_blanks",
    0,
    full_name="Number of starting blank runs to be ignored.",
    explanation=(
        "Often the first blank samples have residuals of the substances that"
        " were measured just before. This means that the blank area might be"
        " larger in the first blank measurements. As this could influence the"
        " blank value, this parameter allows to select how many of the"
        " starting blank runs should be ignored in the calculation."
    ),
    type=int,
    min_val=0,
    decimals=0,
)

IGNORE_N_FIRST_CALIBS = FloatParamter(
    "ignore_n_first_calibs",
    0,
    full_name="Number of starting calibration runs to be ignored.",
    explanation=(
        "Same as :term:`ignore_n_first_blanks` but for the calibration runs."
    ),
    type=int,
    min_val=0,
    decimals=0,
)

USE_FOR_GENERAL_CRF = BoolParameter(
    "use_for_general_crf",
    val=True,
    full_name="Use in the General Mean CRF calculation",
    explanation=(
        "Whether the substance should be used to compute the "
        ":term:`general_mean_carbon_response_factor` . "
    ),
    selectable=Selection.PER_SUBSTANCE,
)


CONC_CALIB = FloatParamter(
    "conc_calib",
    0.0,
    full_name="Certified amount fraction of calibration gas",
    unit="pmol/mol",
    explanation="The amount fraction present in the RGM.",
    tex_name=tex.conc_calib,
    selectable=Selection.PER_SUBSTANCE,
)

SIGMA_REL_SERIES = CalculatedVariable(
    "sigma_rel_series",
    full_name="relative standard deviation of calibrations",
    explanation=(
        "Standard deviation of the area of successive calibration measurements. "
        "This is calculated in tucavoc for each calibration serie. "
        ":ref:`guidelines document <Guidelines>` recommend to use "
        "at least 6 individual measurements "
        "over the considered interval. "
        "However TUCAVOC will also work with less than that."
    ),
    unit="%",
    tex_name=tex.sigma_rel_series,
)

CONC_STD_BLANK = CalculatedVariable(
    "conc_std_blank",
    full_name="Standard deviation of the amount fraction of a serie of blank runs",
    explanation=(
        "Standard deviation of consecutive blank runs. This works only when"
        " blanks are read from data files. If blanks are specified by the user"
        " the current implementation assumes uncertainty is 0."
    ),
    unit="pmol/mol",
    tex_name=tex.sigma_blanks,
)

U_REL_COMBINED = CalculatedVariable(
    "u_rel_combined",
    full_name="Relative combined uncertainty of the sample measurement.",
    unit="%",
    explanation=(
        "The combined uncertainty  of the sample measurement "
        "divided by the amount fraction of the sample."
    ),
    tex_name=tex.frac(tex.u_2_i("sample"), tex.conc_sample),
)
U_REL_EXPANDED = CalculatedVariable(
    "u_rel_expanded",
    full_name="Relative expanded uncertainty of the sample measurement.",
    unit="%",
    explanation=(
        "The combined uncertainty of the sample measurement multiplied by the"
        " factor coverage (k = 2) and divided by the amount fraction of the"
        " sample."
    ),
    tex_name="2*" + tex.frac(tex.u_2_i("sample"), tex.conc_sample),
)

CONC_SAMPLE = CalculatedVariable(
    "conc_sample",
    full_name="Amount fraction of a substance in a sample",
    unit="pmol/mol",
    tex_name=tex.conc_sample,
)

CONC = CalculatedVariable(
    "conc",
    full_name="Concentration or Amount fraction of a substance in a sample",
    unit="pmol/mol",
    explanation="Analogous to :term:`conc_sample` ",
    tex_name=tex.conc_sample,
)


REL_ERROR_CONC_BLANK = FloatParamter(
    "rel_error_conc_blank",
    val=1.0,
    full_name="Relative error of the blanks concentration.",
    unit="%",
    tex_name=tex.u_rel_conc_blank,
    explanation=(
        "Relative error of the blank concentration given by the user."
        " See :term:`blank_conc_preset` ."
    ),
)

CALIB_VOLUME = FloatParamter(
    "volume_calib",
    300,
    full_name="Volume of calibration gas samples",
    unit="ml",
    tex_name=tex.Volume_calib,
)
SAMPLE_VOLUME = FloatParamter(
    "volume_sample",
    300,
    full_name="Volume of measured samples",
    unit="ml",
    tex_name=tex.Volume_sample,
)
VOLUME_ERROR_SAMPLE = FloatParamter(
    "volume_uncertainty_sample",
    1.0,
    unit="ml",
    tex_name=tex.u_vol_sample,
    full_name="Uncertainty of the measured sample volume",
)
VOLUME_ERROR_CALIB = FloatParamter(
    "volume_uncertainty_calib",
    1.0,
    unit="ml",
    tex_name=tex.u_vol_calib,
    full_name="Uncertainty of the calibration volume",
)
CALIB_FACTOR = CalculatedVariable(
    "calib_factor",
    full_name="Calibration Factor",
    tex_name=tex.calib_factor,
    explanation=("The calibration factor is useful for simplfying the equations."),
)
CALIB_FACTOR_UNCERTAINTY = CalculatedVariable(
    "u_calib_factor",
    full_name="Uncertainty of the Calibration Factor",
    tex_name=tex.u_calib_factor,
    explanation=(
        "The uncertainty of the calibraiton factor."
        " Used in the formula for propagating the uncertainty"
    ),
)

LOD = FloatParamter(
    "detection_limit",
    7,
    full_name="Detection Limit",
    unit="pmol/mol",
    selectable=Selection.PER_SUBSTANCE,
    tex_name=tex.lod,
    explanation=(
        "The detection limit is the lowest  amount fraction that can be"
        " measured with a given instrument."
    ),
)

ABS_U_CAL = FloatParamter(
    "abs_u_cal",
    0.001,
    unit="pmol/mol",
    full_name="Certified uncertainty of the RGM amount fraction",
    explanation=(
        "Includes the possible drift of the RGM. Please note that the RGM"
        " amount fraction is generally given with an expanded uncertainty"
        " having a coverage factor of k=2. The standard uncertainty "
        f" {tex.rst_math(tex.u_calib)} is thus half of the expanded"
        " uncertainty."
    ),
    tex_name=tex.u_calib,
    selectable=Selection.PER_SUBSTANCE,
)

ERROR_POTENTIAL_AREA_INTEG_SAMPLE = FloatParamter(
    "u_peak_area_integ_sample",
    0,
    unit="%",
    full_name="Uncertainty from peak integration in the measurement",
    explanation=(
        "Standard relative uncertainty of the peak integration in the measurement."
    ),
    tex_name=tex.frac(tex.u_A_int_sample, tex.area_sample),
    selectable=Selection.PER_SUBSTANCE,
)
ERROR_POTENTIAL_AREA_INTEG_CALIB = FloatParamter(
    "u_peak_area_integ_calib",
    0,
    unit="%",
    full_name="Uncertainty from peak integration in the calibration",
    explanation=(
        "Standard relative uncertainty of the peak integration in the calibration."
    ),
    tex_name=tex.frac(tex.u_A_int_calib, tex.area_calib),
    selectable=Selection.PER_SUBSTANCE,
)
ERROR_SYSTEMATIC_INSTR = FloatParamter(
    "error_systematic_instrument",
    1.0,
    full_name="Systematic Instrument Error",
    unit="%",
    explanation="Relative error due to the instrument.",
    tex_name=tex.u_instrument,
    selectable=Selection.GLOBAL,
)
ERROR_LINEARITY_DUE = FloatParamter(
    "uncertainty_due_to_linearity",
    0.0,
    unit="pmol/mol",
    full_name="Uncertainty from non-linearity",
    tex_name=tex.u_linearity,
    selectable=Selection.PER_SUBSTANCE,
)

ERROR_SAMPLING_VOLUME_ACCURACY = FloatParamter(
    "uncertainty_sampling_volume_accuracy",
    0.0,
    full_name="Uncertainty from sampling volume accuracy",
    unit="pmol/mol",
    tex_name=tex.u_sampling,
    selectable=Selection.PER_SUBSTANCE,
)


CN = FloatParamter(
    "carbon_number",
    val=1,
    full_name="Carbon number",
    tex_name=tex.carbon_number,
    explanation="Number of C atoms in the molecule",
    selectable=Selection.PER_SUBSTANCE,
)
ECN_CONTRIB = FloatParamter(
    "effective_carbon_number_contribution",
    val=1,
    full_name="ECN contribution",
    tex_name=tex.ecn_contrib,
    explanation=(
        "The ECN contribution, i.e. "
        "1.0 for carbon in aliphatic and aromatic bonds, "
        "0.95 per C in olefinic bonds, "
        "1.3 in acetylenic bonds (Sternberg et al., 1962)."
    ),
    selectable=Selection.PER_SUBSTANCE,
)
ECN_CONTRIB_UNCERTAINTY = FloatParamter(
    "u_effective_carbon_number_contribution",
    val=0.0,
    full_name="Uncertainty of the ECN contribution",
    tex_name=tex.u_ecn_contrib,
    explanation="The uncertainty of the ECN contribution.",
    selectable=Selection.PER_SUBSTANCE,
)

CRF = CalculatedVariable(
    "carbon_response_factor",
    full_name="Carbon Response Factor (CRF)",
    tex_name=tex.carbon_response_factor,
)

MEAN_CRF = CalculatedVariable(
    "mean_carbon_response_factor",
    full_name="Mean carbon response factor",
    tex_name=tex.mean_crf,
    explanation=(
        "Determined from selected substances in the RGM "
        "measurements averaging CRF for those substances."
    ),
)
GROUP_MEAN_CRF = CalculatedVariable(
    "group_mean_carbon_response_factor",
    full_name="Mean CRF of a group",
    tex_name=tex.mean_crf[:-1] + "," + tex.mathrm("group") + "}",
    explanation=(
        "Same as :term:`mean_carbon_response_factor` "
        "but including only substances from a group."
    ),
)
GENERAL_MEAN_CRF = CalculatedVariable(
    "general_mean_carbon_response_factor",
    full_name="General Mean Carbon Response Factor (CRF)",
    tex_name=tex.mean_crf[:-1] + "," + tex.mathrm("general") + "}",
    explanation=(
        "Same as :term:`mean_carbon_response_factor` "
        "but including only substances selected for the general CRF."
    ),
)


FLAG = CalculatedVariable(
    "flag",
    full_name="A Flag value",
    explanation="The flag value attributed. See :ref:`flagging`.",
)


GROUP = StrParameter(
    name="group",
    val="",
    full_name="Group name",
    explanation="The name of the group to which a compound belongs.",
)


EXPORT_NAME = StrParameter(
    name="export_name",
    val="",
    full_name="Export name",
    explanation="The name of the export file. This can be used to name the export file.",
)


IN_CALIB = BoolParameter(
    name="in_calib",
    val=True,
    full_name="Present in the calibration sample",
    explanation="Whether the compound is present in the calibration sample. Some compounds are sometimes not present in the calibration sample and must be calculated with the FID method.",
    selectable=Selection.PER_SUBSTANCE,
)
