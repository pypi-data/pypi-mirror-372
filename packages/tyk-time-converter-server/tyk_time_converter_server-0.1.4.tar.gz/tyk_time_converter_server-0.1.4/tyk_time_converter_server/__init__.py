"""tyk_time_converter包初始化文件"""

from .tyk_time_converter_server import convert_seconds_to_time, get_current_time, current_time_iso_resource

__version__ = "0.1.4"
__author__ = "tangyongkang"
__all__ = ["convert_seconds_to_time", "get_current_time", "current_time_iso_resource"]