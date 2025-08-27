"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2025/1/23 11:14
@file: handlers.py
@project: django_aeotrade_connector
@describe: None
"""
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # if settings.DEBUG:
    #     if not isinstance(exc, (RequestNotAccepted, PermissionDenied)):
    #         print_exc()
    # Now add the HTTP status code to the response.

    if response is not None:
        if response.status_code > 100:
            response.status_code = -response.status_code

        response.data["code"] = response.status_code
        response.data["msg"] = response.data.pop("detail")
        response.data["data"] = []
        response.status_code = 200

    return response
