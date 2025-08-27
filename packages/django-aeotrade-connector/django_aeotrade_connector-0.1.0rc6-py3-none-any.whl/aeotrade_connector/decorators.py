"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/9 11:18
@file: decorators.py
@project: django_aeotrade_connector
@describe: decorators
"""
import asyncio
import functools
import importlib


def module_required(module_name: str):
    """Decorator to check if a module is installed."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                importlib.import_module(module_name)
            except ImportError:
                raise ImportError(
                    f"The module '{module_name}' is not installed. "
                    f"Please install it by running `poetry add {module_name}`."
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def cache_result(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = hash((args, tuple(kwargs.items())))

        if key in cache:
            return cache[key]

        result = func(*args, **kwargs)
        cache[key] = result
        return result

    return wrapper


def with_event_loop(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return f(*args, **kwargs)
        else:
            return loop.run_until_complete(f(*args, **kwargs))

    return wrapper


def connector_task(*job_args, **job_kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.is_connector_task = True
        wrapper.job_args = job_args
        wrapper.job_kwargs = job_kwargs
        return wrapper

    return decorator


# def job_lock_decorator(lock_name: str):
#
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             from aeotrade_connector.helpers import RedisLock
#
#             lock = RedisLock(lock_name)
#
#             # Task is running, skip the current task
#             if lock.is_locked():
#                 return
#
#             # Get lock failed, skip the current task
#             if not lock.acquire():
#                 return
#
#             try:
#                 ret = func(*args, **kwargs)
#
#                 # In order to solve the problem of task execution being too fast,
#                 # other worker processes obtained locks and added a delay of 50ms
#                 time.sleep(0.05)
#                 return ret
#             finally:
#                 lock.release()
#
#         return wrapper
#
#     return decorator


# def connector_task_with_lock(*job_args, **job_kwargs):
#
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             connector_task_id = job_kwargs.get('task_id', func.__name__)
#
#             # 获取锁的装饰器
#             def lock_decorator(func):
#                 def lock_wrapper(*args, **kwargs):
#                     from aeotrade_connector.helpers import RedisLock
#
#                     lock = RedisLock(connector_task_id)
#
#                     if lock.is_locked():
#                         return
#
#                     if not lock.acquire():
#                         return
#
#                     try:
#                         ret = func(*args, **kwargs)
#                         time.sleep(0.05)
#                         return ret
#                     finally:
#                         lock.release()
#
#                 return lock_wrapper
#
#             locked_func = lock_decorator(func)
#
#             def run(connector_code):
#                 time.sleep(0.1)
#
#             locked_func(run)(*args, **kwargs)
#
#         wrapper.is_connector_task = True
#         wrapper.job_args = args
#         wrapper.job_kwargs = job_kwargs
#
#         return wrapper
#
#     return decorator
