API 
===


TUCAVOC
-------

.. automodule:: tucavoc


Utilities
---------

Different utility functions to use with TUCAVOC.


reading output files with python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: tucavoc.read_concs

.. autofunction:: tucavoc.read_output



Calculations 
------------

.. autofunction:: tucavoc.calculations.main




TUCAVOC content
---------------

This section describes objects that represent tucavoc content. 


Parameters 
~~~~~~~~~~

Parameters represent variables that are used in tucavoc calculations.
They are all described in the :ref:`parameters_glossary` .

Here are classes that represents possible types of parameters.

.. autoclass:: tucavoc.abstract_uncertainty.Parameter

.. autoclass:: tucavoc.abstract_uncertainty.FloatParamter

.. autoclass:: tucavoc.abstract_uncertainty.BoolParameter

.. autoclass:: tucavoc.abstract_uncertainty.CalculatedVariable


Uncertainties
~~~~~~~~~~~~~

.. autoclass:: tucavoc.abstract_uncertainty.Uncertainty
    :members: calculate


Equations 
~~~~~~~~~

Equations are only used for documentation purposes.  

.. autoclass:: tucavoc.equations.Equation


Additional Data 
~~~~~~~~~~~~~~~

.. autoclass:: tucavoc.additional_data.AdditionalData
    :members: get_data


