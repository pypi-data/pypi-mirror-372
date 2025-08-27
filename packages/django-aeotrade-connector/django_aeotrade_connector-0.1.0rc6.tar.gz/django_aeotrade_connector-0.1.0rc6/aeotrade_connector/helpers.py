"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/11 11:14
@file: helpers.py
@project: django_aeotrade_connector
@describe: None
"""
import importlib
import time
from typing import Any, Callable, Dict, List, Optional, Type, Union, cast
from urllib.parse import urlparse

import redis  # type: ignore[import-untyped]
from apscheduler.jobstores.redis import RedisJobStore
from django.utils import timezone

from aeotrade_connector.db.choices import TaskStatus
from aeotrade_connector.decorators import cache_result
from aeotrade_connector.exceptions import (DataNotExistsException,
                                           DataOperationFailedException,
                                           TaskServicesNotFoundException)
from aeotrade_connector.models import ConnectorTask as TaskORM
from aeotrade_connector.mq.manager import MQManager
from aeotrade_connector.schemas.common import (ConnectorCacheKey,
                                               ConnectorConfig,
                                               MQManagerConfig)
from aeotrade_connector.schemas.connector_services import \
    StatusReportRequestBody
from aeotrade_connector.simple_cache import simple_cache as cache
from aeotrade_connector.utils import logger


@cache_result
def connector_code_mapping():
    """
    :return eg: {"ai_connector_code": "ai_connector"}
    """
    ret = {}
    connector_config = cache.getf(ConnectorCacheKey.Config.value)
    for connector_name, config in connector_config.items():
        config = cast(ConnectorConfig, config)
        ret[config.code] = config.name
    return ret


def connector_mapping(key: str):
    ret = {}
    cache_data = cache.getf(key)
    for connector_name, obj in cache_data.items():
        if isinstance(obj, str):
            ret[connector_name] = importlib.import_module(obj)
        else:
            ret[connector_name] = obj
    return ret


@cache_result
def connector_views_mapping():
    """
    :return eg: {"ai_connector": "ai_connector.views"}
    """
    return connector_mapping(ConnectorCacheKey.Views.value)


@cache_result
def connector_services_mapping():
    return connector_mapping(ConnectorCacheKey.Services.value)


def get_app_services(connector_name: str, connector_code: str, **kwargs):
    services_module = connector_services_mapping()[connector_name]
    if not services_module:
        logger.error(f"[Aeotrade Connector] `{connector_name}` App services not found")
        raise TaskServicesNotFoundException(f"`{connector_name}` App services not found")
    from aeotrade_connector.services import ConnectorServices
    services_module = cast(Type[ConnectorServices], services_module)

    services = services_module
    setattr(services, "connector_code", connector_code)
    for k, v in kwargs.items():
        setattr(services, k, v)
    return services


def task_status_update(
        task: Union[str, TaskORM, None],
        *,
        status: str,
        allowed_status: Union[List[str], str] = "*",
        err_msg: Optional[str] = None,
        call: Optional[Callable] = None,
        code: int = 0,
        **kwargs
) -> TaskORM:
    """
    Update connector task`s status
    :param err_msg: Error message
    :param task: Accept task_id or TaskORM
    :param status: The status will be changed for
    :param allowed_status: The allowed status, "*" means all status
    :param call: Extra validate callback
    :param code: Status code, 0 means success
    :return: TaskORM
    """
    if task is None:
        raise DataNotExistsException

    if isinstance(task, str):
        _task = TaskORM.objects.filter(task_id=task, is_deleted=False).first()
        if not _task:
            raise DataNotExistsException
    elif isinstance(task, TaskORM):
        _task = task
    else:
        raise DataNotExistsException

    if allowed_status == "*":
        allowed_status = [status for status, _ in TaskStatus.Choices]

    if _task.status not in allowed_status:
        logger.info(f"[Aeotrade Connector] Task[{_task.task_id}] status {_task.status} "
                    f"not in allowed status {allowed_status}")
        raise DataOperationFailedException("当前状态不允许更新")

    try:
        if call:
            call(task, **kwargs)

        _task.status = status
        _task.status_update_at = timezone.now()
        _task.err_msg = err_msg if err_msg else ""
        _task.save()

        if status != TaskStatus.Default:
            body = StatusReportRequestBody(
                task_id=_task.task_id,
                code=code,
                task_status=status,
            )
            services = get_app_services(connector_name=_task.task_from, connector_code=_task.connector_code)
            services.task_status_report(body=body)

    except Exception as e:
        logger.exception(f"[Aeotrade Connector] Update task status error: {e}")
        raise DataOperationFailedException("状态更新失败")

    return _task


def scheduler_initialize():
    import sys

    from django.conf import settings

    from aeotrade_connector.management.commands.initconnector import style

    django_cache = getattr(settings, "CACHES", None)

    if not django_cache:
        sys.stdout.write(style.ERROR("[Aeotrade Connector]-[Crontab] missing to set `CACHES` in django.settings"))
        sys.exit(17)

    db_aliases = [alias for alias in django_cache.keys()]

    if not db_aliases:
        sys.stdout.write(style.ERROR("[Aeotrade Connector]-[Crontab] missing to set db alias in django.settings.CACHE"))
        sys.exit(17)
    db_alias = "connector" if "connector" in db_aliases else db_aliases[0]
    db_config = django_cache[db_alias]
    redis_location = db_config.get("LOCATION", None)
    redis_options = db_config.get("OPTIONS", {})

    parsed_url = urlparse(redis_location)
    redis_host = parsed_url.hostname
    redis_port = parsed_url.port
    redis_db = str(parsed_url.path).lstrip('/')

    connection_pool_kwargs = redis_options.get('CONNECTION_POOL_KWARGS', {})

    redis_client_kwargs = {
        "host": redis_host, "port": redis_port, "db": int(redis_db), **connection_pool_kwargs
    }

    jobstores = {
        'default': RedisJobStore(**redis_client_kwargs)
    }

    return jobstores, redis_client_kwargs


class RedisLock:
    def __init__(self, lock_name, expire_time=180):
        """
        初始化 Redis 锁对象。
        :param lock_name: 锁的名称，保证唯一性
        :param expire_time: 锁的过期时间，单位为秒，默认 60 秒
        """
        self.lock_name = lock_name
        self.expire_time = expire_time
        self.redis_client = self.get_redis_client()

    def get_redis_client(self):
        redis_kwargs = scheduler_initialize()[1]
        return redis.StrictRedis(**redis_kwargs)

    def acquire(self):
        """
        尝试获取锁。
        :return: True 如果获取锁成功，False 如果获取锁失败。
        """
        # 使用 SETNX 命令设置锁，只有当键不存在时才会设置成功
        result = self.redis_client.setnx(self.lock_name, "locked")
        if result:
            # 设置锁的过期时间，防止死锁
            self.redis_client.expire(self.lock_name, self.expire_time)
        return result

    def release(self):
        """
        Release lock
        :return: None
        """
        self.redis_client.delete(self.lock_name)

    def is_locked(self):
        """
        Check if the lock exists.
        :return: True, exists, False, not exists
        """
        return self.redis_client.exists(self.lock_name)


def job_lock(*args, **kwargs):
    connector_task_id = kwargs.pop("Y29ubmVjdG9yX3Rhc2tfaWQ=")
    func = kwargs.pop("func")
    lock = RedisLock(connector_task_id)

    # Task is running, skip the current task
    if lock.is_locked():
        time.sleep(0.1)
        return

    # Get lock failed, skip the current task
    if not lock.acquire():
        time.sleep(0.1)
        return

    start_at = time.time() * 1000
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.exception(f"[AeotradeConnector] [Crontab] An error occurred: {e}")
    finally:
        # In order to solve the problem of task execution being too fast,
        # other worker processes obtained locks and added a delay of 20ms
        cost = time.time() * 1000 - start_at
        if cost < 20:  # 20ms
            time.sleep((20 - cost) / 100)

        lock.release()


def build_mq_client(task: TaskORM):
    def build_url(config: Dict[str, Any]) -> str:
        return (f"amqp://{config.get('user', '')}:{config.get('pwd', '')}@{config.get('host', '')}:"
                f"{config.get('port', '')}/{config.get('virtual_host', '')}")

    transfer_send_config = task.transfer_send_config
    transfer_send_config["url"] = build_url(transfer_send_config)
    mq_config = MQManagerConfig(**transfer_send_config)

    try:
        mq_manager = MQManager(**mq_config.to_dict(), ensure_client=True)
    except Exception as e:
        err_msg = f"[build_mq_client] An error occurred: {e}, task: {task}"
        logger.error(err_msg)
        return
    return mq_manager
