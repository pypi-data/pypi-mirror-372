#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AeroSpot自动化报告生成工具的核心模块"""

from .config_validator import ConfigValidator, load_and_validate_config
from .error_handler import ErrorHandler, safe_operation
from .exceptions import (
    AeroSpotError,
    ResourceError,
    DownloadError,
    ResourceNotFoundError,
    DataProcessingError,
    DataExtractionError,
    DataParsingError,
    ConfigError,
    ConfigValidationError,
    ReportGenerationError,
)
from .generator import ReportGenerator
from .log_config import configure_logging
from .resource_manager import ResourceManager

__all__ = [
    # 配置验证
    'ConfigValidator',
    'load_and_validate_config',
    
    # 错误处理
    'ErrorHandler',
    'safe_operation',
    
    # 异常类
    'AeroSpotError',
    'ResourceError',
    'DownloadError',
    'ResourceNotFoundError',
    'DataProcessingError',
    'DataExtractionError',
    'DataParsingError',
    'ConfigError',
    'ConfigValidationError',
    'ReportGenerationError',
    
    # 报告生成
    'ReportGenerator',
    
    # 日志配置
    'configure_logging',
    
    # 资源管理
    'ResourceManager',
]