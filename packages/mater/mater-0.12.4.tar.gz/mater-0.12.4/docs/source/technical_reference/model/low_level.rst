.. _low_level_doc:

=======================
Low level documentation
=======================

Inputs setup
============

.. automethod:: mater.model.Mater._inputs_setup

Outputs setup
=============

Exponential decay
-----------------
.. autofunction:: mater._utils._exponential_decay

Outputs initialization
----------------------
.. automethod:: mater.model.Mater._outputs_initialization

Lifetime computation
--------------------
.. automethod:: mater.model.Mater._lifetime_computation

Process reference capacity computation
--------------------------------------
.. automethod:: mater.model.Mater._process_reference_capacity_computation

Reference intensity of use computation
--------------------------------------
.. automethod:: mater.model.Mater._reference_intensity_of_use_coputation

Exogenously controlled process computation
------------------------------------------
.. automethod:: mater.model.Mater._exogenously_controlled_process_computation

Pseudoinverse computation
-------------------------
.. _pseudoinverse_computation:
.. autofunction:: mater._utils._compute_pseudoinverse

Control flow trade inverse computation
--------------------------------------
.. automethod:: mater.model.Mater._control_flow_trade_inverse_computation

Self-disposal, recycling and control flows
==========================================

Log normal distribution
-----------------------
.. autofunction:: mater._utils._log_normal

Log normal distribution computation
-----------------------------------
.. automethod:: mater.model.Mater._log_normal_distribution_computation

Self-disposal flow computation
------------------------------
.. automethod:: mater.model.Mater._self_disposal_flow_computation

Recycling flow computation
--------------------------
.. automethod:: mater.model.Mater._recycling_flow_computation

Control flow computation
------------------------
.. automethod:: mater.model.Mater._control_flow_computation

Traded control flow computation
-------------------------------
.. automethod:: mater.model.Mater._traded_control_flow_computation

Processes
=========

Endogenously controlled process computation
-------------------------------------------
.. automethod:: mater.model.Mater._endogenously_controlled_process_computation

Controlled process computation
------------------------------
.. automethod:: mater.model.Mater._controlled_process_computation

Free process computation
------------------------
.. automethod:: mater.model.Mater._free_process_computation

Process computation
-------------------
.. automethod:: mater.model.Mater._process_computation

Extraneous flows
================

Control flow composition computation
------------------------------------
.. automethod:: mater.model.Mater._control_flow_composition_computation

Secondary production flow computation
-------------------------------------
.. automethod:: mater.model.Mater._secondary_production_flow_computation

Thermodynamic process flow computation
--------------------------------------
.. automethod:: mater.model.Mater._thermodynamic_process_flow_computation

Extraneous flow computation
---------------------------
.. automethod:: mater.model.Mater._extraneous_flow_computation

Objects stocks
==============

Reference stock computation
---------------------------
.. automethod:: mater.model.Mater._reference_stock_computation

Old stock computation
---------------------
.. automethod:: mater.model.Mater._old_stock_computation

In-use stock computation
------------------------
.. automethod:: mater.model.Mater._in_use_stock_computation

Outputs update and save
=======================

Outputs update
--------------
.. autofunction:: mater.model.Mater._outputs_update

Outputs save
------------
.. automethod:: mater.model.Mater._outputs_save
