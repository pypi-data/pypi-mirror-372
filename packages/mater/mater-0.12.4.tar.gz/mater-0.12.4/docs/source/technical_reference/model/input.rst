.. _input:

====================
Inputs documentation
====================

Input data
==========

The inputs of the MATER model are currently stored in an excel file that you can **download** `here <https://zenodo.org/search?q=parent.id%3A12751420&f=allversions%3Atrue&l=list&p=1&s=10&sort=version>`_.
The team is working on a collaborative user friendly database that will be released in futur versions.

Each excel sheet corresponds to one model input. Except for the *vectors* sheet, 
all data have a standardized structure with aspects (dimensions) and unit as first columns followed by the time series of values.

.. image:: ../../_static/input_example.png
  :width: 800
  :alt: image not found

Keeping the given format, one can add time values or aspect indexes (as location or object items).
The *vectors* sheet references all the dimensions and sub-dimensions items for a mapping purpose in the model code. 
**Any added item has to be referenced in the vectors sheet under the right sub-dimension**.

.. image:: ../../_static/vectors_example.png
  :width: 800
  :alt: image not found


The data are then treated in this :ref:`method <inputs_setup>`.

.. _dimensions:

Variables aspects
====================

Each variable can be a scalar (0 aspect), a vector (1 aspect), a matrix (2 aspects) or a tensor (multiple aspects).
It is defined in the equations by the number of variable indices.
For instance, :math:`F_{o,t,c}` means that the variable :math:`F` has three aspects: `object`, `time` and `age_cohort`.
:math:`F_{o,c}(k)` means that the variable :math:`F` is used at the time :math:`k`.

.. In this case, the variable has only two dimensions remained : :math:`e` and :math:`c`.

All the aspects and their dimension used in the model are listed in the table below and are defined in the *vector* sheet of the input data `Excel file <https://zenodo.org/search?q=parent.id%3A12751420&f=allversions%3Atrue&l=list&p=1&s=10&sort=version>`_.

.. list-table:: Dimensions and aspects of the MATER's data model
   :widths: 20 40 20
   :header-rows: 1
   :align: center

   * - dimension
     - aspect
     - index letter
   * - time
     - .. raw:: html

            time<br>age-cohort
     - .. raw:: html

            t<br>c
   * - location
     - .. raw:: html

            location<br>location production
     - .. raw:: html

            l<br>l<sub>p</sub>
   * - object
     - .. raw:: html

            object<br>object composition<br>object downgrading<br>object SU<br>object efficiency
     - .. raw:: html

            o<br>o<sub>c</sub><br>o<sub>d</sub><br>o<sub>s</sub><br>o<sub>e</sub>
   * - process
     - process
     - p


