from __future__ import annotations
from abc import ABCMeta, abstractmethod, abstractproperty
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
import itertools
import logging
import re
from typing import TYPE_CHECKING, Any, Type
import numpy as np

from tucavoc import tex

if TYPE_CHECKING:
    from tucavoc.equations import Equation


class Selection(Enum):
    """How the parameter is selectable."""

    PER_SUBSTANCE = 0
    GLOBAL = 1


_ALL_PARAMETERS = []
PARAMETERS_BY_NAME: dict[str, Parameter] = {}
_NAMES: list[str] = []


@dataclass
class Parameter:
    """Base class for tucavoc parameters.

    Contains different attributes that are need by all the parameters.
    They are compatible with the widget and with the docs, allowing for
    easy additions of new parameters.

    :param name: Name of the parameter.
    :param val: Value of the parameter.

    Used only for documentation purposes or for the widget:

    :param full_name: Full name of the parameter.
    :param explanation: Explanation of the parameter.
    :param unit: Unit of the parameter.
    :param tex_name: Name of the parameter in latex.
    :param selectable: Whether parameter is selectable
        for one substance or for all.
    :param type: (Python) Type of the parameter.


    """

    name: str
    val: float | str | bool | None

    full_name: str | None = None
    explanation: str = ""
    unit: str = "-"
    tex_name: tex.texstr = tex.texstr("")
    selectable: Selection = Selection.GLOBAL
    type: Type | None = None

    def __post_init__(self):
        if self.name in _NAMES:
            raise ValueError(
                f"Parameter {self} has a name already registered."
            )
        _NAMES.append(self.name)

        if self.full_name is None:
            self.full_name = self.name

        _ALL_PARAMETERS.append(self)

        PARAMETERS_BY_NAME[self.name] = self


@dataclass
class FloatParamter(Parameter):
    """A parameter that is a float.

    :param min_val: Minimum value of the parameter.
    :param max_val: Maximum value of the parameter.
    :param decimals: Number of decimals to display.

    """

    val: float
    min_val: float = 0
    max_val: float = 1e9
    decimals: int = 6
    type: Type = float


@dataclass
class BoolParameter(Parameter):
    """A parameter that is a boolean.

    The value is either True or False.
    """

    val: bool
    type: Type = bool
    unit: str = "-"


@dataclass
class StrParameter(Parameter):
    """A parameter that is a string.

    The value is a string.
    """

    val: str
    type: Type = str

@dataclass
class CalculatedVariable(Parameter):
    """A variable that is calculated from other variables.


    :param val: Value of the variable.
    :param equations: List of equations that are used to calculate the variable.
        (only used for documentation purposes)
    """

    val: None = None
    equations: list[Equation] = field(default_factory=list)


@dataclass
class DataVariable(Parameter):
    """Variable read from the data."""

    val: None = None


@dataclass
class OptionalDataVariable(Parameter):
    """Variable read from the data, but is optional (requires default value)."""

    ...


@dataclass
class OptionalFloatParameter(FloatParamter):
    """Parameter that can be either set by user or read in data."""

    ...


@dataclass
class OptionalDataVariableOrCalculated(CalculatedVariable):
    """Variable read from the data, but is optional (requires default value).

    It can also be calculated.
    """

    ...


# Some colors used for default
_COLORS_ITER = itertools.cycle(
    [
        "#377eb8",
        "#4daf4a",
        "#984ea3",
        "#ff7f00",
        "#ffff33",
        "#a65628",
        "#f781bf",
        "#999999",
    ]
)


class Uncertainty:
    """An abstract class for the uncertainties calculated by TUCAVOC.

    The attributes of this class are used to generate the documentation.

    Only :py:meth:`calculate` needs to be implemented in each subclass, and
    is used to calculate the uncertainty during the execution in
    :py:func:`tucavoc.calculations.main` .

    :param name: Name of the uncertainty.
    :param param_name: Name of the uncertainty when in a funciton parameter.
    :param name_camel_case: Name of the uncertainty in camel case.
    :param latex_name: Name of the uncertainty in latex.
    :param title_name: Name of the uncertainty in the title.
    :param title_char: Character to use to underline the title.
        Used for specifying the title level.

    :param short_explanation: A short explanation text for what this uncertainty.
        This is shown in the glossary.
    :param explanation: An explanation text for what this uncertainty
        is about.
    :param color: A color corresponding to
        this uncertainty value (used for plotting).
    :param parameters: A list of the name of the attributes that should
        be selectable by the user.
    :param parameters_dict: Mapps the name of the param to the paramter.
    """

    short_explanation: str = "Unkonwn. Please implement."
    explanation: str = "Unkonwn. Please implement."

    name: str
    param_name: str = ""
    name_camel_case: str
    latex_name: str
    title_name: str = ""
    title_char: str = '^'

    color: str

    latex_formula: str = r"\mathrm{Unkonwn. Please implement.}"

    parameters: list[Parameter | Uncertainty]
    parameters_dict: dict[str, Parameter | Uncertainty]

    def __init__(self) -> None:
        self.parameters_dict = {param.name: param for param in self.parameters}
        self.color = next(_COLORS_ITER)

        if not self.param_name:
            self.param_name = f"Uncertainty of the {self.name_camel_case}"
        if not self.title_name:
            self.title_name = f"Uncertainty of the {self.name_camel_case}"

    @cached_property
    def name(self):
        """Find out the name of the uncertainty."""
        class_name = type(self).__name__
        # split by camel case
        words: list[str] = re.findall("[A-Z][^A-Z]*", class_name)
        # To snake case
        return "_".join([w.lower() for w in words])

    @cached_property
    def name_camel_case(self):
        """Find out the name of the uncertainty."""
        class_name = type(self).__name__
        # split by camel case
        words: list[str] = re.findall("[A-Z][^A-Z]*", class_name)
        # To snake case
        return " ".join(words)

    @cached_property
    def latex_name(self):

        # Create a latex variable that represent this uncertainty
        return tex.u_2_i(self.name_camel_case.lower())

    @abstractmethod
    def calculate(self, *args, **kwargs) -> np.ndarray:
        """Calculate the uncertainty.

        This should return the value for all the samples in pmol/mol.
        """
        return NotImplemented

    def get_param(self, name) -> float | int | bool | str:
        return self.parameters_dict[name].val

    def __repr__(self) -> str:
        return self.name
