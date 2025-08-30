import frictionless
from django.core.management.base import BaseCommand

from django_oemof.models import Simulation, Result
from django_oemof.settings import OEMOF_STATIC_DIR


class Command(BaseCommand):
    help = "Adds static result. Static result must be present in folder `oemof_static` in MEDIA_ROOT."

    def add_arguments(self, parser):
        parser.add_argument("scenarios", nargs="*", type=str, default=None)

    def handle(self, *args, **options):
        scenarios = options["scenarios"] or [scenario.name for scenario in OEMOF_STATIC_DIR.iterdir()]
        for scenario in scenarios:
            if Simulation.objects.filter(scenario=scenario).exists():
                self.stdout.write(
                    self.style.NOTICE(f"Simulation for scenario '{scenario}' already exists. Skipping...")
                )
                continue
            package = frictionless.Package(OEMOF_STATIC_DIR / scenario / "datapackage.json")
            parameters = package.get("parameters")
            simulation = Simulation(scenario=scenario, parameters=parameters)
            simulation.save()
            for resource in package.resources:
                df = resource.to_pandas()
                result = Result(
                    simulation=simulation,
                    name=resource.name,
                    data_type="series" if len(df.columns) == 2 else "frame",
                    data=df.to_json(orient="table"),
                )
                result.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully created results for scenario '{scenario}'"))
