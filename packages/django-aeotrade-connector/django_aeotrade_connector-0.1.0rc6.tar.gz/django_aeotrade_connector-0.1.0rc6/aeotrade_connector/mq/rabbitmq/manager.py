"""
@company: 慧贸天下(北京)科技有限公司
@author: zfj@aeotrade.com
@time: 2025/03/18 14:15
@file: manager.py
@project: django_aeotrade_connector
@describe: RabbitMQ Manager implementation.
"""

import asyncio
import logging
import time
from ..manager import MQManager
from .client import AsyncRabbitMQClient

logger = logging.getLogger(__name__)


class RabbitMQManager(MQManager):
    """RabbitMQ Manager implementation."""

    def get_mq_client(self):
        """Get the RabbitMQ client."""
        self.mq_client = AsyncRabbitMQClient(
            amqp_url=self.url,
            exchange_name=self.exchange,
            queue_name=self.queue,
            routing_key=self.routing_key,
            **self.kwargs
        )
        return self.mq_client

    async def listen_to_queue(self):
        """Asyncio listener function for RabbitMQ."""
        client = self.get_mq_client()
        try:
            async with client.manage():
                await client.start()
        except KeyboardInterrupt:
            await client.aclose(True)

    def queue_listener(self):
        """Queue listener function for RabbitMQ."""
        while True:
            try:
                asyncio.run(self.listen_to_queue())
            except Exception as e:
                logger.exception(f"[MQManager] Error in queue listener: {e}")

            logger.error(f"[MQManager] Restarting queue listener {self.pot.value} in 5 seconds...")
            time.sleep(5)  # Wait for 5 seconds before restarting


