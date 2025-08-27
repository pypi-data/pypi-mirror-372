"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/5 17:40
@file: client.py
@project: django_aeotrade_connector
@describe: None
"""
import asyncio
import sys
from typing import Callable, Optional
from urllib.parse import urlparse

import aio_pika

from aeotrade_connector.management.commands.initconnector import style
from aeotrade_connector.mq.base import AsyncMessageQueueBase
from aeotrade_connector.utils import logger

MAX_CONCURRENT_TASKS = 50


class InvalidAMQPURLException(Exception):
    """Custom exception  raised when the AMQP URL is invalid."""
    pass


class AsyncRabbitMQClient(AsyncMessageQueueBase):
    """Async RabbitMQ client for sending and receiving messages."""

    def __init__(
            self,
            amqp_url: str,
            exchange_name: str,
            queue_name: str,
            routing_key: Optional[str] = None,
            exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.DIRECT,
            **kwargs
    ):
        super().__init__()
        if kwargs is None:
            kwargs = {}

        self.amqp_url = amqp_url
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.exchange_type = exchange_type
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None
        self._validate_amqp_url()

        self.is_closed = False
        self.kwargs = kwargs

        # asyncio setting
        self.task_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=MAX_CONCURRENT_TASKS + 10)
        self.stop_event: asyncio.Event = asyncio.Event()
        self.pending_tasks: set = set()
        self.tasks_in_progress = 0

    def _validate_amqp_url(self):
        """ Validate the AMQP URL format. """
        parsed_url = urlparse(self.amqp_url)

        # Check the scheme is correct (should be 'amqp' or 'amqps')
        if parsed_url.scheme not in ["amqp", "amqps"]:
            raise InvalidAMQPURLException(
                f"[AsyncRabbitMQClient] Invalid URL scheme '{parsed_url.scheme}', expected 'amqp' or 'amqps'.")

        # Ensure the URL contains a hostname and a path (path is the virtual host in RabbitMQ)
        if not parsed_url.hostname:
            raise InvalidAMQPURLException("[AsyncRabbitMQClient] AMQP URL must contain a hostname.")

        if not parsed_url.path:
            raise InvalidAMQPURLException("[AsyncRabbitMQClient] AMQP URL must contain a virtual host (path part).")

        # Optionally, you can add more validation, such as checking if username, password, and port are present
        if parsed_url.username is None or parsed_url.password is None:
            raise InvalidAMQPURLException("[AsyncRabbitMQClient] AMQP URL must contain a username and password.")

    async def aconnect(self):
        """ Connect to RabbitMQ and initialize exchange and queue. """
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(self.exchange_name, self.exchange_type, durable=True)
        self.queue = await self.channel.declare_queue(self.queue_name, durable=True)
        await self.queue.bind(self.exchange, routing_key=self.routing_key)

    async def publish(self, message: str):
        """ Publish a message to the exchange. """
        await self.exchange.publish(  # type: ignore[attr-defined]
            aio_pika.Message(body=message.encode()),
            routing_key=self.routing_key
        )

    async def consume(self, callback: Callable):
        """Consume messages from the queue."""
        runtime_kw = {
            "task_stop_when_error": self.kwargs.get("task_stop_when_error", False)
        }
        async with self.queue.iterator() as queue_iter:  # type: ignore[attr-defined]
            async for message in queue_iter:
                if self.stop_event.is_set():
                    # fixme: 这里有可能会造成数据丢失！！！
                    break
                async with message.process(requeue=True):
                    try:
                        # Extend task to the thread pool
                        # Executor.submit(callback, message
                        self.tasks_in_progress += 1
                        await self.task_queue.put((callback, message, runtime_kw))
                    except Exception as e:
                        logger.exception(f"[AsyncRabbitMQClient] message decode error: {e}")
                        continue

    async def process_tasks(self):
        """ Process tasks from the task queue. """
        while not self.stop_event.is_set() or not self.task_queue.empty() or self.tasks_in_progress > 0:
            try:
                callback, message, runtime_kw = await self.task_queue.get()
                task = asyncio.create_task(self._run_task(callback, message, **runtime_kw))
                self.pending_tasks.add(task)
                task.add_done_callback(self._on_task_done)
            except asyncio.CancelledError:
                continue
            except Exception as e:
                logger.exception(f"[AsyncRabbitMQClient] Task processing error: {e}")

    def _on_task_done(self, task: asyncio.Task):
        """ Task done callback. Discard the task from the pending tasks set. """
        self.pending_tasks.discard(task)
        self.tasks_in_progress -= 1
        self.task_queue.task_done()

    async def _run_task(self, callback: Callable, message, **kwargs):
        async with self.task_semaphore:
            try:
                await callback(message, **kwargs)
            except Exception as e:
                logger.exception(f"[AsyncRabbitMQClient] Task execution error: {e}")

    async def start(self, callback: Callable):
        consumer_task = asyncio.create_task(self.consume(callback))
        processor_task = asyncio.create_task(self.process_tasks())
        await asyncio.gather(consumer_task, processor_task)

    async def aclose(self, wait_for_tasks: bool):
        """Close the connection."""
        self.stop_event.set()

        if self.is_closed:
            return

        if wait_for_tasks:
            sys.stdout.write(style.WARNING("[AsyncRabbitMQClient] Waiting for all tasks to complete...\n"))
            while not self.task_queue.empty() or len(self.pending_tasks) > 0 or self.tasks_in_progress > 0:
                sys.stdout.write(style.WARNING(
                    f"[AsyncRabbitMQClient] Remaining tasks - Queue: {self.task_queue.qsize()}, "
                    f"Pending: {len(self.pending_tasks)}\n"
                ))
                await asyncio.sleep(0.5)

        if self.channel is not None:
            await self.channel.close()

        if self.connection is not None:
            await self.connection.close()

        self.is_closed = True

        if wait_for_tasks:
            sys.stdout.write(style.SUCCESS("[AsyncRabbitMQClient] Connection closed.\n"))
