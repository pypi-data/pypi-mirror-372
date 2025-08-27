"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/5 17:34
@file: base.py
@project: django_aeotrade_connector
@describe: None
"""
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager


class MessageQueueBase(ABC):

    def __init__(self):
        self.is_closed = False
        self.connection = None

    @abstractmethod
    def close(self):
        raise NotImplementedError

    @abstractmethod
    def connect(self):
        raise NotImplementedError


class AsyncMessageQueueBase(ABC):

    def __init__(self):
        self.is_closed = False
        self.connection = None

    @abstractmethod
    def aclose(self, wait_for_tasks):
        raise NotImplementedError

    @abstractmethod
    def aconnect(self):
        raise NotImplementedError

    @asynccontextmanager
    async def manage(self, wait_for_tasks: bool = True):
        """Async context manager to handle connection lifecycle."""
        try:
            await self.aconnect()
            yield self
        finally:
            await self.aclose(wait_for_tasks)
