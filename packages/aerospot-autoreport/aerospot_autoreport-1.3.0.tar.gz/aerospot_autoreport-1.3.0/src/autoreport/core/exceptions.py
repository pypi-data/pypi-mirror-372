#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AeroSpot自动化报告生成工具的异常类定义"""

class AeroSpotError(Exception):
    """所有自定义异常的基类"""
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

# 资源类异常
class ResourceError(AeroSpotError):
    """资源相关错误的基类"""
    pass

class DownloadError(ResourceError):
    """下载资源时的错误"""
    pass

class ResourceNotFoundError(ResourceError):
    """资源未找到错误"""
    pass

# 数据处理类异常
class DataProcessingError(AeroSpotError):
    """数据处理相关错误的基类"""
    pass

class DataExtractionError(DataProcessingError):
    """数据解压缩错误"""
    pass

class DataParsingError(DataProcessingError):
    """数据解析错误"""
    pass

# 配置类异常
class ConfigError(AeroSpotError):
    """配置相关错误的基类"""
    pass

class ConfigValidationError(ConfigError):
    """配置验证错误"""
    pass

# 报告生成类异常
class ReportGenerationError(AeroSpotError):
    """报告生成相关错误的基类"""
    pass 