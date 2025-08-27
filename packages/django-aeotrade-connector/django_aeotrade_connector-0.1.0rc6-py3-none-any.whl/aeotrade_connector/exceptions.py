"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/9 11:37
@file: exceptions.py
@project: django_aeotrade_connector
@describe: None
"""
from rest_framework.exceptions import APIException


class AeotradeConnectorException(Exception):
    pass


class MethodNotAllowed(APIException):
    """
    Method NOT Allowed
    """

    status_code = 405
    default_detail = "Method not allowed"


class RequestBodyException(APIException):
    status_code = 412
    default_detail = "请求体错误"


class DataExistsException(APIException):
    """ 数据已存在 """
    status_code = 413
    default_detail = "数据已存在"


class DataNotExistsException(APIException):
    """ 数据不存在 """
    status_code = 414
    default_detail = "数据不存在"


class DataOperationFailedException(APIException):
    """ 数据操作失败 """
    status_code = 415
    default_detail = "数据操作失败"


class InvalidArgument(APIException):
    status_code = 422
    default_detail = "参数错误"


class InvalidConnectorCode(APIException):
    status_code = 423
    default_detail = "连接器编码错误"


class StartUpException(AeotradeConnectorException):
    pass


class TaskDistributeException(Exception):
    """Task distribute error."""
    pass


class ExternalApiException(TaskDistributeException):
    """External api error."""
    pass


class MQMessageParserException(TaskDistributeException):
    """Parser MQ message error."""
    pass


class DXPMessageParserException(TaskDistributeException):
    """Parser DXP message error."""
    pass


class TaskNotFoundDataException(TaskDistributeException):
    """Task not found error."""
    pass


class TaskStatusIllegalException(TaskDistributeException):
    """Task status is illegal error."""
    pass


class TaskParamsIllegalException(TaskDistributeException):
    """Task params is illegal error."""
    pass


class TaskExceptedException(TaskDistributeException):
    """Task excepted error."""
    pass


class TaskServicesNotFoundException(TaskDistributeException):
    """Task excepted error."""
    pass


class XMLParserException(Exception):
    pass
