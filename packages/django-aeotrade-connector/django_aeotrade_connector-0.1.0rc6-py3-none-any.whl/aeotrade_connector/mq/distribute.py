"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/12 14:18
@file: distribute.py
@project: django_aeotrade_connector
@describe: None
"""
import base64
import json
import logging
from enum import Enum
from typing import Any, Dict, Optional

from aio_pika import IncomingMessage
from django.core.exceptions import SynchronousOnlyOperation

from aeotrade_connector.db.choices import TaskStatus
from aeotrade_connector.decorators import with_event_loop
from aeotrade_connector.exceptions import (DXPMessageParserException,
                                           MQMessageParserException,
                                           TaskExceptedException,
                                           TaskNotFoundDataException,
                                           TaskParamsIllegalException,
                                           TaskServicesNotFoundException,
                                           TaskStatusIllegalException,
                                           XMLParserException)
from aeotrade_connector.helpers import (build_mq_client, get_app_services,
                                        task_status_update)
from aeotrade_connector.models import ConnectorTask as TaskORM
from aeotrade_connector.models import ConnectorTaskLog as TaskLogORM
from aeotrade_connector.models import QueueMessage as QueueMessageORM
from aeotrade_connector.utils import XMLHandler

logger = logging.getLogger('log')


class BizKeyEnum(Enum):
    BPTNo = "BPTNo"  # 合约编号
    BizCoID = "BizCollaborationId"  # 业务协作编号
    ActivityID = "ActivityId"  # 活动ID


def parser_dxp_message(json_message: dict) -> Dict[str, Any]:
    ret = {}
    dxp_message = json_message.get("dxp:DxpMsg", {})
    # trans_info = dxp_message.get("dxp:TransInfo", {})
    # get data
    bs64_data = dxp_message.get("dxp:Data", "")
    decoded_bytes = base64.b64decode(bs64_data)
    decoded_string = decoded_bytes.decode('utf-8')
    try:
        ret["data"] = json.loads(decoded_string)
    except json.decoder.JSONDecodeError:
        try:
            ret["data"] = parser_json_message(decoded_string)
        except Exception as e:
            err_msg = f"[MessageDistribute] JSON decode error, data: {str(json_message)}, error: {e}"
            logger.exception(err_msg)
            raise DXPMessageParserException(err_msg)
    except Exception as e:
        err_msg = f"[MessageDistribute] JSON decode error, data: {str(json_message)}, error: {e}"
        logger.exception(err_msg)
        raise DXPMessageParserException(err_msg)

    add_info = dxp_message.get("dxp:AddInfo", {})
    # get biz key
    biz_key = add_info.get("dxp:BizKey", {})
    biz_items = biz_key.get("dxp:Key")
    for item in biz_items:
        if item.get("@name") == BizKeyEnum.BPTNo.value:  # 合约编号
            ret[BizKeyEnum.BPTNo.value] = item.get("#text")
        if item.get("@name") == BizKeyEnum.BizCoID.value:  # 业务协作编号
            ret[BizKeyEnum.BizCoID.value] = item.get("#text")
        if item.get("@name") == BizKeyEnum.ActivityID.value:  # 活动ID
            ret[BizKeyEnum.ActivityID.value] = item.get("#text")
        # todo: 这里应该要获取连接器编码，并且需要在TaskORM中验证这个值是否正确
    return ret


def parser_json_message(source_message: str):
    try:
        handler = XMLHandler()
        json_message = handler.xml_to_dict(source_message)
    except XMLParserException:
        try:
            json_message = json.loads(source_message)
        except Exception as e:
            err_msg = f"[MessageDistribute] JSON decode error: {e}, message: {source_message}"
            logger.error(err_msg)
            raise MQMessageParserException(err_msg)
    except Exception as e:
        err_msg = f"[MessageDistribute] An error occurred: {e}, message: {source_message}"
        logger.exception(err_msg)
        raise MQMessageParserException(err_msg)
    return json_message


async def get_task(dxp_message: dict, raise_exception: bool = True) -> TaskORM:
    # Query unique data by BPTNo and ActivityID
    task = await TaskORM.objects.filter(
        contract_id=dxp_message.get(BizKeyEnum.BPTNo.value),
        activity_code=dxp_message.get(BizKeyEnum.ActivityID.value),
    ).afirst()
    if not task:
        err_msg = (f"[MessageDistribute] Task not found, "
                   f"BPTNo: {dxp_message.get(BizKeyEnum.BPTNo.value)}, "
                   f"ActivityID: {dxp_message.get(BizKeyEnum.ActivityID.value)}")
        logger.error(err_msg)
        raise TaskNotFoundDataException(err_msg)

    if task.status not in [TaskStatus.Running, TaskStatus.Warning] and raise_exception:
        err_msg = f"[MessageDistribute] Task not running, current status: {task.status}"
        logger.error(err_msg)
        raise TaskStatusIllegalException(err_msg)

    return task


def handle_exception(e, custom_msg="", print_detail=True):
    err_msg = f"{custom_msg}[{type(e).__name__}] {str(e)}"
    if print_detail:
        logger.exception(err_msg)
    else:
        logger.error(f"{custom_msg}[{type(e).__name__}] async method or function required!")
    return err_msg


@with_event_loop
async def message_distribute(
        incoming_message: IncomingMessage,
        task_stop_when_error: bool = False,
        up_chain: bool = False
):
    """ Task distribute center """

    # Save incoming message
    message_orm = await QueueMessageORM.objects.acreate(
        message=incoming_message.body,
        queue_info=incoming_message.info(),
    )
    task_log_orm = None
    err_msg = ""
    task: Optional[TaskORM] = None
    try:
        try:
            # Decode IncomingMessage
            message = incoming_message.body.decode()
        except Exception as e:
            err_msg = f"[MessageDistribute] IncomingMessage decode error: {e}"
            logger.exception(err_msg)
            message_orm.status = QueueMessageORM.message_status.Failed
            raise MQMessageParserException(err_msg)

        # Transform message(from mq) to json
        json_message = parser_json_message(message)

        # Transform json to dxp message
        dxp_message = parser_dxp_message(json_message)

        # Get task
        task = await get_task(dxp_message)
        message_orm.connector_task_id = task.connector_task_id
        # Create task log
        task_log_orm = await TaskLogORM.objects.acreate(connector_task_id=task.connector_task_id)

        # Get services
        services = get_app_services(task.task_from, task.connector_code)

        # Validate params
        message_orm.status = QueueMessageORM.message_status.Running
        task_log_orm.process = TaskLogORM.process_status.ParamsCheck
        model_data = await services.params_check(task, dxp_message)

        # Execute
        task_log_orm.process = TaskLogORM.process_status.Execute
        response = await services.execute(model_data=model_data)

        # Response handler
        task_log_orm.process = TaskLogORM.process_status.ResponseHandler
        send_message = await services.response_handler(response, task, task_log_orm)

        # Up Chain
        if up_chain:
            task_log_orm.process = TaskLogORM.process_status.UpChain
            await services.up_chain(response, task)

        # Publish message to send MQ
        if send_message:
            # Build send MQ client
            mq_manager = build_mq_client(task)
            # Send response
            await services.publish(send_message, mq_manager)

        # Task Done
        message_orm.status = QueueMessageORM.message_status.Success
        task_log_orm.process = TaskLogORM.process_status.Done
        logger.info(f"[MessageDistribute] Task done, task_id: {task.task_id}")
    except (MQMessageParserException, DXPMessageParserException, TaskNotFoundDataException) as e:
        err_msg = handle_exception(e)
        return
    except TaskStatusIllegalException as e:
        err_msg = handle_exception(e)
        task_status_update(task, err_msg=str(e), status=TaskStatus.Running)
    except TaskParamsIllegalException as e:
        err_msg = handle_exception(e)
        task_status_update(task, err_msg=str(e), status=TaskStatus.Running)
    except TaskServicesNotFoundException as e:
        err_msg = handle_exception(e)
        return
    except TaskExceptedException as e:
        err_msg = handle_exception(e)
        return
    except SynchronousOnlyOperation as e:
        err_msg = handle_exception(e, custom_msg="[MessageDistribute] ", print_detail=False)
        return
    except Exception as e:
        err_msg = handle_exception(e, custom_msg="[MessageDistribute] An unexpected error occurred: ")
        task_status_update(task, err_msg=err_msg, status=TaskStatus.Failed, stop_task=task_stop_when_error)
        return
    finally:
        if message_orm:
            await message_orm.asave()
        if task_log_orm:
            task_log_orm.err_msg += f"\n{err_msg}" if task_log_orm.err_msg else err_msg
            await task_log_orm.asave()
    return
