"""
@company: 慧贸天下(北京)科技有限公司
@author: zfj@aeotrade.com
@time: 2025/03/18 14:15
@file: factory.py
@project: django_aeotrade_connector
@describe: Base class for MQ Manager and dynamic loading of MQ classes from installed apps.
"""
import logging
from typing import Union, Optional
from importlib import import_module
from django.apps import apps

from aeotrade_connector.mq.manager import MQManager
from aeotrade_connector.schemas.common import MQType, POT
from .rabbitmq import RabbitMQManager


logger = logging.getLogger(__name__)


class MQManagerFactory:
    """Factory class to create MQ Managers based on MQ type."""

    _mq_manager_classes = None

    @classmethod
    def _discover_mq_manager_classes(cls):
        """Discover MQ manager classes from installed apps."""
        if cls._mq_manager_classes is not None:
            return cls._mq_manager_classes

        cls._mq_manager_classes = {}
        for app_config in apps.get_app_configs():
            try:
                # Attempt to import the mq.managers module from the app
                managers_module = import_module(f"{app_config.name}.mq.managers")
                for name, obj in managers_module.__dict__.items():
                    if isinstance(obj, type) and issubclass(obj, MQManager) and obj != MQManager:
                        # Ensure the class has a valid MQType
                        if hasattr(obj, 'mq_type') and isinstance(obj.mq_type, MQType):
                            cls._mq_manager_classes[obj.mq_type.name] = obj

            except ImportError:
                # If the module doesn't exist, skip this app
                continue

        return cls._mq_manager_classes

    @classmethod
    def create_mq_manager(
            cls,
            mq_type: Union[MQType, str],
            url: str,
            exchange: str,
            queue: str,
            routing_key: str,
            pot: POT = POT.Thread,
            ensure_client: bool = False,
            **kwargs,
    ) -> Optional[MQManager]:
        """
        Create an MQ Manager based on the MQ type.
        :param mq_type: MQ type (e.g., RabbitMQ, EMQ, Kafka)
        :param url: MQ URL
        :param exchange: MQ exchange
        :param queue: MQ queue
        :param routing_key: MQ routing key
        :param pot: Process or Thread
        :param ensure_client: Ensure client is initialized
        :param kwargs: Additional keyword arguments
        :return: MQManager instance
        """
        if isinstance(mq_type, str):
            mq_type = MQType.value_of(mq_type)

        # Discover and load MQ manager classes
        mq_manager_classes = cls._discover_mq_manager_classes()

        # Find the appropriate MQ manager class
        mq_manager_class = mq_manager_classes.get(mq_type.name, RabbitMQManager)
        if mq_manager_class is None:
            logger.error(f"[MQManagerFactory] No MQ manager found for type: {mq_type.name}")
            return None

        return mq_manager_class(
            url=url,
            exchange=exchange,
            queue=queue,
            routing_key=routing_key,
            pot=pot,
            ensure_client=ensure_client,
            **kwargs
        )


# Example usage
def get_mq_manager(mq_type: Union[MQType, str], **kwargs) -> MQManager:
    """Get an MQ Manager instance using dynamic discovery."""
    return MQManagerFactory.create_mq_manager(mq_type, **kwargs)
