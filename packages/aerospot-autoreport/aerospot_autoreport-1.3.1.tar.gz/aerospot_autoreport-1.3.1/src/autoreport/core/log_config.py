#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AeroSpot自动化报告生成工具的日志配置"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

def configure_logging(log_dir: str, 
                    level: int = logging.INFO, 
                    log_file_prefix: str = "aerospot",
                    max_bytes: int = 10*1024*1024,  # 10MB
                    backup_count: int = 5,
                    console=False) -> logging.Logger:
    """配置日志系统
    
    Args:
        log_dir: 日志目录
        level: 日志级别
        log_file_prefix: 日志文件前缀
        max_bytes: 每个日志文件的最大大小
        backup_count: 最多保留的日志文件数
        
    Returns:
        logging.Logger: 配置好的根日志记录器
    """
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    if console:
        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # 创建日志文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"{log_file_prefix}_{timestamp}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    # 添加文件处理器
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # 文件日志使用更详细的格式
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(pathname)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    # 设置未捕获异常处理器
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # 键盘中断交由系统处理
            import sys
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        # 记录未捕获的异常
        root_logger.critical("未捕获的异常:", exc_info=(exc_type, exc_value, exc_traceback))
    
    import sys
    sys.excepthook = handle_exception
    
    # 记录日志系统初始化信息
    root_logger.info(f"日志系统已初始化，主日志文件: {log_path}")
    
    return root_logger 