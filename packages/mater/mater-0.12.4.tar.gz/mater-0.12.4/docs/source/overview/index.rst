.. _overview:


========
Overview
========

Introduction
============

The MATER model provides a comprehensive framework for integrating biophysical constraints with socioeconomic rules to explore interactions within socioecological systems (SES). Building on the socioeconomic metabolism (SEM) paradigm, MATER encompasses concepts such as energy, material flows, and pollution, offering a demand-driven approach to model human-induced and natural processes. The model aims to facilitate detailed understanding of sectoral interconnections and feedback mechanisms, enabling simulation of various scenarios with an emphasis on adaptable socio-economic rules and prioritization of biophysical constraints.

SEM Paradigm's Tools
====================

Sociometabolic research (SMR) examines the interactions between socioeconomic metabolism (SEM) and nature, quantifying planetary boundary overshoots based on future societal choices :cite:p:`haberl_contributions_2019`. This field aims to inform public debates on sustainable resource management, exemplified by the Sustainable Development Goals (SDGs).

SEM characterizes transformations and activities through flows and processes of human-controlled object stocks (e.g., cars, industries, materials, livestock). These stocks, along with society’s biophysical structure, form the biophysical basis of society :cite:p:`pauliuk_socioeconomic_2015`.

Various tools describe SEM at different spatial-temporal scales:

- **Urban Metabolism**: Focuses on material and energy flows at the urban scale.
- **MuSIASEM**: Adds social and economic components to urban metabolism :cite:p:`giampietro_multi-scale_2009`, :cite:p:`gerber_search_2018`.
- **Biophysical Economics**: Concentrates on the link between energy and economics :cite:p:`ayres_production_1969`. The concept of energy return on investment (EROI) is central to this community :cite:p:`cleveland_energy_1984`.
- **MEFA**: Accounts for material flows at both macro and micro scales :cite:p:`krausmann_material_2017`.
- **EE-IOA**: Focuses on monetary and biophysical flows between regions and economic sectors, building on the work of :cite:p:`leontief_environmental_1970`. Recent studies feature annual economic exchange tables through tools like Exiobase :cite:p:`stadler_exiobase_2018`.
- **LCA**: Assesses life cycle impacts of products :cite:p:`earles_consequential_2011`.
- **IAMs**: Global and comprehensive models that often lack stock representation and detailed material accounting :cite:p:`pauliuk_industrial_2017`.

Limits of the SEM Paradigm
==========================

The SEM paradigm often struggles to describe nature and its interactions with society :cite:p:`pauliuk_socioeconomic_2015`. It typically enforces a clear boundary between society’s biophysical basis and the natural environment, a boundary that is becoming obsolete in the Anthropocene era :cite:p:`steffen_anthropocene_2011`. 

Coupled Human and Natural Systems (CHANS) strive to integrate human-nature interactions using both ecological and sociological approaches :cite:p:`liu_complexity_2007`. This field is closely related to SMR and socioecological systems (SES), which often lack proprietary numerical tools and generally use small-scale system dynamics models :cite:p:`liu_coupled_2021`.

MATER Model Framework
=====================

The MATER model integrates both SEM and natural driving forces, recognizing their mutual influence within socioecological systems (SES). It aims to capture all impacts, such as CO2 emissions, while considering local specificities, allowing the evaluation of global policy changes and behavioral shifts on local ecosystems and vice versa.

Fundamental Concepts
--------------------

- **Nothing comes for free**: Accounts for all consumption, co-production, or emissions associated with any flow.
- **Demand-driven approach**: Ensures that supply consistently meets human needs and desires, adapting to and influencing ecosystems and natural processes.
- **Technological choices**: Reflects the preference for technologies driven by biophysical constraints and socio-economic rules.

Conceptual Approach
-------------------

MATER aims to integrate various modeling communities into collaborative thematic work. The model considers constraints in a specific order, prioritizing biophysical constraints over socio-economic ones, which are mutable and chosen by humans. This approach tests the feasibility of future scenarios within biophysical constraints first, ensuring comprehensive integration and avoiding the overlooking of immutable physical constraints :cite:p:`fisher-vanden_evolution_2020`.

History of the Modeling Approach
--------------------------------

The MATER model was conceptualized by Olivier Vidal :cite:p:`vidal_metals_2013` and initially implemented at ISTerre :cite:p:`francois_regionalisation_2017`, :cite:p:`vidal_modelling_2018`, :cite:p:`vidal_preypredator_2019`. It evolved from the DyMEMDs (Dynamic Modeling of Energy and Matter Demand and Supply) model, leading to several sectoral studies :cite:p:`le_boulzec_dynamic_2022`, :cite:p:`le_boulzec_material_2023`. Increased collaboration and the need for a general and flexible model drove the development of MATER :cite:p:`monfort-climent_inventaires_2019`.

MATER integrates biophysical constraints with human decisions, recognizing every flow's inherent cost and adopting a demand-driven methodology. The model acknowledges a diverse array of technological solutions to meet human needs, influenced by physical barriers and socio-economic rules, allowing these choices to evolve over time :cite:p:`pauliuk_toward_2016`.

Building Blocks: Objects and Flows
==================================

The MATER model consists of objects and flows that interact. Objects are quantified in stocks that provide various processes when functioning. Processes link flows together, representing the recipes for production, consumption, or emissions. Flows include the production of resources, provision of services, or energy use.

Stocks can be in-use (operational objects) or old (non-functional objects), and they change over time based on various flows:

- **External flows (F^e)**: Induced by processes.
- **Control flows (F^c)**: Generated from other objects.
- **Self-disposal flows (F^d)**: Represent the end-of-life phase.
- **Recycling flows (F^r)**: Transform old objects into new ones.

Model Behavior: Socio-Economic Equations
========================================

The MATER model's biophysical structure includes objects and processes with defined behaviors for recycling and control flows. The recycling flow is modeled by a linear equation relative to the self-disposal flow, while control flows ensure stock levels follow reference levels, adjusting to perturbation flows.

Controlled objects have reference stocks based on scenarios or endogenous processes, ensuring coherence with final demand scenarios. Cascading control endogenizes industrial flow, ensuring consistency with final demand and evolving resource quality.

Implementations and Applications
================================

The MATER model is implemented in Python and continuously developed on a public GitLab. It aims to converge towards the general framework by exploring multiple implementation methods. The model tests pre-produced scenarios, comparing recalculated energy consumption and dynamic Life Cycle Assessments (LCAs).

Future Development
==================

Future developments aim to improve data completeness, explore advanced control theory concepts, and integrate economic theories and optimization methodologies. Enhancements will ensure model precision, stability, and applicability, contributing to sustainable resource management and environmental stewardship.

Conclusion
==========

The MATER model represents a significant advancement in integrating biophysical and socioeconomic dimensions within socioecological system modeling. By leveraging a hierarchical structure of objects, stocks, and flows, MATER facilitates the detailed examination of human activities and natural processes interactions. Its flexibility and adaptability make it a robust tool for scenario analysis and sustainable development planning.

Continued developments will enhance its precision, stability, and applicability, ensuring its relevance in addressing sustainable resource management challenges. The MATER model offers valuable insights for guiding sustainable development policies and practices, contributing to a more resilient and equitable future.

References
==========

.. bibliography::