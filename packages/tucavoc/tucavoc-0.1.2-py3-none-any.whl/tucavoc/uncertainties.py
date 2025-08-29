"""Different uncertainty implemented.


u: uncertainty
cal: calibration
sub: substance
conc: concentration
rel: relative
"""

# For the documentation of these see
#  https://www.actris.eu/sites/default/files/Documents/ACTRIS-2/Deliverables/WP3_D3.17_M42.pdf

import numpy as np

# Import under another name to avoid naming conflicts in classes declarations
from tucavoc import equations
from tucavoc import parameters
from tucavoc import parameters as tucavoc_parameters
from tucavoc import tex
from tucavoc.abstract_uncertainty import FloatParamter, Parameter, Uncertainty
from tucavoc.parameters import (
    CONC_SAMPLE,
    ERROR_LINEARITY_DUE,
    ERROR_SAMPLING_VOLUME_ACCURACY,
    ERROR_SYSTEMATIC_INSTR,
    LOD,
    VOLUME_ERROR_CALIB,
    VOLUME_ERROR_SAMPLE,
)


class Precision(Uncertainty):
    title_name = (
        "Uncertainty linked to the reproducibility of the measurement method"
        " (Precision)"
    )
    param_name = (
        "Uncertainty of the measurement method associated to the" " reproducibility"
    )

    short_explanation: str = "Standard uncertainty due to the precision."
    explanation: str = (
        " The precision is a measure for the closeness of the agreement"
        " between measured values obtained by replicate measurements on the"
        " same or similar objects under specified conditions (VIM (BIPM))."
        " This is expressed as standard uncertainty reflecting the variability"
        " of the measurement system due to random errors."
    )

    parameters = [CONC_SAMPLE, parameters.SIGMA_REL_SERIES, LOD]

    latex_formula: str = (
        tex.texstr(f"({tex.conc_sample} * {tex.sigma_rel_series})^2")
        + "+"
        + tex.parenthesis(tex.frac(tex.lod, "3"))
        + tex.pow(2)
    )

    def calculate(
        self, sample_concentration, rel_std_area_cal_series, detection_limit
    ) -> np.ndarray:
        return np.sqrt(
            # 1rst part: Error on the std gases
            # TODO: check if the *100 is an error in the excell
            (rel_std_area_cal_series * sample_concentration) ** 2
            # 2nd part: Error due to the limit of detection
            + (detection_limit / 3.0) ** 2
        )


class Calibration(Uncertainty):
    param_name = "Uncertainty of the calibration RGM"

    short_explanation: str = "Standard uncertainty of the calibration."
    explanation: str = (
        " Standard uncertainty due to the calibration. Behaviour not"
        " defined for calculation using the FID formula."
    )

    parameters = [
        parameters.SAMPLE_AREA,
        parameters.CALIB_AREA,
        parameters.BLANK_AREA,
        parameters.CALIB_VOLUME,
        parameters.SAMPLE_VOLUME,
        parameters.ABS_U_CAL,
        parameters.CONC_SAMPLE,
        parameters.CONC_CALIB,
    ]
    latex_formula: str = (
        tex.parenthesis(
            tex.frac(
                tex.parenthesis(tex.area_sample - tex.area_blank) * tex.Volume_calib,
                tex.Volume_sample * tex.parenthesis(tex.area_calib - tex.area_blank),
            )
            * tex.u_calib
        )
        + tex.pow(2)
        + tex.texstr("=")
        + tex.parenthesis(tex.frac(tex.conc_sample, tex.conc_calib) * tex.u_calib)
        + tex.pow(2)
    )

    def calculate(
        self,
        sample_concentration,
        cal_substance_concentration,
        abs_u_cal,
    ) -> np.ndarray:
        return abs_u_cal * (
            # Scale the unceratinty with calculation
            sample_concentration
            / cal_substance_concentration
        )


class PeakIntegration(Uncertainty):
    short_explanation = "Combined uncertainty of the peak integration"
    explanation: str = " The standard uncertainty due to peak integration."
    title_char: str = '"'

    parameters = [
        parameters.CALIB_FACTOR,
        parameters.SAMPLE_VOLUME,
        parameters.ERROR_POTENTIAL_AREA_INTEG_SAMPLE,
        parameters.SAMPLE_AREA,
        parameters.CALIB_VOLUME,
        parameters.CONC_CALIB,
        parameters.CALIB_AREA,
        parameters.ERROR_POTENTIAL_AREA_INTEG_CALIB,
    ]

    latex_formula: str = (
        tex.parenthesis(
            tex.frac(tex.calib_factor, tex.Volume_sample) * tex.u_A_int_sample
        )
        + tex.pow(2)
        + "+"
        + tex.parenthesis(
            tex.frac(
                tex.area_sample * tex.Volume_calib * tex.conc_calib,
                tex.Volume_sample * tex.area_calib + tex.pow(2),
            )
            * tex.u_A_int_calib
        )
        + tex.pow(2)
    )

    def calculate(
        self,
        calibration_factor,
        calibration_volume,
        calibration_substance_concentration,
        calibration_area,
        area_sample,
        volume_sample,
        u_peak_area_integ_sample,
        u_peak_area_integ_calib,
    ) -> np.ndarray:
        return np.sqrt(
            # Error on the integration method
            (
                calibration_factor
                # Convert from percent
                * (u_peak_area_integ_sample * 0.01 * area_sample)
                / volume_sample
            )
            ** 2
            # error from the machine (a kind of rescaling from the calibration area to this area)
            + (
                calibration_volume
                / volume_sample
                * area_sample
                / calibration_area**2
                * calibration_substance_concentration
                # Convert from percent
                * (u_peak_area_integ_calib * 0.01 * calibration_area)
            )
            ** 2
        )


class Volume(Uncertainty):
    short_explanation = (
        "Combined uncertainty due to the difference between sampling and"
        " calibration volumes."
    )

    explanation: str = (
        " The standard uncertainty due to the difference between sampling and"
        " calibration volumes."
    )
    title_char: str = '"'

    parameters = [
        parameters.CONC_SAMPLE,
        parameters.VOLUME_ERROR_SAMPLE,
        parameters.VOLUME_ERROR_CALIB,
        parameters.SAMPLE_VOLUME,
        parameters.CALIB_VOLUME,
    ]

    latex_formula: str = (
        tex.parenthesis(tex.frac(tex.conc_sample, tex.Volume_sample) * tex.u_vol_sample)
        + tex.pow(2)
        + "+"
        + tex.parenthesis(tex.frac(tex.conc_sample, tex.Volume_calib) * tex.u_vol_calib)
        + tex.pow(2)
    )

    def calculate(
        self,
        sample_concentration,
        volume_sample,
        calibration_volume,
        volume_uncertainty_sample,
        volume_uncertainty_calib,
    ) -> np.ndarray:
        return np.sqrt(
            # Error from the sample volume
            (sample_concentration / volume_sample * volume_uncertainty_sample) ** 2
            # Error from the calibration volume
            + (sample_concentration / calibration_volume * volume_uncertainty_calib)
            ** 2
        )


class FurtherInstrumentalProblems(Uncertainty):
    short_explanation: str = (
        "Standard uncertainty associated a further instrumental problems, such"
        " as the systematic instrument error."
    )

    explanation: str = " Standard uncertainty due to specific instrumental problems."
    title_char: str = '"'

    parameters = [parameters.CONC_SAMPLE, ERROR_SYSTEMATIC_INSTR]
    latex_formula: str = tex.parenthesis(tex.conc_sample * tex.u_instrument) + tex.pow(
        2
    )

    def calculate(
        self,
        sample_concentration,
        error_systematic_instrument,
    ) -> np.ndarray:
        return sample_concentration * error_systematic_instrument / 100.0


class Linearity(Uncertainty):
    short_explanation: str = "Standard uncertainty of the system linearity."
    explanation: str = (
        " Standard uncertainty due to lack of linearity of the measurement system."
    )
    title_char: str = '"'
    parameters = [ERROR_LINEARITY_DUE]
    latex_formula: str = tex.u_linearity + tex.pow(2)

    def calculate(self, uncertainty_due_to_linearity) -> float:
        return uncertainty_due_to_linearity


class Sampling(Uncertainty):
    title_name = "Uncertainty of the sampling method"
    param_name: str = "Uncertainty of the sampling system"
    short_explanation: str = "Standard uncertainty of the sampling techniques."
    explanation: str = (
        " The standard uncertainty due to application of off-line sampling"
        " techniques depends on the technique used. Contributions to the"
        " uncertainty common to all off-line techniques (cleaning of the"
        " samplers, storage, adsorption effects, etc.) should be evaluated"
        " case-by-case and per individual component. If not available in"
        " literature, a proper validation of the sorbent tubes is recommended"
        " prior to their use in the field to establish the efficiency of"
        " adsorption/desorption and the safe sampling volume at different"
        " composition levels and atmospheric conditions."
    )

    parameters = [ERROR_SAMPLING_VOLUME_ACCURACY]
    latex_formula: str = tex.u_sampling + tex.pow(2)

    def calculate(self, uncertainty_sampling_volume_accuracy) -> float:
        return uncertainty_sampling_volume_accuracy


# TODO: this should be added for fid
class BlankConcentration(Uncertainty):
    explanation: str = " The uncertainty due to the blank concentration."

    parameters = [
        parameters.BLANK_CONC_PRESET,
        parameters.REL_ERROR_CONC_BLANK,
    ]
    latex_formula: str = tex.parenthesis(
        tex.u_rel_conc_blank * tex.conc_blank
    ) + tex.pow(2)

    def calculate(self, u_rel_conc_blank, conc_blank) -> np.ndarray:
        return u_rel_conc_blank * conc_blank


class Blank(Uncertainty):
    explanation: str = (
        " The uncertainty due to the deviation of blank samples from the mean"
        " blank values."
    )

    parameters = [
        parameters.CONC_STD_BLANK,
    ]
    latex_formula: str = tex.sigma_blanks + tex.pow(2)

    def calculate(self, area_std_blank, area_blank, conc_blank) -> np.ndarray:
        # Here I now use the relative deviation and apply it to the concentraation
        # See issue #41
        return area_std_blank / area_blank * conc_blank


PRECISION = Precision()
CALIBRATION = Calibration()
SAMPLING = Sampling()
PEAKINTEGRATION = PeakIntegration()
VOLUME = Volume()
FURTHERINSTRUMENTALPROBLEMS = FurtherInstrumentalProblems()
LINEARITY = Linearity()
BLANK = Blank()


class Instrument(Uncertainty):
    param_name: str = "Uncertainty of the analytical system"
    short_explanation: str = (
        " Combined uncertainty of the instrument, which includes the standard"
        " uncertainties of the peak integration, linearity and further"
        " instrumental problems."
    )

    explanation: str = """
        The overall uncertainty of the instrument is the result of combining the standard uncertainties of the peak integration, sample volume, further instrumental problems (e.g. sampling line artefacts) and the uncertainty due to the lack of linearity. 
    """

    parameters: list[Parameter] = [
        PEAKINTEGRATION,
        VOLUME,
        FURTHERINSTRUMENTALPROBLEMS,
        LINEARITY,
    ]
    latex_formula: str = "+".join(
        [
            tex.u_2_i(u)
            for u in (
                "peak integration",
                "volume",
                "further instrumental problems",
                "linearity",
            )
        ]
    )


INSTRUMENT = Instrument()


class CombinedStandardUncertainty(Uncertainty):
    title_name = "Combined Standard Uncertainty of the measurement"
    param_name: str = "Combined Standard Uncertainty"
    explanation: str = """
        The combination of all the standard uncertainties associated
        with the input quantities in the measurement model (VIM (BIPM)). 
        Also called overall uncertainty.

        The combined uncertainty, or overall uncertainty,
        is calculated using the law of propagation of the uncertainties
        (considering that the standard uncertainties are not correlated)
        according to the 
        :ref:`Guide to the Expression of Uncertainty in Measurement <UncertaintyGuide>` . 
    """
    parameters: list[Parameter] = [
        PRECISION,
        CALIBRATION,
        INSTRUMENT,
        SAMPLING,
    ]
    # latex_formula: str = tex.sum( tex.mathrm("u"), tex.mathrm(r"All\ Uncertainties"), tex.u_2_i("u"))

    latex_formula: str = "+".join(
        [
            tex.u_2_i(u)
            for u in (
                "precision",
                "calibration",
                "instrument",
                "sampling",
            )
        ]
    )

    def __init__(self) -> None:
        super().__init__()
        # Correct the auto defined name
        self.latex_name = tex.u_2_i("sample")


COMBINEDSTANDARDUNCERTAINTY = CombinedStandardUncertainty()


class ExpandedUncertainty(Uncertainty):
    title_name: str = "Expanded Uncertainty"
    explanation: str = """
        The combined uncertainty is the product
        of the combined standard uncertainty of the measurement
        by a number greater than 1 (the coverage factor k).
    """
    parameters: list[Parameter] = [COMBINEDSTANDARDUNCERTAINTY]
    latex_formula: str = tex.texstr("2") * tex.u_2_i("sample")[:-4]

    def __init__(self) -> None:
        super().__init__()
        # Correct the auto defined name
        self.latex_name = tex.u_expanded


# Order as in the documentation
ALL_UNCERTAINTIES: list[Uncertainty] = [
    COMBINEDSTANDARDUNCERTAINTY,
    # Inputs of the combined
    PRECISION,
    CALIBRATION,
    INSTRUMENT,
    PEAKINTEGRATION,
    VOLUME,
    FURTHERINSTRUMENTALPROBLEMS,
    LINEARITY,
    SAMPLING,
    BLANK,
    EXPANDEDUNCERTAINTY := ExpandedUncertainty(),
]

if __name__ == "__main__":
    p = Precision()
    print(p.name)
