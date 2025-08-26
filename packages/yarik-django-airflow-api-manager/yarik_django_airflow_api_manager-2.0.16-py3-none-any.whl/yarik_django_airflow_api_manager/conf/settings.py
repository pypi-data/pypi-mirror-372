from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

VERSION_TAG = getattr(settings, "VERSION_TAG")

DEFAULT_REDIRECT_URI = getattr(settings, "DEFAULT_REDIRECT_URI", "/")

AIRFLOW_HOST = getattr(settings, "AIRFLOW_HOST")
AIRFLOW_PORT = getattr(settings, "AIRFLOW_PORT")
AIRFLOW_USER = getattr(settings, "AIRFLOW_USER")
AIRFLOW_PSWD = getattr(settings, "AIRFLOW_PSWD")
AIRFLOW_BASE_URL = getattr(settings, "AIRFLOW_BASE_URL")
LOGIN_APP_ROUTE = getattr(settings, "LOGIN_APP_ROUTE")


if (
    AIRFLOW_HOST is None
    or AIRFLOW_PORT is None
    or AIRFLOW_USER is None
    or AIRFLOW_PSWD is None
    or AIRFLOW_BASE_URL is None
):
    raise ImproperlyConfigured(
        "Could not find one of AIRFLOW_HOST, AIRFLOW_PORT, AIRFLOW_USER, AIRFLOW_PSWD, AIRFLOW_BASE_URL in environment"
    )
