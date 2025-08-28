"""
工具函数模块
===========

提供各种辅助工具函数，包括：
- 字体处理
- 地理坐标处理
- 文件IO操作
- 路径管理
- 文本处理
"""

# 延迟导入以避免循环依赖
# from .font import set_default_font
# from .geo import *
# from .io import merge_data_files
# from .path import PathManager
# from .text import *

__all__ = [
    "set_default_font",
    "merge_data_files",
    "PathManager",
]