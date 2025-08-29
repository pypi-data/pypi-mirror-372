# Import the MATER package and matplotlib.pyplot
import matplotlib.pyplot as plt

from mater import Mater

# Create a Mater instance
model = Mater()

# Select the output directory where the run results are stored
model.set_output_dir()  # default to working directory

# Set the run directory name
model.set_run_name("run0")

# Get a variable
in_use_stock = model.get("in_use_stock")
control_flow = model.get("control_flow")
self_disposal_flow = model.get("self_disposal_flow")
secondary_production = model.get("secondary_production")
process = model.get("process")

# Transform the dataframe and plot the results
in_use_stock.groupby(level=["location", "object"]).sum().T.plot(title="in_use_stock")
# # Plot the process variable
# process.T.plot(title="process")
# Plot control_flow with explicit legend labels
control_flow_linestyle = "solid"
axe = control_flow.T.plot(linestyle=control_flow_linestyle)

# Plot self_disposal_flow with explicit legend labels
self_disposal_flow_linestyle = "dashed"
self_disposal_flow.groupby(level=["location", "object"]).sum().T.plot(ax=axe, linestyle=self_disposal_flow_linestyle)

# Set a unified title
axe.set_title(f"Control Flow '{control_flow_linestyle}' and Self Disposal Flow '{self_disposal_flow_linestyle}'")

# Adjust the legend title
axe.legend(title="DataFrame - Location/Object")

# Adjust the legend
axe.legend(title="Flow Type")

# # Plot steel total production
# df = pd.concat(
#     [
#         control_flow.loc[:, ["steel"], :],
#         secondary_production.groupby(level=["location", "object"]).sum().loc[:, ["steel"], :],
#     ],
#     keys=["primary", "recycling"],
#     names=["production"],
# )
# df.T.plot(kind="area", title="Total steel production")

# Show all graphs
plt.show()
