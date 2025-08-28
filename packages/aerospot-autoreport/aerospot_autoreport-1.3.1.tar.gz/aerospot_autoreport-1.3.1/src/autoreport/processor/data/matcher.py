"""
数据匹配模块
提供航测数据与人工采样数据的匹配和分析功能
"""
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional

from ...utils.geo import haversine
from .analyzer import analyze_errors

logger = logging.getLogger(__name__)

def find_common_indicators(merged_data: pd.DataFrame, measure_data: pd.DataFrame) -> List[str]:
    """
    查找共同的指标列
    
    Args:
        merged_data: 合并后的航测数据DataFrame
        measure_data: 人工采样数据DataFrame
        
    Returns:
        List[str]: 共同的指标列名列表
    """
    common_indicators = list(set(merged_data.columns) & set(measure_data.columns))
    # common_indicators = [col for col in common_indicators if col not in ['index', 'latitude', 'longitude']]
    
    if not common_indicators:
        logger.warning("没有找到共同的指标列")
    else:
        logger.info(f"找到共同指标: {', '.join(common_indicators)}")
        
    return common_indicators

def match_nearest_points(measure_data: pd.DataFrame, merged_data: pd.DataFrame) -> List[int]:
    """
    为每个人工采样点找到最近的航测点

    Args:
        measure_data: 人工采样数据DataFrame
        merged_data: 合并后的航测数据DataFrame

    Returns:
        List[int]: 匹配的航测点索引列表
    """
    matched_idx = []

    logger.info(f"开始匹配人工采样点与航测点，总共{len(measure_data)}个人工采样点，{len(merged_data)}个航测点。")

    # 对每个人工采样点，找到最近的航测点
    for idx, measure_row in measure_data.iterrows():
        measure_lat = measure_row['latitude']
        measure_lon = measure_row['longitude']

        # 计算到所有航测点的距离
        distances = []
        for _, merged_row in merged_data.iterrows():
            dist = haversine(measure_lat, measure_lon,
                           merged_row['latitude'], merged_row['longitude'])
            distances.append(dist)

        # 找到最近的点
        min_dist_idx = np.argmin(distances)
        matched_idx.append(min_dist_idx)
        logger.info(f"人工采样点 {idx} (lat: {measure_lat}, lon: {measure_lon}) 匹配到最近航测点索引 {min_dist_idx}，距离为 {distances[min_dist_idx]:.4f} 米。")

    logger.info(f"所有人工采样点已完成匹配。")
    return matched_idx

def handle_invalid_values(pred_data: pd.DataFrame, matched_merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    处理无效值，用原始航测数据替换
    
    Args:
        pred_data: 预测数据DataFrame
        matched_merged_df: 匹配的原始航测数据DataFrame
        
    Returns:
        pd.DataFrame: 处理后的预测数据DataFrame
    """
    # 检查pred_data中缺失的列
    missing_cols = set(matched_merged_df.columns) - set(pred_data.columns)
    if missing_cols:
        logger.warning(f"发现{len(missing_cols)}个缺失列: {', '.join(missing_cols)}")
        # 从matched_merged_df中复制缺失的列
        for col in missing_cols:
            pred_data[col] = matched_merged_df[col]
        logger.info("已从原始航测数据补充缺失列")

    # 检查pred_data中的无效值
    invalid_mask = pred_data.isna() | (pred_data <= 0)
    invalid_count = invalid_mask.sum().sum()
    
    if invalid_count > 0:
        logger.warning(f"发现{invalid_count}个无效值(NA或非正数)")
        
        # 记录每个指标中无效值的数量
        for col in pred_data.columns:
            col_invalid = invalid_mask[col].sum()
            if col_invalid > 0:
                logger.warning(f"指标 {col} 中存在 {col_invalid} 个无效值")
                
                # 记录具体的行索引
                invalid_rows = pred_data.index[invalid_mask[col]].tolist()
                logger.warning(f"无效值出现在行: {invalid_rows}")
        
        # 用matched_merged_df的值替换无效值
        pred_data = pred_data.where(~invalid_mask, matched_merged_df)
        logger.info("已用原始航测数据替换所有无效值")
    else:
        logger.info("未发现无效值")
    
    # 按照matched_merged_df的列顺序重新排列pred_data的列
    pred_data = pred_data[matched_merged_df.columns]
        
    return pred_data

    