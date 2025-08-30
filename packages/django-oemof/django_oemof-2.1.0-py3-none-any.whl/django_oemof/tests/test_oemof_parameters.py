"""Tests to parametrize oemof energysystems before simulation start"""

import copy
import pathlib
import time
import unittest

# pylint: disable=W0611
import oemof.tabular.datapackage  # noqa
import pytest
from django.test import TransactionTestCase

from django_oemof import simulation

OEMOF_DATAPACKAGE = pathlib.Path(__file__).parent / "test_data" / "oemof" / "dispatch" / "datapackage.json"
OEMOF_BIG_DATAPACKAGE = pathlib.Path(__file__).parent / "test_data" / "oemof" / "test_scenario" / "datapackage.json"


class OemofParameterTest(TransactionTestCase):
    """Test case for paramtrizing oemof ES after initialization"""

    def test_without_parameterization(self):
        """Build ES from datapacakge and simulate as reference to 'test_with_parameterization'"""
        energysystem = simulation.build_energysystem(str(OEMOF_DATAPACKAGE))
        _, results_data = simulation.simulate_energysystem(energysystem)
        assert list(results_data.values())[6]["sequences"].flow[0] == pytest.approx(7.37660)
        assert list(results_data.values())[6]["sequences"].flow[1] == pytest.approx(9.20905)
        assert list(results_data.values())[6]["sequences"].flow[2] == pytest.approx(11.19685)

    def test_with_parameterization(self):
        """Build ES from datapacakge and change parameter afterwards before simulation"""
        parameters = {"wind": {"capacity": 5}}
        energysystem = simulation.build_energysystem(str(OEMOF_DATAPACKAGE))
        energysystem = simulation.adapt_energysystem(energysystem, parameters)
        _, results_data = simulation.simulate_energysystem(energysystem)
        assert list(results_data.values())[6]["sequences"].flow[0] == pytest.approx(7.37660 / 10)
        assert list(results_data.values())[6]["sequences"].flow[1] == pytest.approx(9.20905 / 10)
        assert list(results_data.values())[6]["sequences"].flow[2] == pytest.approx(11.19685 / 10)


class OemofBuildTest(TransactionTestCase):
    """Test case for copying existing ES"""

    def test_build_large_es(self):
        """Test building a large ES"""
        start = time.time()
        energysystem = simulation.build_energysystem(str(OEMOF_BIG_DATAPACKAGE))
        print("Time to build ES:", time.time() - start)  # ~5s
        start = time.time()
        simulation.simulate_energysystem(energysystem)
        print("Time to simulate ES:", time.time() - start)  # 28s

    @unittest.skip("Copying ES does not work!")
    def test_copying_es(self):
        """Test to copy ES"""
        energysystem = simulation.build_energysystem(str(OEMOF_DATAPACKAGE))
        energysystem_copy = copy.deepcopy(energysystem)
        parameters = {"wind": {"capacity": 5}}
        energysystem_changed = simulation.adapt_energysystem(energysystem_copy, parameters)
        _, results_data = simulation.simulate_energysystem(energysystem)
        _, results_data_changed = simulation.simulate_energysystem(energysystem_changed)

        assert list(results_data.values())[6]["sequences"].flow[0] == pytest.approx(7.37660)
        assert list(results_data_changed.values())[6]["sequences"].flow[0] == pytest.approx(7.37660 / 10)
