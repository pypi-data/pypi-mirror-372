"""Hooks can be used to change default behaviour of parameter, ES or model setup."""
import logging
from inspect import signature
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Union


from django_oemof import settings


# pylint:disable=R0903
class AllScenarios:
    """Used to apply hook to all scenarios"""

    def __str__(self):
        return "ALL_SCENARIOS"


ALL_SCENARIOS = AllScenarios()

DEFAULT_PARAMETERS = ["scenario", "data"]


class HookType(Enum):
    """Hook types - define where to apply hooks"""

    SETUP = ("setup", [])
    PARAMETER = ("parameter", [])
    ENERGYSYSTEM = ("energysystem", ["energysystem"])
    MODEL = ("model", ["model"])
    POSTPROCESSING = ("postprocessing", ["model", "meta"])

    def __init__(self, label, parameters):
        self.label = label
        self.parameters = parameters


@dataclass
class Hook:
    """Hook class is used to set up a hook for specific scenario"""

    scenario: Union[str, AllScenarios]
    function: Callable

    def __str__(self):
        return f"<Hook '{self.function.__name__}' @{self.scenario}>"


def register_hook(hook_type: HookType, hook: Hook):
    """Registers hook depending on hook type"""
    sig = signature(hook.function)
    function_parameters = sig.parameters.keys()
    if any(parameter not in function_parameters for parameter in hook_type.parameters + DEFAULT_PARAMETERS):
        error_msg = f"Hook function '{hook.function.__name__}' misses parameters. Needed parameters: {hook_type.parameters + DEFAULT_PARAMETERS}, given: {list(function_parameters)}"
        raise KeyError(error_msg)
    if list(function_parameters)[:2] != DEFAULT_PARAMETERS:
        error_msg = f"Hook function '{hook.function.__name__}' must start with parameters {DEFAULT_PARAMETERS}, instead it starts with: {list(function_parameters)[:2]}"
        raise KeyError(error_msg)
    settings.HOOKS[hook_type].append(hook)


def apply_hooks(hook_type: HookType, scenario: str, data: Any, **kwargs) -> dict:
    """Applies hooks for a given hook type and scenario"""
    hooked_data = deepcopy(data)
    if hook_type == HookType.POSTPROCESSING:
        meta = deepcopy(kwargs["meta"])

    for hook in settings.HOOKS[hook_type]:
        if hook.scenario != scenario and hook.scenario is not ALL_SCENARIOS:
            continue
        logging.info(f"Applying {hook}")
        if hook_type == HookType.ENERGYSYSTEM:
            hook.function(scenario, hooked_data, energysystem=kwargs["energysystem"])
        elif hook_type == HookType.MODEL:
            hook.function(scenario, hooked_data, model=kwargs["model"])
        elif hook_type == HookType.POSTPROCESSING:
            meta = hook.function(scenario, hooked_data, meta=meta, model=kwargs["model"])
        else:
            hooked_data = hook.function(scenario, hooked_data)

    if hook_type == HookType.POSTPROCESSING:
        return meta
    return hooked_data
