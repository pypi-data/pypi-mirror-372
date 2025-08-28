"""
资源文件模块
===========

包含项目使用的各种资源文件，包括：
- 图片资源
- 配置文件
- 模板文件
"""

import os

# 获取资源目录路径
RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(RESOURCE_DIR, "images")

__all__ = [
    "RESOURCE_DIR",
    "IMAGES_DIR",
]