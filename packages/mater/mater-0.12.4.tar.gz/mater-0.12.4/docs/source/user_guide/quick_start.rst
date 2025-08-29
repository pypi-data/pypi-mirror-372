.. _user_guide_quick_start:

===========
Quick start
===========

For now, the simulations are always split into 2 parts:

* Change input data from the excel file
* Run simulations

Get data from excel file
========================

Download the `input excel file <https://zenodo.org/search?q=parent.id%3A12751420&f=allversions%3Atrue&l=list&p=1&s=10&sort=version>`_ (chose a compatible version): and put it in your project directory.

Each sheet from the excel file corresponds to one input variable of the MATER model. You can change the data following the excel file structure by adding lines in the sheets. The Home sheet provides guidelines to build a model and a scenario.

Run simulation
==============

Use the mater command line interface (CLI) to run a simulation from your excel input file. You can change the default result folder name using the `-o` option 

.. code-block:: bash

   mater run -i <YOUR_INPUT_FILE_NAME>

The results are now stored in the result folder.
