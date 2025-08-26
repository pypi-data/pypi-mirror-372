
.. _groups:

Grouped substances 
------------------


TUCAVOC can group substances in a new one.
For example you have substances A, B and D, and you want to make 
a new substance called S.

S is a *grouped substance*.

Grouped substances are usually used when you have coeluting substances, 
that come sometimes in one peak and sometimes in different peaks.

Calculation 
^^^^^^^^^^^

TUCAVOC will handle this case by simply adding the amount fraction of
the individual substances contained in the group.
The uncertainty of the amount fraction calculated for the grouped substance 
is calculated applying the squared sum of the uncertainty of each substance.

Behaviour for flagging and missing data 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If one or more group members have invalid data (nan values), 
the group will be flagged as invalid.

If the area of a substance is zero, TUCAVOC assumes that the substance was 
included in the area of another substance from the group.

Groups selection in TUCAVOC widget
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can select which group a substance belong to, using the combo box
in the substances widget. 
You can also create a new group using the '+' button at the 
top of the *Group* column.

If you want a substance to be present only in a group, but not in the 
output, you have to untick the include substance column, and add a group 
for the substance. TUCAVOC will automatically remove that substance from 
the output, but still include it in the calculation of the grouped amount fraction
and in the calculation of the mean CRF (if selected in the *use for general crf* column).

Mean carbon response factor calculation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Substances in the same group will share
the same :term:`mean_carbon_response_factor` value.
This means that only substance in the calibration for that group are taken
into account in this calculation.

For substances not in any group, the :term:`mean_carbon_response_factor` is
taken to be the mean of all substances in the calibration that do not belong to 
any group. This is the *general* :term:`mean_carbon_response_factor`.

As a suggestion for the *general* :term:`mean_carbon_response_factor`,
we recommend using all the substances having from 2 to 4 carbon atoms,
excluding *ethyne*. 