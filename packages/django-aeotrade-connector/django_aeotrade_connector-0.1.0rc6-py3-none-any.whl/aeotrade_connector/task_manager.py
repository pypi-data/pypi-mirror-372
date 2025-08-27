import asyncio
import threading
from typing import Dict, Optional

from django.conf import settings
from aeotrade_connector.models import ConnectorTask as TaskORM
from aeotrade_connector.db.choices import TaskStatus
from aeotrade_connector.utils import logger


class TaskThread(threading.Thread):
    """后台任务线程"""
    def __init__(self, task: TaskORM, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = task
        self.running = True
        self.daemon = True

    def stop(self):
        """停止任务"""
        self.running = False

    def run(self):
        """运行任务"""
        try:
            while self.running:
                # 在这里执行具体的任务逻辑
                # 可以根据task.event_action_params中的参数来执行相应的操作
                asyncio.run(self._execute_task())
                if not self.running:
                    break

        except Exception as e:
            logger.exception(f"Task execution error: {e}")
            self.task.status = TaskStatus.Failed
            self.task.err_msg = str(e)
            self.task.save()

    async def _execute_task(self):
        """执行具体的任务逻辑"""
        # 这里可以根据具体需求实现任务逻辑
        await asyncio.sleep(1)  # 示例：每秒执行一次检查


class TaskManager:
    """任务管理器"""
    _instance = None
    _lock = threading.Lock()
    _tasks: Dict[str, TaskThread] = {}
    _connectors: Dict[str, 'Connector'] = {}

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    @classmethod
    def get_instance(cls) -> 'TaskManager':
        if cls._instance is None:
            cls._instance = TaskManager()
        return cls._instance

    def start_task(self, task: TaskORM) -> bool:
        """启动任务"""
        try:
            if task.task_id in self._tasks:
                return False

            task_thread = TaskThread(task=task)
            task_thread.start()
            self._tasks[task.task_id] = task_thread

            task.status = TaskStatus.Running
            task.save()
            return True
        except Exception as e:
            logger.exception(f"Start task error: {e}")
            return False

    def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        try:
            task_thread = self._tasks.get(task_id)
            if task_thread is None:
                return False

            task_thread.stop()
            task_thread.task.status = TaskStatus.Stopped
            task_thread.task.save()
            del self._tasks[task_id]
            return True
        except Exception as e:
            logger.exception(f"Stop task error: {e}")
            return False

    def get_task_thread(self, task_id: str) -> Optional[TaskThread]:
        """获取任务线程"""
        return self._tasks.get(task_id)

    async def load_running_tasks(self):
        """加载运行中的任务"""
        try:
            tasks = TaskORM.objects.filter(status=TaskStatus.Running, is_deleted=False)
            for task in tasks:
                self.start_task(task)
        except Exception as e:
            logger.exception(f"Load running tasks error: {e}")

    def run(self):
        """运行任务管理器"""
        asyncio.run(self.load_running_tasks())
        logger.info("Task manager started.")
