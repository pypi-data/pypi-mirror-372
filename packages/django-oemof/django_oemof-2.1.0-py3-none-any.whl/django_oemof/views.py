"""Views for django_oemof"""
import json
import logging

from celery.result import AsyncResult
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.views.generic import TemplateView

from django_oemof import hooks, results, settings, simulation, models


class SimulateEnergysystem(APIView):
    """View to build and simulate Oemof energysystem from datapackage"""

    @staticmethod
    def get(request):
        """
        Checks simulation run using celery task ID

        Parameters
        ----------
        request
            Holding celery task ID

        Returns
        -------
        Response
            holding simulation ID if simulation is ready, otherwise simulation ID is None
        """
        task_id = request.GET["task_id"]
        task = AsyncResult(task_id)
        if task.ready():
            if task.failed():
                logging.info(f"Task #{task.task_id} failed: {task.result.args[0]}")
                return Response({"msg": f"Simulation error: {task.result.args[0]}"}, status=status.HTTP_400_BAD_REQUEST)
            logging.info(f"Task #{task.task_id} finished.")
            try:
                simulation_id = task.get()
            except:  # noqa: E722
                return Response({"msg": "Simulation error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if simulation_id is None:
                return Response({"msg": "Simulation is infeasible"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"simulation_id": simulation_id})
        return Response({"simulation_id": None})

    @staticmethod
    def post(request):
        """
        Simulates ES given by scenario and parameters

        Parameters
        ----------
        request
            Request holding scenario and parameters as JSON

        Returns
        -------
        Response
            holding celery task ID
        """
        scenario = request.POST["scenario"]
        parameters = hooks.apply_hooks(
            hook_type=hooks.HookType.SETUP, scenario=scenario, data=request.POST.dict()
        )
        task = simulation.simulate_scenario.delay(scenario, parameters)
        logging.info(f"Started simulation task #{task.task_id}.")
        return Response({"task_id": task.task_id})


class TerminateSimulationView(APIView):
    """View to terminate Oemof simulation run"""

    @staticmethod
    def post(request):
        """
        Delete task for given task ID

        Parameters
        ----------
        request
            Holding celery task ID

        Returns
        -------
        Response
            whether task deletion has been successful
        """
        task_id = request.POST["task_id"]
        task = AsyncResult(task_id)
        task.revoke(terminate=True)
        logging.info(f"Terminated task #{task_id}.")
        return Response()


class CalculateResults(APIView):
    """View calculate results from oemof simulation"""

    @staticmethod
    def get(request):
        """
        Calculates results for given scenario (with parameters)

        Parameters
        ----------
        request
            Request

        Returns
        -------
        Response
        """
        simulation_id = request.GET["simulation_id"]
        calculations = request.GET.getlist("calculations")
        calculated_results = results.get_results(simulation_id, calculations)
        return Response(calculated_results)


class FlowsView(TemplateView):
    template_name = "django_oemof/flows.html"

    def get_context_data(self, **kwargs):
        simulation_id = self.request.GET["simulation_id"]
        # Additional storages with different naming can be excluded via URl parameter "storages"
        storages = self.request.GET.getlist("storages") + ["storage", "battery"]
        try:
            sim = models.Simulation.objects.get(pk=simulation_id)  # pylint: disable=E1101
        except models.Simulation.DoesNotExist:  # pylint: disable=E1101
            # pylint: disable=W0707
            raise simulation.SimulationError(f"Simulation with ID#{simulation_id} not present in database.")

        _, results = sim.dataset.restore_results()
        links = [{"source": source, "target": target, "value": data["sequences"]["flow"].sum()} for (source, target), data in results.items() if "flow" in data["sequences"]]
        # Filter storages in order to avoid cycles (not possible with eCharts Sankeys) and zeros to avoid thin lines
        links = [link for link in links if all(storage not in link["target"] for storage in storages) and link["value"] > 0]
        names_raw = {link["source"] for link in links} | {link["target"] for link in links}
        names = [{"name": name} for name in names_raw]
        return {
            "results": results,
            "simulation_id": simulation_id,
            "chart_data": {
                "names": names,
                "links": links,
            },
        }
