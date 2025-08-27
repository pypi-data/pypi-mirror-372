"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/12 14:15
@file: manager.py
@project: django_aeotrade_connector
@describe: None
"""
import asyncio
import time
from typing import Callable, Union

from aeotrade_connector.mq.rabbitmq.client import (AsyncRabbitMQClient,
                                                   InvalidAMQPURLException)
from aeotrade_connector.schemas.common import POT, MQType
from aeotrade_connector.utils import logger


class MQManager:
    def __init__(
            self,
            *,
            url: str,
            exchange: str,
            queue: str,
            routing_key: str,
            mq_type: Union[MQType, str] = MQType.RabbitMQ,
            pot: POT = POT.Thread,
            ensure_client: bool = False,
            **kwargs,
    ):
        """
        MQ Manager
        :param url: MQ URL to connect
        :param exchange: MQ exchange
        :param queue: MQ queue
        :param mq_type: Supported RabbitMQ
        :param pot: Process or Thread to start listener
        :param kwargs: Additional keyword arguments
        """
        if kwargs is None:
            kwargs = {}

        if isinstance(mq_type, str):
            mq_type = MQType.value_of(mq_type)

        if isinstance(pot, str):
            pot = POT.value_of(pot)

        self.mq_type = mq_type
        self.pot = pot
        self.runner = None

        # mq config
        self.url = url
        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key

        # mq client
        self.mq_client = None
        self.kwargs = kwargs

        if ensure_client:
            self.ensure_client()

    def start(self):
        if self.mq_type == MQType.RabbitMQ:
            self.start_queue(self.queue_listener, True)
        else:
            raise InvalidAMQPURLException(f"[MQManager] Unsupported MQ type: {self.mq_type}")

    def ensure_client(self):
        if self.mq_client is None:
            self.get_mq_client()

    def get_mq_client(self):
        if self.mq_type == MQType.RabbitMQ:
            self.mq_client = AsyncRabbitMQClient(
                amqp_url=self.url,
                exchange_name=self.exchange,
                queue_name=self.queue,
                routing_key=self.routing_key,
                **self.kwargs
            )
            return self.mq_client
        else:
            raise InvalidAMQPURLException(f"[MQManager] Unsupported MQ type: {self.mq_type}")

    async def listen_to_queue(self):
        """ Asyncio listener function. Runs in the event loop. """

        from aeotrade_connector.mq.distribute import message_distribute

        client = self.get_mq_client()

        async with client.manage():
            await client.start(message_distribute)

    def queue_listener(self):
        """ Queue listener function. Runs in a separate thread. """

        while True:
            try:
                asyncio.run(self.listen_to_queue())
            except Exception as e:
                logger.exception(f"[MQManager] Error in queue listener: {e}")

            logger.error(f"[MQManager] Restarting queue listener {self.pot.value} in 5 seconds...")
            time.sleep(5)  # Wait for 5 seconds before restarting

    def start_queue(self, target_function: Callable, daemon: bool = True):
        if self.pot == POT.Process:
            import multiprocessing
            self.runner = multiprocessing.Process(target=target_function, daemon=daemon)  # type: ignore[assignment]
        else:
            import threading
            self.runner = threading.Thread(target=target_function, daemon=daemon)  # type: ignore[assignment]

        self.runner.start()  # type: ignore[attr-defined]
        # sys.stdout.write(style.SUCCESS(f"[Aeotrade Connector]-[QueueManager] Starting queue listener
        # {self.pot.value} success \n"))

    def publish(self, message: str):
        if self.mq_client:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.mq_client.publish(message))
            else:
                asyncio.run(self.mq_client.publish(message))
        else:
            logger.error("[MQManager] MQ client is not initialized")

    def close(self, wait_for_tasks: bool = True):
        try:
            if self.mq_client:
                asyncio.create_task(self.mq_client.aclose(wait_for_tasks=wait_for_tasks))

            if self.runner:
                if self.pot == POT.Process:
                    self.runner.terminate()
                else:
                    self.runner.join()
            logger.info("[MQManager] close success")
        except RuntimeWarning:
            # Ignore RuntimeWarning: coroutine 'AsyncRabbitMQClient.aclose' was never awaited
            pass
        except Exception as e:
            logger.exception(f"[MQManager] close error: {e}")

    def __del__(self):
        self.close(wait_for_tasks=False)
