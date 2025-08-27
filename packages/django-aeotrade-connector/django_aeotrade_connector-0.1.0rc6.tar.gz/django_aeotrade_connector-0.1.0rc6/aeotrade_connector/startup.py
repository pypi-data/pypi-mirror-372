"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/10 16:53
@file: startup.py
@project: django_aeotrade_connector
@describe: None
"""
import importlib
import inspect
import sys

from django.apps import apps
from django.conf import settings

from aeotrade_connector.helpers import get_app_services, scheduler_initialize
from aeotrade_connector.management.commands.startconnector import style
from aeotrade_connector.mq.manager import MQManager
from aeotrade_connector.schemas.common import (ConnectorBaseConfig,
                                               ConnectorCacheKey,
                                               ConnectorConfig, Trigger)
from aeotrade_connector.services import ConnectorServices
from aeotrade_connector.simple_cache import SimpleCache
from aeotrade_connector.simple_cache import simple_cache as cache
from aeotrade_connector.utils import logger


class AeotradeConnectorReady:

    def __init__(self):
        self.connector_apps = []
        self.skip_ready = True

        for app_config in apps.get_app_configs():
            config = getattr(app_config, 'Config', None)
            connector = getattr(config, 'connector', None) if config else None
            if connector is not True:
                continue

            app_name = app_config.name
            # ConnectorBaseConfig is required in connector app
            connector_config_model = getattr(config, 'connector_config_model', None)
            if not connector_config_model:
                logger.error(f'App `{app_name}` required a connector_config_model')
                sys.exit(17)

            if not isinstance(connector_config_model, ConnectorBaseConfig):
                logger.error(f'App `{app_name}` connector_config_model must be a ConnectorBaseConfig')
                sys.exit(17)

            # Set default name
            if connector_config_model.name == "":
                connector_config_model.name = app_name

            # Set connector_config_model
            setattr(app_config, 'connector_config_model', connector_config_model)
            self.connector_apps.append((app_config, connector_config_model))

        if self.connector_apps:
            self.skip_ready = False
            self.django_settings_required()

        self.cache = SimpleCache()
        # self.prefer_concurrency: bool = settings.AC_PREFER_CONCURRENCY
        self.queue_managers = []

    @staticmethod
    def django_settings_required():
        for variable in ["IS_TEST", "AC_MANAGEMENT_ENDPOINT"]:
            if not hasattr(settings, variable):
                sys.stdout.write(style.ERROR(f"[Aeotrade Connector] missing to set `{variable}` in django.settings"))
                sys.exit(17)

    @staticmethod
    def params_require(config, variable: str, expected_type: type = str, default=None, required=True):
        if hasattr(config.Config, variable):
            val = getattr(config.Config, variable)
            app_name = getattr(config, "name")
            assert isinstance(val, expected_type), f'App {app_name} {variable} must be a {expected_type.__name__}'
            return val
        else:
            if default:
                return default
            if not required:
                return
            logger.exception(f'[Aeotrade Connector] App {config} requires {variable}')
            sys.exit(17)

    def ready_connector_map(self):
        connector_config = {}

        # Load connector config
        for _, config_model in self.connector_apps:
            current_config = {
                "name": config_model.name,
                "label": config_model.label,
                "code": config_model.code
            }
            connector_config[current_config['name']] = ConnectorConfig(**current_config)

        # Save in cache
        self.cache.setf(ConnectorCacheKey.Config.value, connector_config)
        return connector_config

    def ready_views(self):
        connector_views, cache_views = {}, {}
        required_views = ['task_account_check', 'task_create', 'task_update', 'task_delete', 'task_start', 'task_stop']

        for _, config_model in self.connector_apps:
            app_name = config_model.name
            try:
                views_module = importlib.import_module(f'{app_name}.views')
                available_functions = [name for name, func in inspect.getmembers(views_module, inspect.isfunction)]
                missing_functions = [view for view in required_views if view not in available_functions]
                if not missing_functions:
                    connector_views[app_name] = views_module
                    cache_views[app_name] = views_module.__name__
                else:
                    raise Exception(
                        f"[Aeotrade Connector] connector app {app_name} not implemented: {missing_functions}")
            except ModuleNotFoundError:
                sys.stdout.write(
                    style.WARNING(
                        f"[Aeotrade Connector] connector app {app_name} raise ModuleNotFoundError "
                        f"when load views, skip this app\n")
                )
                continue

        # Save in cache
        self.cache.setf(ConnectorCacheKey.Views.value, cache_views)
        return connector_views

    def ready_services(self):
        connector_services, cache_services = {}, {}
        required_methods = ['params_check', 'execute', 'response_handler']

        for _, config_model in self.connector_apps:
            services_loaded = False
            app_name = config_model.name
            try:
                services_module = importlib.import_module(f'{app_name}.services')
                for name, obj in inspect.getmembers(services_module, inspect.isclass):
                    if issubclass(obj, ConnectorServices) and obj is not ConnectorServices and services_loaded is False:
                        if all(hasattr(obj, method) for method in required_methods):
                            connector_services[app_name] = obj
                            cache_services[app_name] = f"{obj.__module__}.{obj.__name__}"
                            services_loaded = True
                        else:
                            raise Exception(
                                f"[Aeotrade Connector] class {name} in {app_name} must "
                                f"implement all required methods: {', '.join(required_methods)}")

                if not services_loaded:
                    raise Exception(
                        f"[Aeotrade Connector] connector app {app_name}"
                        f" need a class that inherits from ConnectorServices")
            except ModuleNotFoundError:
                sys.stdout.write(
                    style.WARNING(
                        f"[Aeotrade Connector] connector app {app_name} raise ModuleNotFoundError "
                        f"when load services, skip this app\n")
                )
                continue

        # Save in cache
        cache.setf(ConnectorCacheKey.Services.value, cache_services)
        return connector_services

    def ready_scheduler(self):
        jobs = []
        for _, config_model in self.connector_apps:
            # Load scheduler
            app_name = config_model.name
            # Validate AC_CLEAN_CACHE variable type
            if hasattr(settings, 'AC_CLEAN_CACHE') and not isinstance(settings.AC_CLEAN_CACHE, bool):
                raise Exception(
                    "[Aeotrade Connector] settings.AC_CLEAN_CACHE must be a bool"
                )
            # Default AC_CLEAN_CACHE is True
            if getattr(settings, 'AC_CLEAN_CACHE', True):
                # Clean Redis cache
                scheduler_initialize()[0]["default"].remove_all_jobs()

            try:
                tasks_module = importlib.import_module(f'{app_name}.tasks')

                # Load custom tasks
                for name, obj in inspect.getmembers(tasks_module):
                    if inspect.isfunction(obj) and getattr(obj, 'is_connector_task', False):
                        job_args = getattr(obj, 'job_args', [])
                        job_kwargs = getattr(obj, 'job_kwargs', {})
                        jobs.append({"func": obj, "args": job_args, "kwargs": job_kwargs, "app_name": app_name})

                # Load heartbeat tasks
                services = get_app_services(config_model.name, config_model.code)  # noqa
                if config_model.auto_heartbeat:
                    jobs.append({
                        "func": services.heartbeat,
                        "args": [],
                        "kwargs": {'trigger': Trigger.Interval.value, 'seconds': 5},
                        "app_name": app_name
                    })
            except ModuleNotFoundError as e:
                sys.stdout.write(style.ERROR(f"[Aeotrade Connector] connector app load failed: {e}"))
                sys.exit(17)

        return jobs

    def ready_mq_manager(self):
        receive_managers = []
        try:
            for _, config_model in self.connector_apps:
                mq_model = config_model.mq_recv_model
                mq_receive_manager = MQManager(**mq_model.to_dict(),
                                               **{"task_stop_when_error": config_model.task_stop_when_error})
                receive_managers.append(mq_receive_manager)
                mq_receive_manager.start()
                sys.stdout.write(
                    style.SUCCESS(f"[Aeotrade Connector]-[QueueManager] "
                                  f"{config_model.name} message queue manager started\n"))
        except Exception as e:
            raise OSError(style.ERROR(f"[Aeotrade Connector] Failed to start mq manager: {e}"))

        self.queue_managers = receive_managers
        return receive_managers

    def ready_callback(self):
        # Load connector config

        for _, config_model in self.connector_apps:
            if config_model.callback:
                try:
                    config_model.callback(*config_model.callback_args, **config_model.callback_kwargs)
                except Exception as e:
                    sys.stdout.write(style.ERROR(f"[Aeotrade Connector] connector app callback error: {e}"))
                    raise e

    def get_mq_managers(self):
        return self.queue_managers

    def __call__(self, *args, **kwargs):
        if self.skip_ready:
            sys.stdout.write(style.WARNING("[Aeotrade Connector] skip the ready, no connector apps found\n"))
            return self.skip_ready

        # ready_methods = [method for method in dir(self) if method.startswith('ready_')]
        # for method in ready_methods:
        #     getattr(self, method)()

        app_jobs = []
        self.ready_connector_map()
        self.ready_views()
        self.ready_services()
        app_jobs.extend(self.ready_scheduler())
        self.ready_mq_manager()
        self.ready_callback()

        if app_jobs:
            from aeotrade_connector.crontab import register_jobs
            register_jobs(app_jobs)
