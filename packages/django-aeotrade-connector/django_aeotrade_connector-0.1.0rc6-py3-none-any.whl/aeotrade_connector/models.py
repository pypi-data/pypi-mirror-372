"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/5 17:26
@file: .py
@project: django_aeotrade_connector
@describe: None
"""
from typing import Self

from django.db import models

from aeotrade_connector.db import (Model, SoftDeleteMixin, TimestampsMixin,
                                   choices)


class ConnectorTask(Model, TimestampsMixin, SoftDeleteMixin):
    """Connector Task"""

    TaskStatus = choices.TaskStatus

    connector_task_id = models.UUIDField(max_length=36, db_index=True, unique=True)
    task_id = models.CharField(max_length=50, db_index=True, help_text="关联任务id", null=False, blank=False)
    org_id = models.CharField(max_length=50, help_text="组织id", null=False, blank=False)
    uscc = models.CharField(max_length=20, default="", help_text="组织社会信用代码")

    contract_id = models.CharField(max_length=50, help_text="合约id", null=False, blank=False)
    activity_code = models.CharField(max_length=50, help_text="活动编号", null=False, blank=False)
    connector_code = models.CharField(max_length=50, help_text="连接器编码", null=False, blank=False)
    event_action_id = models.CharField(
        max_length=50,
        default="",
        help_text="触发事件id/执行动作id"
    )
    event_action_params = models.JSONField(
        default=dict,
        help_text="触发事件/执行动作 的执行参数(json格式字符串)"
    )  # eg: asst_id asst_key prompt

    status = models.CharField(choices=TaskStatus.Choices, default=TaskStatus.Default, help_text="任务状态",
                              max_length=30)
    status_update_at = models.DateTimeField(verbose_name='最新状态变更时间', null=True)
    is_send_qty = models.BooleanField(default=False, help_text="是否上报协作数")
    target_qty = models.IntegerField(default=0, help_text="目标总量")
    done_qty = models.IntegerField(default=0, help_text="已完成数量")

    transfer_id = models.CharField(max_length=50, default="", help_text="传输身份id")
    transfer_receive_config = models.JSONField(default=dict, help_text="传输接收队列配置")
    transfer_send_config = models.JSONField(default=dict, help_text="传输发送队列配置")
    task_from = models.CharField(max_length=50, help_text="任务来源(连接器)")
    err_msg = models.TextField(default="", help_text="错误信息")

    class Meta:
        db_table = "connector_task"


class ConnectorTaskLog(Model, TimestampsMixin, SoftDeleteMixin):
    """ Connector Execute log"""
    process_status = choices.TaskProcess

    log_id = models.UUIDField(max_length=36, db_index=True, unique=True)
    connector_task_id = models.UUIDField(max_length=36, db_index=True, help_text="关联任务id")
    err_msg = models.TextField(default="", help_text="错误信息")
    process = models.CharField(max_length=20, choices=process_status.Choices, default=process_status.Waiting,
                               help_text="任务处理进度")
    success = models.BooleanField(default=True, help_text="是否成功")

    class Meta:
        db_table = "connector_task_log"

    async def expected_err(self, message: str, save: bool = False) -> Self:
        self.success = False
        self.err_msg = message
        if save:
            await self.asave()
        return self


class QueueMessage(Model, TimestampsMixin, SoftDeleteMixin):
    """ Connector Execute log"""
    message_status = choices.QueueMessageStatus

    message_id = models.UUIDField(max_length=36, db_index=True, unique=True)
    connector_task_id = models.UUIDField(max_length=36, db_index=True, null=True, help_text="关联任务id")
    message = models.BinaryField(help_text="原始报文")
    queue_info = models.JSONField(default=dict, help_text="队列信息")
    status = models.CharField(
        max_length=30,
        choices=message_status.Choices,
        default=message_status.Waiting,
        help_text="状态"
    )

    class Meta:
        db_table = "connector_queue_message"
