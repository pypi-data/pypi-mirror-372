.. _user_guide_data_visualization:

Data visualization
===================

Simulation results are stored locally in `Parquet <https://parquet.apache.org/docs/>` (.mater) files.

User Interface
--------------

Results can be visualize in a built-in user interface. Go to the directory containing the result folder and use the following command :

.. code-block:: bash

   mater plot -o <YOUR_RESULT_FOLDER_NAME>

Accessing the Results from a Python Script
------------------------------------------

Below is an example Python script using `pandas` and `matplotlib` to plot specific simulation results. Each folder in the output directory corresponds to a variable that can be loaded with `pandas`.

.. code-block:: python

   # Import the MATER package and matplotlib.pyplot
   import matplotlib.pyplot as plt
   from mater import Mater

   # Create a Mater instance
   model = Mater()

   # Select the output directory where the run results are stored
   model.set_output_dir()  # Defaults to the working directory

   # Set the run directory name
   model.set_run_name("run0")

   # Get a variable
   in_use_stock = model.get("in_use_stock")

   # Transform the dataframe and plot the results
   in_use_stock.groupby(level=["location", "object"]).sum().T.plot()
   plt.show()

This example demonstrates how to access and plot variables from simulation outputs. Adjust the code to fit your analysis needs.


