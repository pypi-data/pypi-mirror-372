#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路径管理模块，提供统一的路径管理功能

此模块提供了PathManager类，用于管理项目中的所有路径。
主要功能包括：
1. 创建和维护项目目录结构
2. 获取各类文件和目录的路径
3. 自动生成唯一的文件名，避免重名
4. 支持嵌套路径处理
"""

import logging
import os
from datetime import datetime

# 获取模块日志记录器
logger = logging.getLogger(__name__)


class PathManager:
    """
    路径管理器类

    此类用于管理项目中的所有路径，提供统一的路径访问接口，简化路径管理。
    自动创建必要的目录结构，并提供各种便捷方法来获取不同类型的文件路径。

    主要功能:
    - 根据配置创建和维护项目目录结构
    - 提供统一的路径获取接口
    - 自动生成唯一的文件名，避免文件覆盖
    - 支持嵌套路径和动态创建目录

    属性:
        base_dir (str): 项目的基础目录
        dirs (dict): 包含所有主要目录路径的字典

    示例:
        # 创建路径管理器
        pm = PathManager("./project_dir")

        # 获取下载目录路径
        downloads_dir = pm.get_path("downloads")

        # 获取报告文件路径
        report_path = pm.get_report_path("测试报告")
    """

    def __init__(self, base_dir: str = None):
        """初始化路径管理器

        创建路径管理器实例并初始化目录结构。

        Args:
            base_dir: 基础目录，如果为None则使用当前目录
        """
        self.base_dir = base_dir or os.getcwd()
        logger.info(f"初始化路径管理器，使用基础目录: {self.base_dir}")

        # 完全使用v1版本的目录结构
        self.dirs = {
            "downloads": os.path.join(
                self.base_dir, "downloads"
            ),  # 通过链接下载的所有文件，包括压缩包、csv和图片
            "reports": os.path.join(self.base_dir, "reports"),  # 生成的报告文件
            "extracted": os.path.join(self.base_dir, "extracted"),  # 解压后的文件
            "maps": os.path.join(self.base_dir, "maps"),  # 基于下载的图片生成的地图文件
            "logs": os.path.join(self.base_dir, "logs"),  # 日志文件
            "models": os.path.join(self.base_dir, "models"),  # 模型文件
            "predict": os.path.join(self.base_dir, "predict"),  # 反演结果文件
        }

        # 创建必要的目录
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
            logger.debug(f"创建目录: {dir_path}")

        logger.info(f"路径管理器初始化完成，基础目录: {self.base_dir}")

    def get_path(self, path_type: str) -> str:
        """获取指定类型的路径

        根据路径类型获取对应的目录路径。支持直接路径和嵌套路径，
        对于未知的路径类型会自动创建相应的目录。

        Args:
            path_type: 路径类型，如'downloads', 'images'等，
                      也支持嵌套路径如'psj/image/report'

        Returns:
            对应类型的路径字符串

        示例:
            # 获取下载目录
            downloads_dir = pm.get_path("downloads")

            # 获取嵌套目录
            nested_dir = pm.get_path("psj/image/report")
        """
        # 直接路径
        if path_type in self.dirs:
            return self.dirs[path_type]

        # 嵌套路径处理 (例如 'psj/image/report')
        if "/" in path_type:
            parts = path_type.split("/")
            # 根据路径层级构建完整路径
            full_path = os.path.join(self.base_dir, *parts)
            # 确保该目录存在
            os.makedirs(full_path, exist_ok=True)
            return full_path

        # 兼容'image'和'images'
        if path_type == "image" and "images" in self.dirs:
            logger.debug("使用'images'目录代替'image'")
            return self.dirs["images"]

        # 如果是其他未知类型，则在base_dir下创建该目录
        new_dir = os.path.join(self.base_dir, path_type)
        os.makedirs(new_dir, exist_ok=True)
        logger.debug(f"创建新目录: {new_dir}")
        return new_dir

    def get_file_path(self, path_type: str, filename: str) -> str:
        """获取指定类型目录下的文件路径

        根据路径类型和文件名生成完整的文件路径。

        Args:
            path_type: 路径类型，如'downloads', 'images'等
            filename: 文件名

        Returns:
            完整的文件路径

        示例:
            # 获取CSV文件路径
            csv_path = pm.get_file_path("downloads", "data.csv")
        """
        return os.path.join(self.get_path(path_type), filename)

    def get_unique_filename(self, path_type: str, filename: str) -> str:
        """获取唯一的文件名，避免重名

        生成一个保证唯一的文件路径。如果文件名已存在，会自动添加时间戳。

        Args:
            path_type: 路径类型，如'downloads', 'images'等
            filename: 文件名

        Returns:
            唯一的文件路径

        示例:
            # 获取唯一的报告文件路径
            unique_report = pm.get_unique_filename("reports", "report.docx")
            # 如果文件已存在，返回类似 "report_20250508133049.docx" 的路径
        """
        base_path = self.get_path(path_type)
        name, ext = os.path.splitext(filename)

        # 尝试使用原始文件名
        full_path = os.path.join(base_path, filename)
        if not os.path.exists(full_path):
            return full_path

        # 如果文件已存在，添加时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{name}_{timestamp}{ext}"
        return os.path.join(base_path, new_filename)

    def get_report_path(self, report_name: str) -> str:
        """获取报告文件路径

        获取报告文件的完整路径，自动添加.docx扩展名（如果需要）。

        Args:
            report_name: 报告名称

        Returns:
            报告文件路径

        示例:
            # 获取报告文件路径
            report_path = pm.get_report_path("项目进度报告")
            # 返回类似 "reports/项目进度报告.docx" 的路径
        """
        if not report_name.endswith(".docx"):
            report_name = f"{report_name}.docx"

        return self.get_unique_filename("reports", report_name)

    def get_log_path(self, log_name: str) -> str:
        """获取日志文件路径

        获取日志文件的完整路径，自动添加.log扩展名（如果需要）。

        Args:
            log_name: 日志文件名

        Returns:
            日志文件路径

        示例:
            # 获取日志文件路径
            log_path = pm.get_log_path("application")
            # 返回类似 "logs/application.log" 的路径
        """
        if not log_name.endswith(".log"):
            log_name = f"{log_name}.log"

        return self.get_unique_filename("logs", log_name)

    def get_image_path(self, image_type: str, filename: str) -> str:
        """获取图片文件路径

        根据图片类型和文件名获取图片文件的完整路径。

        Args:
            image_type: 图片类型/子目录路径
            filename: 文件名

        Returns:
            图片文件路径

        示例:
            # 获取报告图片路径
            image_path = pm.get_image_path("report", "screenshot.png")

            # 获取嵌套路径下的图片
            nested_image = pm.get_image_path("psj/image/wayline", "route.png")
        """
        # 构建图片路径 (允许嵌套路径)
        image_path = self.get_path(
            f"images/{image_type}" if "/" not in image_type else image_type
        )
        return os.path.join(image_path, filename)

    def get_log_dir(self) -> str:
        """获取日志目录路径

        Returns:
            日志目录路径
        """
        return self.get_path("logs")

    def get_base_dir(self) -> str:
        """获取基础目录路径

        Returns:
            基础目录路径
        """
        return self.base_dir
