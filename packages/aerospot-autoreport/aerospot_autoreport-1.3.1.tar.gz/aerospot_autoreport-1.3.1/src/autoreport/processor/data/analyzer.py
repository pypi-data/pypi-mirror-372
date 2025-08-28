"""
数据分析模块
提供数据分析和误差计算功能
"""
import logging
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def _safe_relative_error(predicted: float, actual: float, abs_threshold: float = 1e-10) -> Optional[float]:
    """
    安全的相对误差计算
    
    Args:
        predicted: 预测值
        actual: 实际值
        abs_threshold: 绝对值阈值，当实际值小于此阈值时返回None
        
    Returns:
        相对误差百分比，如果计算不可行则返回None
    """
    try:
        # 检查输入值是否有效
        if not (math.isfinite(predicted) and math.isfinite(actual)):
            return None
        
        # 当实际值很小时，相对误差无意义
        if abs(actual) < abs_threshold:
            return None
        
        # 计算相对误差
        relative_error = (predicted - actual) / actual * 100
        
        # 检查结果是否有效
        if not math.isfinite(relative_error):
            return None
        
        return round(relative_error, 2)
    
    except (ZeroDivisionError, ValueError, TypeError):
        return None

def calculate_statistics(data: pd.DataFrame, indicator_columns: list, get_unit_func) -> Dict[str, Dict[str, Any]]:
    """
    计算每个指标的基本统计信息
    
    Args:
        data: 数据DataFrame
        indicator_columns: 指标列名列表
        get_unit_func: 获取指标单位的函数
        
    Returns:
        Dict[str, Dict[str, Any]]: 指标统计信息字典
    """
    statistics = {}
    
    for indicator in indicator_columns:
        # 基本统计量
        stats = data[indicator].describe()
        
        statistics[indicator] = {
            'min': float(stats['min']),
            'max': float(stats['max']),
            'mean': float(stats['mean']),
            'std': float(stats['std']),
            'median': float(data[indicator].median()),
            'units': get_unit_func(indicator)
        }
    
    return statistics

def generate_data_summary(data: pd.DataFrame, indicator_columns: list) -> Dict[str, Any]:
    """
    生成数据摘要
    
    Args:
        data: 数据DataFrame
        indicator_columns: 指标列名列表
        
    Returns:
        Dict[str, Any]: 数据摘要字典
    """
    return {
        'sample_count': len(data),
        'indicators': indicator_columns,
        'geo_range': {
            'latitude': {
                'min': float(data['latitude'].min()),
                'max': float(data['latitude'].max())
            },
            'longitude': {
                'min': float(data['longitude'].min()),
                'max': float(data['longitude'].max())
            }
        }
    }

def analyze_errors(matched_measure_df: pd.DataFrame, matched_merged_df: pd.DataFrame, 
                   pred_data: pd.DataFrame, output_file: Optional[str] = None) -> Dict[str, Any]:
    """
    分析原始航测数据和新反演数据的误差
    
    Args:
        matched_measure_df: 实测数据
        matched_merged_df: 原始航测数据
        pred_data: 新反演数据
        output_file: 输出文件路径（可选）
    
    Returns:
        Dict[str, Any]: 包含误差分析结果的字典
    """
    result = {
        'matches': [],
        'statistics': {}
    }
    
    # 获取所有指标
    indicators = [col for col in matched_measure_df.columns if col not in ['index', 'latitude', 'longitude']]
    
    # 对每个点进行分析
    for idx in matched_measure_df.index:
        measure_row = matched_measure_df.loc[idx]
        merged_row = matched_merged_df.loc[idx]
        pred_row = pred_data.loc[idx]
        
        match = {
            'point_index': idx,
            'indicators': {}
        }
        
        # 比较三个数据集的值
        for indicator in indicators:
            measure_value = float(measure_row[indicator])
            merged_value = float(merged_row[indicator])
            pred_value = float(pred_row[indicator])
            
            match['indicators'][indicator] = {
                'measure_value': measure_value,
                'merged_value': merged_value,
                'pred_value': pred_value,
                'merged_diff': round(merged_value - measure_value, 4),
                'pred_diff': round(pred_value - measure_value, 4),
                'merged_rel_diff': _safe_relative_error(merged_value, measure_value),
                'pred_rel_diff': _safe_relative_error(pred_value, measure_value)
            }
        
        result['matches'].append(match)
    
    # 计算整体统计信息
    for indicator in indicators:
        merged_diffs = []
        pred_diffs = []
        merged_rel_diffs = []
        pred_rel_diffs = []
        
        for match in result['matches']:
            ind_data = match['indicators'][indicator]
            merged_diffs.append(ind_data['merged_diff'])
            pred_diffs.append(ind_data['pred_diff'])
            if ind_data['merged_rel_diff'] is not None:
                merged_rel_diffs.append(ind_data['merged_rel_diff'])
            if ind_data['pred_rel_diff'] is not None:
                pred_rel_diffs.append(ind_data['pred_rel_diff'])
        
        result['statistics'][indicator] = {
            'merged': {
                'mean_diff': float(np.mean(merged_diffs)),
                'std_diff': float(np.std(merged_diffs)),
                'mean_rel_diff': float(np.mean(merged_rel_diffs)) if merged_rel_diffs else None,
                'std_rel_diff': float(np.std(merged_rel_diffs)) if merged_rel_diffs else None
            },
            'predicted': {
                'mean_diff': float(np.mean(pred_diffs)),
                'std_diff': float(np.std(pred_diffs)),
                'mean_rel_diff': float(np.mean(pred_rel_diffs)) if pred_rel_diffs else None,
                'std_rel_diff': float(np.std(pred_rel_diffs)) if pred_rel_diffs else None
            }
        }
    
    # 保存到输出文件
    if output_file:
        output_data = []
        for match in result['matches']:
            row = {'point_index': match['point_index']}
            for indicator, values in match['indicators'].items():
                row[f'{indicator}_measure'] = values['measure_value']
                row[f'{indicator}_merged'] = values['merged_value']
                row[f'{indicator}_pred'] = values['pred_value']
                row[f'{indicator}_merged_diff'] = values['merged_diff']
                row[f'{indicator}_pred_diff'] = values['pred_diff']
                row[f'{indicator}_merged_rel_diff'] = values['merged_rel_diff']
                row[f'{indicator}_pred_rel_diff'] = values['pred_rel_diff']
            output_data.append(row)
        
        pd.DataFrame(output_data).to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"误差分析结果已保存到: {output_file}")
    
    logger.info("误差分析完成")
    return result 