"""Settings for django_oemof"""

import environ
import pathlib
from collections import defaultdict

from django.conf import settings

env = environ.Env()

OEMOF_DIR = pathlib.Path(settings.MEDIA_ROOT) / getattr(settings, "DJANGO_OEMOF_DIR", "oemof")
OEMOF_STATIC_DIR = pathlib.Path(settings.MEDIA_ROOT) / getattr(settings, "DJANGO_OEMOF_STATIC_DIR", "oemof_static")

HOOKS = defaultdict(list)

DJANGO_OEMOF_IGNORE_SIMULATION_PARAMETERS = env.list("DJANGO_OEMOF_IGNORE_SIMULATION_PARAMETERS", default=[])
DJANGO_OEMOF_TIMELIMIT = env.int("DJANGO_OEMOF_TIMELIMIT", default=600)
