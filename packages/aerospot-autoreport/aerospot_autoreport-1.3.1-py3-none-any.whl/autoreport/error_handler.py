#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AeroSpot自动化报告生成工具的错误处理器"""

import logging
from typing import Callable, TypeVar, Any, Optional
import traceback
import functools

T = TypeVar('T')

class ErrorHandler:
    """异常处理器，提供统一的异常处理机制"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_exception(self, 
                        exc: Exception, 
                        error_msg: str = "操作执行失败", 
                        default_return: Any = None,
                        log_level: int = logging.ERROR,
                        raise_exception: bool = False) -> Any:
        """处理异常并记录日志
        
        Args:
            exc: 捕获的异常
            error_msg: 错误消息前缀
            default_return: 默认返回值
            log_level: 日志级别
            raise_exception: 是否重新抛出异常
            
        Returns:
            默认返回值或重新抛出异常
        """
        error_type = exc.__class__.__name__
        error_detail = str(exc)
        
        # 构造完整错误消息
        full_message = f"{error_msg}: [{error_type}] {error_detail}"
        
        # 记录日志
        self.logger.log(log_level, full_message)
        
        # 对于严重错误，记录完整堆栈
        if log_level >= logging.ERROR:
            self.logger.log(log_level, traceback.format_exc())
        
        # 决定是返回默认值还是重新抛出异常
        if raise_exception:
            raise exc
        else:
            return default_return
    
    def safe_execute(self, 
                   func: Callable[..., T], 
                   *args, 
                   error_msg: str = "函数执行失败",
                   default_return: Any = None,
                   log_level: int = logging.ERROR,
                   raise_exception: bool = False,
                   **kwargs) -> T:
        """安全执行函数，统一处理异常
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            error_msg: 错误消息前缀
            default_return: 出错时的默认返回值
            log_level: 日志级别
            raise_exception: 是否重新抛出异常
            **kwargs: 函数关键字参数
            
        Returns:
            函数返回值或默认返回值
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return self.handle_exception(
                e, error_msg, default_return, log_level, raise_exception
            )


def safe_operation(error_msg: str = "操作执行失败", 
                 default_return: Any = None,
                 log_level: int = logging.ERROR,
                 raise_exception: bool = False):
    """装饰器: 为函数添加异常处理
    
    Args:
        error_msg: 错误消息前缀
        default_return: 出错时的默认返回值
        log_level: 日志级别
        raise_exception: 是否重新抛出异常
        
    Returns:
        装饰后的函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # 获取或创建错误处理器
            handler = getattr(self, 'error_handler', None)
            if handler is None:
                handler = ErrorHandler(getattr(self, 'logger', None))
            
            return handler.safe_execute(
                func, self, *args,
                error_msg=error_msg,
                default_return=default_return,
                log_level=log_level,
                raise_exception=raise_exception,
                **kwargs
            )
        return wrapper
    return decorator 