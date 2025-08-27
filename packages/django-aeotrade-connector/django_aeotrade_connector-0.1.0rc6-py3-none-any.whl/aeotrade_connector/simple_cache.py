"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/10 16:23
@file: simple_cache.py
@project: django_aeotrade_connector
@describe: None
"""
import fcntl
import importlib
import os.path
import pickle
import types
from typing import Any, Optional

from django.conf import settings
from django.core.cache import cache

from aeotrade_connector.schemas.common import ConnectorCacheKey
from aeotrade_connector.utils import singleton


def import_module_if_needed(obj):
    if hasattr(obj, '__name__') and isinstance(obj, types.ModuleType):
        return obj
    elif isinstance(obj, str):
        return importlib.import_module(obj)
    return obj


def to_module(cache_key, cache_data):
    if not cache_data:
        return cache_data

    k = ConnectorCacheKey.value_of(cache_key)

    for key, obj in cache_data.items():
        if k == ConnectorCacheKey.Views:
            cache_data[key] = import_module_if_needed(obj)

        elif k == ConnectorCacheKey.Services:
            if isinstance(obj, str):
                module_path, class_name = obj.rsplit('.', 1)
                module = importlib.import_module(module_path)
                services_cls = getattr(module, class_name)
                cache_data[key] = services_cls
            else:
                cache_data[key] = import_module_if_needed(obj)

    return cache_data


@singleton
class SimpleCache:
    """
    Cache data in file
    """

    def __init__(self, cache_filename: Optional[str] = None, *args, **kwargs):
        self.cache_filename = cache_filename or ".simple_cache.pkl"
        self.cache = cache
        self.CACHE_FILE_PATH = os.path.join(settings.BASE_DIR, self.cache_filename)  # type: ignore[arg-type]

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value: Any):
        self.cache.set(key, value)

    def setx(self, key: str, value: Any, ex: int):
        self.cache.set(key, value, ex)

    def setf(self, key: str, value: Any):
        """Set in cache and save in file"""
        self.cache.set(key, value)
        self.write_in_file_with_lock(key, value)

    def getf(self, key: str):
        """Get from cache default, if not, from file. and reload in cache"""
        ret = self.cache.get(key, {})
        if not ret:
            pickle_data = self.read_from_file()
            new_ret = pickle_data.get(key, {})
            if new_ret:
                self.cache.set(key, new_ret)
            return to_module(key, new_ret)
        return to_module(key, ret)

    def write_in_file_with_lock(self, key: str, data: Any):
        """Using file locks to ensure thread safety when writing to cache"""
        insert_data = {}

        if os.path.exists(self.CACHE_FILE_PATH):
            insert_data = self.read_from_file()

        insert_data[key] = data

        with open(self.CACHE_FILE_PATH, 'wb') as file:
            # Get file lock
            fcntl.flock(file, fcntl.LOCK_EX)  # type: ignore[attr-defined]
            try:
                pickle.dump(insert_data, file)
            finally:
                # Release file lock
                fcntl.flock(file, fcntl.LOCK_UN)  # type: ignore[attr-defined]

    def read_from_file(self):
        if os.path.exists(self.CACHE_FILE_PATH):
            with open(self.CACHE_FILE_PATH, 'rb') as file:
                return pickle.load(file)
        return {}

    def remove_pkl_file(self):
        try:
            if os.path.exists(self.CACHE_FILE_PATH):
                os.remove(self.CACHE_FILE_PATH)
        except FileNotFoundError:
            return


simple_cache = SimpleCache()

# def sigint_handler(signum, frame):
#     simple_cache.remove_pkl_file()
#
#
# signal.signal(signal.SIGINT, sigint_handler)
