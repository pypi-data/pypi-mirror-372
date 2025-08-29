"""
This module is a coupling iris model.
"""

import numpy as np
import pandas as pd

from mater._pre_processing import _MaterPreProcess
from mater._utils import _groupby_sum_empty, _log_normal

pd.set_option("future.no_silent_downcasting", True)


class _MaterProcessBioPhysical(_MaterPreProcess):
    def __init__(self):
        super().__init__()

    def _log_normal_distribution_computation(self, k):
        r"""
        Compute the log-normal distribution for lifetime data based on mean and standard deviation.

        This method calculates the log-normal distribution using specified lifetime mean values, standard deviations, and a shift index. It's primarily used for modeling the distribution of lifetimes that are not constant but follow a log-normal distribution due to variability in the data.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The log-normal distribution is computed as:

        .. math::
            L_{l,o,t} = d^{log}_{l,o,t}[t,\mu_{l,o,t},\sigma_{l,o,t},k-1]
            :label: log_normal_calc

        Where:

        - :math:`L_{l,o,t}` is the log-normal distribution.
        - :math:`d^{log}_{l,o,t}` is the probability density function for a log-normal distribution :eq:`probability_density_function`.
        - :math:`t` is the `Time` input, representing the times at which the distribution is evaluated.
        - :math:`\mu_{l,o,t}` is the `lifetime_mean_value_log` ouput :eq:`lifetime_mean_value_log`.
        - :math:`\sigma_{l,o,t}` is the `lifetime_standard_deviation_log` output :eq:`lifetime_standard_deviation_log`.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self.df_log_normal = _log_normal(
            self.lifetime_mean_value_log, self.lifetime_standard_deviation_log, k - self.offset, self.offset
        )  # For now it only allows to have life time in time. Add the feature to have life time in usage (a bit like on branch "dev" but with the actual usage (process) per time)

    # @profile
    def _self_disposal_flow_computation(self, k: int):
        r"""
        Compute and update the self-disposal flow for products based on their production dates and control flow.

        This method integrates the log-normal distribution computed by the log-normal distribution computation method with the control flow to determine the self-disposal flow at each production date.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The self-disposal flow distribution is calculated by multiplying the log-normal distribution with the control flow. The production date is then equal to the control flow last time. The calculation proceeds as follows:

        .. math::
            F^d_{l,o,t}(k-1) = L_{l,o,t} \odot F^c_{l,o}(k-1)
            :label: self_disposal_flow_calc

        Where:

        - :math:`F^d_{l,o,t}(k-1)` represents the `self_disposal_flow` for `age_cohort` :math:`k-1`.
        - :math:`L_{l,o,t}` is the log-normal distribution output :eq:`log_normal_calc`, reflecting variability in cohort lifetimes.
        - :math:`F^c_{l,o}(k-1)` is the `control_flow` output :eq:`control_flow_calc` at `time` :math:`k-1`.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors. In the case where the dimensions of both matrices or vectors are different, the missing dimensions are added with replicate values before performing the product.
        - indices are the :ref:`variables dimensions <dimensions>`.

        Notes
        -----
        The operation is computationally intensive and may require optimization if performance issues are encountered.
        """
        # self-disposal flow distribution

        self_disposal_flow_distribution = pd.concat(
            [
                self.df_log_normal.mul(self.outputs1["control_flow"], axis=0).dropna(axis=0, how="all")
            ],  # .dropna(axis=0, how="all")
            keys=[k - self.offset],
            names=["age_cohort"],
        )
        # self-disposal flow per production date
        self.outputs["self_disposal_flow"] = self.outputs["self_disposal_flow"].add(
            self_disposal_flow_distribution, fill_value=0
        )  # Takes a lot of time when profiling...

    def _traded_control_flow_computation(self, k: int):
        r"""
        Compute the traded control flow based on the control flow and trade data at a specific time point :math:`k`.

        This method calculates the traded control flow by modifying the existing control flows based on trading ratios defined for each production location and object at the given time. The calculation directly multiplies the control flow vector by the control flow trade matrix to reflect the effective redistribution of production efforts across locations.
        The traded control flow is equal to the control flow if the trade matrix input is empty.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The traded control flow is computed as:

        .. math::
            F^{c^T}_{l_p,o}(k) = F^c_{l,o}(k) \, T^c_{l,o,l_p}(k) \ (= \sum_{l}F^c_{l,o}(k) \, T^c_{l,o,l_p}(k) \ \text{a matrix product})
            :label: traded_control_flow_computation

        Where:

        - :math:`F^{c^T}_{l_p,o}(k)` is the `control_flow_trade` output at `time` :math:`k`.
        - :math:`F^c_{l,o}(k)` represents the `control_flow` output :eq:`control_flow_calc` at `time` :math:`k`.
        - :math:`T^c_{l,o,l_p}(k)` is the :ref:`control_flow_trade <input>` input at `time` :math:`k`.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        if self.trade:
            traded_control_flow = (
                self.outputs["control_flow"]
                .mul(self.inputs.control_flow_trade[k])
                .dropna(axis=0, how="all")
                .groupby(level=["location_production", "object"])
                .sum()
                .rename_axis(index={"location_production": "location"})
            )
            self.outputs["traded_control_flow"] = (
                self.outputs["control_flow"]
                .mul(traded_control_flow, fill_value=1)
                .div(traded_control_flow.replace(0, np.nan), fill_value=1)
            )
            # Use combine_first instead of loc[df.index] = df
            self.outputs["traded_control_flow"] = traded_control_flow.reorder_levels(
                self.outputs["traded_control_flow"].index.names
            ).combine_first(self.outputs["traded_control_flow"])
        else:
            self.outputs["traded_control_flow"] = self.outputs["control_flow"].copy()

    def _endogenously_controlled_process_computation(self, k: int):
        r"""
        Compute the endogenously controlled processes based on adjusted traded control flow and recycled flow contributions at time point :math:`k`.

        This method calculates the controlled object processes by allocating the traded controled flow and recycling flow productions between the different processes.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The endogenously controlled reference process :math:`P^{endo}_k` is computed as follows:

        .. math::
            P^{endo^{ref}}_{l,p}(k) = \sum_{o}[F^{c^T}_{l,o}(k) \, s^c_{l,o,p}(k) + \sum_{o}[F^r_{l,o,c}(k)] \, s^r_{l,o,p}(k)]
            :label: endo_control_ref_process

        Where:

        - :math:`P^{endo^{ref}}_{l,p}(k)` is the `endogenously_controlled_reference_process` output at `time` :math:`k`.
        - :math:`F^{c^T}_{l,o}(k)` is the `traded_control_flow` output :eq:`traded_control_flow_computation` at `time` :math:`k`.
        - :math:`s^c_{l,o,p}(k)` is the :ref:`control_flow_shares <input>` input at `time` :math:`k`.
        - :math:`F^r_{l,o,c}(k)` represents the `recycling_flow` output :eq:`recycling_flow_calc` at `time` :math:`k`.
        - :math:`s^r_{l,o,p}(k)` is the :ref:`recycling_flow_shares <input>` input at `time` :math:`k`.
        - indices are the :ref:`variables dimensions <dimensions>`.

        Subsequently, the computed reference process is copied to the model's operational process:

        .. math::
            P^{endo}_{l,p}(k) = P^{endo^{ref}}_{l,p}(k)
            :label: endo_controlled_process

        Where:

        - :math:`P^{endo}_{l,p}(k)` is the `endogenously_controlled_process` output at `time` :math:`k`.
        - :math:`P^{endo^{ref}}_{l,p}(k)` is the `endogenously_controlled_reference_process` output :eq:`endo_control_ref_process` at `time` :math:`k`.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        #### WARNING: very important not to dropna before groupby !!!
        #### Otherwise, the free_process will be accounted for non free object in the _process_computation
        #### And the model will diverge
        # If both inputs are empty, return a empty Series with the right multiindex
        if self.inputs.control_flow_shares[k].empty and self.inputs.recycling_flow_shares[k].empty:
            self.endogenously_controlled_reference_process = (
                self.inputs.control_flow_shares[k].groupby(level=["location", "process"]).sum()
            )
        # If control flow process shares is empty, return only the recycling process
        elif self.inputs.control_flow_shares[k].empty:
            self.endogenously_controlled_reference_process = (
                (self.outputs["recycling_flow"].groupby(level=["location", "object"]).sum())
                .mul(self.inputs.recycling_flow_shares[k])
                .groupby(level=["location", "process"])
                .sum()
            )
        # If recycling process shares is empty, return only the control flow process
        elif self.inputs.recycling_flow_shares[k].empty:
            self.endogenously_controlled_reference_process = (
                (self.outputs["traded_control_flow"].mul(self.inputs.control_flow_shares[k]))
                .groupby(level=["location", "process"])
                .sum()
            )
        # If both are not empty, return the merge of both, privileging the control flow process
        else:
            self.endogenously_controlled_reference_process = (
                (
                    (self.outputs["traded_control_flow"].mul(self.inputs.control_flow_shares[k])).combine_first(
                        (self.outputs["recycling_flow"].groupby(level=["location", "object"]).sum()).mul(
                            self.inputs.recycling_flow_shares[k]
                        )
                    )
                )
                .groupby(level=["location", "process"])
                .sum()
            )
        # distinction between endogenously_controlled_reference_process and endogenously_controlled_reference_process
        # useful when introducing the possibility to saturate endogenously_controlled_process
        # for now they are always equal
        self.endogenously_controlled_process = self.endogenously_controlled_reference_process.copy()

    def _controlled_process_computation(self, k: int):
        r"""
        Compute the total controlled object processes at a specific time point :math:`k` by integrating both endogenous and exogenous control processes.

        This method combines the endogenously controlled processes with exogenously controlled processes, each adjusted by respective process shares, to compute a comprehensive controlled process.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The controlled process is computed as follows:

        .. math::
            P^c_{l,o,p}(k) = P^{endo}_{l,p}(k) \odot s^p_{l,o,p}(k) + P^{exo}_{l,o,p}(k)
            :label: controlled_process_computation

        Where:

        - :math:`P^c_{l,o,p}(k)` is the `controlled_process` output at `time` :math:`k`.
        - :math:`P^{endo}_{l,p}(k)` is the `endogenously_controlled_process` output :eq:`endo_controlled_process` at `time` :math:`k`.
        - :math:`s^p_{l,o,p}(k)` is the :ref:`process_shares <input>` input at `time` :math:`k`.
        - :math:`P^{exo}_{l,o,p}(k)` is the `exogenously_controlled_process` output :eq:`exogenously_controlled_process_calc` at `time` :math:`k`.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors. In the case where the dimensions of both matrices or vectors are different, the missing dimensions are added with replicate values before performing the product.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        # why multiply by process_shares ? fill_value=1 to accept process without a industry (nan in object aspect) to make it
        if self.exogenously_controlled_process[k].empty:
            self.controlled_process = self.endogenously_controlled_process.mul(
                self.inputs.process_shares[k], fill_value=1
            )
        else:
            process = self.endogenously_controlled_process.mul(self.inputs.process_shares[k])
            self.controlled_process = (
                process.reorder_levels(self.exogenously_controlled_process.index.names)
            ).combine_first(self.exogenously_controlled_process[k])

    def _free_process_computation(self, k: int):
        r"""
        Compute the free processes based on in-use stock and reference intensity of use at a specific time point :math:`k-1`.

        This method calculates the free processes for objects designated as "free" or "flow-driven" by multiplying their in-use stock values at :math:`k-1` by the corresponding reference intensity of use values.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The free process is computed as follows:

        .. math::
            P^f_{l,o,p}(k) = \sum_{d}[S^u_{l,o,c}(k-1)] \odot u^{\text{ref}}_{l,o,p}(k-1)
            :label: free_process_computation

        Where:

        - :math:`P^f_{l,o,p}(k)` represents the `free_process` output for "free" `objects` at `time` :math:`k`.
        - :math:`S^u_{l,o,c}(k-1)` represents the `in_use_stock` output :eq:`in_use_stock_computation` for "free" `objects` at `time` :math:`k-1`.
        - :math:`u^{\text{ref}}_{l,o,p}(k-1)` corresponds to `reference_intensity_of_use` output :eq:`ref_intensity_of_use_calc` for "free" `objects` at `time` :math:`k-1`.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors. In the case where the dimensions of both matrices or vectors are different, the missing dimensions are added with replicate values before performing the product.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        # object free processes at k-1.
        #### WARNING: Now the free_process is way to wide in term of perimeter but is added to process with combine_first so it is ok
        self.free_process = _groupby_sum_empty(
            self.outputs["reference_intensity_of_use"][k - self.offset].mul(
                self.outputs1["in_use_stock"].apply(pd.to_numeric, errors="coerce")
            ),
            ["location", "object", "process"],
        )

    # @profile
    def _process_computation(self, k: int):
        r"""
        Aggregate and compute the total processes at time point :math:`k` by summing controlled and free process contributions.

        This method finalizes the process output by adding together the controlled and free processes calculated in prior steps. This aggregation results in a comprehensive process output that reflects all controlled and naturally occurring flows within the system at time :math:`k`.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The total process output is computed as follows:

        .. math::
            P^{\text{des}}_{l,o,p}(k) = P^c_{l,o,p}(k) + P^f_{l,o,p}(k)
            :label: total_desagregated_process_computation

        Where:

        - :math:`P^{\text{des}}_{l,o,p}(k)` is the desagragated `process` output at `time` :math:`k`.
        - :math:`P^c_{l,o,p}(k)` is the `controlled_process` output :eq:`controlled_process_computation` for "controlled" `objects` at `time` :math:`k`.
        - :math:`P^f_{l,o,p}(k)` represents the `free_process` output :eq:`free_process_computation` for "free" `objects` at `time` :math:`k`.
        - indices are the :ref:`variables dimensions <dimensions>`.

        After computing the total processes, the results are further aggregated across 'location' and 'process' dimensions.

        .. math::
            P_{l,p}(k) = \sum_{o}P^{\text{des}}_{l,o,p}(k)
            :label: total_process_computation

        Where:

        - :math:`P_{l,p}(k)` is the `process` output at `time` :math:`k`.
        - :math:`P^{\text{des}}_{l,o,p}(k)` is the desagragated `process` output :eq:`total_desagregated_process_computation` at `time` :math:`k`.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        # combine first needed to not take into account the to wide perimeter of free_process
        # if statement to handle empty dataframe with combine
        if self.controlled_process.empty and self.free_process.empty:
            self.outputs["process"] = self.controlled_process.copy()
        elif self.controlled_process.empty:
            self.outputs["process"] = self.free_process.copy()
        elif self.free_process.empty:
            self.outputs["process"] = self.controlled_process.copy()
        else:
            self.outputs["process"] = self.controlled_process.combine_first(
                self.free_process.reorder_levels(list(self.controlled_process.index.names))
            )
        self.process = self.outputs["process"].groupby(level=["location", "process"]).sum()

    def _control_flow_composition_computation(self, k: int):
        r"""
        Compute the object composition of control flows at time point :math:`k`.

        This method calculates the control flow composition by taking into account the trades between locations. Indeed, the object composition can be different from a location to another. One location produces an object with the desired composition of the importing location.
        It skips the flows with trade material intensity computation if the trade matrix input is empty.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The control flow composition taking into account the trades is computed using the following equation:

        .. math::
            F^{c^{comp}}_{l_p,p,o_c}(k) = \sum_{o}[\sum_{l}[s^c_{l_p,o,p}(k) \odot T^{c^{-1}}_{l_p,o,l}(k) \odot E^{comp}_{l,o,o_c}(k) \odot P_{l_p,p}(k)]]
            :label: control_flow_composition

        Where:

        - :math:`F^{c^{comp}}_{l_p,p,o_c}(k)` is the `control_flow_composition` output at `time` :math:`k`.
        - :math:`s^c_{l_p,o,p}(k)` represents the :ref:`control_flow_shares <input>` input at `time` :math:`k`.
        - :math:`T^{c^{-1}}_{l_p,o,l}(k)` is the `control_flow_trade_inverse_matrix` output :eq:`trade_inverse_calc` at `time` :math:`k`.
        - :math:`E^{comp}_{l,o,o_c}(k)` is the :ref:`object_composition <input>` input at `time` :math:`k`.
        - :math:`P_{l_p,p}(k)` is the `process` output :eq:`total_process_computation` at `time` :math:`k`.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors. In the case where the dimensions of both matrices or vectors are different, the missing dimensions are added with replicate values before performing the product.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        # flows without trade computation
        self.outputs["main_object_composition"] = _groupby_sum_empty(
            (self.inputs.control_flow_shares[k].mul(self.inputs.object_composition[k]).mul(self.process)).dropna(
                axis=0, how="all"
            ),
            ["location", "process", "object_composition"],
        ).rename_axis(index={"object_composition": "object"})

        # flows with trade computation
        if self.trade:
            main_object_demand_composition = (
                self.inputs.control_flow_shares[k]
                .rename_axis(index={"location": "location_production"})
                .mul(self.control_flow_trade_inverse_matrix[k])
                .mul(self.inputs.object_composition[k])
                .mul(self.process.rename_axis(index={"location": "location_production"}))
                .dropna(axis=0, how="all")
                .groupby(level=["location_production", "process", "object_composition"])
                .sum()
                .rename_axis(
                    index={
                        "location_production": "location",
                        "object_composition": "object",
                    }
                )
            )
            self.outputs["main_object_composition"] = (
                self.outputs["main_object_composition"]
                .mul(main_object_demand_composition, fill_value=1)
                .div(main_object_demand_composition, fill_value=1)
            )  # only needed if the the control flow trade matrix is not complete.
            self.outputs["main_object_composition"] = main_object_demand_composition.combine_first(
                self.outputs["main_object_composition"]
            )
            # only needed if the the control flow trade matrix is not complete.

    def _secondary_production_flow_computation(self, k: int):
        r"""
        Compute the secondary production flows at a specific time point :math:`k` based on recycling flows and object compositions.

        This method calculates the contribution of recycled materials to secondary production, factoring in the composition of recycled objects and the specific shares of recycling flows. It integrates these factors to assess how effectively recycled materials are transformed back into the production cycle.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The object composition ratio :math:`R_{comp}` is calculated by:

        .. math::
            R^{comp}_{l,o,o_c}(k) = \frac{\sum_{d}[F^r_{l,o,c}(k) \odot E^{comp}_{l,o,o_c,c}]}{\sum_{d}[F^r_{l,o,c}(k)]}
            :label: recycling_composition

        Where:

        - :math:`R^{comp}_{l,o,o_c}(k)` is the `recycling_composition` output at `time` :math:`k`.
        - :math:`F^r_{l,o,c}(k)` represents the `recycling_flow` output :eq:`recycling_flow_calc` at `time` :math:`k`.
        - :math:`E^{comp}_{l,o,o_c,c}` is the :ref:`object_composition <input>` input with the `time` dimension :math:`t` renamed in the `age_cohort` dimension :math:`c`.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors. In the case where the dimensions of both matrices or vectors are different, the missing dimensions are added with replicate values before performing the product.
        - indices are the :ref:`variables dimensions <dimensions>`.

        The secondary production flow is then computed as follows:

        .. math::
            F^{r^{comp}}_{l,p,o_d}(k) = \sum_{o_c}[\sum_{o}[s^r_{l,o,p}(k) \odot R^{comp}_{l,o,o_c}(k) \odot P_{l,p}(k)] \odot r_{l,o_c,o_d}(k)]
            :label: secondary_production

        Where:

        - :math:`F^{r^{comp}}_{l,p,o_d}(k)` is the `secondary_production` output at `time` :math:`k`.
        - :math:`s^r_{l,o,p}(k)` is the :ref:`recycling_flow_shares <input>` input at `time` :math:`k`.
        - :math:`R^{comp}_{l,o,o_c}(k)` is the `recycling_composition` output :eq:`recycling_composition` at `time` :math:`k`.
        - :math:`P_{l,p}(k)` is the `process` output :eq:`total_process_computation` at `time` :math:`k`.
        - :math:`r_{l,o_c,o_d}(k)` is the :ref:`recycling_rate <input>` input at time :math:`k` with the `object` dimension :math:`e` renamed as the `object_composition` dimension :math:`o_c`.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors. In the case where the dimensions of both matrices or vectors are different, the missing dimensions are added with replicate values before performing the product.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """

        # flows du to object composition recycling
        recycling_composition = (
            (self.outputs["recycling_flow"].unstack("age_cohort").rename_axis(columns={"age_cohort": "time"}))
            .mul(self.inputs.object_composition)
            .sum(axis=1)
        ).div(self.outputs["recycling_flow"].groupby(level=["location", "object"]).sum())  # risk of division by 0
        # secondary production
        self.outputs["secondary_production"] = (
            _groupby_sum_empty(
                (
                    self.inputs.recycling_flow_shares[k]
                    .mul(recycling_composition)
                    .mul(self.inputs.recycling_rate[k])
                    .mul(self.process)
                ).dropna(how="any"),
                ["location", "process", "object_downgrading"],
            )
        ).rename_axis(index={"object_downgrading": "object"})

    def _thermodynamic_process_flow_computation(self, k: int):
        r"""
        Compute the thermodynamic process flows at time point :math:`k`, accounting for consumption or co-production within the system.

        This method calculates thermodynamic process flows by integrating the specified thermodynamic processes with the overall process flows, adjusting for control flows and including contributions from secondary production. It effectively captures the energy and material flows influenced by these thermodynamic processes within the production system. The efficiency of an object producing the thermodynamic process is taken into account later in the model.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The thermodynamic process flow is computed as follows:

        .. math::
            F^{thP}_{l,o_s,o}(k) = \sum_{p}[[P^{th}_{l,p,o}(k) \odot P_{l,p}(k) - F^{c^{comp}}_{l,p,o}(k) + F^{r^{comp}}_{l,p,o}(k)] \odot s^p_{l,o_s,p}(k)]
            :label: thermodynamic_process_flow_computation

        Where:

        - :math:`F^{thP}_{l,o_s,o}(k)` is the `thermodynamic_process_flow` output at `time` :math:`k`.
        - :math:`P^{th}_{l,p,o}(k)` is the :ref:`thermodynamic_process <input>` input at `time` :math:`k`.
        - :math:`P_{l,p}(k)` is the `process` output :eq:`total_process_computation` at `time` :math:`k`.
        - :math:`F^{c^{comp}}_{l_p,p,o_c}(k)` is the `control_flow_composition` output :eq:`control_flow_composition` at `time` :math:`k`.
        - :math:`F^{r^{comp}}_{l,p,o}(k)` is the `secondary_production` output :eq:`secondary_production` at `time` :math:`k`.
        - :math:`s^p_{l,o_s,p}(k)` is the :ref:`process_shares <input>` input at `time` :math:`k` with the `object` dimension :math:`e` renamed as the `object_Su` dimension :math:`o_s`.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors. In the case where the dimensions of both matrices or vectors are different, the missing dimensions are added with replicate values before performing the product.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        # flows du to process consumption or coproduction
        self.outputs["non_embedded_flow"] = (
            self.inputs.thermodynamic_process[k].mul(self.process).dropna(axis=0, how="all")
        )
        if self.outputs["non_embedded_flow"].empty:
            df = self.outputs["non_embedded_flow"].copy()
        else:
            # sum of flows per process
            df = (
                self.outputs["non_embedded_flow"]
                .sub(self.outputs["main_object_composition"], fill_value=0)
                .add(self.outputs["secondary_production"], fill_value=0)
            ).mul(self.inputs.process_shares[k].rename_axis(index={"object": "object_Su"}), fill_value=1)
            # extract multiindex of df
            df_index_df = df.index.to_frame(index=False)
            # Replace NaN values in the 'object_Su' column with 'default industry' so that it can be calculated by the model
            df_index_df["object_Su"] = df_index_df["object_Su"].fillna("default industry")
            # Recreate the MultiIndex with the updated 'object_Su' values
            updated_index = pd.MultiIndex.from_frame(df_index_df)
            # Assign the updated MultiIndex back to the DataFrame
            df.index = updated_index
        self.thermodynamic_process_flow = _groupby_sum_empty(df, ["location", "object_Su", "object"])

    # @profile
    def _extraneous_flow_computation(self, k: int):
        r"""
        Compute extraneous flows at time point :math:`k` by integrating object efficiency with thermodynamic process flows.

        This method enhances the calculation of thermodynamic process flows by incorporating object-specific efficiencies. The result is an adjusted measure of extraneous flows that accounts for efficiencies in the production of various processes within the production system.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The extraneous flow is computed as follows:

        .. math::
            F^e_{l,o_s,o_e}(k) = F^{thP}_{l,o_s,o_e}(k) + \sum_{o}[E^{eff}_{l,o_s,o,o_e}(k) \odot F^{thP}_{l,o_s,o}(k)]
            :label: extraneous_flow_computation

        Where:

        - :math:`F^e_{l,o_s,o_e}(k)` is the `extraneous_flow` output at `time` :math:`k`.
        - :math:`E^{eff}_{l,o_s,o,o_e}(k)` represents the :ref:`object efficiency <input>` input at `time` :math:`k`.
        - :math:`F^{thP}_{l,o_s,o_e}(k)` is the `thermodynamic_process_flow` output :eq:`thermodynamic_process_flow_computation` at `time` :math:`k` with the `object` dimension :math:`e` replaced by the `object_efficincy` dimension :math:`o_e`.
        - :math:`F^{thP}_{l,o_s,o}(k)` is the `thermodynamic_process_flow` output :eq:`thermodynamic_process_flow_computation` at `time` :math:`k`.
        - :math:`\odot` the `Hadamard product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#:~:text=In%20mathematics%2C%20the%20Hadamard%20product,of%20the%20multiplied%20corresponding%20objects.>`_ of two matrices or vectors. In the case where the dimensions of both matrices or vectors are different, the missing dimensions are added with replicate values before performing the product.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        # extraneous flow
        self.outputs["extraneous_flow"] = (
            self.thermodynamic_process_flow.add(
                self.inputs.object_efficiency[k]
                .mul(self.thermodynamic_process_flow)
                .groupby(level=["location", "object_Su", "object_efficiency"])
                .sum()
                .rename_axis(index={"object_efficiency": "object"}),
                fill_value=0,
            )
            .replace(0, np.nan)
            .dropna(axis=0, how="all")
        )

    def _old_stock_computation(self, k: int):
        r"""
        Update the old stock levels at time point :math:`k` by accounting for self-disposal and recycling flows.

        This method adjusts the old stock by adding the volume of self-disposal flows and subtracting the volume of recycled materials at time :math:`k`. This provides a net change in the old stock.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The updated old stock is computed as follows:

        .. math::
            S^o_{l,o,c}(k) = S^o_{l,o,c}(k-1) + F^d_{l,o,c}(k) - F^r_{l,o,c}(k)
            :label: old_stock_computation

        Where:

        - :math:`S^o_{l,o,c}(k-1)` is the `old_stock` output from the previous time step.
        - :math:`F^d_{l,o,c}(k)` is the `self_disposal_flow` output :eq:`self_disposal_flow_calc` at `time` :math:`k`.
        - :math:`F^r_{l,o,c}(k)` is the `recycling_flow` output :eq:`recycling_flow_calc` at `time` :math:`k`.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        self.outputs["old_stock"] = (
            self.outputs1["old_stock"]
            .add(self.outputs["self_disposal_flow"][k], fill_value=0)
            .sub(self.outputs["recycling_flow"], fill_value=0)
        )

    def _in_use_stock_computation(self, k: int):
        r"""
        Update the in-use stock levels at time point :math:`k` by integrating changes from control flows, extraneous flows, and self-disposal flows.

        This method calculates the net change in in-use stock by subtracting the volume of self-disposal flows and adding the volumes from both control and extraneous flows at time :math:`k`. The adjustments provide an updated measure of in-use stock that reflects ongoing consumption and replenishment within the production system.

        :param k: the current simulation `time`.
        :type k: int

        Calculation
        -----------
        The updated in-use stock is computed as follows:

        .. math::
            S^u_{l,o,c}(k) = S^u_{l,o,c}(k-1) - F^d_{l,o,c}(k) + \sum_{o_s}[F^e_{l,o_s,o}(k,k)] + F^c_{l,o}(k,k)
            :label: in_use_stock_computation

        Where:

        - :math:`S^u_{k-1}` is the `in_use_stock` output from the previous time step.
        - :math:`F^d_{l,o,c}(k)` is the `self_disposal_flow` output :eq:`self_disposal_flow_calc` at `time` :math:`k`.
        - :math:`F^e_{l,o_s,o}(k,k)` is the `extraneous_flow` output :eq:`extraneous_flow_computation` at `time` :math:`k` and `age_cohort` :math:`k` with the `object_efficiency` dimension :math:`o_e` replaced by the `object` dimension :math:`e`.
        - :math:`F^c_{l,o}(k,k)` represents the `control_flow` output :eq:`control_flow_calc` at `time` :math:`k` and `age_cohort` :math:`k`.
        - indices are the :ref:`variables dimensions <dimensions>`.
        """
        # extraneous flow with production date
        extraneous_flow = pd.concat(
            {k: self.outputs["extraneous_flow"].groupby(level=["location", "object"]).sum()}, names=["age_cohort"]
        )
        # control flow with production date
        control_flow = pd.concat({k: self.outputs["control_flow"]}, names=["age_cohort"])
        # in-use stock
        self.outputs["in_use_stock"] = (
            self.outputs1["in_use_stock"]
            .sub(self.outputs["self_disposal_flow"][k], fill_value=0)
            .add(extraneous_flow, fill_value=0)
            .add(control_flow, fill_value=0)
        )

    def _outputs_update(self, k: int):
        r"""
        Update the previous output storage by copying the current state of outputs at time point :math:`k`.

        This method synchronizes the previous outputs (`self.outputs1`) with the current outputs (`self.outputs`) by copying each output state. This ensures that changes reflected in the current outputs during the computations of a particular time step are mirrored in the previous outputs, maintaining consistency across model states.

        :param k: the current simulation `time`.
        :type k: int

        Method Operation
        ----------------
        Iterates over each output key in `self.outputs` and copies its current state to `self.outputs1`. This operation is essential for models where outputs are progressively updated and require historical tracking or rollback capabilities.
        """
        for output in self.outputs1:
            self.outputs1[output] = self.outputs[output].copy()
