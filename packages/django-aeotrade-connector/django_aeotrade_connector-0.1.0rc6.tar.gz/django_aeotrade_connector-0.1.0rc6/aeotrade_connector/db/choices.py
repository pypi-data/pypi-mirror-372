"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/10 16:04
@file: choices.py
@project: django_aeotrade_connector
@describe: None
"""


class TaskStatus:
    """Connector Task Status"""
    Default = "default"
    Waiting = "waiting"
    Running = "running"
    Stopped = "stopped"  # stopped by manual
    Failed = "failed"  # execute task failed
    Warning = "warning"  # strange status ^_^
    Done = "done"

    Choices = (
        (Default, ""),
        (Waiting, "等待中"),
        (Running, "运行中"),
        (Stopped, "已停止"),
        (Failed, "失败"),
        (Warning, "异常"),
        (Done, "完成"),
    )


class QueueMessageStatus:
    """Connector Queue Message Status"""
    Waiting = "waiting"
    Running = "running"
    Failed = "failed"
    Success = "success"

    Choices = (
        (Waiting, "等待中"),
        (Running, "运行中"),
        (Failed, "执行失败"),
        (Success, "执行成功"),
    )


class TaskProcess:
    """Connector Task Process"""
    Waiting = "waiting"
    ParamsCheck = "params_check"
    Execute = "execute"
    ResponseHandler = "response_handler"
    UpChain = "up_chain"
    Publish = "publish"
    Done = "done"

    Choices = (
        (Waiting, "等待中"),
        (ParamsCheck, "参数检查"),
        (Execute, "任务执行"),
        (ResponseHandler, "响应处理"),
        (UpChain, "上链"),
        (Publish, "发送消息"),
        (Done, "完成"),
    )
