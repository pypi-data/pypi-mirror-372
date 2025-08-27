"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/10 17:07
@file: common.py
@project: django_aeotrade_connector
@describe: None
"""
from enum import Enum
from typing import Callable, Optional

from pydantic import Field, model_validator
from typing_extensions import Self

from aeotrade_connector.schemas import RWModel


class ConnectorConfig(RWModel):
    name: str = Field(..., title="Connector Name", max_length=100)
    label: str = Field(..., title="Connector Label(Chinese)", max_length=100)
    code: str = Field(..., title="Connector Code", max_length=50)


class ConnectorCacheKey(Enum):
    Config = "connector_config"
    Views = "connector_views"
    Services = "connector_services"

    @classmethod
    def value_of(cls, value: str) -> 'ConnectorCacheKey':
        """
        Get value of given cache key.

        :param value: connector cache key
        :return: ConnectorCacheKey items
        """
        for path in cls:
            if path.value == value:
                return path
        raise ValueError(f'invalid connector cache key {value}')


class ConnectorRespStatus:
    Success = 0


class TaskParamsModel(RWModel):
    pass


class MQType(str, Enum):
    RabbitMQ = "RabbitMQ"

    @classmethod
    def value_of(cls, value: str) -> 'MQType':
        """
        Get value of given message queue key.

        :param value: message queue key
        :return: MQType items
        """
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f'invalid message queue key {value}')


# Process or Thread
class POT(str, Enum):
    Process = "process"
    Thread = "thread"

    @classmethod
    def value_of(cls, value: str) -> 'POT':
        """
        Get value of given pot key.

        :param value: pot key
        :return: POT items
        """
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f'invalid pot key {value}')


class Trigger(Enum):
    Interval = "interval"
    Date = "date"
    Cron = 'cron'


class MQManagerConfig(RWModel):
    url: str = Field(..., title="MQ URL to connect")
    exchange: str = Field(..., title="MQ exchange")
    queue: str = Field(..., title="MQ queue")
    mq_type: MQType = MQType.RabbitMQ
    pot: POT = POT.Process
    routing_key: Optional[str] = Field(default=None, title="MQ routing key")

    def validate_params(self) -> Self:
        if not all([self.url, self.exchange, self.queue, self.mq_type, self.pot, self.routing_key]):
            raise ValueError(
                "All fields (url, exchange, queue, mq_type, pot, routing_key) must be provided and non-empty.")
        return self

    @model_validator(mode="after")
    def validate_callback(self) -> Self:
        if not self.routing_key:
            self.routing_key = self.queue
        return self


class ConnectorBaseConfig(RWModel):
    name: str = Field(default="", title="Connector App Name", max_length=100)
    label: str = Field(..., title="Connector Label(Chinese)", max_length=100)
    code: str = Field(..., title="Connector Code", max_length=50)
    desc: str = Field(default="", title="Connector Description", max_length=1000)
    event_up_chain: bool = Field(default=False, title="Connector Event Up Chain")
    files_up_chain: bool = Field(default=False, title="Connector Files Up Chain")
    callback: Callable = Field(default=None, title="Connector Callback Function",
                               description="Connector Callback Function")
    callback_args: list = Field(default=[], title="Connector Callback Function Args")
    callback_kwargs: dict = Field(default={}, title="Connector Callback Function Kwargs")
    mq_recv_model: MQManagerConfig = Field(..., title="Connector MQ Config")
    task_stop_when_error: bool = Field(default=False, title="Connector Task Stop When Error")
    auto_heartbeat: bool = Field(default=True, title="Connector Auto Heartbeat")
    kw: dict = Field(default={}, title="Connector Keyword Args")

    @model_validator(mode="after")
    def validate_callback(self) -> Self:
        if not all([self.label, self.code, self.mq_recv_model]):
            raise ValueError(
                f"[{self.label}] All fields (label, code, mq_recv_model) must be provided and non-empty.")
        self.mq_recv_model = self.mq_recv_model.validate_params()
        return self


class EmptyModel(RWModel):
    pass
