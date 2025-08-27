"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/11 17:47
@file: signals.py
@project: django_aeotrade_connector
@describe: None
"""
from django.db.models.signals import pre_save
from django.dispatch import receiver

from aeotrade_connector.models import (ConnectorTask, ConnectorTaskLog,
                                       QueueMessage)
from aeotrade_connector.utils import generate_tsid


@receiver(pre_save, sender=ConnectorTask)
@receiver(pre_save, sender=ConnectorTaskLog)
@receiver(pre_save, sender=QueueMessage)
def tsid_signal(sender, instance, **kwargs):
    if isinstance(instance, ConnectorTask):
        field = 'connector_task_id'
    elif isinstance(instance, ConnectorTaskLog):
        field = 'log_id'
    else:
        field = 'message_id'

    if getattr(instance, field):
        return

    # set tsid
    tsid = generate_tsid(as_string=False, include_hyphens=False)
    setattr(instance, field, tsid)
