import json
import logging
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from yarik_django_airflow_api_manager.conf.settings import LOGIN_APP_ROUTE

from .airflow_api_manager import AirflowManager

logger = logging.getLogger(__name__)


@sync_to_async
@login_required(login_url=(reverse_lazy(LOGIN_APP_ROUTE) if LOGIN_APP_ROUTE else "/"))
def check_connection(request: HttpRequest):

    if not AirflowManager().conn_good():
        return JsonResponse(
            {"title": "Не удалось установить соединение с Airflow"}, status=503
        )

    if not AirflowManager().creds_is_valid():
        return JsonResponse({"title": "Ошибка авторизации Airflow API"}, status=401)

    return JsonResponse({}, status=200)


@sync_to_async
@login_required(login_url=(reverse_lazy(LOGIN_APP_ROUTE) if LOGIN_APP_ROUTE else "/"))
def dag(request: HttpRequest):
    if request.method == "GET":
        dag_id = request.GET.get("dag_id")
        if dag_id is None or dag_id in ["undefined", "null"]:
            return JsonResponse({}, status=400)

        dag = AirflowManager(dag_id=dag_id).get_dag()

        if not dag:
            return JsonResponse({"msg": "Даг не найден"}, status=404)

        return JsonResponse({"dag": dag.model_dump(by_alias=True)})

    else:
        return JsonResponse({"msg": "Метод не разрешён"}, status=405)


@sync_to_async
@login_required(login_url=(reverse_lazy(LOGIN_APP_ROUTE) if LOGIN_APP_ROUTE else "/"))
def dag_run(request: HttpRequest):
    if request.method == "GET":

        dag_id = request.GET.get("dag_id")
        by_user = request.GET.get("by_user", "false") == "true"
        if dag_id in ["undefined", "null"]:
            dag_id = None
        if dag_id is None:
            return JsonResponse({}, status=400)

        dag_run_id = request.GET.get("dag_run_id")
        if dag_run_id in ["undefined", "null"]:
            dag_run_id = None
        airflow_manager = AirflowManager(dag_id=dag_id)
        dag_run = None
        if dag_run_id is None:
            # todo: убрать это прибитое гвоздями условие dag_id == "generator_rules", но это изменение будет ломающим
            if (dag_id == "generator_rules" or by_user) and isinstance(
                request.user, User
            ):
                dag_run = airflow_manager.get_last_dag_run(
                    username=request.user.username
                )
            else:
                dag_run = airflow_manager.get_last_dag_run()
        else:
            airflow_manager.dag_run_id = dag_run_id
            dag_run = airflow_manager.get_current_dag_run()

        logger.debug(f"dag_run={dag_run}")
        if not dag_run:
            return JsonResponse({"msg": "Запуск дага не найден"}, status=404)

        task_instances = airflow_manager.get_task_instances()

        if not task_instances:
            return JsonResponse({"msg": "Экземпляры задач не найдены"}, status=404)

        return JsonResponse(
            {
                "dagRun": (dag_run.model_dump(by_alias=True)),
                "taskInstances": (task_instances.model_dump(by_alias=True)),
            }
        )
    else:
        action = json.loads(request.body.decode("utf-8")).get("action")

        dag_id = json.loads(request.body.decode("utf-8")).get("dag_id")
        if dag_id is None:
            return JsonResponse({}, status=400)

        dag_run_id = json.loads(request.body.decode("utf-8")).get("dag_run_id")

        dag_run = None
        task_instances = None
        airflow_manager = AirflowManager(dag_id=dag_id)
        match action:
            case "start":
                conf = json.loads(request.body.decode("utf-8")).get("conf")
                if conf is not None and "run_username" not in conf:
                    conf["run_username"] = request.user.username
                dag_run = airflow_manager.trigger(conf=conf)
                if not dag_run:
                    logger.error(f"Не удалось запустить даг {dag_id}")

            case "restart":
                if dag_run_id is None:
                    return JsonResponse({}, status=400)
                airflow_manager.dag_run_id = dag_run_id
                dag_run = airflow_manager.clear()
                if not dag_run:
                    logger.error(f"Не удалось перезапустить даг {dag_id}")

            case "stop":
                if dag_run_id is None:
                    return JsonResponse({}, status=400)
                airflow_manager.dag_run_id = dag_run_id
                dag_run = airflow_manager.stop()
                if not dag_run:
                    logger.error(f"Не удалось остановить даг {dag_id}")

            case _:
                JsonResponse({}, status=501)

        if not dag_run:
            return JsonResponse(
                {"title": "Ошибка при выполнении операции с дагом"}, status=404
            )

        task_instances = airflow_manager.get_task_instances()
        if not task_instances:
            logger.warning(
                f"Не удалось получить список экземпляров задач дага {dag_id} для запуска {dag_run.dag_run_id}"
            )

        return JsonResponse(
            {
                "dagRun": dag_run.model_dump(by_alias=True) if dag_run else None,
                "taskInstances": (
                    task_instances.model_dump(by_alias=True) if task_instances else None
                ),
            }
        )


@sync_to_async
@login_required(login_url=(reverse_lazy(LOGIN_APP_ROUTE) if LOGIN_APP_ROUTE else "/"))
def ti_logs(request: HttpRequest):
    if request.method == "GET":
        dag_id = request.GET.get("dag_id")
        if dag_id in ["undefined", "null"]:
            dag_id = None
        if dag_id is None:
            return JsonResponse({}, status=400)

        dag_run_id = request.GET.get("dag_run_id")
        if dag_run_id in ["undefined", "null"]:
            dag_run_id = None
        if dag_run_id is None:
            return JsonResponse({}, status=400)

        task_id = request.GET.get("task_id")
        if task_id in ["undefined", "null"]:
            task_id = None
        if task_id is None:
            return JsonResponse({}, status=400)

        try_num = request.GET.get("try_num")
        if try_num in ["undefined", "null"]:
            try_num = None
        if try_num is None or not try_num.isdigit():
            try_num = "1"
        try_num = int(try_num)

        continuation_token = request.GET.get("continuation_token")

        if continuation_token in ["undefined", "null"]:
            continuation_token = None

        airflow_manager = AirflowManager(dag_id=dag_id, dag_run_id=dag_run_id)

        logs = airflow_manager.get_logs(
            task_id=task_id, try_num=try_num, continuation_token=continuation_token
        )

        if not logs:
            logger.error(
                f"Не удалось получить логи для дага {dag_id} и запуска {dag_run_id}"
            )
            return JsonResponse({"title": "Ошибка при получении логов"}, status=404)

        return JsonResponse({"logs": logs.model_dump(by_alias=True)})
    else:
        return HttpResponse()
