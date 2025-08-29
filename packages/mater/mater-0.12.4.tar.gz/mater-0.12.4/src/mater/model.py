"""
Model module to create the MATER class.
"""

import logging
from typing import Dict, List, Literal

import numpy as np
import pandas as pd
from data_completion_tool import dct
from tqdm import tqdm

from mater._non_physical import _MaterProcessNonPhysical
from mater._utils import (
    api_session_auth,
    convert_to_datetime,
    extract_variables,
    get_data_from_api,
    input_completion,
    read_json,
)
from mater._variable_classes import Parameter

# from mater.utils import profile


class Mater(_MaterProcessNonPhysical):
    def __init__(self):
        super().__init__()

    def parameter_from_db(
        self,
        username: str,
        password: str,
        run_name: str,
        simulation_start_time: int | str | pd.DatetimeIndex,
        simulation_end_time: int | str | pd.DatetimeIndex,
        time_frequency: str,
        scenario: str,
    ) -> List[Parameter | Dict[str, pd.DataFrame]]:
        """Returns the parameters of the mater compiler and a dictionary with all variables by getting data from the mater database API.

        :param username: The mater database API username
        :type username: str
        :param password: The mater database API password
        :type password: str
        :param run_name: Name of the directory where the results will be stored
        :type run_name: str
        :param simulation_start_time: The simulation initial time
        :type simulation_start_time: int | str | pd.DatetimeIndex
        :param simulation_end_time: The simulation end time
        :type simulation_end_time: int | str | pd.DatetimeIndex
        :param time_frequency: The time step of the simulation from years "YS" to nano seconds "ns". See the Parameter class for more information
        :type time_frequency: str
        :param scenario: The choice in the scenario to chose for future data. "historical" and `nan` scenarios are chosen by default
        :type scenario: str
        :return: The variable Class that aggregate all the parameters needed to run a mater simulation and all variables into a dictionary to perform any pre calculation
        :rtype: List[Parameter | Dict[str, pd.DataFrame]]

        Examples
        --------
        .. code-block:: python

            from mater import Mater

            # instance of Mater class
            model = Mater()
            # define the parameter for the simulation from a data folder at the root
            # Access environment variables

            username = "YOUR_USERNAME"  # mater API username
            password = "YOUR_PASSWORD"  # mater API password
            result = model.parameter_from_db(
                username,
                password,
                "run0",
                1901,
                2100,
                "YS",
                "BAU Scenario",
            )
            # whatever parameter processing here using result[1] dictionary

            # run
            model.run(result[0])
        """
        # api url http://127.0.0.1:8000/inputdatas/?format=json
        API_URL = "http://127.0.0.1:8000"

        ## Authenticate and get session
        session = api_session_auth(API_URL, username, password)

        # Inputs loading
        logging.info("Inputs loading...")

        # set the dimension dataframe
        dimension = read_json("dimension")

        # set the variable_dimension dataframe
        variable_dimension = read_json("variable_dimension")

        # set the input_data dictionary
        if session:
            # Use the session for subsequent API requests
            inputs_data = pd.DataFrame(get_data_from_api(session, API_URL, "inputdatas")).drop(
                ["metadata", "provider"], axis=1
            )

        return self.parameter_from_df(
            run_name,
            simulation_start_time,
            simulation_end_time,
            time_frequency,
            scenario,
            dimension,
            variable_dimension,
            inputs_data,
        )

    def parameter_from_json(
        self,
        run_name: str,
        simulation_start_time: int | str | pd.DatetimeIndex,
        simulation_end_time: int | str | pd.DatetimeIndex,
        time_frequency: str,
        scenario: str,
    ) -> List[Parameter | Dict[str, pd.DataFrame]]:
        """Returns the parameters of the mater compiler and a dictionary with all variables by loading data from the json files ordered in a data directory, as defined by the `mater-data-providing` package.

        :param run_name: Name of the directory where the results will be stored
        :type run_name: str
        :param simulation_start_time: The simulation initial time
        :type simulation_start_time: int | str | pd.DatetimeIndex
        :param simulation_end_time: The simulation end time
        :type simulation_end_time: int | str | pd.DatetimeIndex
        :param time_frequency: The time step of the simulation from years "YS" to nano seconds "ns". See the Parameter class for more information
        :type time_frequency: str
        :param scenario: The choice in the scenario to chose for future data. "historical" and `nan` scenarios are chosen by default
        :type scenario: str
        :return: The variable Class that aggregate all the parameters needed to run a mater simulation and all variables into a dictionary to perform any pre calculation
        :rtype: List[Parameter | Dict[str, pd.DataFrame]]

        Examples
        --------
        .. code-block:: python

            from mater import Mater

            # instance of Mater class
            model = Mater()
            # define the parameter for the simulation from a data folder at the root
            result = model.parameter_from_json(
                "run0", 1900, 2100, "YS", "BAU Scenario"
            )
            # whatever parameter processing here using result[1] dictionary

            # run
            model.run(result[0])
        """
        # Inputs loading
        logging.info("Inputs loading...")

        # set the dimension dataframe
        dimension = read_json("dimension")

        # complete and format the inputs
        inputs_data = read_json("input_data")

        variable_dimension = read_json("variable_dimension")

        return self.parameter_from_df(
            run_name,
            simulation_start_time,
            simulation_end_time,
            time_frequency,
            scenario,
            dimension,
            variable_dimension,
            inputs_data,
        )

    def parameter_from_df(
        self,
        run_name: str,
        simulation_start_time: int | str | pd.DatetimeIndex,
        simulation_end_time: int | str | pd.DatetimeIndex,
        time_frequency: str,
        scenario: str,
        dimension: pd.DataFrame,
        variable_dimension: pd.DataFrame,
        inputs_data: pd.DataFrame,
    ) -> List[Parameter | Dict[str, pd.DataFrame]]:
        """Returns the parameters of the mater compiler and a dictionary with all variables by loading data from the input_data, dimension and variable_dimension dataframes.

        :param run_name: Name of the directory where the results will be stored
        :type run_name: str
        :param simulation_start_time: The simulation initial time
        :type simulation_start_time: int | str | pd.DatetimeIndex
        :param simulation_end_time: The simulation end time
        :type simulation_end_time: int | str | pd.DatetimeIndex
        :param time_frequency: The time step of the simulation from years "YS" to nano seconds "ns". See the Parameter class for more information
        :type time_frequency: str
        :param scenario: The choice in the scenario to chose for future data. "historical" and `nan` scenarios are chosen by default
        :type scenario: str
        :param dimension: The dimension dataframe with hierarchies and equivalences
        :type dimension: pd.DataFrame
        :param variable_dimension: The variable_dimension dataframe with dimension lists and properties per variable
        :type variable_dimension: pd.DataFrame
        :param inputs_data: The dataframe with all the mater variable values
        :type inputs_data: pd.DataFrame
        :return: The variable Class that aggregate all the parameters needed to run a mater simulation and all variables into a dictionary to perform any pre calculation
        :rtype: List[Parameter | Dict[str, pd.DataFrame]]
        """
        self.set_time(simulation_start_time, simulation_end_time, time_frequency)
        inputs_dict = extract_variables(inputs_data, scenario)
        input_dict = {}
        ds = dct.DataSet()
        if "parents_values" in dimension.columns:
            dimension["parents_values"] = dimension["parents_values"].apply(
                lambda x: x.get("default") if isinstance(x, dict) and "default" in x else np.nan
            )
            ds.set_dimension(dimension)
            for input_name, input in inputs_dict.items():
                completed_input = input_completion(input_name, input, ds, variable_dimension)
                input_dict[input_name] = self.input_formatting(completed_input)
        else:
            for input_name, input in inputs_dict.items():
                input.rename({"date": "time"}, axis=1, inplace=True)  # For now it is "time" everywhere
                input["time"] = convert_to_datetime(input["time"])
                #### WARNING if the conversion is not possible it returns NaT.
                input = input.dropna()
                ds._set_indexes(input)
                input_dict[input_name] = self.input_formatting(input)
        # keep only keys that are in Parameter dataclass
        keys = np.intersect1d(list(input_dict.keys()), list(Parameter.__annotations__.keys()))
        param_dict = {var: input_dict[var] for var in keys}
        params = Parameter(
            simulation_end_time=self.simulation_end_time,
            simulation_start_time=self.simulation_start_time,
            time_frequency=time_frequency,
            run_name=run_name,
            **param_dict,
        )
        params.set_default()
        return [params, input_dict]

    def run_from_excel(
        self,
        run_name: str,
        input_file: str,
        simulation_start_time: int | str | pd.DatetimeIndex,
        simulation_end_time: int | str | pd.DatetimeIndex,
        time_frequency: str,
    ):
        """Execute a simulation of the MATER model from `simulation_start_time` to `simulation_end_time` using the input from the Excel `input_file`.

        The variable outputs are stored in a `run_name` directory in folders containing `Parquet <https://parquet.apache.org/docs/overview/>`_ files.

        :param run_name: Name of the directory where the results will be stored
        :type run_name: str
        :param input_file: Input excel file path starting from the root directory
        :type input_file: str
        :param simulation_start_time: The simulation initial time
        :type simulation_start_time: int | str | pd.DatetimeIndex
        :param simulation_end_time: The simulation end time
        :type simulation_end_time: int | str | pd.DatetimeIndex
        :param time_frequency: The time step of the simulation from years "YS" to nano seconds "ns". See the Parameter class for more information
        :type time_frequency: str
        """
        # Inputs loading

        logging.info("Inputs loading...")
        self.set_time(simulation_start_time, simulation_end_time, time_frequency)
        input_dict = self._format_inputs(input_file)
        params = Parameter(
            simulation_end_time=self.simulation_end_time,
            simulation_start_time=self.simulation_start_time,
            time_frequency=time_frequency,
            run_name=run_name,
            **input_dict,
        )
        self.run(params)

    # @profile
    def run(self, params: Parameter):
        """Simulate the MATER model.

        :param params: The Parameter dataclass stores all the inputs and parameters needed to simulate the MATER model
        :type params: Parameter
        """
        # Run parameters setup

        self.set_time(
            params.simulation_start_time,
            params.simulation_end_time,
            params.time_frequency,
        )
        self.run_name = params.run_name
        self.inputs = params

        self._save_inputs()

        # Model simulation

        logging.info("Model simulation...")
        self._outputs_setup()
        ### ToDo : change to support datetime format
        date_range = pd.date_range(
            start=self.simulation_start_time,
            end=self.simulation_end_time,
            freq=self.time_frequency,
        )
        with tqdm(date_range, desc="Simulating time steps") as pbar:
            for k in pbar:
                pbar.set_description(str(k))
                self._self_disposal_recycling_control_flows_computation(k)
                self._processes_computation(k)
                self._extraneous_flows_computation(k)
                self._objects_computation(k)
                self._outputs_update(k)
                self._outputs_save(k)
            pbar.close()

    # Sub-methods of the run method

    def _outputs_setup(self):
        r"""
        Set up and initialize all necessary outputs for the MATER simulation model.

        This method orchestrates the initialization and configuration of various model outputs and parameters that can be computed outside the for loop for performance issues.
        It skips the `control_flow_trade_inverse` computation if the trade matrix input is empty.

        Summary of Operations
        ---------------------
        - :meth:`_outputs_initialization`: Prepares the outputs dictionary and sets initial conditions based on historical data. This involves initializing dictionaries to store simulation results across different time steps.
        - :meth:`_lifetime_computation`: Transforms raw lifetime data into log-normal distribution parameters suitable for the modeling of lifetime distributions for the objects.
        - :meth:`_process_reference_capacity_computation`: Calculates reference capacities of process by objects based on their maximum capacities, adjusting for data availability.
        - :meth:`_reference_intensity_of_use_coputation`: Calculates the reference intensity of use of each object per time period.
        - :meth:`_exogenously_controlled_process_computation`: Calculates the reference processes of the exogenously controlled objects such as cars or residential buildings.
        - :meth:`_control_flow_trade_inverse_computation`: Computes the inverse of the control flow trade matrix.
        """
        if not self.inputs.assembly_stock.empty:
            self._assembly_computation()
        if not self.inputs.object_composition.empty:
            self._composition_computation()
        self._outputs_initialization()
        self._lifetime_computation()
        self._process_reference_capacity_computation()
        self._reference_intensity_of_use_coputation()
        self._exogenously_controlled_process_computation()
        # skip trade calculation if the trade matrix is empty
        if self.trade:
            self._control_flow_trade_inverse_computation()

    # @profile
    def _self_disposal_recycling_control_flows_computation(self, k: int):
        r"""
        Manage the computation of self-disposal, recycling, and control flows at a specific simulation time point :math:`k`.

        First the self-disposal flow is calculated as a log-normal delay of the control flow. The recycling flow is a share of the self-disposal flow, the control flow is calculated as the state feedback command to track the reference in stock.
        Finally these control flows are spread between location for production.

        :param k: the current simulation `time`
        :type k: int

        Operations Summary
        ------------------
        - :meth:`_log_normal_distribution_computation`: Initializes the calculation of log-normal distribution parameters, which are essential for modeling variable lifetime distributions.
        - :meth:`_self_disposal_flow_computation`: Utilizes the log-normal distributions to estimate the rate of cohort arriving at their end of life.
        - :meth:`_recycling_flow_computation`: Calculates how much of the disposed material is successfully recycled, based on current collection rates and the efficiency of recycling processes.
        - :meth:`_control_flow_computation`: Adjusts resource usage and disposal based on predefined control strategies aimed at achieving stock targets.
        - :meth:`_traded_control_flow_computation`: Modifies control flows to account for trade and exchange of resources between different production locations, ensuring the model captures economic interactions and dependencies.
        """
        self._log_normal_distribution_computation(k)
        self._self_disposal_flow_computation(k)
        self._recycling_flow_computation(k)
        self._control_flow_computation(k)
        self._traded_control_flow_computation(k)

    def _processes_computation(self, k: int):
        r"""
        Coordinate the computation of various types of processes within the MATER model at a specific time point :math:`k`.

        This method orchestrates the calculation of endogenously controlled, controlled, free, and total processes to accurately simulate the interactions and dependencies within the model's ecosystem. These calculations reflect both internally controlled adjustments and naturally occurring flows.

        :param k: the current simulation `time`
        :type k: int

        Operations Summary
        ------------------
        - :meth:`_endogenously_controlled_process_computation`: Determines the processes influenced by internal management strategies that account for traded control flows and recycling outputs.
        - :meth:`_controlled_process_computation`: Integrates both endogenously controlled processes and exogenous interventions, providing a holistic view of controlled environmental impacts.
        - :meth:`_free_process_computation`: Computes the unmanaged or free-flowing processes driven by previous time stock levels and current usage intensities.
        - :meth:`_process_computation`: Aggregates controlled and free processes to generate a comprehensive output that reflects total system flows.

        Key Calculations
        ----------------
        The model uses the following formula to aggregate these computations:

        .. math::
            P_{l,p}(k) = \sum_{o}[(P^{endo}_{l,o,p}(k) + P^{exo}_{l,o,p}(k)) + P^{free}_{l,o,p}(k)]
            :label: total_process_aggregation

        Where:

        - :math:`P_{l,p}(k)` represents the total processes.
        - :math:`P^{endo}_{l,o,p}(k)` and :math:`P^{exo}_{l,o,p}(k)` are outputs from endogenously and exogenously controlled processes respectively.
        - :math:`P^{free}_{l,o,p}(k)` denotes the contribution from free processes.
        - indices are the :ref:`variables dimensions <dimensions>`.

        Notes
        -----
        This method relies on accurate data from both control and free flow processes. Errors in upstream data can significantly impact the reliability and accuracy of the model's outputs. Additionally, this method integrates several complex calculations, each requiring careful consideration of temporal dynamics and operational scales.
        """
        self._endogenously_controlled_process_computation(k)
        self._controlled_process_computation(k)
        self._free_process_computation(k)
        self._process_computation(k)

    # @profile
    def _extraneous_flows_computation(self, k: int):
        r"""
        Compute and integrate various flows contributing to extraneous system outputs at a specific time point :math:`k`.

        This method coordinates the computation of control flow compositions, secondary production flows, thermodynamic process flows, and extraneous flows. These components reflect complex interactions and efficiency considerations within the model's production systems, emphasizing how controlled, recycled, and thermodynamic processes impact the overall system efficiency and output.

        :param k: the current simulation `time`
        :type k: int

        Overview of Operations
        ----------------------
        - :meth:`_control_flow_composition_computation`: Determines the distribution of control flows across objects, adjusted for trade and object compositions.
        - :meth:`_secondary_production_flow_computation`: Calculates the contributions of recycled materials to secondary production, integrating object composition impacts.
        - :meth:`_thermodynamic_process_flow_computation`: Assesses energy and material flows within the system's processes, adjusting for both control and secondary production influences.
        - :meth:`_extraneous_flow_computation`: Enhances the system's output calculations by integrating object-specific efficiencies with thermodynamic flows.

        Key Formulas and Concepts
        -------------------------
        The method integrates these computations to assess the overall extraneous flows through a series of matrix operations, which balance production dynamics against recycling and control strategies. The primary equation used to aggregate these flows is:

        .. math::
            F^e_{l}(k) = F^{thP}_{l}(k) + \sum_{o_s}[E^{eff}_{l,o_s}(k) \odot F^{thP}_{l,o_s}(k)]
            :label: extraneous_flow_aggregation

        Where:

        - :math:`F^e_{l}(k)` represents the total extraneous flows at time `k`.
        - :math:`F^{thP}_{l}(k)` is the aggregated thermodynamic process flows.
        - :math:`E^{eff}_{l,o_s}(k)` and :math:`F^{thP}_{l,o_s}(k)` are the efficiency and thermodynamic flows adjusted for specific objects and scenarios, illustrating how efficiencies modulate the system's outputs.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self._control_flow_composition_computation(k)
        self._secondary_production_flow_computation(k)
        self._thermodynamic_process_flow_computation(k)
        self._extraneous_flow_computation(k)

    def _objects_computation(self, k: int):
        r"""
        Calculate the object stock dynamics within the MATER model at a specific time point :math:`k`.

        This method manages the computation of three core stock types within the system: reference, old, and in-use stocks. These calculations are pivotal for maintaining accurate material flow accounts and ensuring the integrity of the model's state at each simulation step.

        :param k: the current simulation `time`
        :type k: int

        Overview of Operations
        ----------------------
        - :meth:`_reference_stock_computation`: Computes the reference stocks for endogenously controlled objects based on their controlled processes and usage intensities.
        - :meth:`_old_stock_computation`: Adjusts old stocks by considering the material that has either been disposed of or recycled.
        - :meth:`_in_use_stock_computation`: Updates in-use stocks by integrating net changes due to control flows, extraneous influences, and self-disposal.
        """
        self._reference_stock_computation(k)
        self._old_stock_computation(k)
        self._in_use_stock_computation(k)

    def set_time(
        self,
        simulation_start_time: int | str | pd.DatetimeIndex,
        simulation_end_time: int | str | pd.DatetimeIndex,
        time_frequency: Literal["YS", "QS", "MS", "W", "D", "h", "min", "s", "ms", "us", "ns"],
    ):
        """Set the three time attributes as datetime format

        :param simulation_start_time: First date of the simulation
        :type simulation_start_time: int, str or DatetimeIndex
        :param simulation_end_time: Last date of the simulation
        :type simulation_end_time: int, str or DatetimeIndex
        :param time_frequency: The time step of the simulation
        :type time_frequency: str
        :raises ValueError: Wrong value for time_frequency
        """
        # Ensure conversion to datetime
        self.time_frequency = time_frequency
        self.simulation_start_time = pd.to_datetime(str(simulation_start_time), utc=True)
        self.simulation_end_time = pd.to_datetime(str(simulation_end_time), utc=True)
        # Determine the proper offset based on the time frequency to ajust the starting time
        if time_frequency == "YS":
            self.offset = pd.DateOffset(years=1)
        elif time_frequency == "QS":
            self.offset = pd.DateOffset(quarters=1)
        elif time_frequency == "MS":
            self.offset = pd.DateOffset(months=1)
        elif time_frequency == "W":
            self.offset = pd.DateOffset(weeks=1)
        elif time_frequency == "D":
            self.offset = pd.DateOffset(days=1)
        elif time_frequency in {"h", "min", "s", "ms", "us", "ns"}:
            self.offset = pd.Timedelta(1, unit=time_frequency)
        else:
            raise ValueError(
                f"""Unsupported time frequency: {time_frequency}. It must be "YS", "QS", "MS", "W", "D", "h", "min", "s", "ms", "us" or "ns" """
            )
