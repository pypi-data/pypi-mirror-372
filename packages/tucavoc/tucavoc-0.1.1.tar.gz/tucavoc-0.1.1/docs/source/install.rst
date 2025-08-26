.. _installation:

Installation
============

If you want to use TUCAVOC, you can either download
the executable for windows or download and install the source code (works 
on every OS)


Using executable for windows
---------------------------- 

You will find .exe file at https://polybox.ethz.ch/index.php/s/Z78706Xrzfk5ZRv .

Download the file on your computer and run it (double clicking should work).

It should take about 10 seconds before TUCAVOC opens.

If you have any issue using it, please :ref:`contact us <contact>` .

Installation from source
------------------------


This guide will help you installing TUCAVOC step by step.

If you have any issue, please :ref:`contact us <contact>`  


1. python 
^^^^^^^^^

You will find the last installers for python on their website: 
https://www.python.org/downloads/ 
You need to have a version of python which is at least 3.10 

Make sure that during the installation you activate pip and add python to environement variables.
See image below.

.. image::
    images/python.png
    :width: 45%

.. image::
    images/python_next.png
    :width: 45%


2. git 
^^^^^^

Git is a free and open source distributed version control system.

You can find it there:
https://git-scm.com/

Download it and install it.
You can select the default options during the installation.


3.  tucavoc 
^^^^^^^^^^^

You will find tucavoc in our official repository.
But the simplest way is to install it using command line.

For that open a command line prompt in
the directory where you want to 
install tucavoc.

Then run the following lines of codes.
They will download tucavoc and install it

.. code-block::

    git clone https://gitlab.com/empa503/atmospheric-measurements/tucavoc.git
    cd tucavoc 
    pip install -e .


4. create a short cut to the executable 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This works for Windows only.

Open the folder where tucavoc is installed and find the 
file `start.bat` . You can right click the file and create 
a short cut on your desktop.

Double left click on the file or shortcut will start 
tucavoc-widget.