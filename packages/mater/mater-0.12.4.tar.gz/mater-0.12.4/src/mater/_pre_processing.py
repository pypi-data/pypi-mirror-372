"""
This module creates the class to compute the pre processing of the MATER model.
"""

import os
from typing import Dict

import numpy as np
import pandas as pd

from mater._utils import _compute_pseudoinverse, _exponential_decay


class CompatibilityError(Exception):
    """Raised when the Excel template is incompatible with the MATER Python code."""

    pass


class _MaterPreProcess:
    """Pre processing of the MATER model."""

    def __init__(self):
        self.input_dir_path = os.getcwd()
        self.output_dir_path = os.getcwd()

    def _to_mater(self, variable: str, k=None):
        r"""
        Save a specified variable to durable storage in the Parquet format, optionally at a specific time point.

        This method handles the saving of model outputs to a file system, organizing the files within directories corresponding to the simulation run and scenario. It can save data either for a specific time point or for the entire set of outputs depending on the presence of the `k` parameter.

        **Parameters:**

        - `variable`: The name of the variable (output) to be saved.
        - `k`: Optional; an integer representing the time step at which the data should be saved. If not provided, the entire data set for the variable is saved.

        Method Operation
        ----------------
        - Directories are created for the variable if they do not exist.
        - If `k` is not specified, the entire data set for the variable is saved.
        - If `k` is specified, only the data corresponding to that time step is saved.
        - The data is saved in the Parquet format using the PyArrow engine with snappy compression.

        Examples
        --------
        .. code-block:: python

            instance._to_mater("self_disposal_flow", k=5)

        This would save the 'self_disposal_flow' output at time step 5 to the appropriate directory structure.

        Notes
        -----
        It is important to ensure that `self.outputs[variable]` contains data that can be successfully saved. This might involve handling different data structures (e.g., DataFrames, Series) appropriately. The method handles exceptions related to data saving by falling back to alternative saving procedures if the primary method fails (e.g., due to missing indices).
        """
        if self.outputs[variable].empty:
            return None
        # Directory creation for saving the outputs
        os.makedirs(
            os.path.join(self.output_dir_path, self.run_name, variable),
            exist_ok=True,
        )
        # Save logic depending on the presence of k
        if k is None:
            self.outputs[variable].stack(future_stack=True).to_frame("value").to_parquet(
                os.path.join(
                    self.output_dir_path,
                    self.run_name,
                    variable,
                    variable + ".mater",
                ),
                engine="pyarrow",
                compression="snappy",
            )
        else:
            # format for file name
            k_name = str(k).replace(" ", "_").replace(":", "-")
            try:
                self.outputs[variable].to_frame(k).rename_axis("time", axis=1).stack(future_stack=True).to_frame(
                    "value"
                ).to_parquet(
                    os.path.join(
                        self.output_dir_path,
                        self.run_name,
                        variable,
                        k_name + ".mater",
                    ),
                    engine="pyarrow",
                    compression="snappy",
                )
            except AttributeError:
                # Fallback for different data structures
                self.outputs[variable].stack(future_stack=True).to_frame("value").to_parquet(
                    os.path.join(
                        self.output_dir_path,
                        self.run_name,
                        variable,
                        k_name + ".mater",
                    ),
                    engine="pyarrow",
                    compression="snappy",
                )

    def set_input_dir(self, path: str | None = None):
        r"""Set the input directory path. The default path is the current directory.

        :param path: Input directory path, defaults to os.getcwd()
        :type path: str | None, optional
        """
        if path:
            self.input_dir_path = path

    def set_output_dir(self, path: str | None = None):
        """Set the output directory path. The default path is the current directory.

        :param path: Output directory path, defaults to os.getcwd()
        :type path: str | None, optional
        """
        if path:
            self.output_dir_path = path

    def set_run_name(self, run_name: str):
        r"""Set the name of the run (self.run_name).

        The outputs folders will be stored in a folder named

        :param run_name: the name of the run
        :type run_name: str
        """
        self.run_name = run_name

    def get(self, variable: str, t: int | None = None):
        r"""
        Retrieve data for a specified variable from durable storage in Parquet format, potentially filtered by simulation time or scenario.

        This method reads data from the file system where simulation outputs and inputs are stored. It can retrieve data for a specific variable across all scenarios, at a particular time step, or for the entire duration of a scenario depending on the parameters provided.

        :param variable: The name of the output variable to be read from storage.
        :type variable: str
        :param t: an integer representing the time step for which data should be retrieved. If not provided, data across all time steps is retrieved, defaults to None
        :type t: int, optional
        :param scenarios: a list or array of scenario names to be specifically read. If not provided, data is read for the current scenario unless `t` is specified, defaults to None
        :type scenarios: list, optional
        :return: A pandas DataFrame containing the requested data, structured according to the variable and time or scenario specifications.
        :rtype: pd.DataFrame

        Method Operation
        ----------------
        - If `scenarios` is provided, the method retrieves data for the specified variable across all listed scenarios.
        - If `t` is provided, the method retrieves data for the specified variable at the given time step.
        - If neither `t` nor `scenarios` is provided, data for the specified variable across all time steps is retrieved for the current scenario.

        Examples
        --------
        .. code-block:: python

            # Create a Mater instance
            model = Mater()

            # Retrieve data for 'YOUR_VARIABLE' variable across all time steps in the current scenario
            data = model.get("YOUR_VARIABLE")

            # Retrieve data for 'YOUR_VARIABLE' at time step 2015
            data = model.get("YOUR_VARIABLE", t=2015)

        Ensure that the file paths and structures are correctly set up and that data integrity is maintained to prevent errors during data retrieval.
        """
        if t is None:
            return pd.read_parquet(os.path.join(self.output_dir_path, self.run_name, variable))["value"].unstack("time")
        else:
            return pd.read_parquet(
                os.path.join(
                    self.output_dir_path,
                    self.run_name,
                    variable,
                    str(t) + ".mater",
                )
            )["value"].unstack("time")[t]

    def _check_excel_requirements(self, input_file, excel_version, requires_mater):
        # check version compatibility
        ## Load the pyproject.toml file
        ## Access the mater version and the required excel version
        mater_version = self.__version__
        requires_excel = self.requires_excel
        ## compare the versions with the version requirements
        if mater_version < requires_mater:
            raise CompatibilityError(
                f"Version mismatch: mater version {mater_version} is not compatible with {input_file} version {excel_version}.\n"
                f"Update to mater version {requires_mater} or downgrade to {input_file} version {requires_excel}"
            )
        if excel_version < requires_excel:
            raise CompatibilityError(
                f"Version mismatch: {input_file} version {excel_version} is not compatible with mater version {mater_version}.\n"
                f"Update to {input_file} version {requires_excel} or downgrade to mater version {requires_mater}"
            )

    def input_formatting(self, input: pd.DataFrame):
        input = input[~input.index.duplicated(keep="first")]
        # Formatting
        formatted_input = input.droplevel(list(set(input.index.names).intersection(["unit", "scenario"])))[
            "value"
        ].unstack("time")
        # Interpolation
        df2 = pd.DataFrame(
            data=np.nan,
            index=formatted_input.index,
            columns=pd.date_range(
                start=self.simulation_start_time - self.offset,
                end=self.simulation_end_time,
                freq=self.time_frequency,
                tz="UTC",
            ),
        )
        ## rename column
        df2.columns.name = formatted_input.columns.name
        interpolated_input = df2.add(formatted_input, fill_value=0)  # to do panda.reindex

        # linear interpolation and extrapolation on the full timeframe
        interpolated_input.interpolate(axis=1, limit_direction="both", inplace=True)
        return interpolated_input

    def _format_inputs(self, input_file: str):
        r"""
        Initialize the model inputs by loading and processing data from an Excel file.

        This method reads an :ref:`Excel file <input>` containing various sheets that correspond to different components
        of the model's input data. It processes each sheet to format and interpolate the data for use in
        simulations, and then saves the processed data in a structured format.

        :param input_file: A string specifying the path to the Excel file relative to the "mater" directory.
                           This file should contain all necessary sheets for the model inputs.
        :type input_file: str

        Procedure
        ---------
        1. **Reading the Excel File:**
           The file is loaded with all sheets being read into a dictionary of DataFrames, where each key
           represents a sheet name corresponding to a specific input.

        2. **Processing Other Inputs:**
           For other sheets, the method sets appropriate indices based on common dimensions found across the
           dataset, performs linear interpolation to fill gaps in the timeline, and extrapolates where necessary
           to cover the entire model timeframe from 1900 to 2100.

        3. **Saving Processed Data:**
           Each processed DataFrame is saved in a Parquet file for efficient storage and retrieval. The files
           are organized by creating directories named after the run and scenario names, and the input type.

        Notes
        -----
        It is essential that the Excel file is correctly formatted with the expected sheets and that directory
        paths for saving outputs are accessible and writable.
        """
        # read the input Excel file
        path = os.path.join(self.input_dir_path, input_file)
        input_dict = pd.read_excel(path, sheet_name=None, skiprows=3)

        # # Access the excel version and the required mater version
        # excel_version = input_dict["Home"].iloc[1, 1]
        # requires_mater = input_dict["Home"].iloc[2, 1][2:]

        # self._check_excel_requirements(input_file, excel_version, requires_mater)

        # remove "Home" sheet to the dictionnary
        del input_dict["Home"]
        # extracting inputs from the Excel file by sheets
        for input in input_dict:
            df = input_dict[input]
            # list of all the possible dimensions of the inputs
            dims_list = list(
                set(df.columns).intersection(
                    [
                        "object",
                        "object_composition",
                        "object_downgrading",
                        "object_Su",
                        "object_efficiency",
                        "location",
                        "location_production",
                        "process",
                        "unit",
                    ]
                )
            )

            df[dims_list] = df[dims_list].astype(str)
            # df["process"] = df["process"].astype(str)

            df.set_index(dims_list, inplace=True)
            # Convert to datetime
            df.columns = pd.to_datetime(df.columns.astype(str), errors="coerce", utc=True)
            # reindex the dataframe with the adequate timeframe if it not a historical data
            if "histo" in input.lower():
                df2 = df.copy()
            else:
                df2 = pd.DataFrame(
                    data=np.nan,
                    index=df.index,
                    columns=pd.date_range(
                        start=self.simulation_start_time - self.offset,
                        end=self.simulation_end_time,
                        freq=self.time_frequency,
                    ),
                )
                df2 = df2.add(df, fill_value=0)  # to do panda.reindex

                # linear interpolation and extrapolation on the full timeframe
                df2.interpolate(axis=1, limit_direction="both", inplace=True)
                df2.columns.name = "time"

                # update inputs dictionnary
                input_dict[input] = df2.droplevel("unit")
        return input_dict

    # @profile
    def _save_inputs(self):
        for input_name, input_value in vars(self.inputs).items():
            if isinstance(input_value, pd.DataFrame) and not input_value.empty:
                try:
                    # Create the folder to store the input
                    output_path = os.path.join(self.output_dir_path, self.run_name, input_name)
                    os.makedirs(output_path, exist_ok=True)

                    # Save the DataFrame to parquet format
                    parquet_file_path = os.path.join(output_path, f"{input_name}.mater")
                    stacked_df = input_value.stack(future_stack=True).to_frame("value")
                    stacked_df.to_parquet(parquet_file_path, engine="pyarrow", compression="snappy")

                except Exception as e:
                    print(f"Error processing {input_name}: {e}")
        # check wether the trade matrix has data. If not, trade = False to skip the trade calculations in the model
        if self.inputs.control_flow_trade.empty:
            self.trade = False
        else:
            self.trade = True

    def infinite_geometric_series(self, A: np.ndarray, diagonal: bool = True):
        """
        Compute the infinite geometric series for a square matrix A.
        That is, return (I - A)^(-1), assuming the series converges.
        This version uses NumPy's optimized linear algebra routines for speed.
        Remove the identity if the diagonal is not wanted in the resulting infinite geometric series calculation.
        """

        n = A.shape[0]

        # Convert A to float64 to handle object dtype issues
        try:
            A_float = A.astype(np.float64)
        except (ValueError, TypeError):
            # If conversion fails, fall back to manual conversion
            A_float = np.array([[float(x) for x in row] for row in A], dtype=np.float64)

        # Create identity matrix and compute (I - A)
        identity = np.eye(n, dtype=np.float64)
        I_minus_A = identity - A_float

        # Check for numerical issues before inversion
        if np.any(np.isnan(I_minus_A)) or np.any(np.isinf(I_minus_A)):
            raise ValueError("Matrix contains NaN or infinity values")

        # Use NumPy's optimized matrix inversion
        try:
            inv_matrix = np.linalg.inv(I_minus_A)
        except np.linalg.LinAlgError as e:
            raise np.linalg.LinAlgError(f"Matrix inversion failed: {e}")

        if not diagonal:
            inv_matrix = inv_matrix - identity

        return inv_matrix

    def _assembly_computation(self):
        def compute_group_geometric_series(group: pd.DataFrame.groupby):
            """ """
            # Pivot the group into a square matrix.

            M = group.pivot(index="object", columns="object_Su", values="value")
            # Compute the infinite geometric series.
            S = self.infinite_geometric_series(M.values)
            return pd.DataFrame(S, index=M.index, columns=M.columns)

        # get the input variable
        df = self.inputs.assembly_stock.reorder_levels(["location", "object", "object_Su"])
        # exctract all the objects to create a square matrix
        labels = list(set(df.index.get_level_values("object_Su")).union(set(df.index.get_level_values("object"))))
        # create the new dataframe with square matrices
        df2 = pd.DataFrame(
            index=pd.MultiIndex.from_product(
                [list(df.index.get_level_values("location").unique()), labels, labels],
                names=list(df.index.names),
            ),
            columns=df.columns,
        )
        # add the values at the right indexes
        df3 = df2.add(df, fill_value=0).stack(future_stack=True).fillna(0).rename("value").reset_index()
        # group the dataframe to apply the square_matrix function
        grouped = df3.groupby(["location", "time"])
        # infinite geometric series for each group
        result = (
            grouped.apply(compute_group_geometric_series)
            .stack(future_stack=True)
            .replace(0, np.nan)
            .dropna()
            .unstack("time")
        )
        self.inputs.assembly_stock = result.copy()

    def _multiply_assembly_stock(self, df: pd.DataFrame | pd.Series, k: pd.DatetimeIndex | None = None):
        """add assembly_stock multiplied by input df (to avoid double counting) that doesn't exist in input df, in the input df.
        If k is specified the operation is done on the specofoc simulation time.
        It handles an empty assembly stock

        :param df: input df
        :type df: pd.DataFrame | pd.Series
        :param k: the current simulation `time`, defaults to None
        :type k: pd.DatetimeIndex | None, optional
        :return: final df
        :rtype: _type_
        """
        if self.inputs.assembly_stock.empty or df.empty:
            return df
        else:
            if k:
                df2 = df.combine_first(
                    self.inputs.assembly_stock[k]
                    .mul(df)
                    .dropna(how="all")
                    .groupby(level=["location", "object_Su"])
                    .sum()
                    .rename_axis(index={"object_Su": "object"})
                )
            else:
                df2 = df.combine_first(
                    self.inputs.assembly_stock.mul(df)
                    .dropna(how="all")
                    .groupby(level=["location", "object_Su"])
                    .sum()
                    .rename_axis(index={"object_Su": "object"})
                )
            return df2

    def _composition_computation(self):
        print("composition_computation ...")

        def compute_group_geometric_series(group: pd.DataFrame.groupby):
            """ """
            # Pivot the group into a square matrix.

            M = group.pivot(index="object", columns="object_composition", values="value")
            filter = M.index[(M == 0).all(axis=1)].tolist()
            # Compute the infinite geometric series.
            S = self.infinite_geometric_series(M.values, diagonal=False)
            # Filter to keep only the (raw) composition and not the indermediate products ex : screw is and intermediate composition as steel is the raw composition
            result_unfiltered = pd.DataFrame(S, index=M.index, columns=M.columns)
            return result_unfiltered.loc[M.index, filter].T

        # get the input variable
        df = self.inputs.object_composition.reorder_levels(["location", "object", "object_composition"])
        # exctract all the objects to create a square matrix
        labels = list(
            set(df.index.get_level_values("object_composition")).union(set(df.index.get_level_values("object")))
        )
        # create the new dataframe with square matrices
        df2 = pd.DataFrame(
            index=pd.MultiIndex.from_product(
                [list(df.index.get_level_values("location").unique()), labels, labels],
                names=list(df.index.names),
            ),
            columns=df.columns,
        )
        # add the values at the right indexes
        df3 = df2.add(df, fill_value=0).stack(future_stack=True).fillna(0).rename("value").reset_index()
        # group the dataframe to apply the square_matrix function
        grouped = df3.groupby(["location", "time"])
        # infinite geometric series for each group
        result = (
            grouped.apply(compute_group_geometric_series)
            .stack(future_stack=True)
            .replace(0, np.nan)
            .dropna()
            .unstack("time")
        )
        self.inputs.object_composition = result.copy()

    def _outputs_initialization(self):
        r"""
        Initialize the dictionaries for storing simulation outputs and set up initial conditions for the simulation model.

        This method prepares initial states and operational structures for the simulation, focusing on key attributes stored in the outputs dictionaries. It processes historical data to set initial conditions for various simulation scenarios.

        Attributes and calculation
        --------------------------
        - `outputs`: Dictionary to store overall outputs of the simulation.
        - `outputs1`: Dictionary to store outputs at the time :math:`k-1`.
        - `Time`: DataFrame to track the simulation time and apply decay functions.

        - **In-use Stock Initialization**:
            Sets up the in-use stock to the historical stock initial value

            .. math::
                S^u_{l,o}(k_0-1,k_0-1) = S^e_{l,o}(k_0-1)
                :label: in_use_stock_init

            Where:

            - :math:`S^u_{l,o}(k_0-1,k_0-1)` is the `in_use_stock` output at `time` :math:`k_0-1` and `age_cohort` :math:`k_0-1`.
            - :math:`S^e_{l,o}(k_0-1)` is the :ref:`exogenous_stock <input>` input at `time` :math:`k_0-1`.
            - :math:`k_0` is the `simulation_start_time` input.
            - indices are the :ref:`variables dimensions <dimensions>`.

        - **Self-disposal flow**:
            Initializes the self-disposal flow at production date :math:`k_0` using the decay function :eq:`exponential_decay` :

            .. math::
                F^d_{l,o,t}(k_0-1) = d^{l,o}_{l,o}[t,L^m_{l,o,t},k_0-1] \, S^u_{l,o}(k_0-1,k_0-1)
                :label: self_disposal_flow_calc

            Where:

            - :math:`F^d_{l,o,t}(k_0-1)` is the `self_disposal_flow` output at `age_cohort` :math:`k_0-1`.
            - :math:`d^e_{l,o}` is the `exponential_decay` function :eq:`exponential_decay`.
            - :math:`S^u_{l,o}(k_0-1,k_0-1)` is the `in_use_stock` output :eq:`in_use_stock_init` at `time` :math:`k_0-1` and `age_cohort` :math:`k_0-1`.
            - :math:`k_0` is the `simulation_start_time` input.
            - :math:`t` is the `Time` input.
            - :math:`L^m_{l,o,t}` is the `lifetime_mean_value` input.
            - indices are the :ref:`variables dimensions <dimensions>`.
        """

        # outputs (dictionnary of all the outputs)
        self.outputs: Dict[str, pd.DataFrame | pd.Series] = {}
        # outputs1 (outputs dictionnary at time k-1)
        #### ToDo: delete outputs1, initialize with outputs instead
        self.outputs1: Dict[str, pd.DataFrame | pd.Series] = {}
        # # reorder levels of self.inputs.exogenous_stock to apply .loc latter in the model
        # self.inputs.exogenous_stock = self.inputs.exogenous_stock.reorder_levels(["location", "object"])
        # keep only the first year of self.inputs.exogenous_stock and self.inputs.init_non_exo_in_use_stock to initialize other outputs
        #### ToDo: self.inputs.init_non_exo_in_use_stock[self.simulation_start_time - self.offset].combine_first(self.inputs.exogenous_stock[self.simulation_start_time - self.offset])
        #### if self.inputs.init_non_exo_in_use_stock exists. Else, self.inputs.exogenous_stock[self.simulation_start_time - self.offset].copy()
        #### but it will only be for the exogenous controlled objects

        # add assembly_stock*exogenous_stock to exogenous_stock to take into account assembly stock, before any operations using exogenous_stock
        self.inputs.exogenous_stock = self._multiply_assembly_stock(self.inputs.exogenous_stock)

        # if empty because of combine_first
        if self.inputs.init_non_exo_in_use_stock.empty:
            df = self.inputs.exogenous_stock[self.simulation_start_time - self.offset].copy()
        else:
            # add assembly_stock*init_non_exo_in_use_stock to init_non_exo_in_use_stock to take into account assembly stock, before any operations using init_non_exo_in_use_stock
            self.inputs.init_non_exo_in_use_stock = self._multiply_assembly_stock(self.inputs.init_non_exo_in_use_stock)
            df = self.inputs.init_non_exo_in_use_stock[self.simulation_start_time - self.offset].combine_first(
                self.inputs.exogenous_stock.reorder_levels(self.inputs.init_non_exo_in_use_stock.index.names)[
                    self.simulation_start_time - self.offset
                ]
            )
        # in-use stock
        self.outputs1["in_use_stock"] = pd.concat(
            [df], keys=[self.simulation_start_time - self.offset], names=["age_cohort"]
        ).replace(0, np.nan)
        # old stock
        self.outputs1["old_stock"] = pd.Series(data=np.nan, index=self.outputs1["in_use_stock"].index)
        # reference_stock
        #### ToDo: default to 0 (or 1 for the fundamental "industry" object or the "nature" object) if self.inputs.init_non_exo_in_use_stock doesn't exist
        #### WARNING: it should be strange for the first simulation iteration but normal for the next ones
        self.outputs1["reference_stock"] = df.copy()
        # control_flow
        self.outputs1["control_flow"] = pd.Series(data=np.nan, index=df.index)
        # self-disposal flow
        # time = pd.date_range(
        #     start=self.simulation_start_time - self.offset, end=self.simulation_end_time, freq=self.time_frequency
        # )
        # self.time = pd.DataFrame(
        #     data=[time] * len(self.inputs.lifetime_mean_value.index),
        #     index=self.inputs.lifetime_mean_value.index,
        #     columns=time,
        # )
        # self.time.columns.name = "time"

        df = _exponential_decay(
            self.inputs.lifetime_mean_value,
            self.simulation_start_time - self.offset,
            self.offset,
        )
        # create the first data in self-disposal flow with in-use stock of simulation start time being exponentially depreciated over the futur times
        self.outputs["self_disposal_flow"] = df.mul(self.outputs1["in_use_stock"], axis=0).dropna(axis=0, how="all")

    def _process_reference_capacity_computation(self):
        r"""
        Compute the reference capacity for processes based on maximum capacity values.

        This method updates the :ref:`process_reference_capacity <input>` by scaling it with the :ref:`process_max_capacity <input>`. It multiplies these values, using a fill value of 1 where data is missing, and drops any rows that result in all NaNs.

        Calculation
        -----------
        .. math::
            c^{\text{ref}}_{l,p,o,t} = c^{\text{refs}}_{l,p,o,t} \odot c^{\text{max}}_{l,p,o,t}
            :label: process_reference_capacity_calc

        Where:

        - :math:`c^{\text{ref}}_{l,p,o,t}` is the `process_reference_capacity` output.
        - :math:`c^{\text{refs}}_{l,p,o,t}` is the :ref:`process_reference_capacity <input>` input. It is a share of the :ref:`process_max_capacity <input>` input.
        - :math:`c^{\text{max}}_{l,p,o,t}` is the :ref:`process_max_capacity <input>` input.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self.process_reference_capacity = self.inputs.process_reference_capacity.mul(
            self.inputs.process_max_capacity, fill_value=1
        ).dropna(axis=0, how="all")

    def _reference_intensity_of_use_coputation(self):
        r"""
        Compute the reference intensity of use for each process.

        This method calculates the `reference_intensity_of_use` :math:`u_{\text{ref}}` by multiplying the process shares by the reference capacities. It then ensures that the resulting DataFrame has no rows filled entirely with NaNs and reorders the DataFrame levels to ["location", "object", "process"] for consistent access and manipulation.

        Calculation
        -----------
        .. math::
            u^{\text{ref}}_{l,p,o,t} = s^p_{l,p,o,t} \odot c^{\text{ref}}_{l,p,o,t}
            :label: ref_intensity_of_use_calc

        Where:

        - :math:`u^{\text{ref}}_{l,p,o,t}` is the `reference_intensity_of_use` output.
        - :math:`s^p_{l,p,o,t}` is the :ref:`process_share <input>` input, representing the distribution of each process across different productive objects.
        - :math:`c^{\text{ref}}_{l,p,o,t}` is the :ref:`process_reference_capacity <input>` input, representing the production capacity of each process.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self.outputs["reference_intensity_of_use"] = self.inputs.process_shares.mul(
            self.process_reference_capacity
        ).dropna(axis=0, how="all")

    def _exogenously_controlled_process_computation(self):
        r"""
        Compute the processes for exogenously controlled objects.

        This method calculates the `exogenously_controlled_process` :math:`P^{\text{exo}}` attribute by multiplying the exogenous stock values by the reference intensity of use, calculated previously in :eq:`ref_intensity_of_use_calc`. The method ensures that the resulting DataFrame is free from rows entirely filled with NaNs and reorders the DataFrame levels to ["location", "object", "process"] for consistent access.

        Calculation
        -----------
        .. math::
            P^{\text{exo}}_{l,p,o,t} = S^{\text{exo}}_{l,p,o,t} \odot u^{\text{ref}}_{l,p,o,t}
            :label: exogenously_controlled_process_calc

        Where:

        - :math:`P^{\text{exo}}_{l,p,o,t}` is the `exogenously_controlled_process` output.
        - :math:`S^{\text{exo}}_{l,p,o,t}` is the :ref:`exogenous_stock <input>` input.
        - :math:`u^{\text{ref}}_{l,p,o,t}` is the `reference_intensity_of_use` output :eq:`ref_intensity_of_use_calc`.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self.exogenously_controlled_process = self.inputs.exogenous_stock.mul(
            self.outputs["reference_intensity_of_use"]
        ).dropna(axis=0, how="all")

    def _control_flow_trade_inverse_computation(self):
        r"""
        Compute the inverse of the control flow trade matrix.

        This method calculates the inverse (pseudoinverse) of the `control_flow_trade` matrix. The inverse is used to model the reverse dynamics of trade flows between production locations over time.

        Calculation
        -----------
        The pseudoinverse of the control flow trade matrix :math:`T^{c^{-1}}` is computed.

        .. math::
            T^{c^{-1}}_{l_p,o,l,t} = \text{pseudoinverse}_{l_p,o,l,t}[T^c_{l,o,l_p,t}]
            :label: trade_inverse_calc

        Where:

        - :math:`T^{c^{-1}}_{l_p,o,l,t}` is the `control_flow_trade_inverse_matrix` output.
        - :math:`T^c_{l,o,l_p,t}` is the :ref:`control_flow_trade <input>` input.
        - :math:`\text{pseudoinverse}_{l_p,o,l,t}` is the :ref:`pseudoinverse function <pseudoinverse_computation>`.
        - indices are the :ref:`variables dimensions <dimensions>`.

        Notes
        -----
        It is assumed that `self.inputs` contains a complete and appropriately structured `control_flow_trade` matrix before this method is called. Missing values or incorrect data structures can affect the accuracy and feasibility of the pseudoinverse computation.
        """
        # the dimension elements of the trade matrix
        location = self.inputs.control_flow_trade.index.get_level_values("location").unique().to_list()
        location_production = (
            self.inputs.control_flow_trade.index.get_level_values("location_production").unique().to_list()
        )
        # start the pseudo inverse computation
        #### ToDo: check wether it works with location and location production being different
        to_inverse = (
            self.inputs.control_flow_trade.unstack("location_production").stack("time", future_stack=True).fillna(0)
        )
        grouped = to_inverse.groupby(level=["object", "time"])
        pseudoinverses = grouped.apply(_compute_pseudoinverse).reset_index()
        # or location
        pseudoinverses["location_production"] = [location_production] * len(pseudoinverses)
        pseudoinverses = pseudoinverses.explode(["location_production", 0])
        # or location_production
        pseudoinverses["location"] = [location] * len(pseudoinverses)
        pseudoinverses = pseudoinverses.explode(["location", 0])
        # apply to_numeric otherwise there is an issue later
        self.control_flow_trade_inverse_matrix = (
            pseudoinverses.set_index(["location_production", "object", "location", "time"])[0]
            .unstack("time")
            .apply(pd.to_numeric, errors="coerce")
        )

    def _lifetime_computation(self):
        r"""
        Compute the log-normal parameters for lifetime data based on the mean values and standard deviations provided.

        This method transforms the raw lifetime mean values and standard deviations into log-normal distribution parameters (logarithmic mean and standard deviation). These parameters are used for probabilistic modeling of lifetime distributions within the system, facilitating more accurate and statistically relevant computations.

        Calculation
        -----------
        1. **Standard Deviation Transformation:**
            The standard deviation input is a share of the lifetime mean value. The first step is to multiply both inputs to calculate the real extensive value of the lifetime standard deviation:

            .. math::
                L^{sd}_{l,o,t} = L^{sds}_{l,o,t} \odot L^m_{l,o,t}
                :label: lifetime_standard_deviation

            Where:

            - :math:`L^{sd}_{l,o,t}` is the `lifetime_standard_deviation` output.
            - :math:`L^{sds}_{l,o,t}` is the :ref:`lifetime_standard_deviation <input>` input.
            - :math:`L^m_{l,o,t}` is the :ref:`lifetime_mean_value <input>` input.
            - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors.
            - indices are the :ref:`variables dimensions <dimensions>`.

        2. **Log-normal Standard Deviation Computation:**
            Calculates the log-normal standard deviation :math:`\sigma`: by applying the following formula:

            .. math::
                \sigma_{l,o,t} = \sqrt{\ln(1+(\frac{L^{sd}_{l,o,t}}{L^m_{l,o,t}})^{2})}
                :label: lifetime_standard_deviation_log

            Where:

            - :math:`\sigma_{l,o,t}` is the `lifetime_standard_deviation_log` output.
            - :math:`L^{sd}_{l,o,t}` is the `lifetime_standard_deviation` output :eq:`lifetime_standard_deviation`.
            - :math:`L^m_{l,o,t}` is the :ref:`lifetime_mean_value <input>` input.
            - indices are the :ref:`variables dimensions <dimensions>`.

        3. **Logarithmic Mean Computation:**
            Computes the log-normal mean value :math:`\mu` :

            .. math::
                \mu_{l,o,t} = \ln(L^m_{l,o,t}) - \frac{1}{2(\sigma_{l,o,t})^{2}}
                :label: lifetime_mean_value_log

            Where :

            - :math:`\mu_{l,o,t}` is the `lifetime_mean_value_log` output.
            - :math:`L^m_{l,o,t}` is the :ref:`lifetime_mean_value <input>` input.
            - :math:`\sigma_{l,o,t}` represents the `lifetime_standard_deviation_log` output :eq:`lifetime_standard_deviation_log`.
            - indices are the :ref:`variables dimensions <dimensions>`.
        """
        lifetime_standard_deviation = self.inputs.lifetime_mean_value.mul(self.inputs.lifetime_standard_deviation)

        self.lifetime_standard_deviation_log = np.sqrt(
            np.log(1 + (lifetime_standard_deviation / self.inputs.lifetime_mean_value) ** 2)
        ).dropna(axis=0, how="all")

        self.lifetime_mean_value_log = (
            np.log(self.inputs.lifetime_mean_value) - 1 / 2 * self.lifetime_standard_deviation_log**2
        ).dropna(axis=0, how="all")
