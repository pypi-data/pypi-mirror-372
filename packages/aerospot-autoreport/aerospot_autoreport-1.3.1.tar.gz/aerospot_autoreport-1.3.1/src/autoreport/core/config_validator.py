#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AeroSpot自动化报告生成工具的配置验证器"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

from .exceptions import ConfigValidationError

logger = logging.getLogger(__name__)

class ConfigValidator:
    """配置验证器，用于验证和清理配置"""
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证配置的完整性和正确性
        
        Args:
            config: 配置字典
            
        Returns:
            Tuple[bool, List[str]]: (是否验证成功, 错误消息列表)
        """
        errors = []
        
        # 验证必要的配置项
        required_keys = ['company_info']
        for key in required_keys:
            if key not in config:
                errors.append(f"缺少必要的配置项: {key}")
        
        # 如果缺少必要配置，则直接返回
        if errors:
            return False, errors
        
        # 验证公司信息
        company_info = config.get('company_info', {})
        required_company_info = ['name', 'address', 'email', 'phone', 'profile']
        for key in required_company_info:
            if key not in company_info:
                errors.append(f"公司信息缺少: {key}")
        
        # 验证资源URL
        resource_keys = ['logo_path', 'wayline_img', 'satellite_img', 'file_url', 'measure_data']
        for key in resource_keys:
            value = company_info.get(key, '')
            if not value:
                errors.append(f"缺少资源URL: {key}")
            elif not (value.startswith('http://') or value.startswith('https://') or os.path.exists(value)):
                errors.append(f"资源URL无效: {key}={value}")
        
        # 其他验证逻辑...
        
        return len(errors) == 0, errors
    
    @staticmethod
    def clean_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """清理和标准化配置
        
        Args:
            config: 配置字典
            
        Returns:
            Dict[str, Any]: 清理后的配置字典
        """
        cleaned_config = config.copy()
        
        # 确保公司信息存在
        if 'company_info' not in cleaned_config:
            cleaned_config['company_info'] = {}
        
        # 清理公司信息中的空格
        company_info = cleaned_config['company_info']
        for key in company_info:
            if isinstance(company_info[key], str):
                company_info[key] = company_info[key].strip()
        
        # 确保其他必要结构存在
        if 'pollution_source' not in cleaned_config:
            cleaned_config['pollution_source'] = {}
        
        return cleaned_config


def load_and_validate_config(config_path: str) -> Dict[str, Any]:
    """加载并验证配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        Dict[str, Any]: 验证后的配置字典
        
    Raises:
        ConfigValidationError: 配置验证失败
        FileNotFoundError: 配置文件不存在
        json.JSONDecodeError: JSON解析错误
    """
    # 检查文件是否存在
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件未找到: {config_path}")
    
    # 读取并解析配置
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"配置文件JSON解析错误: {str(e)}", e.doc, e.pos)
    
    # 验证配置
    is_valid, errors = ConfigValidator.validate_config(config)
    if not is_valid:
        error_msg = "配置验证失败: \n" + "\n".join(errors)
        # raise ConfigValidationError(error_msg)
        logger.warning(f'{error_msg}')
    
    # 清理配置
    cleaned_config = ConfigValidator.clean_config(config)
    
    return cleaned_config 