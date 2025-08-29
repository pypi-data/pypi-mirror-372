# MATER

Metabolic Analysis for Transdisciplinary Ecological Research

[TOC]

## 📋 Requirements

- Python 3.12 or higher

We recommend using one virtual environment per Python project to manage dependencies and maintain isolation. You can use a package manager like [uv](https://docs.astral.sh/uv/) to help you with library dependencies and virtual environments.

## 📦 Install the Mater Package

Install the `mater` package via pip:

```bash
pip install mater
```

## ⚙️ Run a Simulation

The `mater` command line interface (CLI) makes it easy to run simulations. Ensure the required [Excel input file](https://zenodo.org/search?q=parent.id%3A12751420&f=allversions%3Atrue&l=list&p=1&s=10&sort=version) (chose a compatible version) is located in the root of your working directory.

Run the following command to start a simulation from your excel file:

```bash
mater run -i <YOUR_INPUT_FILE_NAME>
```

## 📊 Visualize Variables

Simulation results are stored locally in [Parquet](https://parquet.apache.org/docs/) (.mater) files.

### Output variables description

| **Output variable**        | **Unit**                          | **Definition**                                         | **Example**                                                                                                      |
|----------------------------|-----------------------------------|--------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| control_flow               | <object_unit>/time                | Object footprint demand before trade between locations | Number of cars consumed in China (included the imported ones)                                                     |
| extraneous_flow            | <object_unit>/time                | Object consumption or coproduction                     | C02 coproduced (+ value) and coal consumed (- value) by the electricity production process of a coal power plant |
| in_use_stock               | <object_unit>                     | Object in use stock                                    | Number of cars in use                                                                                            |
| old_stock                  | <object_unit>                     | Object stock in landfill                               | Number of end of life cars unrecycled                                                                            |
| process                    | <process_unit>/time               | Number of process made by an object                    | Transportation process (km/year) made by cars                                                                    |
| recycling_flow             | <object_unit>/time                | Quantity of recycled objects                           | Recycled end of life cars                                                                                        |
| reference_intensity_of_use | <process_unit>/<object_unit>/time | Intensity of use                                       | Number of km per year made by a car                                                                              |
| reference_stock            | <object_unit>                     | How many objects should be in the in use stock         | Installed power plant capacity to fulfill the electricity demand                                                 |
| secondary_production       | <object_unit>/time                | Coproduction due to recycling processes                | Quantity of steel recycled (coproduce by recycling) in a year                                                    |
| self_disposal_flow         | <object_unit>/time                | End of life flow                                       | Number of cars that cannot work anymore                                                                       |
| traded_control_flow        | <object_unit>/time                | Object supply after trade between locations            | Number of cars produced in China (included the exported ones)                                                    |

### User Interface

Results can be visualize in a built-in user interface. Go to the directory containing the result folder and use the following command :

```bash
mater plot -o <YOUR_RESULT_FOLDER_NAME>
```

### Accessing the Results from a Python Script

Below is an example Python script using `pandas` and `matplotlib` to plot specific simulation results. Each folder in the output directory corresponds to a variable that can be loaded with `pandas`.

```python
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
```

This example demonstrates how to access and plot variables from simulation outputs. Adjust the code to fit your analysis needs.

## 🤝 Contributing

We welcome contributions to the MATER project! To get started, please refer to the [CONTRIBUTING](CONTRIBUTING.md) file for detailed guidelines.

## 📚 Online Documentation

For more information, refer to the official **[MATER documentation](https://isterre-dynamic-modeling.gricad-pages.univ-grenoble-alpes.fr/mater-project/mater/)**.
