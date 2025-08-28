"""
数据标准化模块
提供数据列名和指标名称的标准化功能
"""
import logging
import pandas as pd
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

def standardize_column_names(data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    标准化列名，将经纬度相关列统一为标准格式
    
    Args:
        data: 输入的DataFrame
        
    Returns:
        Tuple[pd.DataFrame, Dict[str, str]]: 
            - 标准化后的DataFrame
            - 列名映射字典
    """
    column_mapping = {}
    for col in data.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['latitude', 'lat', '纬度', '维度']):
            column_mapping[col] = 'latitude'
        elif any(keyword in col_lower for keyword in ['longitude', 'lon', 'lng', '经度', '精度']):
            column_mapping[col] = 'longitude'
        elif any(keyword == col_lower for keyword in ['index', 'id', '编号', '采样点', '点位', 'ID']):
            column_mapping[col] = 'index'
    
    # 重命名列
    if column_mapping:
        data = data.rename(columns=column_mapping)
        logger.info(f"列名标准化映射: {column_mapping}")
    
    return data, column_mapping

def standardize_indicator_names(data: pd.DataFrame, indicator_columns: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """
    标准化指标名称
    
    Args:
        data: 输入的DataFrame
        indicator_columns: 指标列名列表
        
    Returns:
        Tuple[pd.DataFrame, List[str]]: 
            - 标准化后的DataFrame
            - 标准化后的指标列名列表
    """
    # 水质参数标准名称映射表
    indicator_name_mapping = {
        # 浊度相关
        'turbidity': 'turbidity',
        '浊度': 'turbidity',
        'turb': 'turbidity',
        # 悬浮物相关
        'ss': 'ss',
        '悬浮物': 'ss',
        'suspended solids': 'ss',
        # 溶解氧相关
        'do': 'do',
        '溶解氧': 'do',
        'dissolved oxygen': 'do',
        # 化学需氧量相关
        'cod': 'cod',
        '化学需氧量': 'cod',
        'chemical oxygen demand': 'cod',
        # 生化需氧量相关
        'bod': 'bod',
        'bod5': 'bod',
        '生化需氧量': 'bod',
        'biochemical oxygen demand': 'bod',
        # 氨氮相关
        'nh3-n': 'nh3n',
        'nh3n': 'nh3n',
        '氨氮': 'nh3n',
        'nh3_n': 'nh3n',
        'ammonia nitrogen': 'nh3n',
        # 总氮相关
        'tn': 'tn',
        '总氮': 'tn',
        'total nitrogen': 'tn',
        # 总磷相关
        'tp': 'tp',
        '总磷': 'tp',
        'total phosphorus': 'tp',
        # pH值相关
        'ph': 'ph',
        'ph值': 'ph',
        # 电导率相关
        'ec': 'ec',
        '电导率': 'ec',
        'conductivity': 'ec',
        # 温度相关
        'temp': 'temperature',
        '温度': 'temperature',
        'temperature': 'temperature',
        'bga': 'bga',
        '蓝绿藻': 'bga',
        'chla': 'chla',
        '叶绿素': 'chla',
        'chlorophyll': 'chla',
        'chl': 'chla',
        'chl_a': 'chla'
    }
    
    # 创建新的标准化指标列表和重命名映射
    standardized_columns = []
    rename_mapping = {}
    
    for col in indicator_columns:
        col_lower = col.lower()
        if col_lower in indicator_name_mapping:
            standard_name = indicator_name_mapping[col_lower]
            rename_mapping[col] = standard_name
            standardized_columns.append(standard_name)
        else:
            # 如果没有匹配的标准名称，则使用小写形式
            rename_mapping[col] = col_lower
            standardized_columns.append(col_lower)
    
    # 重命名指标列
    data = data.rename(columns=rename_mapping)
    
    logger.info(f"指标名称标准化完成，标准化后的指标: {', '.join(standardized_columns)}")
    return data, standardized_columns 