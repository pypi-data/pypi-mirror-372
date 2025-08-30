"""Simulation module"""

import json
import logging
from typing import Optional
from collections import namedtuple

# pylint: disable=W0611
import oemof.tabular.datapackage  # noqa
from celery import shared_task
from django.conf import settings
from . import settings as do_settings
from oemof import solph
from oemof.tabular.facades import TYPEMAP

from django_oemof import hooks, models


FlowAttribute = namedtuple("FlowAttribute", ("from_node", "to_node", "attribute", "value"))


class SimulationError(Exception):
    """Raised if simulation failed or simulation is not present"""


@shared_task
def simulate_scenario(scenario: str, parameters: dict, lp_file: Optional[str] = None) -> int:
    """
    Returns ID to oemof results from simulated/restored scenario

    Already stored scenarios are identified by scenario name and
    adapted parameters.

    Parameters
    ----------
    scenario: str
        Name of scenario (used to load related datapackage)
    parameters: dict
        Parameters which are adapted to ES before simulation
    lp_file: Optional[str]
        If set, LP file is stored under given path

    Returns
    -------
    int
        Simulation ID where results are stored
    """
    try:
        simulation = models.Simulation.objects.get(scenario=scenario, parameters=parameters)  # pylint: disable=E1101
        logging.info(f"Simulation for {scenario=} and {parameters=} already present.")
    except models.Simulation.DoesNotExist:  # pylint: disable=E1101
        logging.info(f"Simulating energysystem for {scenario=} and {parameters=}.")
        oemof_datapackage = f"{settings.MEDIA_ROOT}/oemof/{scenario}/datapackage.json"
        energysystem = build_energysystem(oemof_datapackage)
        build_parameters = hooks.apply_hooks(hook_type=hooks.HookType.PARAMETER, scenario=scenario, data=parameters)
        energysystem = adapt_energysystem(energysystem, build_parameters)
        hooks.apply_hooks(hook_type=hooks.HookType.ENERGYSYSTEM, scenario=scenario, data=parameters, energysystem=energysystem)
        termination_condition, input_data, results_data, meta_results = simulate_energysystem(
            scenario, energysystem, parameters, lp_file
        )
        if termination_condition == "infeasible":
            logging.warning(f"Simulation run for {scenario=} and {parameters=} is infeasible.")
            return
        dataset = models.OemofDataset.store_results(input_data, results_data, meta_results)
        # pylint: disable=E1101
        try:
            # Add additional check in case simulation with same parameters has been run in parallel
            simulation = models.Simulation.objects.get(scenario=scenario, parameters=parameters)
            logging.info(
                f"Simulation results for {scenario=} and {parameters=} are stored already by other simulation run."
            )
        except models.Simulation.DoesNotExist:
            simulation = models.Simulation.objects.create(scenario=scenario, parameters=parameters, dataset=dataset)
            simulation.save()
            logging.info(f"Stored simulation results for {scenario=} and {parameters=}.")
    return simulation.id


def build_energysystem(oemof_datapackage: str):
    """
    Builds energysystem from datapackage

    Parameters
    ----------
    oemof_datapackage: str
        Path to oemof.tabular datapackage

    Returns
    -------
    energysystem: Energysystem build from datapacakge
    """
    logging.info(f"Building energysystem from datapackage at '{oemof_datapackage}'.")
    return solph.EnergySystem.from_datapackage(oemof_datapackage, typemap=TYPEMAP)


def adapt_energysystem(energysystem: solph.EnergySystem, parameters: dict):
    """
    Adapt parameters in ES

    This allows loading standard ES and changing specific parameters after build.

    Parameters
    ----------
    energysystem: EnergySystem
        Components in Energysystem are changed by given parameters

    parameters: dict
        Parameters which shall be adapted in ES

    Returns
    -------
    energysystem: Energysystem with changed parameters
    """
    parameters = parameters or {}
    logging.info(f"Adapting parameters in ES using {parameters=}.")

    for node_name, attributes in parameters.items():
        if node_name == "flow":
            logging.warning(
                f"This is deprecated. Flows are adapted using input_parameters and output_parameters instead."
            )
            continue
        if node_name not in [n.label for n in energysystem.nodes]:
            log_msg = f"Cannot adapt component '{node_name}', as it cannot be found in energysystem."
            logging.warning(log_msg)
            continue
        if not isinstance(attributes, dict):
            log_msg = (
                f"Cannot adapt attributes for component '{node_name}', as there is no dictionary. Skipping it." 
                """Try something like {"wind_onshore": {"capacity": 100}} instead."""
            )
            logging.warning(log_msg)
            continue

        node = next(n for n in energysystem.nodes if node_name == n.label)
        for attribute, value in attributes.items():
            if not hasattr(node, attribute):
                logging.warning(
                    f"Attribute '{attribute}' not found in component '{node_name}' in energysystem. "
                    "Adapting the attribute might have no effect."
                )
            setattr(node, attribute, value)
        node.update()
    return energysystem


def simulate_energysystem(scenario, energysystem, user_data: Optional[dict] = None, lp_file: Optional[str] = None):
    """
    Simulates ES, stores results to DB and returns simulation ID

    Parameters
    ----------
    scenario: str
        Name of current scenario (used to apply hooks)
    energysystem : EnergySystem
        Built energysystem to be solved
    user_data: Optional[dict]
        Optional user data to be passed to hooks
    lp_file: Optional[str]
        If set, LP file is stored under given path

    Returns
    -------
    results : tuple(bool, dict, dict, dict, dict)
        Simulation termination condition, input, results, meta results and custom results
    """
    logging.info(f"Building model for {scenario=}.")
    model = solph.Model(energysystem)
    hooks.apply_hooks(hook_type=hooks.HookType.MODEL, scenario=scenario, data=user_data, model=model)
    logging.info(f"Starting simulation for {scenario=}.")
    model_results = model.solve(
        solver="cbc", cmdline_options={"mipgap": "0.1", "seconds": do_settings.DJANGO_OEMOF_TIMELIMIT}
    )
    if lp_file:
        model.write(lp_file, io_options={"symbolic_solver_labels": True})
    logging.info(f"Simulation for {scenario=} finished.")

    input_data = solph.processing.parameter_as_dict(
        energysystem,
        exclude_attrs=["bus", "from_bus", "to_bus", "from_node", "to_node"],
    )
    results_data = solph.processing.results(model)
    # Clean-up meta results by dumping and loading and neglecting non-serializable key/values
    meta_results = json.loads(
        json.dumps(solph.processing.meta_results(model), skipkeys=True, default=lambda x: "Not serializable")
    )
    meta_results = hooks.apply_hooks(
        hook_type=hooks.HookType.POSTPROCESSING, scenario=scenario, data=user_data, model=model, meta=meta_results
    )

    return (
        model_results.solver.termination_condition,
        *map(solph.processing.convert_keys_to_strings, (input_data, results_data)),
        meta_results,
    )
