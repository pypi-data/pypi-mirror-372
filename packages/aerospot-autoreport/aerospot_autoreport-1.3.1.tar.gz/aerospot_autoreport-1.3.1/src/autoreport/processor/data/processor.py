"""
数据处理器模块
提供数据处理和分析的核心功能
"""

import logging
from typing import Any, Dict, Optional

import pandas as pd
from autowaterqualitymodeler.run import main

from .analyzer import analyze_errors, calculate_statistics, generate_data_summary
from .matcher import find_common_indicators, handle_invalid_values, match_nearest_points
from .standardizer import standardize_column_names, standardize_indicator_names
from .utils import get_indicator_unit

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    数据处理器类
    用于处理和分析航测数据
    """

    def __init__(self, config=None):
        """
        初始化数据处理器

        Args:
            config: 配置字典，包含数据处理的相关配置
        """
        self.config = config or {}

    def _get_indicator_unit(self, indicator):
        """
        根据指标名称获取单位

        Args:
            indicator: 指标名称

        Returns:
            指标单位字符串
        """
        return get_indicator_unit(indicator, self.config)

    def process_data(self, merged_data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        处理合并后的数据，计算统计信息

        Args:
            merged_data: 合并后的数据DataFrame

        Returns:
            处理后的统计信息字典
        """
        try:
            logger.info("开始处理数据")

            # 初始化结果字典
            result = dict()

            # 定义非指标列名的关键词列表
            non_indicator_keywords = [
                "index",
                "latitude",
                "longitude",
                "lat",
                "lon",
                "lng",
                "采样点",
                "精度",
                "维度",
                "经度",
                "纬度",
                "点位",
                "编号",
                "id",
                "ID",
            ]

            # 标准化列名
            merged_data, column_mapping = standardize_column_names(merged_data)

            # 确保必要的列存在
            required_columns = ["index", "latitude", "longitude"]
            for col in required_columns:
                if col not in merged_data.columns:
                    logger.warning(f"缺少必要的列: {col}")

            # 提取指标列
            indicator_columns = [
                col
                for col in merged_data.columns
                if col not in ["index", "latitude", "longitude"]
            ]
            logger.info(
                f"找到 {len(indicator_columns)} 个指标: {', '.join(indicator_columns)}"
            )

            # 标准化指标名称
            merged_data, indicator_columns = standardize_indicator_names(
                merged_data, indicator_columns
            )

            # 存储处理后的数据
            result["processed_data"] = merged_data

            # 计算统计信息
            result["statistics"] = calculate_statistics(
                merged_data, indicator_columns, self._get_indicator_unit
            )

            # 生成数据摘要
            result["data_summary"] = generate_data_summary(
                merged_data, indicator_columns
            )

            logger.info("数据处理完成")
            return result
        except Exception as e:
            logger.error(f"处理数据时出错: {str(e)}")
            return None

    def match_and_analyze_data(
        self,
        merged_data: pd.DataFrame,
        measure_data: pd.DataFrame,
        ref_data: pd.DataFrame,
        output_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        匹配和分析航测数据与人工采样数据

        Args:
            merged_data: 合并后的航测数据DataFrame
            measure_data: 人工采样数据DataFrame
            ref_data: 参考数据DataFrame
            output_file: 可选的输出文件路径

        Returns:
            匹配和分析结果字典
        """
        try:
            logger.info("开始匹配和分析数据")

            # 初始化结果字典
            result = {"matches": [], "statistics": {}}

            # 获取共同的指标列
            common_indicators = find_common_indicators(merged_data, measure_data)
            if not common_indicators:
                return result

            # 找到最近的航测点
            matched_idx = match_nearest_points(measure_data, merged_data)
            if len(set(matched_idx)) <= 1:
                logger.error("所有实测值点位匹配同一条无人机数据，请核对数据GPS信息。")
            if len(set(matched_idx)) != len(measure_data):
                logger.warning(f"实测数据和无人机数据不是一一对应！{matched_idx}")


            # 将匹配的点转换为DataFrame
            matched_measure_df = measure_data[common_indicators]
            matched_merged_df = merged_data.iloc[matched_idx][common_indicators]
            matched_merged_df.index = matched_measure_df.index
            matched_ref_df = ref_data.iloc[matched_idx]
            matched_ref_df.index = matched_measure_df.index

            # 进行建模，获取新的反演值
            model_func, pred_data, all_pred_data = main(
                ref_data,
                merged_data[common_indicators],
                measure_data[common_indicators],
                matched_idx,
            )

            # 处理无效值
            pred_data = handle_invalid_values(pred_data, matched_merged_df)
            all_pred_data = handle_invalid_values(all_pred_data, merged_data)

            # 分析误差
            return (
                analyze_errors(
                    matched_measure_df=matched_measure_df,
                    matched_merged_df=matched_merged_df,
                    pred_data=pred_data,
                    output_file=output_file,
                ),
                pred_data,
                model_func,
                all_pred_data,
            )

        except Exception as e:
            logger.error(f"匹配和分析数据时出错: {str(e)}")
            return None
