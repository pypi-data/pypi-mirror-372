
.. _methodology:

Method
======

This page describes the calculation method.
The method is described in detail in the :ref:`guidelines document <Guidelines>` .


Currently TUCAVOC can only be applied to online GC measurements,
but in the future it is planned to extend it to other techniques.

If you want to use TUCAVOC for other techniques, please :ref:`contact us <contact>`.


Calculation of VOC amount fraction 
----------------------------------

Default method based on calibration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This method compares the peak area obtained during the calibration 
of the instrument/GC-FID - using reference gas mixtures 
of known amount fractions - to the sample (measurement) area 
to retrieve the correct amount fraction.

This is based on the assumption that the area in the chromatograms
is linearly dependent on the amount fraction of the substance in the sample.

The calculation is based on the :ref:`guidelines document <Guidelines>`:

.. include:: equations/calculationofamountfractionsforlineardetectionsystems.rst

With the calibration factor being

.. include:: equations/calibrationfactor.rst

.. _fid_method:

Method based on the effective carbon number (for GC-FID)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The effective carbon number concept (ECN) (Sternberg et al., 1962, Dietz et al., 1967) states that the
response (peak area) of the FID is proportional to the number of molecules times the effective number of
carbon atoms per analyte molecule. This holds for single hydrogen-carbon bonds. If other bonds in a
specific molecule occurs, the response of the respective carbon atom is adjusted to yield an effective carbon
number.


.. include:: equations/amountfractionusingcrf.rst

The C-response factor :math:`C_{\mathrm{resp}}` 
is derived for each substance from the measurement of the certified standard
reference gas mixture.
Using the ECN-concept, reliable calibration factors can also be estimated for
substances not present in the calibration gas mixture. In this case, the 
amount fraction is calculated via the
mean carbon-response factor :math:`\overline{C}_{\mathrm{resp}}` ,
which is determined from selected substances in the standard gas
measurements averaging the :math:`\overline{C}_{\mathrm{resp}}` 
for those substances.


.. include:: equations/carbonresponsefactorequation.rst


Uncertainties 
-------------

This section describes the sources of uncertainty considered by TUCAVOC
to calculate the overall uncertainty of the measurements.
The main uncertainties taken into account are associated with
the reproducibility of the measurement,
calibration procedure,
sampling method
and analytical system used. 


.. include:: uncertainties/uncertainties.rst


Calibration Values 
------------------ 

To calculate the calibration value of each measurements TUCAVOC uses an interpolation 
method that helps estimating better the real reference value at the time 
of the measurements. 
TUCAVOC assumes linear deviation with time.
The uncertainties of the calibration are also obtained based on interpolation 
between the neighboring calibration series.

On the following plot you can see how the calibration value (in orange) changes between 
calibration runs over time.
The area around the orange line shows the standard deviation of the calibration value

.. image:: images/example_interpolation.png
  :alt: Example of interpolation for the calibration



Blank Correction
----------------

Incorporate blank measurements in the measurement sequence is highly recommended
to correct by substances under study that might appear due to artefacts [Guidelines]_ . 

The blank correction will correct the area measured 
by substracting from it the area of the blank, as 
indicated in equations
:math:numref:`calculationofamountfractionsforlineardetectionsystems`
:math:numref:`calibrationfactor`
:math:numref:`carbonresponsefactorequation`
:math:numref:`amountfractionusingcrf`
.

As the blank measured value can vary over time, TUCAVOC interpolates 
between the measurements to approximate the real blank value.

When using the widget, you can select if the blank areas are present in 
the data, or you can select if you want to specify a blank value 
to the substances.


When specifying the blank amount fraction, TUCAVOC will use equations
:math:numref:`retrievalofblankareafromamountfraction` and 
:math:numref:`retrievalofblankareafromamountfractionforsubstancesnotinthecalibrationgas` 
to calculate the blank area.


.. _flagging:

Flagging
--------



.. automodule:: tucavoc.flags
    :members: