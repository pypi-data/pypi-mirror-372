"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/11 14:30
@file: server_mode.py
@project: django_aeotrade_connector
@describe: Server mode definitions
"""
from enum import Enum


class ServerMode(str, Enum):
    """服务器运行模式枚举类"""
    # 纯云端模式
    CLOUD = "cloud"
    # 混合模式-云端
    MIX_CLOUD = "mix_cloud"
    # 混合模式-本地端
    MIX_LOCAL = "mix_local"

    @classmethod
    def value_of(cls, value: str) -> 'ServerMode':
        """
        根据给定的值获取对应的服务器模式
        :param value: 服务器模式值
        :return: ServerMode枚举项
        """
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f'无效的服务器模式值 {value}')
