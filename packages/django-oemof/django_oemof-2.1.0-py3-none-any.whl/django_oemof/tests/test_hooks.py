"""Tests for hooks"""

from django.test import TestCase

from django_oemof import hooks


class TestHooks(TestCase):
    """Testing hooks"""

    def test_parameter_hook(self):
        """Testing multiple hooks but for different scenarios"""

        def parameter_hook_1(scenario, data, request):
            return {key: f"{value}_1" for key, value in data.items()}

        def parameter_hook_2(scenario, data, request):
            return {key: f"{value}_2" for key, value in data.items()}

        def parameter_hook_all(scenario, data, request):
            return {key: f"{value}_all" for key, value in data.items()}

        hook1 = hooks.Hook(scenario="1", function=parameter_hook_1)
        hook2 = hooks.Hook(scenario="2", function=parameter_hook_2)
        hook_all = hooks.Hook(scenario=hooks.ALL_SCENARIOS, function=parameter_hook_all)
        hooks.register_hook(hooks.HookType.PARAMETER, hook1)
        hooks.register_hook(hooks.HookType.PARAMETER, hook2)
        hooks.register_hook(hooks.HookType.PARAMETER, hook_all)

        original_parameters = {"a": "1", "b": "2"}
        parameters_from_hook1 = hooks.apply_hooks(hooks.HookType.PARAMETER, scenario="1", data=original_parameters)
        assert parameters_from_hook1 == {"a": "1_1_all", "b": "2_1_all"}
        parameters_from_hook2 = hooks.apply_hooks(hooks.HookType.PARAMETER, scenario="2", data=original_parameters)
        assert parameters_from_hook2 == {"a": "1_2_all", "b": "2_2_all"}
