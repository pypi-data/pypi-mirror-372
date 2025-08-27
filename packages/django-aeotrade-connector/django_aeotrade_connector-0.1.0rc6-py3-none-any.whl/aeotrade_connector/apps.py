"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/5 17:26
@file: apps.py
@project: django_aeotrade_connector
@describe: None
"""
import copy
import sys

from django.apps import AppConfig

from aeotrade_connector.management.commands.startconnector import style


class DjangoAeotradeConnectorConfig(AppConfig):
    name = 'aeotrade_connector'
    verbose_name = "Django Aeotrade Connector"

    def ready(self):
        from aeotrade_connector.db import signals  # noqa: F401
        try:
            from django.core.management import get_commands

            from aeotrade_connector.startup import AeotradeConnectorReady

            # Check if command is runserver
            commands = copy.deepcopy(get_commands())
            commands.pop("runserver")
            if any(command in sys.argv for command in commands):
                return

            # Load connector
            if not AeotradeConnectorReady()():
                sys.stdout.write(style.SUCCESS("[Aeotrade Connector] Aeotrade Connector register successfully \n\n"))

            # TODO: ensure mq message are consumed successfully, gunicorn默认模型为gevent, 但是gevent的事件循环会和asyncio冲突
            # Get mq manager
            # managers = ready_cls.get_mq_managers()
            # if not managers:
            #     return
            #
            # # Shutdown mq manager
            # def shutdown(mngrs, signum, frame):
            #     for manager in mngrs:
            #         manager.close()
            #
            # signal.signal(signal.SIGINT, partial(shutdown, managers))

        except Exception as e:
            sys.stdout.write(f"[Aeotrade Connector] unknown error occurred when aeotrade_connector app start: {e}\n")
            raise e
