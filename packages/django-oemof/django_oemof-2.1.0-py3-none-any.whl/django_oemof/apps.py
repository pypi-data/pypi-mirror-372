"""Config for django app"""

from django.apps import AppConfig


class DjangoOemofConfig(AppConfig):
    """Config for django-oemof app"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_oemof"
