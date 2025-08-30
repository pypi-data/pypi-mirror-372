"""Urls for django-oemof package"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django_oemof import views

router = DefaultRouter()

# pylint:disable=C0103
app_name = "django_oemof"

urlpatterns = [
    path("", include(router.urls)),
    path("simulate", views.SimulateEnergysystem.as_view(), name="simulate"),
    path("terminate", views.TerminateSimulationView.as_view()),
    path("calculate", views.CalculateResults.as_view()),
    path("flows", views.FlowsView.as_view()),
]
