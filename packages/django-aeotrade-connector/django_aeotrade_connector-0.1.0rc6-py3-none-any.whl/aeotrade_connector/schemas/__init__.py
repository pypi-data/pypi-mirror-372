"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/5 17:55
@file: __init__.py.py
@project: django_aeotrade_connector
@describe: None
"""
from datetime import datetime
from typing import Union

from pydantic import BaseModel, ConfigDict

from aeotrade_connector.encoders import jsonable_encoder


# datetime to iso 8601
def convert_datetime_to_iso_8601(dt: Union[datetime, str]) -> str:
    if isinstance(dt, str):
        return dt
    # remove timezone
    dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class RWModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: convert_datetime_to_iso_8601},
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    def to_dict(self) -> dict:
        return jsonable_encoder(self)
