from django.urls import path
from . import views

app_name = "yarik_django_airflow_api_manager"

urlpatterns = [
    path("check_connection", views.check_connection, name="check_connection"),
    path("dag", views.dag, name="dag"),
    path("dag_run", views.dag_run, name="dag_run"),
    path("ti_logs", views.ti_logs, name="ti_logs"),
]
