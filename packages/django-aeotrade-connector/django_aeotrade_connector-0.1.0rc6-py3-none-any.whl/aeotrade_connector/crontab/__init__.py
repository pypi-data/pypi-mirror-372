"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/6 11:02
@file: __init__.py.py
@project: django_aeotrade_connector
@describe: None
"""
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

from aeotrade_connector.helpers import job_lock, scheduler_initialize
from aeotrade_connector.management.commands.initconnector import style

job_store = getattr(settings, "AC_TASK_STORE", 'cache')
if not job_store:
    job_store = 'cache'

if job_store not in ["db", "cache"]:
    raise Exception("settings.AC_TASK_STORE options are `db` and `cache`")

# scheduler = BackgroundScheduler(jobstores=scheduler_initialize()[0])
scheduler = BackgroundScheduler()
if job_store == "cache":
    scheduler.add_jobstore(scheduler_initialize()[0]["default"], "default")
else:
    try:
        from django_apscheduler.jobstores import DjangoJobStore
    except ImportError as exc:  # pragma: nocover
        raise ImportError("Crontab requires django-apscheduler installed") from exc

    scheduler.add_jobstore(DjangoJobStore(), "default")


def register_jobs(jobs):
    """ All jobs register here"""

    for job in jobs:
        app_name = job.get("app_name")
        task_id = f"{app_name}_{job['func'].__name__}"
        try:
            func = job.get("func")
            if not func:
                sys.stdout.write(style.SUCCESS("[Aeotrade Connector]-[Crontab] register func is None\n"))
            args = job.get("args", [])
            kwargs = job.get("kwargs", {})
            exists_kwargs = kwargs.get("kwargs", {})
            exists_kwargs["Y29ubmVjdG9yX3Rhc2tfaWQ="] = task_id
            exists_kwargs["func"] = func
            kwargs["kwargs"] = exists_kwargs

            scheduler.add_job(job_lock, *args, **kwargs, id=task_id, replace_existing=True)
            # scheduler.add_job(func, *args, **kwargs, id=task_id, replace_existing=True)
            sys.stdout.write(style.SUCCESS(f"[Aeotrade Connector]-[Crontab] register "
                                           f"{app_name}.{func.__name__} Success\n"))
        except Exception as e:
            sys.stdout.write(style.ERROR(f"[Aeotrade Connector]-[Crontab] register Error:\n {e}\n"))

    scheduler.start()

# def register_jobs(jobs):
#     """ All jobs register here"""
#     scheduler = scheduler_initialize()
#
#     for job in jobs:
#         try:
#             func = job.get("func")
#             if not func:
#                 sys.stdout.write(style.SUCCESS("[Aeotrade Connector]-[Crontab] register func is None\n"))
#             args = job.get("args", [])
#             kwargs = job.get("kwargs", {})
#             scheduler.add_job(func, *args, **kwargs)
#             sys.stdout.write(style.SUCCESS("[Aeotrade Connector]-[Crontab] register Success\n"))
#         except Exception as e:
#             sys.stdout.write(style.ERROR(f"[Aeotrade Connector]-[Crontab] register Error:\n {e}\n"))
#
#     scheduler.start()
