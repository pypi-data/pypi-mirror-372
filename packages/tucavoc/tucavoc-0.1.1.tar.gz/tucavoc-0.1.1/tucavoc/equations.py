from dataclasses import dataclass, field
from tucavoc.abstract_uncertainty import CalculatedVariable, Parameter


from tucavoc import tex, parameters


@dataclass
class Equation:
    """An equation used to calculate a variable.

    During building of the documentation, the equations are saved in a
    rst file, and is then automatically added to an equation glossary.

    See file `conf.py` in the docs folder.

    :param full_name: Full name of the equation.
    :param latex_equation: LaTeX equation.
    :param output_variable: Variable calculated by the equation.
    :param variables: Variables used in the equation.

    :param name: Name of the equation (lowercase, no spaces).
    :param derivation: LaTeX equations for the derivation of the equation.
    """

    full_name: str
    latex_equation: tex.texstr
    output_variable: CalculatedVariable | None
    variables: list[Parameter]

    name: str = field(init=False)
    derivation: tex.texstr | None = None

    def __post_init__(self):
        if self.output_variable is not None:
            self.output_variable.equations.append(self)

        self.name = self.full_name.replace(" ", "").lower()


MAIN_CALCULATION = Equation(
    full_name="Calculation of amount fractions for linear detection systems",
    latex_equation=tex.conc_sample
    + "="
    + tex.frac(tex.area_sample - tex.area_blank, tex.Volume_sample)
    * tex.calib_factor,
    output_variable=parameters.CONC_SAMPLE,
    variables=[
        parameters.SAMPLE_AREA,
        parameters.BLANK_AREA,
        parameters.SAMPLE_VOLUME,
        parameters.CALIB_FACTOR,
    ],
)

CALIBRATION_FACTOR = Equation(
    full_name="Calibration Factor",
    latex_equation=tex.calib_factor
    + "="
    + tex.frac(
        tex.Volume_calib * tex.conc_calib, tex.area_calib - tex.area_blank
    ),
    output_variable=parameters.CALIB_FACTOR,
    variables=[
        parameters.CALIB_VOLUME,
        parameters.CONC_CALIB,
        parameters.CALIB_AREA,
        parameters.BLANK_AREA,
    ],
)


CARBON_RESPONSE_FACTOR_EQUATION = Equation(
    full_name="Carbon Response Factor Equation",
    latex_equation=tex.carbon_response_factor
    + "="
    + tex.frac(
        tex.area_calib - tex.area_blank,
        tex.carbon_number
        * tex.ecn_contrib
        * tex.Volume_calib
        * tex.conc_calib,
    )
    + "="
    + tex.frac(1, tex.carbon_number * tex.ecn_contrib * tex.calib_factor),
    output_variable=parameters.CRF,
    variables=[
        parameters.CALIB_AREA,
        parameters.BLANK_AREA,
        parameters.CN,
        parameters.ECN_CONTRIB,
        parameters.CALIB_VOLUME,
        parameters.CONC_CALIB,
        parameters.CALIB_FACTOR,
    ],
)


CONCENTRATION_USING_CRF = Equation(
    full_name="Amount fraction using CRF",
    latex_equation=tex.conc_sample
    + "="
    + tex.frac(
        tex.area_sample - tex.area_blank,
        tex.Volume_sample * tex.carbon_number * tex.ecn_contrib * tex.mean_crf,
    ),
    output_variable=parameters.CONC_SAMPLE,
    variables=[
        parameters.SAMPLE_AREA,
        parameters.BLANK_AREA,
        parameters.SAMPLE_VOLUME,
        parameters.CN,
        parameters.ECN_CONTRIB,
        parameters.MEAN_CRF,
        parameters.USE_FOR_GENERAL_CRF,
    ],
)


BLANK_AREA_FROM_CONC = Equation(
    full_name="Retrieval of blank area from amount fraction",
    latex_equation=tex.area_blank
    + "="
    + tex.frac(
        tex.conc_blank,
        tex.parenthesis(
            tex.frac(tex.Volume_calib, tex.Volume_sample)
            + tex.conc_calib
            + "+"
            + tex.conc_blank
        ),
    )
    + tex.area_calib,
    output_variable=parameters.BLANK_AREA,
    variables=[
        parameters.BLANK_CONC_PRESET,
        parameters.CONC_CALIB,
        parameters.CALIB_AREA,
        parameters.CALIB_VOLUME,
        parameters.SAMPLE_VOLUME,
        parameters.CALIB_FACTOR,
    ],
    derivation=tex.multiline(
        tex.conc_sample
        + "&="
        + tex.frac(tex.area_sample - tex.area_blank, tex.Volume_sample)
        * tex.calib_factor,
        tex.mathrm("In the case of blanks transforms to: "),
        tex.conc_blank
        + "&="
        + tex.frac(tex.area_blank, tex.Volume_sample) * tex.calib_factor,
        tex.calib_factor
        + "&="
        + tex.frac(
            tex.Volume_calib * tex.conc_calib, tex.area_calib - tex.area_blank
        ),
        tex.mathrm("Merging the equations together: "),
    )
    + 2 * "\n\t"
    + tex.multiline(
        tex.conc_blank
        + "&="
        + tex.frac(tex.Volume_calib, tex.Volume_sample)
        + tex.frac(tex.area_blank, tex.area_calib - tex.area_blank)
        * tex.conc_calib,
        tex.conc_blank * tex.parenthesis(tex.area_calib - tex.area_blank)
        + "&="
        + tex.frac(tex.Volume_calib, tex.Volume_sample)
        * tex.area_blank
        * tex.conc_calib,
        tex.conc_blank * tex.area_calib
        + "&="
        + tex.parenthesis(
            tex.frac(tex.Volume_calib, tex.Volume_sample) * tex.conc_calib
            + "+"
            + tex.conc_blank
        )
        * tex.area_blank,
        tex.texstr(r"\Rightarrow ")
        + tex.area_blank
        + "="
        + tex.frac(
            tex.conc_blank,
            tex.parenthesis(
                tex.frac(tex.Volume_calib, tex.Volume_sample)
                + tex.conc_calib
                + "+"
                + tex.conc_blank
            ),
        )
        + tex.area_calib,
    ),
)
BLANK_AREA_FROM_CONC_FID = Equation(
    full_name=(
        "Retrieval of blank area from amount fraction for substances not in"
        " the calibration gas"
    ),
    latex_equation=tex.area_blank
    + "="
    + tex.conc_blank
    * tex.Volume_sample
    * tex.carbon_number
    * tex.ecn_contrib
    * tex.mean_crf,
    output_variable=parameters.BLANK_AREA,
    variables=[
        parameters.BLANK_CONC_PRESET,
        parameters.SAMPLE_VOLUME,
        parameters.CN,
        parameters.ECN_CONTRIB,
        parameters.MEAN_CRF,
    ],
    derivation=tex.multiline(
        tex.conc_sample
        + "&="
        + tex.frac(
            tex.area_sample - tex.area_blank,
            tex.Volume_sample
            * tex.carbon_number
            * tex.ecn_contrib
            * tex.mean_crf,
        ),
        tex.mathrm("In the case of blanks transforms to: "),
        tex.conc_blank
        + "&="
        + tex.frac(
            tex.area_blank,
            tex.Volume_sample
            * tex.carbon_number
            * tex.ecn_contrib
            * tex.mean_crf,
        ),
        tex.texstr(r"\Rightarrow ")
        + tex.area_blank
        + "="
        + tex.conc_blank
        * tex.Volume_sample
        * tex.carbon_number
        * tex.ecn_contrib
        * tex.mean_crf,
    ),
)

GENERAL_UNCERTAINTY_CALCULATION = Equation(
    full_name="General uncertainty calculation",
    output_variable=None,
    variables=[],
    latex_equation=tex.multiline(
        # tex.mathrm("Assuming that we have a function to calculate a value x:"),
        "x &= f(a,b,c)",
        # tex.mathrm("If variables a,b,c are uncorrelated,"),
        # tex.mathrm(" the uncertainty on x can be approximated as: "),
        tex.u2_of("x")
        + "&="
        + tex.derivative("f", "a")
        + tex.pow(2)
        + tex.u2_("a")
        + "+"
        + tex.derivative("f", "b")
        + tex.pow(2)
        + tex.u2_("b")
        + "+"
        + tex.derivative("f", "c")
        + tex.pow(2)
        + tex.u2_("c"),
    ),
)

UNCERTAINTIES_DERIVATION = Equation(
    full_name=(
        "Derivation of the uncertainties propagated during the calculation of"
        " the amount fraction"
    ),
    output_variable=None,
    variables=[],
    latex_equation="",
    derivation=tex.multiline(
        tex.u2_of(tex.conc_sample)
        + "&="
        + "+".join(
            (
                tex.partial_squared_derivative_for_u(
                    tex.conc_sample, tex.conc_calib
                ),
                tex.partial_squared_derivative_for_u(
                    tex.conc_sample, tex.area_sample
                ),
                tex.partial_squared_derivative_for_u(
                    tex.conc_sample, tex.area_calib
                ),
                tex.partial_squared_derivative_for_u(
                    tex.conc_sample, tex.area_blank
                ),
                tex.partial_squared_derivative_for_u(
                    tex.conc_sample, tex.Volume_sample
                ),
                tex.partial_squared_derivative_for_u(
                    tex.conc_sample, tex.Volume_calib
                ),
            )
        ),
        tex.partial_squared_derivative_for_u(tex.conc_sample, tex.conc_calib)
        + "&="
        + tex.conc_sample
        + tex.pow(2)
        + tex.u_rel_as_frac(tex.conc_calib)
        + tex.pow(2)
        + "=>"
        + tex.mathrm("Calibration uncertainty"),
        tex.partial_squared_derivative_for_u(tex.conc_sample, tex.area_sample)
        + "&="
        + tex.conc_sample
        + tex.pow(2)
        + tex.frac(tex.u_(tex.area_sample), tex.area_sample - tex.area_blank)
        + tex.pow(2)
        + "=>"
        + tex.mathrm(
            "Peak integration U (sample part) (by modifying some terms)"
        ),
        tex.partial_squared_derivative_for_u(tex.conc_sample, tex.area_calib)
        + "&="
        + tex.conc_sample
        + tex.pow(2)
        + tex.frac(tex.u_(tex.area_calib), tex.area_calib - tex.area_blank)
        + tex.pow(2)
        + "=>"
        + tex.mathrm(
            "Peak integration U (calib part) (by modifying some terms)"
        ),
        tex.partial_squared_derivative_for_u(tex.conc_sample, tex.area_blank)
        + "&="
        + tex.conc_sample
        + tex.pow(2)
        + tex.frac(
            tex.u_(tex.area_blank)
            * tex.parenthesis(tex.area_sample - tex.area_calib),
            tex.parenthesis(tex.area_calib - tex.area_blank)
            * tex.parenthesis(tex.area_sample - tex.area_blank),
        )
        + tex.pow(2)
        + "=>"
        + tex.mathrm("Not taken into account"),
        tex.partial_squared_derivative_for_u(
            tex.conc_sample, tex.Volume_sample
        )
        + "&="
        + tex.conc_sample
        + tex.pow(2)
        + tex.u_rel_as_frac(tex.Volume_sample)
        + "=>"
        + tex.mathrm("Volume uncertainty (sample part)"),
        tex.partial_squared_derivative_for_u(tex.conc_sample, tex.Volume_calib)
        + "&="
        + tex.conc_sample
        + tex.pow(2)
        + tex.u_rel_as_frac(tex.Volume_calib)
        + tex.mathrm("Volume uncertainty (calib part)"),
    ),
)


UNCERTANTY_ON_CALIB_FACTOR = Equation(
    full_name="Calculation of the uncertainty on the calibration factor",
    output_variable=parameters.CALIB_FACTOR_UNCERTAINTY,
    variables=[
        parameters.CALIB_FACTOR,
        parameters.CALIB_VOLUME,
        parameters.CONC_CALIB,
        parameters.CALIB_AREA,
        parameters.BLANK_AREA,
    ],
    latex_equation="",
    derivation=tex.multiline(
        # Derivate over the 4 variables
        tex.u2_of(tex.calib_factor)
        + "&="
        + tex.derivative(tex.calib_factor, tex.conc_calib)
        + tex.pow(2)
        + tex.u2_(tex.conc_calib)
        + "+"
        + tex.derivative(tex.calib_factor, tex.Volume_calib)
        + tex.pow(2)
        + tex.u2_(tex.Volume_calib)
        + "+"
        + tex.derivative(tex.calib_factor, tex.area_calib)
        + tex.pow(2)
        + tex.u2_(tex.area_calib)
        + "+"
        + tex.derivative(tex.calib_factor, tex.area_blank)
        + tex.pow(2)
        + tex.u2_(tex.area_blank),
        # apply the derivatives to the formula
        tex.u2_of(tex.calib_factor)
        + "&="
        + tex.pow(
            tex.parenthesis(
                tex.frac(
                    tex.Volume_calib * tex.u_(tex.conc_calib),
                    tex.area_calib - tex.area_blank,
                )
            ),
            2,
        )
        + "+"
        + tex.pow(
            tex.parenthesis(
                tex.frac(
                    tex.conc_calib * tex.u_(tex.Volume_calib),
                    tex.area_calib - tex.area_blank,
                )
            ),
            2,
        )
        + "+"
        + tex.pow(
            tex.parenthesis(
                tex.frac(
                    tex.conc_calib * tex.Volume_calib,
                    tex.pow(
                        tex.parenthesis(tex.area_calib - tex.area_blank), 2
                    ),
                )
            ),
            2,
        )
        * tex.parenthesis(
            tex.u2_(tex.area_calib) + "+" + tex.u2_(tex.area_blank)
        ),
        # simplify
        tex.u2_of(tex.calib_factor)
        + "&="
        + tex.pow(
            tex.parenthesis(
                tex.frac(
                    tex.calib_factor * tex.u_(tex.conc_calib),
                    tex.conc_calib,
                )
            ),
            2,
        )
        + "+"
        + tex.pow(
            tex.parenthesis(
                tex.frac(
                    tex.calib_factor * tex.u_(tex.Volume_calib),
                    tex.Volume_calib,
                )
            ),
            2,
        )
        + "+"
        + tex.frac(
            tex.pow(
                tex.calib_factor,
                2,
            )
            * tex.parenthesis(
                tex.u2_(tex.area_calib) + "+" + tex.u2_(tex.area_blank)
            ),
            tex.pow(tex.parenthesis(tex.area_calib - tex.area_blank), 2),
        ),
        # simplify more
        tex.u2_of(tex.calib_factor)
        + "&="
        + tex.calib_factor
        + tex.pow(2)
        + tex.parenthesis(
            tex.pow(
                tex.frac(
                    tex.u_(tex.conc_calib),
                    tex.conc_calib,
                ),
                2,
            )
            + "+"
            + tex.pow(
                tex.frac(
                    tex.u_(tex.Volume_calib),
                    tex.Volume_calib,
                ),
                2,
            )
            + "+"
            + tex.frac(
                tex.parenthesis(
                    tex.u2_(tex.area_calib) + "+" + tex.u2_(tex.area_blank)
                ),
                tex.pow(tex.parenthesis(tex.area_calib - tex.area_blank), 2),
            ),
        ),
    ),
)


UNCERTAINTY_ON_CRF = Equation(
    full_name="Calculation of the uncertainty on the CRF of one compound",
    output_variable=None,
    variables=[
        parameters.CALIB_FACTOR,
        parameters.CALIB_FACTOR_UNCERTAINTY,
        parameters.ECN_CONTRIB,
        parameters.ECN_CONTRIB_UNCERTAINTY,
    ],
    latex_equation=tex.u_of(tex.carbon_response_factor),
    derivation=tex.multiline(
        tex.u2_of(tex.carbon_response_factor)
        + "&="
        + tex.derivative(tex.carbon_response_factor, tex.ecn_contrib)
        + tex.u2_(tex.ecn_contrib)
        + "+"
        + tex.derivative(tex.carbon_response_factor, tex.calib_factor)
        + tex.u2_of(tex.calib_factor),
        # Simplify directly
        tex.u2_of(tex.carbon_response_factor)
        + "&="
        + tex.carbon_response_factor
        + tex.pow(2)
        + tex.parenthesis(
            tex.pow(
                tex.parenthesis(
                    tex.frac(
                        tex.u_(tex.ecn_contrib),
                        tex.ecn_contrib,
                    )
                ),
                2,
            )
            + "+"
            + tex.pow(
                tex.parenthesis(
                    tex.frac(
                        tex.u_(tex.calib_factor),
                        tex.calib_factor,
                    )
                ),
                2,
            )
        ),
    ),
)


UNCERTAINTY_OF_CONC_FOR_FID_SUBSTANCES = Equation(
    full_name=(
        "Calculation of the uncertainties on the concentration of a compound"
        " measured by FID"
    ),
    output_variable=None,
    variables=[],
    latex_equation=tex.u_of(tex.carbon_response_factor),
    derivation=tex.multiline(
        tex.u_of(tex.conc_sample)
        + "="
        + tex.frac(
            tex.conc_sample + tex.pow(2),
            tex.pow(tex.parenthesis(tex.area_sample - tex.area_blank), 2),
        )
        * tex.parenthesis(
            tex.u2_(tex.area_sample) + "+" + tex.u2_(tex.area_blank)
        )
        + "+"
        + tex.conc_sample
        + tex.pow(2)
        * tex.parenthesis(
            tex.pow(
                tex.parenthesis(
                    tex.frac(tex.u_(tex.Volume_sample), tex.Volume_sample)
                ),
                2,
            )
            + "+"
            + tex.pow(
                tex.parenthesis(
                    tex.frac(tex.u_(tex.ecn_contrib), tex.ecn_contrib)
                ),
                2,
            )
            + "+"
            + tex.pow(
                tex.parenthesis(
                    tex.frac(
                        tex.u_of(tex.mean_crf),
                        tex.mean_crf,
                    )
                ),
                2,
            )
        ),
    ),
)
