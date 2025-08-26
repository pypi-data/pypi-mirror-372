import base64
import codecs
import logging
import requests
from copy import deepcopy
from urllib import request
from socket import timeout
from functools import wraps
from collections import deque
from datetime import datetime
from pydantic import BaseModel
from urllib.error import HTTPError, URLError
from pydantic.alias_generators import to_camel
from typing import Any, Callable, List, Literal, Optional, TypeAlias, TypeVar
from urllib.parse import urlencode, urlunparse
from yarik_django_airflow_api_manager.conf.settings import (
    AIRFLOW_HOST,
    AIRFLOW_PORT,
    AIRFLOW_USER,
    AIRFLOW_PSWD,
    AIRFLOW_BASE_URL,
)

logger = logging.getLogger(__name__)

AIRFLOW_AUTH = (AIRFLOW_USER, AIRFLOW_PSWD)

URL_SCHEME = "http"
URL_NETLOC = f"{AIRFLOW_HOST}:{AIRFLOW_PORT}"
URL_PATH = f"{AIRFLOW_BASE_URL}/api/v1/"


HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
CONN_TIMEOUT = 10

COMMON_REQUEST_PARAMS: dict[str, Any] = {
    "headers": HEADERS,
    "auth": AIRFLOW_AUTH,
    "timeout": CONN_TIMEOUT,
}


class Components(BaseModel):
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str

    @property
    def components(self):
        return (
            self.scheme,
            self.netloc,
            self.path,
            self.params,
            self.query,
            self.fragment,
        )


RunType: TypeAlias = Literal["backfill", "manual", "scheduled", "dataset_triggered"]
DagState: TypeAlias = Literal["queued", "running", "success", "failed"]
TaskState: TypeAlias = Literal[
    "success",
    "running",
    "failed",
    "upstream_failed",
    "skipped",
    "up_for_retry",
    "up_for_reschedule",
    "queued",
    "none",
    "scheduled",
    "deferred",
    "removed",
    "restarting",
]
TriggerRule: TypeAlias = Literal[
    "all_success",
    "all_failed",
    "all_done",
    "one_success",
    "one_failed",
    "none_failed",
    "none_skipped",
    "none_failed_or_skipped",
    "none_failed_min_one_success",
    "dummy",
]


class ModelWithAliasGenerator(BaseModel):

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class SLAMiss(BaseModel):
    task_id: str
    dag_id: str
    execution_date: datetime
    email_sent: bool
    timestamp: datetime
    description: Optional[str] = None
    notification_sent: bool


class Trigger(BaseModel):
    id: int
    classpath: str
    kwargs: str
    created_date: datetime
    trigger_id: Optional[int] = None


class Job(BaseModel):
    id: int
    dag_id: Optional[str] = None
    state: Optional[str] = None
    job_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    latest_heartbeat: Optional[datetime] = None
    executor_class: Optional[str] = None
    hostname: Optional[str] = None
    unixname: Optional[str] = None


class Tag(BaseModel):
    name: str


class Dag(ModelWithAliasGenerator):
    dag_id: str
    root_dag_id: Optional[str] = None
    is_paused: Optional[bool] = None
    is_active: Optional[bool] = None
    is_subdag: bool
    last_parsed_time: Optional[datetime] = None
    last_pickled: Optional[datetime] = None
    last_expired: Optional[datetime] = None
    scheduler_lock: Optional[bool] = None
    pickle_id: Optional[str] = None
    default_view: Optional[str] = None
    fileloc: str
    file_token: str
    owners: List[str]
    description: Optional[str] = None
    schedule_interval: Optional[Any] = None
    timetable_description: Optional[str] = None
    tags: Optional[List[Tag]] = None
    max_active_tasks: Optional[int] = None
    max_active_runs: Optional[int] = None
    has_task_concurrency_limits: Optional[bool] = None
    has_import_errors: Optional[bool] = None
    next_dagrun: Optional[datetime] = None
    next_dagrun_data_interval_start: Optional[datetime] = None
    next_dagrun_data_interval_end: Optional[datetime] = None
    next_dagrun_create_after: Optional[datetime] = None
    max_consecutive_failed_dag_runs: Optional[int] = None


class Dags(ModelWithAliasGenerator):
    dags: List[Dag]
    total_entries: int


class DagRun(ModelWithAliasGenerator):
    dag_run_id: Optional[str] = None
    dag_id: str
    logical_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    data_interval_start: Optional[datetime] = None
    data_interval_end: Optional[datetime] = None
    last_scheduling_decision: Optional[datetime] = None
    run_type: RunType
    state: DagState
    external_trigger: bool
    conf: dict[str, Any]
    note: Optional[str] = None


class DagRuns(ModelWithAliasGenerator):
    dag_runs: List[DagRun]
    total_entries: int


class Task(ModelWithAliasGenerator):
    class_ref: Any
    task_id: str
    owner: str
    start_date: datetime
    end_date: Optional[datetime] = None
    trigger_rule: TriggerRule
    extra_links: list[Any]
    depends_on_past: bool
    is_mapped: bool
    wait_for_downstream: bool
    retries: int
    queue: Optional[str] = None
    pool: str
    pool_slots: int
    execution_timeout: Any
    retry_delay: Any
    retry_exponential_backoff: bool
    priority_weight: int
    weight_rule: Literal["downstream", "upstream", "absolute"]
    ui_color: str
    ui_fgcolor: str
    template_fields: list[str]
    sub_dag: Optional[Dag] = None
    downstream_task_ids: list[str]


class Tasks(ModelWithAliasGenerator):
    tasks: list[Task]


class TaskInstance(ModelWithAliasGenerator):
    task_id: str
    dag_id: str
    dag_run_id: str
    execution_date: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration: Optional[float] = None
    state: Optional[TaskState] = None
    try_number: int
    map_index: int
    max_tries: int
    hostname: str
    unixname: str
    pool: str
    pool_slots: int
    queue: Optional[str]
    priority_weight: Optional[int] = None
    operator: Optional[str] = None
    queued_when: Optional[str] = None
    pid: Optional[int] = None
    executor_config: str
    sla_miss: Optional[SLAMiss] = None
    rendered_fields: dict[str, Any]
    trigger: Optional[Trigger] = None
    triggerer_job: Optional[Job] = None
    note: Optional[str] = None


class TaskInstances(ModelWithAliasGenerator):
    task_instances: List[TaskInstance]
    total_entries: int


class Logs(ModelWithAliasGenerator):
    continuation_token: str
    content: str


class ErrorResponce(ModelWithAliasGenerator):
    type: str
    title: Optional[str]
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None


RT = TypeVar("RT")


def catch_airflow_errors() -> (
    Callable[[Callable[..., RT | None]], Callable[..., RT | None]]
):
    """Декоратор перехватывает все исключения при работе с Airflow и логирует причину ошибки.

    Returns:
        out: `Any | None`
            Возвращаемое значение оборачиваемой функции или None в случае ошибки.
    """

    def decorator(func: Callable[..., RT | None]) -> Callable[..., RT | None]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            try:
                return func(*args, **kwargs)
            except ConnectionError as e:
                logger.error(f"Ошибка соединения с Airflow: {e}")
                logger.debug(e)
                return None
            except URLError as e:
                if isinstance(e.reason, timeout):
                    logger.error(
                        f"Превышено время ожидания ответа от Airflow {e.reason}"
                    )
                else:
                    logger.error(f"Не удаётся разрешить URL Airflow {e.reason}")
                logger.debug(e)
                return None
            except requests.Timeout as e:
                logger.error(
                    "Ошибка при выполнении запроса к Airflow: превышено время ожидания запроса"
                )
                return None
            except requests.RequestException as e:
                if isinstance(e.args[0], ErrorResponce):
                    logger.error(
                        f"Ошибка при выполнении запроса к Airflow, причина: {e.args[0].status} {e.args[0].title}. {e.args[0].type}"
                    )
                else:
                    logger.error(f"Ошибка при выполнении запроса к Airflow: {e.args}")
                return None
            except Exception as e:
                logger.error(
                    f"Неизвестная ошибка при работе менеджера соединений Airflow API {e.args}"
                )
                logger.debug(e)
                return None

        return wrapper

    return decorator


def get_request(url: str):
    responce = requests.get(url, **COMMON_REQUEST_PARAMS)

    if responce.status_code == requests.codes["ok"]:
        return responce
    else:
        raise requests.RequestException(ErrorResponce(**responce.json()))


def post_request(url: str, payload: Any | None = None):
    responce = requests.post(url, json=payload, **COMMON_REQUEST_PARAMS)

    if responce.status_code == requests.codes["ok"]:
        return responce
    else:
        raise requests.RequestException(ErrorResponce(**responce.json()))


def patch_request(url: str, payload: Any | None = None):
    responce = requests.patch(url, json=payload, **COMMON_REQUEST_PARAMS)

    if responce.status_code == requests.codes["ok"]:
        return responce
    else:
        raise requests.RequestException(ErrorResponce(**responce.json()))


class AirflowManager:
    """Интерфейс для работы с Airflow"""

    def __init__(self, dag_id: Optional[str] = None, dag_run_id: Optional[str] = None):
        """Инициализация экземпляра интерфейса для работы с Airflow

        Args:
            dag_id (Optional[str], optional): идентификатор дага. По умолчанию None.
            dag_run_id (Optional[str], optional): идентификатор запуска дага. По умолчанию None.
        """
        self.url = Components(
            scheme=URL_SCHEME,
            netloc=URL_NETLOC,
            path=AIRFLOW_BASE_URL,
            params="",
            query="",
            fragment="",
        )
        self.url.path = URL_PATH
        self.dag_id = dag_id
        self.dag_run_id = dag_run_id

    def conn_good(self):
        """Проверяет соединение с Airflow

        Возвращает:
            bool: доступность Airflow
        """
        url = Components(
            scheme=URL_SCHEME,
            netloc=URL_NETLOC,
            path=AIRFLOW_BASE_URL,
            params="",
            query="",
            fragment="",
        )
        # Проверка соединения
        logger.debug(urlunparse(url.components))
        try:
            request.urlopen(urlunparse(url.components), timeout=CONN_TIMEOUT)
        except ConnectionError as e:
            logger.error(f"Ошибка соединения с Airflow: {e}")
            logger.debug(e)
            return False
        except URLError as e:
            if isinstance(e.reason, timeout):
                logger.error(f"Превышено время ожидания ответа от Airflow {e.reason}")
            else:
                logger.error(f"Не удаётся разрешить URL Airflow {e.reason}")
            logger.debug(e)
            return False
        except TimeoutError as e:
            logger.error("Превышено время ожидания ответа от Airflow")
            return False
        except Exception as e:
            logger.error(
                f"Неизвестная ошибка при проверке соединения с Airflow {e.args}"
            )
            logger.debug(e)
            return False
        return True

    def creds_is_valid(self):
        """Проверяет корректность учетных данных пользователя API

        Returns:
            bool: корректность учетных данных
        """
        try:
            url = deepcopy(self.url)
            url.path += "dags?limit=0"
            req = request.Request(urlunparse(url.components))
            base64string = base64.b64encode(bytes("%s:%s" % AIRFLOW_AUTH, "ascii"))
            req.add_header("Authorization", "Basic %s" % base64string.decode("utf-8"))
            request.urlopen(req, timeout=CONN_TIMEOUT)
        except HTTPError as e:
            logger.error("Учётные данные пользователя Airflow API некорректны")
            return False
        except URLError as e:
            if isinstance(e.reason, timeout):
                logger.error(f"Превышено время ожидания ответа от Airflow {e.reason}")
            else:
                logger.error(f"Не удаётся разрешить URL Airflow {e.reason}")
            logger.debug(e)
            return False
        except Exception as e:
            logger.error(
                f"Не удалось проверить учетные данные пользователя Airflow API {e.args}"
            )
            logger.debug(e)
            return False
        return True

    @catch_airflow_errors()
    def get_dag(self) -> Optional[Dag]:
        """Получить даг

        Возвращает:
            Dag | None: объект дага или None в случае ошибки
        """
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}"

        dag = Dag(**(get_request(urlunparse(url.components)).json()))

        return dag

    @catch_airflow_errors()
    def get_dags_dict(
        self,
        tags: list[str] = [],
        dag_id_pattern: str = "",
        only_active: bool = True,
        limit: int = 100,
        offset: int = 0,
        fields: Optional[list[str]] = None,
    ) -> Optional[dict[str, Any]]:
        """Получить даги в формате словаря

        Возвращает:
            dict | None: словарь дага или None в случае ошибки
        """
        url = deepcopy(self.url)
        query_dict: dict[str, Any] = {
            "tags": ",".join(tags) if len(tags) > 0 else None,
            "dag_id_pattern": dag_id_pattern if len(dag_id_pattern) > 0 else "",
            "only_active": only_active,
            "limit": limit,
            "offset": offset,
        }
        if fields:
            query_dict["fields"] = fields
        url.query = urlencode(query_dict)

        url.path += "dags"
        dags = get_request(urlunparse(url.components)).json()

        return dags

    @catch_airflow_errors()
    def get_dags(
        self,
        tags: list[str] = [],
        dag_id_pattern: str = "",
        only_active: bool = True,
        limit: int = 100,
        offset: int = 0,
        fields: Optional[list[str]] = None,
    ) -> Optional[Dags]:
        """Получить даги

        Аргументы:
            tags (list[str], optional): список тегов дага. По умолчанию [].
            dag_id_pattern (str, optional): паттерн идентификатора дага. По умолчанию "".
            only_active (bool, optional): учитывать только активные даги. По умолчанию True.
            limit (int, optional): лимит количества получаемых дагов. Defaults to 100.
            offset (int, optional): позиция, с которой нужно вернуть даги. Defaults to 0.
            fields (list[str] | None, optional): список запрашиваемых полей дага. Defaults to None.

        Возвращает:
            Dags: объект списка дагов или None в случае ошибки
        """
        dct = self.get_dags_dict(
            tags, dag_id_pattern, only_active, limit, offset, fields
        )
        if not dct:
            return None
        return Dags(**dct)

    @catch_airflow_errors()
    def get_dags_count(
        self,
        tags: list[str] = [],
        dag_id_pattern: str = "",
        only_active: bool = True,
    ) -> int:
        """Получить количество дагов

        Аргументы:
            tags (list[str], optional): список тегов дага. По умолчанию [].
            dag_id_pattern (str, optional): паттерн идентификатора дага. По умолчанию "".
            only_active (bool, optional): учитывать только активные даги. По умолчанию True.

        Возвращает:
            int: количество дагов
        """
        dct = self.get_dags_dict(tags, dag_id_pattern, only_active, 1, 0)
        if not dct:
            return 0
        dags = Dags(**dct)
        return dags.total_entries if dags else 0

    @catch_airflow_errors()
    def get_dag_runs(
        self, states: Optional[List[DagState]] = None
    ) -> Optional[List[DagRun]]:
        """Получить список запусков дага 

        Аргументы:
            state (List[DagState] | None, optional): список кодов состояния запусков дага. По умолчанию None.

        Возвращает:
            List[DagRun] | None: список запусков дага или None в случае ошибки
        """
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns"
        query: dict[str, Any] = {"limit": 100, "order_by": "-execution_date"}
        if states and len(states) > 0:
            query["state"] = ",".join(states)

        url.query = urlencode(query)

        dag_runs = DagRuns(**(get_request(urlunparse(url.components)).json()))

        return dag_runs.dag_runs

    @catch_airflow_errors()
    def get_dag_runs_batch(
        self,
        dag_ids: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Optional[DagRuns]:
        """Получить список запусков дага по нескольким dag_id

        Аргументы:
            dag_ids (List[str] | None, optional): список идентификаторов дагов. По умолчанию None.

        Возвращает:
            DagRuns | None: список запусков дага или None в случае ошибки
        """
        url = deepcopy(self.url)
        url.path += "dags/~/dagRuns/list"
        payload: dict[str, Any] = {
            "dag_ids": dag_ids,
            "limit": limit,
            "offset": offset,
        }

        dag_runs = DagRuns(
            **(post_request(urlunparse(url.components), payload=payload).json())
        )

        return dag_runs

    @catch_airflow_errors()
    def get_last_dag_run(self, username: Optional[str] = None) -> Optional[DagRun]:
        """Получить список запусков дага

        Аргументы:
            username (Optional[str], optional): Имя пользователя системы, для которого нужно получить последний запуск дага. По умолчанию None.

        Возвращает:
            List[DagRun] | None: список запусков дага или None в случае ошибки
        """
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns"

        dag_run = None
        if username:
            url.query = urlencode({"limit": 10, "order_by": "-execution_date"})
            dag_runs = DagRuns(**(get_request(urlunparse(url.components)).json()))

            dag_run = next(
                (
                    d
                    for d in dag_runs.dag_runs
                    if "run_username" in d.conf and d.conf["run_username"] == username
                ),
                None,
            )
            if not dag_run:
                for offset in range(10, dag_runs.total_entries, 10):
                    url.query = urlencode(
                        {"limit": 10, "offset": offset, "order_by": "-execution_date"}
                    )
                    dag_runs = DagRuns(
                        **(get_request(urlunparse(url.components)).json())
                    ).dag_runs
                    dag_run = next(
                        (
                            d
                            for d in dag_runs
                            if "run_username" in d.conf and d.conf["run_username"] == username
                        ),
                        None,
                    )
                    if dag_run:
                        break

        else:
            url.query = urlencode({"limit": 1, "order_by": "-execution_date"})
            dag_runs = DagRuns(
                **(get_request(urlunparse(url.components)).json())
            ).dag_runs
            if len(dag_runs) > 0:
                dag_run = dag_runs[0]

        if dag_run:
            self.dag_run_id = dag_run.dag_run_id

        return dag_run

    @catch_airflow_errors()
    def get_current_dag_run(self) -> Optional[DagRun]:
        """Получить текущий запуск дага

        Возвращает:
            DagRun | None: объект текущего запуска дага или None в случае ошибки
        """
        if self.dag_run_id is None:
            return None

        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}"

        return DagRun(**(get_request(urlunparse(url.components)).json()))

    @catch_airflow_errors()
    def trigger(self, conf: Optional[dict[str, Any]] = {}) -> Optional[DagRun]:
        """Запустить даг

        Аргументы:
            conf (dict[str, Any], {}): параметры запуска дага. По умолчанию {}.

        Возвращает:
            DagRun | None: объект нового запуска дага или None в случае ошибки
        """
        if conf is None:
            conf = {}

        payload = {
            "conf": conf,
        }
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns"

        dag_run = DagRun(
            **(post_request(urlunparse(url.components), payload=payload).json())
        )

        self.dag_run_id = dag_run.dag_run_id

        return dag_run

    @catch_airflow_errors()
    def stop(self) -> Optional[DagRun]:
        """Остановить выполнение запущенного дага

        Возвращает:
            DagRun | None: объект остановленного дага или None в случае ошибки
        """
        payload = {
            "state": "failed",
        }
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}"

        dag_run = DagRun(
            **(patch_request(urlunparse(url.components), payload=payload).json())
        )

        return dag_run

    @catch_airflow_errors()
    def clear(self) -> Optional[DagRun]:
        """Очистить все экземпляры задач текущего запуска дага

        Возвращает:
            DagRun | None: объект очищенного запуска дага или None в случае ошибки
        """
        payload = {
            "dry_run": False,
        }
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}/clear"

        dag_run = DagRun(
            **(post_request(urlunparse(url.components), payload=payload).json())
        )

        return dag_run

    @catch_airflow_errors()
    def get_task_instances(self) -> Optional[TaskInstances]:
        """Получить все экземпляры задач текущего запуска дага

        Возвращает:
            TaskInstances | None: список экземпляров задач текущего запуска дага или None в случае ошибки
        """
        if self.dag_run_id is None:
            return None

        # Упорядочить задачи, топологическая сортировка Кана
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/tasks"

        dag_tasks = Tasks(**(get_request(urlunparse(url.components)).json())).tasks

        graph: dict[str, list[str]] = {}
        indegree: dict[str, int] = {}

        for task in dag_tasks:
            task_id = task.task_id
            graph[task_id] = task.downstream_task_ids
            indegree[task_id] = 0

        for task_id, downstreams in graph.items():
            for down in downstreams:
                indegree[down] += 1

        queue = deque([task_id for task_id in indegree if indegree[task_id] == 0])
        topological_order: list[str] = []

        while queue:
            task_id = queue.popleft()
            topological_order.append(task_id)
            for down in graph[task_id]:
                indegree[down] -= 1
                if indegree[down] == 0:
                    queue.append(down)

        # Получить экземпляры задач
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}/taskInstances"

        task_instances = TaskInstances(
            **(get_request(urlunparse(url.components)).json())
        )

        task_instances.task_instances.sort(
            key=lambda ti: topological_order.index(ti.task_id)
        )

        return task_instances

    @catch_airflow_errors()
    def get_task_instance(self, task_id: str) -> Optional[TaskInstance]:
        """Получить все экземпляры задач текущего запуска дага

        Аргументы:
            task_id (str): идентификатор задачи дага

        Возвращает:
            TaskInstance | None: экземпляр задачи текущего запуска дага или None в случае ошибки
        """
        if self.dag_run_id is None:
            return None

        url = deepcopy(self.url)
        url.path += (
            f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}/taskInstances/{task_id}"
        )

        return TaskInstance(**(get_request(urlunparse(url.components)).json()))

    @catch_airflow_errors()
    def get_logs(
        self, task_id: str, try_num: int, continuation_token: str | None = None
    ) -> Optional[Logs]:
        """Получить логи экземпляра задачи текущего запуска дага

        Аргументы:
            task_id (str): идентификатор задачи дага
            try_num (int): номер попытки выполнения задачи
            continuation_token (str | None, optional): токен для слежения за логами. По умолчанию None.

        Returns:
            Logs | None: логи экземпляра задачи текущего запуска дага или None в случае ошибки
        """
        if self.dag_run_id is None:
            return None

        url = deepcopy(self.url)
        query: dict[str, Any] = {"full_content": continuation_token is None}
        if continuation_token is not None:
            query["token"] = continuation_token
        url.query = urlencode(query)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}/taskInstances/{task_id}/logs/{try_num}"

        logs = Logs(**(get_request(urlunparse(url.components)).json()))

        escape_decoded = codecs.escape_decode(bytes(logs.content, "utf-8"))[0]
        if not isinstance(escape_decoded, bytes):
            return None

        logs.content = escape_decoded.decode("utf-8")

        ws_index = logs.content.find(" ")
        first_quot_pos = ws_index + 1
        if logs.content[first_quot_pos] == "'":
            second_quot_pos = logs.content.rfind("'")
        else:
            second_quot_pos = logs.content.rfind('"')

        logs.content = logs.content[first_quot_pos + 1 : second_quot_pos]

        return logs
