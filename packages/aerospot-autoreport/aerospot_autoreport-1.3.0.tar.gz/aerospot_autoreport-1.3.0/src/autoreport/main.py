#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AeroSpot自动化报告生成工具V2版本 (优化版)

主要功能：
1. 从远程服务器下载数据资源
2. 解压数据文件，提取必要信息
3. 处理无人机数据和人工采样数据
4. 根据数据生成报告结构配置
5. 生成完整的遥感报告文档
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import pandas as pd
from autowaterqualitymodeler.utils.encryption import encrypt_data_to_file
from dotenv import load_dotenv

from .config.company_info import DEFAULT_COMPANY_INFO
from .config_validator import load_and_validate_config
from .error_handler import ErrorHandler, safe_operation
from .exceptions import (
    AeroSpotError,
    DataProcessingError,
    ReportGenerationError,
    ResourceError,
)
from .generator import ReportGenerator
from .log_config import configure_logging
from .processor.config import create_updated_config

# 导入自定义模块
from .processor.data import DataProcessor
from .processor.extractor import ZipExtractor
from .processor.maps import SatelliteMapGenerator
from .resource_manager import ResourceManager
from .utils.io import merge_data_files
from .utils.path import PathManager

# 加载环境变量
load_dotenv()

# 获取logger
logger = logging.getLogger(__name__)


class AeroSpotReportGenerator:
    """AeroSpot报告生成器主类 (优化版)"""

    def __init__(
        self,
        output_dir: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        cache_enabled: Optional[bool] = None,
    ):
        """初始化报告生成器

        Args:
            output_dir: 输出目录，如果为None则使用默认目录
            config: 配置字典或配置文件路径
            cache_enabled: 是否启用缓存，如果为None则使用默认值
        """
        # 设置输出目录
        if output_dir is None:
            # 使用默认的输出目录
            self.output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "AutoReportResults"
            )
        else:
            self.output_dir = output_dir

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

        # 初始化路径管理器
        self.path_manager = PathManager(self.output_dir)

        # 设置日志系统
        log_dir = self.path_manager.get_log_dir()
        configure_logging(log_dir, console=False)

        # 初始化错误处理器
        self.error_handler = ErrorHandler(logger)

        # 初始化配置
        self.config = config if isinstance(config, dict) else {}

        # 如果提供了配置文件路径，加载配置
        if isinstance(config, str) and os.path.exists(config):
            self.load_config(config)

        # 初始化资源管理器
        if cache_enabled is not None:
            self.resource_manager = ResourceManager(
                self.path_manager, cache_enabled=cache_enabled
            )
        else:
            self.resource_manager = ResourceManager(self.path_manager)

        # 初始化解压器
        self.extractor = ZipExtractor(self.path_manager)

        # 初始化数据处理器
        self.data_processor = DataProcessor()

        self.maps_processor = SatelliteMapGenerator(self.path_manager)

        # 创建报告数据,用于收集信息
        self.create_report_data()

        logger.info(f"初始化完成，输出目录: {self.output_dir}")

        self.print_info = {}

    def create_report_data(self) -> None:
        """创建报告数据结构"""
        # 创建一个字典，用于收集从config提取的公司信息和资源路径
        company_info = self.config.get("company_info", {})
        self.report_data = {
            "data_root": self.output_dir,
            # 公司基本信息
            "company_info": {
                "name": company_info.get("name", DEFAULT_COMPANY_INFO["name"]),
                "address": company_info.get("address", DEFAULT_COMPANY_INFO["address"]),
                "email": company_info.get("email", DEFAULT_COMPANY_INFO["email"]),
                "phone": company_info.get("phone", DEFAULT_COMPANY_INFO["phone"]),
                "profile": company_info.get("profile", DEFAULT_COMPANY_INFO["profile"]),
                "date": time.strftime("%Y年%m月%d日", time.localtime()),
                "watermark_enabled": company_info.get(
                    "watermark_enabled", DEFAULT_COMPANY_INFO["watermark_enabled"]
                ),
                "watermark_text": company_info.get(
                    "watermark_text", DEFAULT_COMPANY_INFO["watermark_text"]
                ),
                "watermark_size": company_info.get(
                    "watermark_size", DEFAULT_COMPANY_INFO["watermark_size"]
                ),
                "watermark_color": company_info.get(
                    "watermark_color", DEFAULT_COMPANY_INFO["watermark_color"]
                ),
                "watermark_diagonal": company_info.get(
                    "watermark_diagonal", DEFAULT_COMPANY_INFO["watermark_diagonal"]
                ),
                "watermark_use_spire": company_info.get(
                    "watermark_use_spire", DEFAULT_COMPANY_INFO["watermark_use_spire"]
                ),
            },
            # 资源路径，将在下载和处理后更新
            "image_resources": {
                "logo_path": "",
                "wayline_img": "",
                "satellite_img": "",
            },
            # 地理坐标信息
            "geo_info": {
                "north_east": company_info.get("north_east", ""),
                "south_west": company_info.get("south_west", ""),
                "south_east": company_info.get("south_east", ""),
                "north_west": company_info.get("north_west", ""),
            },
            # 污染源信息
            "pollution_source": self.config.get("pollution_source", {}),
        }
        logger.info("已创建报告数据结构")

    @safe_operation(error_msg="加载配置文件失败", default_return=False)
    def load_config(self, config_path: str) -> bool:
        """加载并验证配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            bool: 是否成功加载
        """
        # 使用配置验证器加载和验证配置
        self.config = load_and_validate_config(config_path)

        logger.info(f"成功加载配置文件: {config_path}")

        # 输出配置的关键信息
        self._log_config_info()

        return True

    def _log_config_info(self) -> None:
        """输出配置信息到日志"""
        # 数据根目录
        data_root = self.config.get("data_root", "")
        logger.info(f"数据根目录: {data_root}")

        # 公司信息
        company_info = self.config.get("company_info", {})
        company_name = company_info.get("name", "未指定")
        logger.info(f"公司名称: {company_name}")

        # 资源URL
        logger.info("资源URL:")
        logo_path = company_info.get("logo_path", "")
        logger.info(f"  LOGO: {logo_path[:30]}..." if logo_path else "  LOGO: 未指定")

        wayline_img = company_info.get("wayline_img", "")
        logger.info(
            f"  航线图: {wayline_img[:30]}..." if wayline_img else "  航线图: 未指定"
        )

        satellite_img = company_info.get("satellite_img", "")
        logger.info(
            f"  卫星图: {satellite_img[:30]}..."
            if satellite_img
            else "  卫星图: 未指定"
        )

        measure_data = company_info.get("measure_data", "")
        logger.info(
            f"  测量数据: {measure_data[:30]}..."
            if isinstance(measure_data, str) and measure_data
            else "  测量数据: 未指定"
        )

        # 数据文件
        file_url = company_info.get("file_url", "")
        logger.info(
            f"  数据文件: {file_url[:30]}..." if file_url else "  数据文件: 未指定"
        )

        # 污染源信息
        pollution_source = self.config.get("pollution_source", {})
        logger.info(
            f"污染源信息: {', '.join(pollution_source.keys()) if pollution_source else '未指定'}"
        )

    @safe_operation(error_msg="下载资源失败", default_return=False)
    def download_resources(self) -> bool:
        """下载所有资源文件

        Returns:
            bool: 是否全部下载成功
        """
        logger.info("开始下载资源文件...")

        company_info = self.config.get("company_info", {})
        success = True

        # 资源类型和键的映射
        resource_types = {
            "logo_path": "logo",
            "wayline_img": "wayline",
            "satellite_img": "satellite",
            "measure_data": "measure_data",
            "file_url": "file",
            "kml_boundary_url": "kml",
        }

        # 下载每个资源
        for resource_key, resource_type in resource_types.items():
            url = company_info.get(resource_key)
            if not url:
                continue

            try:
                # 使用资源管理器获取资源
                resource_path = self.resource_manager.get_resource(url, resource_type)

                # 更新配置
                company_info[resource_key] = resource_path
                logger.info(f"{resource_key}资源获取成功: {resource_path}")

                # 更新报告数据中的图像资源路径
                if resource_key in ["logo_path", "wayline_img", "satellite_img"]:
                    self.report_data["image_resources"][resource_key] = resource_path

            except ResourceError as e:
                logger.error(f"获取资源 {resource_key} 失败: {str(e)}")
                success = False

        # 更新配置
        self.config["company_info"] = company_info

        return success

    @safe_operation(error_msg="处理数据失败", default_return=False)
    def process_data(self) -> bool:
        """处理数据文件

        Returns:
            bool: 是否处理成功
        """
        logger.info("开始处理数据...")

        # 获取ZIP文件路径
        zip_path = self.config.get("company_info", {}).get("file_url")
        if not zip_path or not os.path.exists(zip_path):
            raise DataProcessingError("未找到数据文件")

        # 解压文件
        extract_dir = self.extractor.extract(zip_path)
        if not extract_dir:
            raise DataProcessingError("解压文件失败")

        # 查找INDEXS.CSV和POS.TXT文件
        extracted_files = self._find_data_files(extract_dir)
        indices_file = extracted_files["indices_file"]
        pos_file = extracted_files["pos_file"]
        ref_files = extracted_files["ref_file"]

        if not indices_file or not pos_file:
            raise DataProcessingError("未找到INDEXS.CSV或POS.TXT文件")

        # 处理UAV数据
        self._process_uav_data(indices_file, pos_file, ref_files)

        # 处理人工采样数据（如果有）
        self._process_measure_data()

        # 有UAV数据和人工采样数据，则进行匹配分析(如果有)
        self._match_analyze_data()

        # 更新配置
        self.config["data_files"] = extracted_files

        return True

    def _match_analyze_data(self):
        required_keys = ["ref_data", "uav_data", "measure_data"]
        if all(key in self.report_data for key in required_keys):
            merged_data = self.report_data["uav_data"]
            measure_data = self.report_data["measure_data"]
            ref_data = self.report_data["ref_data"]
            try:
                comparison_data, pred_data, model_func, all_pred_data = (
                    self.data_processor.match_and_analyze_data(
                        merged_data, measure_data, ref_data
                    )
                )
            except Exception as e:
                logger.error(f"数据匹配和分析失败: {str(e)}")
                return

            all_pred_data.to_csv(
                self.path_manager.get_file_path("predict", "predict_result.csv")
            )
            logger.info(
                f"模型优化后反演结果已保存至：{self.path_manager.get_file_path('predict', 'predict_result.csv')}"
            )
            self.report_data["comparison_data"] = comparison_data
            self.report_data["pred_data"] = pred_data
            self.report_data["all_pred_data"] = all_pred_data
            self.report_data["model_func"] = model_func

    def _find_data_files(self, extract_dir: str) -> Dict[str, str]:
        """查找解压目录中的数据文件

        Args:
            extract_dir: 解压目录

        Returns:
            Dict[str, str]: 包含文件路径的字典
        """
        result = {
            "indices_file": None,
            "pos_file": None,
            "ref_file": [],
            "extract_dir": extract_dir,
        }

        for root, _, files in os.walk(extract_dir):
            for file_path in files:
                file_path = os.path.join(root, file_path)
                if file_path.upper().endswith("INDEXS.CSV"):
                    result["indices_file"] = file_path
                elif file_path.upper().endswith("POS.TXT"):
                    result["pos_file"] = file_path
                elif "REFL" in file_path.upper():
                    result["ref_file"].append(file_path)

        return result

    def _process_uav_data(
        self, indices_file: str, pos_file: str, ref_files: str
    ) -> None:
        """处理UAV数据

        Args:
            indices_file: 索引文件路径
            pos_file: 位置文件路径
            ref_files: 光谱数据文件路径列表

        Raises:
            DataProcessingError: 数据处理错误
        """
        # 合并数据文件
        merged_data = merge_data_files(indices_file, pos_file)
        if merged_data.empty:
            raise DataProcessingError("数据合并失败")

        # 清洗合并后的反演值数据
        processed_merged_data = self.data_processor.process_data(merged_data)

        if not processed_merged_data:
            raise DataProcessingError("无人机反演数据样本收集失败")
        else:
            # 收集合并后的反演数据
            self.report_data["uav_data"] = processed_merged_data["processed_data"]
            logger.info(
                f"无人机反演数据样本收集完成，样本量：{len(processed_merged_data['processed_data'])}"
            )
            processed_merged_data["processed_data"].to_csv(
                self.path_manager.get_file_path("uav_data", "uav.csv")
            )
            logger.info(
                f"无人机反演结果保存至：{self.path_manager.get_file_path('uav_data', 'uav.csv')}"
            )

        # 收集光谱数据
        if ref_files:
            ref_files.sort(
                key=lambda x: int(os.path.basename(x).split("_")[-1].split(".")[0])
            )
            ref_data = pd.DataFrame()
            for ref_file in ref_files:
                single_ref_data = pd.read_csv(
                    ref_file, encoding="utf-8", header=0, index_col=0
                ).T
                single_ref_data.index = [
                    os.path.basename(ref_file).split("_")[-1].split(".")[0]
                ]
                ref_data = pd.concat([ref_data, single_ref_data], axis=0)

            logger.info(
                f"反射率数据包含 {len(ref_data)} 行和 {len(ref_data.columns)} 列"
            )

        if len(processed_merged_data["processed_data"]) != len(ref_data):
            logger.error(
                f"无人机反演数据样本：{len(processed_merged_data['processed_data'])},光谱样本：{len(ref_data)},不匹配。"
            )
            # 取processed_merged_data["processed_data"]和ref_data索引的交集
            common_index = processed_merged_data["processed_data"].index.intersection(
                ref_data.index
            )
            processed_merged_data["processed_data"] = processed_merged_data[
                "processed_data"
            ].loc[common_index]
            ref_data = ref_data.loc[common_index]
            logger.error(
                f"通过取索引交集的方式对齐反射率数据和反演值数据：{len(common_index)} 条样本！"
            )
        self.report_data["ref_data"] = ref_data
        ref_data.to_csv(self.path_manager.get_file_path("uav_data", "ref_data.csv"))
        logger.info(
            f"无人机光谱数据保存至：{self.path_manager.get_file_path('uav_data', 'ref_data.csv')}"
        )

    def _process_measure_data(self) -> None:
        """处理人工采样数据（如果有）

        Raises:
            DataProcessingError: 数据处理错误
        """
        measure_data_path = self.config.get("company_info", {}).get("measure_data")
        if not measure_data_path or not os.path.exists(measure_data_path):
            logger.info("未找到人工采样数据，跳过处理")
            return

        logger.info(f"开始处理人工采样数据: {measure_data_path}")

        try:
            # 读取人工采样数据
            measure_data = pd.read_csv(
                measure_data_path, encoding="utf-8", header=0, index_col=0
            )

            # 处理人工采样数据
            processed_measure_data = self.data_processor.process_data(measure_data)
            if not processed_measure_data:
                raise DataProcessingError("人工采样数据处理失败")

            # 收集人工采样数据
            self.report_data["measure_data"] = processed_measure_data["processed_data"]
            logger.info("人工采样数据处理完成")

        except Exception as e:
            logger.warning(f"处理人工采样数据时出错: {str(e)}")
            # 人工采样数据处理失败不影响整体流程，继续执行

    @safe_operation(error_msg="生成报告结构失败", default_return=None)
    def generate_config(self) -> Optional[str]:
        """生成报告配置

        Returns:
            str: 报告结构文件路径，失败返回None
        """
        logger.info("开始生成报告结构...")

        # 生成报告结构
        structure_path = create_updated_config(
            updated_data=self.report_data,
            report_structure_file=self.path_manager.get_file_path(
                "reports", "report_structure.json"
            ),
        )

        if not structure_path:
            raise ReportGenerationError("生成报告结构失败")

        logger.info(f"报告结构已生成: {structure_path}")

        # 读取并显示章节信息
        self._log_report_structure(structure_path)

        return structure_path

    def _log_report_structure(self, structure_path: str) -> None:
        """记录报告结构信息

        Args:
            structure_path: 结构文件路径
        """
        try:
            with open(structure_path, "r", encoding="utf-8") as f:
                structure = json.load(f)
                logger.info(f"报告结构包含 {len(structure['chapters'])} 个章节")
                for chapter in structure["chapters"]:
                    logger.info(
                        f"  - 第{chapter.get('chapter_num', '?')}章：{chapter.get('title', '未命名')}"
                    )
        except Exception as e:
            logger.warning(f"读取报告结构时出错: {str(e)}")

    @safe_operation(error_msg="生成报告失败", default_return=False)
    def generate_report(self, config_path: str) -> bool:
        """生成报告

        Args:
            config_path: 配置文件路径（报告结构JSON文件）

        Returns:
            bool: 是否生成成功
        """
        logger.info("开始生成报告...")

        # 读取报告结构
        with open(config_path, "r", encoding="utf-8") as f:
            report_structure = json.load(f)

        # 创建报告生成器
        generator = ReportGenerator(
            output_path=self.path_manager.get_report_path("AeroSpotReport自动报告"),
            report_structure=report_structure,
            update_data=self.report_data,
        )

        # 生成报告
        output_file = generator.generate()

        if not output_file or not os.path.exists(output_file):
            raise ReportGenerationError("报告生成失败，输出文件不存在")

        logger.info(f"报告已生成: {output_file}")

        self.print_info["report"] = os.path.abspath(output_file)
        return True

    @safe_operation(error_msg="保存配置失败", default_return=None)
    def save_processed_config(self) -> Optional[str]:
        """保存处理后的配置

        Returns:
            str: 保存的配置文件路径，失败返回None
        """
        output_path = self.path_manager.get_file_path(
            "reports", "processed_config.json"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

        logger.info(f"处理后的配置已保存到: {output_path}")
        return output_path

    @safe_operation(error_msg="创建指标卫星图失败", default_return=False)
    def generate_indicator_maps(self):
        """
        利用satellite_image和各指标的反演值生成图片
        """
        # 获取边界坐标信息
        geo_info = self.report_data["geo_info"]
        # 获取卫星底图
        satellite_img = self.report_data["image_resources"]["satellite_img"]
        # 获取优化后机载反演值
        pred_data = self.report_data.get("all_pred_data", None)
        uav_data = self.report_data.get("uav_data", None)
        # 获取KML边界文件路径
        kml_boundary_path = self.config.get("company_info", {}).get("kml_boundary_url")
        # 获取可视化模式配置，支持两种位置：根级别或company_info中
        visualization_mode = self.config.get("visualization_mode") or self.config.get(
            "company_info", {}
        ).get("visualization_mode", "quantitative")
        logger.info(f"读取到的可视化模式: {visualization_mode}")
        # 初始化建图参数
        self.maps_processor.init_maps(
            geo_info,
            satellite_img,
            pred_data,
            uav_data,
            kml_boundary_path,
            visualization_mode,
        )
        # 遍历生成每个指标反演结果分布图
        maps_paths = self.maps_processor.generate_indicator_map()
        self.report_data["maps"] = maps_paths

        return True

    @safe_operation(error_msg="保存模型文件到.bin文件失败", default_return=False)
    def save_model_func(self):
        # TODO:加密保存模型系数到.bin
        # 将结果加密并保存到本地
        result = self.report_data.get("model_func", None)
        models_dir = self.path_manager.get_path("models")
        if result:
            try:
                # 使用加密函数
                encrypted_path = encrypt_data_to_file(
                    data_obj=result,
                    password=b"water_quality_analysis_key",
                    salt=b"water_quality_salt",
                    iv=b"fixed_iv_16bytes",
                    output_dir=models_dir,
                    logger=logger,
                )

                if encrypted_path:
                    # 打印output_path的绝对路径
                    self.print_info["bin"] = os.path.abspath(encrypted_path)
            except Exception as e:
                logger.error(f"加密结果时出错: {str(e)}")
        else:
            logger.warning("建模结果为空，没有结果可以加密保存")
        return True


def check_pipe_input() -> bool:
    """检查是否有管道输入"""
    try:
        return not sys.stdin.isatty()
    except Exception:
        # 在某些环境下isatty可能不可用
        import select

        try:
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            return bool(ready)
        except Exception:
            # 如果所有检测方法都失败，则默认为没有管道输入
            return False


def update_output_readme(base_dir: str, timestamp: str, report_path: str) -> None:
    """更新输出目录的README文件，添加本次报告生成记录

    Args:
        base_dir: 基础输出目录
        timestamp: 时间戳
        report_path: 报告文件路径
    """
    readme_path = os.path.join(base_dir, "README.md")

    # 如果README不存在，创建一个新的
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# AeroSpot遥感报告生成记录\n\n")
            f.write("本文件自动记录每次报告生成的时间和位置。\n\n")
            f.write("## 生成历史\n\n")

    # 添加新的记录
    with open(readme_path, "a", encoding="utf-8") as f:
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        relative_path = os.path.relpath(report_path, base_dir)
        f.write(f"- **{report_time}**: 生成报告 `{relative_path}`\n")

    logger.info(f"已更新报告生成记录: {readme_path}")


def main() -> int:
    """主函数

    Returns:
        int: 退出代码
    """
    logger.info("AeroSpot自动化报告生成工具V2启动 (优化版)")

    try:
        # 解析命令行参数
        import argparse

        parser = argparse.ArgumentParser(
            description="AeroSpot自动化报告生成工具V2 (优化版)"
        )
        parser.add_argument("config", nargs="?", help="配置文件路径")
        parser.add_argument("-o", "--output", help="输出目录")
        parser.add_argument(
            "--cache-enabled",
            type=str,
            default="false",
            help="是否启用缓存 (true/false)",
        )
        args = parser.parse_args()

        # 解析缓存设置
        cache_enabled = args.cache_enabled.lower() in ("true", "1", "yes", "on")

        # 确定配置文件路径
        config_path = get_config_path(args)
        if not config_path:
            print("error: 无法获取配置文件路径")
            logger.error("无法获取配置文件路径")
            return 1

        # 加载配置文件
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # 创建输出目录
        output_dir, original_output_dir, timestamp = create_output_directory(
            args, config
        )
        if not output_dir:
            print("error: 无法创建输出目录")
            logger.error("无法创建输出目录")
            return 1

        # 初始化报告生成器
        generator = AeroSpotReportGenerator(
            output_dir, config, cache_enabled=cache_enabled
        )

        # 加载配置
        if not generator.load_config(config_path):
            print("error: 加载配置文件失败")
            logger.error("加载配置文件失败")
            return 1

        # 下载资源
        if not generator.download_resources():
            print("error: 下载资源失败")
            logger.error("下载资源失败，程序终止")
            return 1

        # 处理数据
        if not generator.process_data():
            print("error: 处理数据失败")
            logger.error("处理数据失败")
            return 1

        # 生成各指标卫星图
        if not generator.generate_indicator_maps():
            print("error: 生成指标卫星图失败")
            logger.error("生成指标卫星图失败")
            return 1

        # 保存处理后的配置
        if not generator.save_processed_config():
            print("error: 保存处理后的配置失败")
            logger.error("保存处理后的配置失败")
            return 1

        # 生成报告配置
        structure_path = generator.generate_config()
        if not structure_path:
            print("error: 生成报告配置失败")
            logger.error("生成报告配置失败")
            return 1

        # 生成报告
        if not generator.generate_report(structure_path):
            print("error: 生成报告失败")
            logger.error("生成报告失败")
            return 1

        # 更新README记录
        report_path = os.path.join(output_dir, "AeroSpot遥感报告.docx")
        update_output_readme(original_output_dir, timestamp, report_path)

        logger.info("报告生成完成")

        # 保存模型函数
        if not generator.save_model_func():
            print("保存模型文件到.bin文件失败")
            logger.error("保存模型文件到.bin文件失败")
            return 1

        # 通过print输出print_info
        print(json.dumps(generator.print_info, ensure_ascii=False))
        return 0

    except AeroSpotError as e:
        print(f"error: 报告生成失败 (内部错误): {str(e)}")
        logger.error(f"报告生成失败 (内部错误): {str(e)}")
        return 1
    except Exception as e:
        print(f"error: 报告生成失败 (未捕获异常): {str(e)}")
        logger.error(f"报告生成失败 (未捕获异常): {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


def get_config_path(args) -> Optional[str]:
    """获取配置文件路径

    Args:
        args: 命令行参数

    Returns:
        str: 配置文件路径或None
    """
    # 检查是否有管道输入
    if check_pipe_input():
        # 从标准输入读取内容
        try:
            stdin_content = sys.stdin.read().strip()
            if stdin_content:
                # 尝试将输入作为文件路径
                if os.path.exists(stdin_content):
                    return stdin_content
                else:
                    logger.error("从标准输入读取的文件路径无效")
                    return None
            else:
                logger.error("从标准输入读取的内容为空")
                return None
        except Exception as e:
            logger.error(f"读取标准输入时出错: {str(e)}")
            return None
    else:
        # 使用位置参数的配置文件路径
        if args.config and os.path.exists(args.config):
            return args.config
        # 尝试使用默认配置文件
        else:
            default_config = "test.json"
            if os.path.exists(default_config):
                logger.info(f"使用默认配置文件: {default_config}")
                return default_config
            else:
                logger.error("未提供配置文件路径，也找不到默认配置文件")
                return None


def create_output_directory(args, config) -> Tuple[Optional[str], Optional[str], str]:
    """创建输出目录

    Args:
        args: 命令行参数
        config: 配置字典

    Returns:
        Tuple[Optional[str], Optional[str], str]: (输出目录, 原始输出目录, 时间戳)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 获取配置中的数据根目录
    data_root = config.get("data_root")

    if args.output:
        # 如果命令行指定了输出目录，优先使用
        original_output_dir = args.output
    elif data_root:
        # 如果配置文件中指定了data_root，直接使用
        original_output_dir = data_root
    else:
        logger.error("未指定输出目录，且配置文件中没有data_root")
        return None, None, timestamp

    # 在输出目录下创建时间戳子目录
    output_dir = os.path.join(original_output_dir, f"report_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"创建时间戳输出目录: {output_dir}")

    return output_dir, original_output_dir, timestamp


if __name__ == "__main__":
    sys.exit(main())
