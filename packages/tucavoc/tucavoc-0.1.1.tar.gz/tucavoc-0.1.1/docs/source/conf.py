# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
from datetime import datetime
from pathlib import Path
from tucavoc.abstract_uncertainty import (
    Uncertainty,
    CalculatedVariable,
    Parameter,
    BoolParameter,
)
from tucavoc.uncertainties import (
    ALL_UNCERTAINTIES,
    COMBINEDSTANDARDUNCERTAINTY,
    EXPANDEDUNCERTAINTY,
)
from tucavoc import parameters
from tucavoc import equations
from tucavoc import tex

# -- Project information -----------------------------------------------------

project = "tucavoc"
copyright = f"{datetime.now().year}, Abt. 503, EMPA"
author = "Lionel Constantin, EMPA"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "enum_tools.autoenum",
    # "myst_parser",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Generate the uncertainty file -------------------------------------------

# All the uncertainties are directly documented in the python classes
# so we can just load them and format them in a dedicated rst file.

with open(Path("uncertainties", "uncertainties.rst"), "w") as text_file:
    text_file.write(
        ".. This file is erase and rewritten during compilation of the doc. "
        "Don't write anything in there as it will be deleted. \n\n"
    )
    # text_file.write("Uncertainties\n")
    # text_file.write("-------------\n\n")
    for u in ALL_UNCERTAINTIES:

        text_file.write(f".. _section_{u.name}:\n\n")

        text_file.write(f"{u.title_name}\n{u.title_char * len(u.title_name)}\n\n")
        parsed_explanation = u.explanation.replace("\t", "")
        text_file.write(f"{parsed_explanation}\n\n")
        text_file.write(
            f"Formula:\n\n.. math::\n\n\t{u.latex_name} = "
            f"{u.latex_formula}\n\n"
        )
        for p in u.parameters:
            if isinstance(p, Parameter):
                tex_name = p.tex_name
                full_name = p.full_name
                ref_name = p.name
            elif isinstance(p, Uncertainty):
                # Remove the ^2
                tex_name = p.latex_name[:-4]
                full_name = p.param_name
                ref_name = f"u_{p.name}"
            else:
                raise ValueError(
                    f"Parameter {p} is neither a Parameter nor an Uncertainty"
                )
            text_file.write(
                f"* "
                + (f":math:`{tex_name}` :  " if tex_name else "")
                + f" :term:`{full_name} <{ref_name}>`\n"
            )
        text_file.write("\n")
        text_file.write(f".. include:: uncertainties/{u.name}.rst\n\n")


# -- Generate the Glossary -------------------------------------------

with open(Path("parameters_glossary.rst"), "w") as text_file:
    text_file.write(
        ".. This file is erase and rewritten during compilation of the doc. "
        "Don't write anything in there as it will be deleted. \n\n"
    )
    # Add a line for referencing to the glossary
    text_file.write(".. _parameters_glossary:\n\n")
    text_file.write("Glossary\n=========\n\n")
    text_file.write(
        "This glossary contains all the variables used in TUCAVOC. "
        "The names of the variables correspond to names in Python."
        "\n\n"
    )
    text_file.write(".. glossary::\n")
    text_file.write("\t:sorted:\n\n")
    params = [
        p for p in parameters.__dict__.values() if isinstance(p, Parameter)
    ]
    for p in params:
        text_file.write(f"\t{p.name}\n")
        tex_name = f":math:`{p.tex_name}` [{p.unit}] : " if p.tex_name else ""
        text_file.write(f"\t\t{tex_name}{p.full_name}\n\n")
        if isinstance(p, CalculatedVariable) and p.equations:
            refs = [f":math:numref:`{e.name}`" for e in p.equations]
            text_file.write(f"\t\tCalculated in: {' '.join(refs)}\n\n")
        if p.explanation:
            text_file.write(f"\t\t")
            text_file.write(f"{p.explanation}\n\n")
    for u in ALL_UNCERTAINTIES:
        if u in [COMBINEDSTANDARDUNCERTAINTY, EXPANDEDUNCERTAINTY]:
            # These are written in Parameters (they have different units)
            continue
        text_file.write(f"\tu_{u.name}\n")
        text_file.write(
            f"\t\t:math:`u{tex.parenthesis(tex.conc + tex._(tex.mathrm(u.name_camel_case)))}`"
            f" [pmol/mol] : {u.short_explanation} \n\n"
        )
        text_file.write(f"\t\tExplained in: :ref:`section_{u.name}`\n\n")
        text_file.write(f"\n\n")
# -- Generate the Equations -------------------------------------------


equs = [
    e for e in equations.__dict__.values() if isinstance(e, equations.Equation)
]

for e in equs:
    with open(Path("equations", f"{e.name}.rst"), "w") as eq_file:
        eq_file.write(f"Equation :math:numref:`{e.name}`\n\n")
        eq_file.write(".. math::\n")
        # eq_file.write(f"\t:label: {e.name}\n")
        # eq_file.write(f"\t:caption: {e.name}\n")
        eq_file.write(f"\n\t{e.latex_equation}\n\n")
        for var in [e.output_variable] + e.variables:
            if isinstance(var, BoolParameter) or var is None:
                continue
            eq_file.write(
                f"* {tex.rst_math(var.tex_name)}:"
                f" :term:`{var.full_name} <{(var.name)}>` \n"
            )
        eq_file.write("\n")


# make a glossary for the equations

with open(Path("equations_glossary.rst"), "w") as text_file:
    text_file.write(
        ".. This file is erase and rewritten during compilation of the doc. "
        "Don't write anything in there as it will be deleted. \n\n"
    )
    text_file.write("All equations\n=============\n\n")

    for e in equs:
        text_file.write(f"{e.full_name}\n")
        text_file.write(f"{'-' * len(e.full_name)}\n\n")
        text_file.write(".. math::\n")
        text_file.write(f"\t:label: {e.name}\n\n")
        text_file.write(f"\t{e.latex_equation}\n\n")
        for var in [e.output_variable] + e.variables:
            if var is None:
                continue
            text_file.write(
                f"* {tex.rst_math(var.tex_name) + ':' if var.tex_name else ''} :term:`{var.full_name} <{(var.name)}>` \n"
            )
        text_file.write("\n\n")
        if e.derivation is not None:
            text_file.write("Derivation\n")
            text_file.write("^^^^^^^^^^\n\n")
            text_file.write(".. math::\n")
            text_file.write(f"\t{e.derivation} \n\n")
        text_file.write("\n")
