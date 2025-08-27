"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/9 10:32
@file: services.py
@project: django_aeotrade_connector
@describe: Aeotrade Connector common services
"""
import time
from abc import ABC, abstractmethod
from typing import Any, Optional, Type, Union

from django.conf import settings
from httpx import Response

from aeotrade_connector.http_client import (AsyncHttpClient,
                                            AsyncHttpClientResponse,
                                            SyncHttpClient)
from aeotrade_connector.models import ConnectorTask as TaskORM
from aeotrade_connector.models import ConnectorTaskLog as TaskLogORM
from aeotrade_connector.mq.manager import MQManager
from aeotrade_connector.schemas import RWModel
from aeotrade_connector.schemas.connector_services import (
    CommonApiPath, HeartbeatRequestBody, StatusReportRequestBody)
from aeotrade_connector.utils import logger


class ConnectorServices(ABC):
    # Implement the common parts in the connector development specification, where documents from:
    # https://login.dingtalk.com/oauth2/challenge.htm?redirect_uri=https%3A%2F%2Falidocs.dingtalk.com%2Fi%2Fnodes%2FxdqZp24KneBJzKe0ZLBo8vyb7RA0Nr1E%3Futm_scene%3Dteam_space%26utm_medium%3Dmain_vertical%26utm_source%3Dsearch%26dontjump%3Dtrue&response_type=none&client_id=dingoaxhhpeq7is6j1sapz&scope=openid&tmpCode=crossContainer%3ABCA54205E7ED41298AAC7801E77486FA%3AMTgyNTkxNzEwNw

    connector_code: str
    management_endpoint = settings.AC_MANAGEMENT_ENDPOINT
    ApiPath: Type[CommonApiPath] = CommonApiPath
    MAX_PRINT_COUNT = 720
    heartbeat_count = 0

    @classmethod
    def print_or_not(cls, ok: bool, res: Union[AsyncHttpClientResponse, Response, str], dial_from: str = ""):
        # Count the number of heartbeat execute times
        cls.heartbeat_count = (cls.heartbeat_count + 1) % cls.MAX_PRINT_COUNT

        if cls.heartbeat_count == 1:  # Move the count check to reduce nesting
            if not ok:
                logger.error(f"[ConnectorServices] {dial_from} error: {res}")
                return

            res_json = res.json()  # type: ignore[attr-defined, union-attr]
            if res_json.get("code") != 0:
                logger.error(f"[ConnectorServices] {dial_from} successful, but response error: {res_json}")
            else:
                logger.info(f"[ConnectorServices] {dial_from} successful")

    @classmethod
    def heartbeat(cls, *args, **kwargs):
        """Heartbeat."""
        body = HeartbeatRequestBody(connector_code=cls.connector_code)
        heartbeat_url = cls.management_endpoint + cls.ApiPath.HeartBeat.value
        with SyncHttpClient() as client:
            ok, res = client.post(
                url=heartbeat_url,
                json=body  # noqa
            )
            cls.print_or_not(ok, res, "Heartbeat")

    @classmethod
    async def aheartbeat(cls):
        """Async heartbeat."""
        body = HeartbeatRequestBody(connector_code=cls.connector_code)
        heartbeat_url = cls.management_endpoint + cls.ApiPath.HeartBeat.value
        async with AsyncHttpClient() as client:
            ok, res = await client.post(
                url=heartbeat_url,
                json=body
            )
            cls.print_or_not(ok, res, "Async Heartbeat")

    @classmethod
    def task_status_report(cls, body: StatusReportRequestBody):
        """Task status report"""
        report_url = settings.AC_MANAGEMENT_ENDPOINT + cls.ApiPath.TaskStatusReport.value
        with SyncHttpClient() as client:
            for _ in range(3):
                ok, res = client.post(
                    url=report_url,
                    json=body
                )
                if not ok:
                    logger.error(f"[ConnectorServices] task status report error, request not ok: {res}, "
                                 f"\nbody: {body.to_dict()}")
                    time.sleep(1)
                    continue
                else:
                    if res.json().get("code") != 0:
                        logger.error(f"[ConnectorServices] task status report error, "
                                     f"response status not equals 0: {res.json()}, \nbody: {body.to_dict()}")
                    return res
            else:
                logger.error(f"[ConnectorServices] task status report error: {res}, \nbody: {body.to_dict()}")
                return res

    @classmethod
    @abstractmethod
    async def params_check(cls, task: TaskORM, dxp_message: dict) -> Type[RWModel]:
        """
        Verify the legality of the parameters required for business processing
        :param task: TaskORM
        :param dxp_message: Dxp message in message queue
        :return: A Type[RWModel]
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def execute(cls, model_data: Type[RWModel]) -> Any:
        """
        Business processing here
        :param model_data:
        :return:
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def response_handler(cls, response: Any, task: TaskORM, task_log: TaskLogORM) -> Optional[str]:
        """
        Business result processing, if necessary, you can call the 'task_status_report' function
        to report the task execution status
        :param task_log: TaskLogORM
        :param response: The result of business processing from `cls.execute` method
        :param task: TaskORM
        :return:
        """

        raise NotImplementedError

    @classmethod
    async def publish(cls, message: str, mq_manager: MQManager) -> None:
        async with mq_manager.mq_client.manage(wait_for_tasks=False) as client:  # type: ignore[attr-defined]
            await client.publish(message)

    @classmethod
    async def up_chain(cls):
        pass
