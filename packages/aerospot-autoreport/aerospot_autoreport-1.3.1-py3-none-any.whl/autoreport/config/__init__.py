"""
配置管理模块
============

负责管理应用程序的配置信息，包括：
- 公司信息配置
- 系统常量
- 字体配置
- 样式配置
"""

# 延迟导入以避免循环依赖
# from .company_info import DEFAULT_COMPANY_INFO
# from .constants import *
# from .fonts import *
# from .styles import *

__all__ = [
    "DEFAULT_COMPANY_INFO",
]