"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/10 11:33
@file: initconnector.py
@project: django_aeotrade_connector
@describe: None
"""
import importlib
import os.path
import sys
from pathlib import Path
from typing import Any, cast

from django.core.management.base import BaseCommand
from django.core.management.color import color_style

from aeotrade_connector.utils import get_base_path

style = color_style()


class Command(BaseCommand):
    help = 'Initialize connector project'

    @staticmethod
    def open_file(file_path):
        file_path = Path(file_path)
        if file_path.exists():
            with file_path.open("r") as f:
                return f.read()
        else:
            raise ValueError(f"File {file_path} does not exist")

    def handle(self, *args: Any, **options: Any) -> None:
        # Get the current settings module
        setting_env = os.environ.get("DJANGO_SETTINGS_MODULE")
        assert setting_env, "DJANGO_SETTINGS_MODULE is not set"
        setting_module = importlib.import_module(cast(str, setting_env))
        if not setting_module:
            raise ValueError("DJANGO_SETTINGS_MODULE is not set")

        # Get the current project directory and urls.py path
        project_dir = os.path.dirname(os.path.abspath(setting_module.__file__))   # type: ignore[type-var]
        if not project_dir:
            raise ValueError("Django Project directory is not set")
        urls_path = os.path.join(cast(str, project_dir), 'urls.py')

        # Read the contents of urls template
        aeotrade_connector_path = get_base_path()
        proj_tpl_dir = os.path.join(os.path.join(aeotrade_connector_path, 'templates'), 'proj_tpl')
        urls_tpl = self.open_file(os.path.join(proj_tpl_dir, 'init_urls.tpl'))
        views_tpl = os.path.join(proj_tpl_dir, 'dispatcher.tpl')
        settings_tpl = os.path.join(proj_tpl_dir, 'settings.tpl')

        # Replace the contents of urls.py
        if os.path.exists(urls_path):
            try:
                with open(urls_path, 'a', encoding='utf-8') as f:
                    f.write(urls_tpl)
            except Exception as e:
                sys.stdout.write(style.ERROR(f"Failed to update urls.py: {e}\n"))
        else:
            sys.stdout.write(style.ERROR(f"urls.py not found at {urls_path}\n"))

        target_views_path = os.path.join(project_dir, 'dispatcher.py')
        # Copy views_path to project_dir
        if os.path.exists(target_views_path):
            raise ValueError(f"File {target_views_path} already exists")

        if os.path.exists(views_tpl):
            try:
                with open(views_tpl, 'r', encoding='utf-8') as f:
                    views_content = f.read()
                with open(target_views_path, 'w', encoding='utf-8') as f:
                    f.write(views_content)
            except Exception as e:
                sys.stdout.write(style.ERROR(f"Failed to copy views.py: {e}\n"))

        if os.path.exists(settings_tpl):
            try:
                with open(settings_tpl, 'r', encoding='utf-8') as f:
                    settings_content = f.read()
                with open(os.path.join(project_dir, 'settings.py'), 'a', encoding='utf-8') as f:
                    f.write(settings_content)
            except Exception as e:
                sys.stdout.write(style.ERROR(f"Failed to append settings.py: {e}\n"))

        sys.stdout.write(style.SUCCESS("Initialize connector project success\n"))
