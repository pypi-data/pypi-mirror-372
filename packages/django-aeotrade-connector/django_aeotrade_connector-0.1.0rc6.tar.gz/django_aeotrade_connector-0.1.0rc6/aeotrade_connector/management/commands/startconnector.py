"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/9 15:38
@file: startconnector.py
@project: django_aeotrade_connector
@describe: None
"""
import os.path
import sys
from typing import Any

from django.core import management
from django.core.management.base import BaseCommand
from django.core.management.color import color_style

from aeotrade_connector.utils import get_base_path

style = color_style()


class Command(BaseCommand):
    help = 'Create a new Connector app'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            'name',
            type=str,
            help='Name of the app to import data for',
        )

        parser.add_argument(
            '--template',
            type=str,
            help='Path to the template directory',
            default=None,
        )

    def handle(self, *args: Any, **options: Any) -> None:
        template_dir = options.pop('template', None)
        name = options['name']
        if not template_dir:
            aeotrade_connector_path = get_base_path()
            tpl_dir = os.path.join(aeotrade_connector_path, 'templates')
            template_dir = os.path.join(tpl_dir, 'app_tpl')
        management.call_command('startapp', name, template=template_dir)
        sys.stdout.write(style.SUCCESS("Created %s app success\n" % name))
