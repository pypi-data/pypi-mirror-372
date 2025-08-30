"""Tests storing and restoring of oemof results in DB"""

import pathlib

# pylint: disable=W0611
import oemof.tabular.datapackage  # noqa
from django.test import TransactionTestCase
from oemof import solph

from django_oemof import models, simulation

OEMOF_DATAPACKAGE = pathlib.Path(__file__).parent / "test_data" / "dispatch" / "datapackage.json"


class OemofDBTest(TransactionTestCase):
    """Test case for (re-)storing oemof results in DB"""

    def test_store_and_restore(self):
        """Stores and restores results from simple oemof example"""
        energysystem = simulation.build_energysystem(str(OEMOF_DATAPACKAGE))
        input_data, results_data = simulation.simulate_energysystem(energysystem)
        input_data = solph.processing.convert_keys_to_strings(input_data)
        results_data = solph.processing.convert_keys_to_strings(results_data)

        result_id = models.OemofDataset.store_results(input_data, results_data)
        assert result_id == 1
        dataset = models.OemofDataset.objects.get(pk=result_id)  # pylint: disable=E1101
        restored_input, restored_results = dataset.restore_results()
        assert len(input_data) == len(restored_input)
        assert len(input_data) == len(restored_input)
        assert len(results_data) == len(restored_results)
        assert len(results_data) == len(restored_results)
