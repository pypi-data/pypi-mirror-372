"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/9 11:37
@file: utils.py
@project: django_aeotrade_connector
@describe: None
"""
import datetime
import json
import logging
import os
import random
import re
import string
import sys
import time
import uuid
from functools import wraps
from json import JSONDecodeError
from typing import Any, Optional
from urllib.parse import urlparse

import xmltodict
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator as DjangoPaginator
from rest_framework.response import Response

from aeotrade_connector.exceptions import InvalidArgument, XMLParserException

loger_name = settings.AC_LOG_NAME if hasattr(settings, "AC_LOG_NAME") else "default"
logger = logging.getLogger(loger_name)


def validate_url(url: str, raise_exception: Optional[bool] = False) -> bool:
    """Validate URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception as e:  # noqa
        err = f"[AeotradeUtils] Invalid URL: {url}, error: {e}"
        if raise_exception:
            raise ValueError(err)
        else:
            logger.error(err)
            return False


def random_str(
        length: int, only_digits=False, digits=False, upper=False, hexdigits=False
) -> str:
    """生成随机字符串"""

    if only_digits:
        rand_str = string.digits
        return "".join(random.choices(rand_str[1:], k=1)) + "".join(
            random.choices(rand_str, k=length - 1)
        )
    rand_str = string.ascii_lowercase[: 6 if hexdigits else 26]
    if digits:
        rand_str += string.digits
    if upper:
        rand_str += string.ascii_uppercase[: 6 if hexdigits else 26]
    return "".join(random.choices(rand_str, k=length))


def json_encoder(obj: Any):
    """JSON 序列化, 修复时间"""
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")

    return super().default(obj)  # type: ignore


def json_decoder(obj: Any):
    """JSON 反序列化，加载时间"""
    ret = obj
    if isinstance(obj, list):
        obj = enumerate(obj)
    elif isinstance(obj, dict):
        obj = obj.items()
    else:
        return obj

    for key, item in obj:
        if isinstance(item, (list, dict)):
            ret[key] = json_decoder(item)
        else:
            ret[key] = item
    return ret


def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return get_instance


class JsonFieldMixin:

    def get_prep_value(self, value):
        if not value or not isinstance(value, (list, dict, tuple)):
            return super().get_prep_value(value)  # noqa
        return json.dumps(value, ensure_ascii=False, default=json_encoder)

    def from_db_value(self, value, expression, connection):

        if "dumpdata" in sys.argv:
            return value
        if not value or not isinstance(value, str):
            return value
        try:
            return json.loads(value, object_hook=json_decoder)
        except JSONDecodeError:
            try:
                dumps_value = json.dumps(value, ensure_ascii=False, default=json_encoder)
                return json.loads(dumps_value, object_hook=json_decoder)
            except JSONDecodeError as err:
                return ValidationError(err)


class Paginator(DjangoPaginator):
    def __init__(
            self,
            object_list,
            request,
            per_page=None,
            orphans=0,
            allow_empty_first_page=True,
            check_order=False,
    ):
        self.current_page = request.GET.get("page", request.data.get("page", 1))
        self.check_order = check_order
        if not per_page:
            per_page = settings.DEFAULT_PAGE_SIZE
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)

    def get(self):
        return self.get_page(self.current_page)

    def _check_object_list_is_ordered(self):
        if self.check_order:
            super()._check_object_list_is_ordered()  # noqa


class APIResponse(Response):
    def __init__(
            self,
            data=None,
            status: int = 200,
            msg: str = "Success",
            template_name=None,
            headers=None,
            exception=False,
            content_type=None,
    ):
        ret = {"code": status, "msg": msg, "data": data if data is not None else []}
        super().__init__(ret, status, template_name, headers, exception, content_type)

    def set_data(self, data: Any):
        self.data["data"] = data
        return self

    def set_code(self, code: int):
        self.data["code"] = code
        return self

    def set_msg(self, msg: str):
        self.data["msg"] = msg
        return self

    def set_pagination(self, paginator: Paginator):
        return self.set_pagination_manual(
            paginator.count, paginator.per_page, paginator.current_page
        )

    def set_pagination_manual(self, total: int, per_page: int, current_page: int):
        """更新分页信息 手动"""
        self.data["data"]["pagination"] = {
            "total": total,
            "per_page": per_page,
            "current_page": current_page,
        }
        return self


def get_base_path():
    return os.path.dirname(os.path.abspath(__file__))


def generate_tsid(as_string=False, include_hyphens=True):
    """
    Generate a tsid, a UUID4 with a timestamp in the top half.
    :param as_string: Return as a string
    :param include_hyphens: Include hyphens
    :return:
    """
    timestamp = int(time.time() * 1e7)
    random_uuid = uuid.uuid4().int >> 64  # Take the top half of a UUID4 for randomness
    ordered_uuid = (timestamp << 64) | random_uuid  # Combine the timestamp and randomness

    generated_uuid = uuid.UUID(int=ordered_uuid)

    if as_string:
        uuid_str = str(generated_uuid)
        if not include_hyphens:
            uuid_str = uuid_str.replace('-', '')
        return uuid_str
    else:
        return generated_uuid


def check_request(request, serializer):
    serializer_data = serializer(data=request.data, context={"request": request})
    if not serializer_data.is_valid():
        if settings.IS_TEST or settings.DEBUG:
            logging.error(serializer_data.errors)
        raise InvalidArgument
    request_data = serializer_data.validated_data
    return request_data


class XMLHandler:
    def __init__(self, remove_xml_declaration=True):
        self.remove_xml_declaration = remove_xml_declaration

    def xml_to_dict(self, xml_data: str, raise_exception: bool = True) -> dict:
        """
        xml to dict
        :param raise_exception: bool, if True, raise exception
        :param xml_data: str, XML
        :return: dict
        """

        # remove xml declaration
        if self.remove_xml_declaration:
            xml_data = re.sub(r'<\?xml.*?\?>', '', xml_data).strip()

        try:
            return xmltodict.parse(xml_data)
        except Exception as e:
            if raise_exception:
                raise XMLParserException(f"[XMLHandler] XML 解析失败: {e}")
            logger.info(f"[XMLHandler] XML 解析失败: {e}")
            return {}
