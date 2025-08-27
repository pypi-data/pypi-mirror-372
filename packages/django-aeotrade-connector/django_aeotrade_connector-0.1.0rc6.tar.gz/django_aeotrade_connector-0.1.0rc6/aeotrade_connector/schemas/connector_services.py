"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/9 10:40
@file: connector_services.py
@project: django_aeotrade_connector
@describe: None
"""
from enum import Enum

from pydantic import Field

from aeotrade_connector.schemas import RWModel


class ConnectorCodeModel(RWModel):
    connector_code: str = Field(..., title="Connector Code", max_length=50)


class HeartbeatRequestBody(ConnectorCodeModel):
    pass


class CommonApiPath(Enum):
    # Heartbeat path
    HeartBeat = "/connector/api/connector-health"
    # Report the connector status to the connector management system
    TaskStatusReport = "/connector/api/org-connectors-task-status"

    @classmethod
    def value_of(cls, value: str) -> 'CommonApiPath':
        """
        Get value of given path.

        :param value: aeotrade-os path
        :return: CommonApiPath items
        """
        for path in cls:
            if path.value == value:
                return path
        raise ValueError(f'invalid aeotrade-os path value {value}')


class StatusReportRequestBody(RWModel):
    task_id: str = Field(..., title="任务ID", max_length=50)
    code: int = Field(default=0, title="任务状态编码")
    message: str = Field(default="", title="任务状态消息", max_length=10000)
    task_status: str = Field(default="", title="任务状态", max_length=50)
