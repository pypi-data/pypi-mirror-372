
.. _manual:

User Manual 
===========

This manual explain how to use tucavoc-widget.

The widget is separated in different sections.

Some parameters found in the different sections 
are not required by all
the calculations, so depending on what you calculate
you will need different input data, but the tucavoc widget 
will handle all that.


.. image::
    images/tucavoc_widget.png


Input Files 
-----------

This allow you to select input files.
For the moment we can only handle GCWerks files but if 
you have any needs, please :ref:`contact us <contact>` .

You can also select the runtype of your calibration and blank runs.


Global Parameters 
-----------------

These are parameters of your measurements that are 
required by tucavoc. 


Substances 
----------

This is a table for parameters depending on each substance.

The Groups columns allows you to group substances.
See :ref:`Section <groups>` .

The columns In Calib lets you select which substances are in the calibration
data. 
If a substance is not in the calibration, tucavoc will use :ref:`fid_method` .

The other columns are different parameters required for the calculations. 

Uncertainties Selection 
-----------------------

This allow you to select which uncertainties you want.

Outputs
-------

In the output section you can decide the following.

* The directory in which to save the output.

* The export formats for the output. If you want to export
in a specific format, please :ref:`contact us <contact>` so 
we can add it to tucavoc. 

* The runtypes that should be exported 
  
* Additional data to add to the output.
This might be required by some export formats. Learn more: :ref:`additional_data`.

* Plot a substance. Once the calculation is over you can quickly 
  watch what was going on during the computation by plotting
  the data of a given substance.

* Calculation button. This will start the calculations and export the data.




