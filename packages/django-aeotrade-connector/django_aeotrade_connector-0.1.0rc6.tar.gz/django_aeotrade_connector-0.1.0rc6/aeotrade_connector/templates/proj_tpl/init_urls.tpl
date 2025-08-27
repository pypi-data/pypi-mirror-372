
from django.urls import re_path
from .dispatcher import (task_account_check, task_create, task_start,
                         task_stop, task_update_or_delete)

urlpatterns += [
    path("connector/api/org-connectors-accounts/check", task_account_check, name="账号校验"),
    re_path(r"connector/api/org-connectors-tasks$", task_create, name="新增任务"),
    re_path(r"connector/api/org-connectors-tasks/(?P<task_id>[a-zA-Z0-9\-]+)$", task_update_or_delete, name="更新/删除任务"),
    re_path(r"connector/api/org-connectors-tasks/(?P<task_id>[a-zA-Z0-9\-]+)/start$", task_start, name="启动任务"),
    re_path(r"connector/api/org-connectors-tasks/(?P<task_id>[a-zA-Z0-9\-]+)/stop$", task_stop, name="暂停任务"),
]
