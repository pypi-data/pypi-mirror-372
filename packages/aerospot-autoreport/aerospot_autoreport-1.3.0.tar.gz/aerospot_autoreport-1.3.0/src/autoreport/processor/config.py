"""
配置生成器模块 - 用于生成报告配置文件

此模块负责根据输入数据生成完整的报告配置，包括：
- 公司信息
- 报告结构
- 数据分析章节
- 污染源标记章节
"""

import json
import logging
import os

import pandas as pd

from .data.utils import get_indicator_unit

logger = logging.getLogger(__name__)


def create_updated_config(updated_data, report_structure_file=None):
    """创建更新后的配置文件

    Args:
        source_config: 原始配置（字典或配置文件路径）
        updated_data: 更新的数据
        merged_data: 合并后的数据（可选）
        data_root: 数据根目录（可选）

    Returns:
        str: 更新后的配置文件路径
    """
    logging.info("创建更新后的配置文件")

    company_info = updated_data.get("company_info", {})
    
    # 获取可视化模式配置，支持两种位置：根级别或company_info中
    visualization_mode = (
        updated_data.get("visualization_mode") or 
        company_info.get("visualization_mode", "quantitative")
    )
    image_resources = updated_data.get("image_resources", {})
    DEFAULT_IMAGES_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "resources",
        "images",
    )

    # 构建报告结构
    report_structure = {
        "title": "智能小型机载光谱指数基站AeroSpot分析报告",
        "chapters": [],
    }

    # 添加第一章和第二章（固定结构）
    report_structure["chapters"].extend(
        [
            {
                "chapter_num": 1,
                "title": "智能小型机载光谱指数分析机载AeroSpot简介",
                "sections": [
                    {
                        "name": "系统介绍",
                        "items": [
                            {
                                "type": "text",
                                "content": [
                                    f"{company_info.get('name', '')}积极响应国家政策，根据不同领域的市场需求，推出了智能小型机载光谱指数分析基站AeroSpot,其灵活性、低成本、便于部署等特点，在许多应用场景中展现出显著优势。",
                                    '目前多数行业无人机应用采用手动或半自动作业模式，作业过程需要人员介入，人力要求较高，操作门槛也较高，基于上述应用痛点，AeroSpot在生态环境监测中极具优势，综合利用无人机与光谱科技，通过无人机机场，可轻松实现非现场无人化生态监测，解决实际场景应用难题，提高生态管理效率，为打造"低空+治理"增添助力。',
                                    f'{company_info.get("name", "")}智能小型机载光谱指数分析基站AeroSpot通过获取高精度的点光谱数据，采用"以点带面"的方式，能够实现对全湖或重点区域的全局可视化监测。这种技术不仅弥补了卫星遥感因天气条件、时空分辨率限制而无法按需获取整湖或重点区域水质可视化数据的缺陷，还可以解决无人机高光谱成像技术在大面积水域拼接中的技术难题。',
                                ],
                            }
                        ],
                    },
                    {
                        "name": "设备展示",
                        "items": [
                            {
                                "type": "text",
                                "content": "机载光谱指数分析仪 AeroSpot实体图如下所示。",
                            },
                            {
                                "type": "image",
                                "path": os.path.join(DEFAULT_IMAGES_DIR, "uav.png"),
                                "caption": "机载光谱指数分析仪 AeroSpot实体图",
                            },
                            {
                                "type": "image",
                                "path": os.path.join(DEFAULT_IMAGES_DIR, "airport.png"),
                                "caption": "智能小型机载光谱指数分析基站AeroSpot实体图",
                            },
                        ],
                    },
                    {
                        "name": "技术参数",
                        "items": [
                            {
                                "type": "text",
                                "content": "智能小型机载光谱指数分析基站 AeroSpot 参数如下表所示。",
                            },
                            {
                                "type": "table",
                                "name": "智能小型机载光谱指数分析基站 AeroSpot 参数",
                                "data": [
                                    ["智能小型机载光谱指数分析基站AeroSpot参数", ""],
                                    [
                                        "尺寸",
                                        "舱盖开启：长 1228 mm，宽 583 mm，高 412 mm\n舱盖闭合：长 570 mm，宽 583 mm，高 465 mm",
                                    ],
                                    ["整机重量", "34kg（不包含飞行器）"],
                                    ["输入电压", "100V 至 240V（交流电）, 50/60 Hz"],
                                    ["工作环境温度", "−25℃ 至 45℃"],
                                    ["无人机参数", ""],
                                    ["裸机重量", "1410 克"],
                                    ["最大起飞重量", "1610 克"],
                                    [
                                        "尺寸",
                                        "长 335 mm，宽 398 mm，高 153 mm（不含桨叶）",
                                    ],
                                    [
                                        "广角相机",
                                        "不低于1/1.32英寸CMOS，有效像素不低于2000万",
                                    ],
                                    ["长焦相机", "1/2英寸CMOS，有效像素1200 万"],
                                    ["小型机载单点光谱指数分析仪 AeroSpot", ""],
                                    ["光谱范围", "400 nm - 900 nm"],
                                    ["光谱采样间隔", "1 nm"],
                                    ["视场角", "≤3°"],
                                    ["探测器类型", "CMOS线阵探测器"],
                                    ["重量", "≤200g"],
                                    ["适配无人机", "大疆 M3D、M4D 等"],
                                    ["适配无人机场", "大疆机场2，大疆机场3"],
                                    [
                                        "可实时反演指数",
                                        "水环境方向：叶绿素a、浊度、悬浮物、化学需氧量、总磷、氨氮、色度、蓝绿藻等级等\n农林方向：NDVI、EVI、SIPI、PSRI、mLICI、物候指数、叶锈病程度指数、叶面积指数等多种植被指数和农学参数",
                                    ],
                                ],
                                "merge_cells": [
                                    {
                                        "row": 0,
                                        "col": 0,
                                        "row_span": 1,
                                        "col_span": 2,
                                        "bold": True,
                                    },
                                    {
                                        "row": 5,
                                        "col": 0,
                                        "row_span": 1,
                                        "col_span": 2,
                                        "bold": True,
                                    },
                                    {
                                        "row": 11,
                                        "col": 0,
                                        "row_span": 1,
                                        "col_span": 2,
                                        "bold": True,
                                    },
                                ],
                                "column_widths": ["33%", "67%"],
                            },
                        ],
                    },
                ],
            },
            {
                "chapter_num": 2,
                "title": "飞行区域介绍",
                "sections": [
                    {
                        "name": "飞行区域资料介绍",
                        "items": [{"type": "text", "content": "（用户手动添加）"}],
                    },
                    {
                        "name": "智能小型机载光谱指数分析基站AeroSpot现场采集照片",
                        "items": [
                            {
                                "type": "image",
                                "path": "",
                                "caption": "智能小型机载光谱指数分析基站AeroSpot现场采集照片",
                            }
                        ],
                    },
                    {
                        "name": "水样采集现场照片",
                        "items": [
                            {"type": "image", "path": "", "caption": "水样采集现场照片"}
                        ],
                    },
                    {
                        "name": "智能小型机载光谱指数分析基站AeroSpot航点规划图",
                        "items": [
                            {
                                "type": "image",
                                "path": f"{image_resources['wayline_img']}",
                                "caption": "智能小型机载光谱指数分析基站AeroSpot航点规划图",
                            }
                        ],
                    },
                ],
            },
        ]
    )

    logging.info("已添加基础章节（第1-2章）")

    measure_data = updated_data.get("measure_data", pd.DataFrame())
    pred_data = updated_data.get(
        "pred_data", updated_data.get("uav_data")
    )  # 无实测值情况下无反演值，则用无人机数据代替
    comparison_data = updated_data.get("comparison_data", {})
    maps = updated_data.get("maps", {})
    pollution_source = updated_data.get("pollution_source", {})

    # 添加第三章（如果存在测量数据）
    if isinstance(measure_data, pd.DataFrame) and not measure_data.empty:
        # 从测量数据中提取指标列表（除去经纬度列）
        indicators = [
            col
            for col in measure_data.columns
            if col not in ["index", "latitude", "longitude"]
        ]
        logging.info(f"从测量数据中提取的指标列表: {indicators}")

        # 创建第三章：数据分析
        data_analysis_chapter = {
            "chapter_num": 3,
            "title": "数据分析",
            "sections": [
                {
                    "name": "实测数据",
                    "items": [
                        {
                            "type": "text",
                            "content": "地面采样点的经纬度坐标及各项指标如下表所示",
                        },
                        {
                            "type": "table",
                            "name": "地面采样点的经纬度坐标及各项指标",
                            "headers": ["编号"]
                            + [
                                indicator
                                if indicator in ["longitude", "latitude"]
                                else f"{indicator}\n({get_indicator_unit(indicator)})"
                                for indicator in measure_data.columns.tolist()
                            ],
                            "data": [
                                [str(i + 1)] + row.tolist()
                                for i, row in enumerate(measure_data.values)
                            ],
                        },
                    ],
                },
                {
                    "name": "实测值与反演值对比分析",
                    "items": [
                        {
                            "type": "text",
                            "content": "根据采样点的经纬度位置绘制在卫星影像的底图上，其空间分布图如下。",
                        },
                        {
                            "type": "image",
                            "path": maps.get("distribution_map", ""),
                            "caption": "采样点分布图",
                        },
                        {
                            "type": "text",
                            "content": "绝对误差=反演值-真实值（即反演值与真实值之差）；相对误差=（反演值-真实值）/真实值（即绝对误差所占真实值的百分比）。相对误差指的是反演所造成的绝对误差与真实值之比乘以100%所得的数值，以百分数表示。一般来说，相对误差更能反映反演结果的可信程度。根据《光谱法水质在线监测系统技术导则》和《光谱法水质在线快速监测系统》等行业标准和团体标准，光谱法用于水质检测，其相对误差小于30%则认为有效。",
                        },
                    ],
                },
            ],
        }

        # 获取数据分析章节的items列表
        analysis_items = data_analysis_chapter["sections"][1]["items"]

        # 为每个检测到的指标创建subsection
        for indicator in indicators:
            try:
                # 准备表格数据
                table_data = []

                # 如果有比较数据，优先使用比较数据
                if comparison_data and "matches" in comparison_data:
                    for idx, match in enumerate(comparison_data["matches"]):
                        if indicator in match["indicators"]:
                            ind_data = match["indicators"][indicator]
                            # 添加行数据
                            table_data.append(
                                [
                                    str(idx + 1),  # 编号
                                    str(round(ind_data["measure_value"], 3)),  # 实测值
                                    str(round(ind_data["pred_value"], 3)),  # 反演值
                                    str(round(ind_data["pred_diff"], 3)),  # 绝对误差
                                    str(
                                        round(ind_data["pred_rel_diff"], 3)
                                    ),  # 相对误差
                                ]
                            )

                subsection = {
                    "type": "subsection",
                    "name": indicator,
                    "items": [
                        {
                            "type": "table",
                            "name": f"{indicator}误差分析",
                            "headers": [
                                "编号",
                                f"实测值\n({get_indicator_unit(indicator)})",
                                f"反演值({get_indicator_unit(indicator)})",
                                f"绝对误差({get_indicator_unit(indicator)})",
                                "相对误差(%)",
                            ],
                            "data": table_data,
                        }
                    ],
                }
                analysis_items.append(subsection)
                logging.info(f"已添加 {indicator} 的误差分析表")
            except Exception as e:
                logging.error(f"生成{indicator}误差分析表时出错: {str(e)}")
                continue

        report_structure["chapters"].append(data_analysis_chapter)
        logging.info("已添加第3章：数据分析")
    else:
        logging.warning("未找到测量数据，跳过第3章生成")

    # 添加第4章：水质分布
    if pred_data is not None and not pred_data.empty:
        # ================== 国标分级映射表（GB 3838-2002） ==================
        INDICATOR_GRADE_CONFIG = {
            # COD（化学需氧量，mg/L）
            "cod": {
                "thresholds": [15, 15, 20, 30, 40],
                "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
                "colors": [
                    "#1E90FF",
                    "#00FF7F",
                    "#FFFF00",
                    "#FFA500",
                    "#FF0000",
                    "#8B0000",
                ],
            },
            # 氨氮 NH3-N（mg/L）
            "nh3n": {
                "thresholds": [0.15, 0.5, 1.0, 1.5, 2.0],
                "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
                "colors": [
                    "#1E90FF",
                    "#00FF7F",
                    "#FFFF00",
                    "#FFA500",
                    "#FF0000",
                    "#8B0000",
                ],
            },
            # 总磷 TP（mg/L）
            "tp": {
                "thresholds": [0.02, 0.1, 0.2, 0.3, 0.4],
                "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
                "colors": [
                    "#1E90FF",
                    "#00FF7F",
                    "#FFFF00",
                    "#FFA500",
                    "#FF0000",
                    "#8B0000",
                ],
            },
            # 总氮 TN（mg/L）
            "tn": {
                "thresholds": [0.2, 0.5, 1.0, 1.5, 2.0],
                "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
                "colors": [
                    "#1E90FF",
                    "#00FF7F",
                    "#FFFF00",
                    "#FFA500",
                    "#FF0000",
                    "#8B0000",
                ],
            },
            # 溶解氧 DO（mg/L，越高越好，分级反向）
            "do": {
                "thresholds": [2, 3, 5, 6, 7.5],  # 劣五类, Ⅴ类, Ⅳ类, Ⅲ类, Ⅱ类, Ⅰ类
                "labels": ["劣五类", "Ⅴ类", "Ⅳ类", "Ⅲ类", "Ⅱ类", "Ⅰ类"],
                "colors": [
                    "#8B0000",
                    "#FF0000",
                    "#FFA500",
                    "#FFFF00",
                    "#00FF7F",
                    "#1E90FF",
                ],
                "reverse": True,
            },
            # 高锰酸盐指数 CODMn（mg/L）
            "codmn": {
                "thresholds": [2, 4, 6, 10, 15],
                "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
                "colors": [
                    "#1E90FF",
                    "#00FF7F",
                    "#FFFF00",
                    "#FFA500",
                    "#FF0000",
                    "#8B0000",
                ],
            },
            # 五日生化需氧量 BOD5（mg/L）
            "bod5": {
                "thresholds": [3, 3, 4, 6, 10],
                "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
                "colors": [
                    "#1E90FF",
                    "#00FF7F",
                    "#FFFF00",
                    "#FFA500",
                    "#FF0000",
                    "#8B0000",
                ],
            },
        }

        def get_water_quality_grade(indicator, values):
            """根据指标值统计各等级数量判断主要水质等级

            Args:
                indicator: 指标名称
                values: 指标值列表

            Returns:
                str: 水质等级描述
            """
            if not values or indicator not in INDICATOR_GRADE_CONFIG:
                return "无法确定"

            config = INDICATOR_GRADE_CONFIG[indicator]
            thresholds = config["thresholds"]
            labels = config["labels"]
            is_reverse = config.get("reverse", False)

            # 统计各等级的数量
            grade_counts = {label: 0 for label in labels}
            total_values = len(values)

            for value in values:
                # 根据阈值判断每个值的等级
                if is_reverse:
                    # 溶解氧等指标，值越高等级越好
                    grade = labels[-1]  # 默认最好等级
                    for i, threshold in enumerate(thresholds):
                        if value <= threshold:
                            grade = labels[i]
                            break
                else:
                    # 一般指标，值越低等级越好
                    grade = labels[-1]  # 默认最差等级（劣五类）
                    for i, threshold in enumerate(thresholds):
                        if value <= threshold:
                            grade = labels[i]
                            break

                grade_counts[grade] += 1

            # 过滤掉占比低于30%的等级（排除噪点）
            min_threshold = max(1, int(total_values * 0.3))  # 至少1个，或者30%
            significant_grades = {
                grade: count
                for grade, count in grade_counts.items()
                if count >= min_threshold
            }

            if not significant_grades:
                # 如果所有等级都低于10%，选择数量最多的
                max_grade = max(grade_counts.items(), key=lambda x: x[1])
                return f"{max_grade[0]}"

            # 按数量排序，获取主要等级
            sorted_grades = sorted(
                significant_grades.items(), key=lambda x: x[1], reverse=True
            )

            if len(sorted_grades) == 1:
                # 只有一个主要等级
                grade, count = sorted_grades[0]
                return f"{grade}"
            elif len(sorted_grades) == 2:
                # 两个主要等级
                grade1, count1 = sorted_grades[0]
                grade2, count2 = sorted_grades[1]
                return f"{grade1}和{grade2}"
            else:
                # 三个或更多主要等级
                main_grades = [grade for grade, count in sorted_grades[:3]]
                return f"{', '.join(main_grades[:-1])}和{main_grades[-1]}"

        # 添加指标描述映射
        INDICATOR_DESCRIPTIONS = {
            "nh3n": "氨氮（NH₃-N）指水中以游离氨（NH₃）和铵离子（NH₄⁺）形式存在的氮。氨氮是水体中的营养素，可导致水体富营养化现象产生，是水体中的主要耗氧污染物，对鱼类及某些水生生物有毒害。",
            "tp": "总磷（Total phosphorus，TP），指水样经消解后将各种形态的磷转变成正磷酸盐后测定的结果，以每升水样含磷毫克数计量。水中磷可以以元素磷、正磷酸盐、缩合磷酸盐、焦磷酸盐、偏磷酸盐和有机团结合的磷酸盐等形式存在。其主要来源为生活污水、化肥、有机磷农药及近代洗涤剂所用的磷酸盐增洁剂等。水体中的磷是藻类生长需要的一种关键元素，过量磷是造成水体污秽异臭，使湖泊发生富营养化和海湾出现赤潮的主要原因。",
            "tn": "总氮（Total Nitrogen，TN），指水中各种形态的氮的总量，包括NO3-、NO2-和NH4+等无机氮和蛋白质、氨基酸和有机胺等有机氮，以每升水含氮毫克数计算。总氮作为是衡量水质的重要指标之一，其测定有助于评价水体被污染和自净状况。地表水中氮、磷物质超标时，微生物大量繁殖，浮游生物生长旺盛，水体出现富营养化状态。",
            "cod": "化学需氧量（Chemical Oxygen Demand，COD），指在一定的条件下，采用一定的强氧化剂处理水样时，所消耗的氧化剂量。它是表示水中还原性物质多少的一个指标。水中的还原性物质有各种有机物、亚硝酸盐、硫化物、亚铁盐等，但主要的是有机物。因此，化学需氧量（COD）又往往作为衡量水中有机物质含量多少的指标。化学需氧量越大，说明水体受有机物的污染越严重。",
            "codmn": "高锰酸钾指数（CODMn）指在酸性或碱性介质中，以高锰酸钾为氧化剂，处理水样时所消耗的氧量，以氧的mg/L来表示。 高锰酸钾指数可反映出水体中有机及无机可氧化物质的污染程度。水中高锰酸钾指数浓度增加，说明水中有机物含量增加，提示可能存在更大的微生物危险和化学危险。",
            "bod": "五日生化需氧量（Biochemical oxygen demand，BOD5），指在一定条件下，微生物分解存在于水中的可生化降解有机物所进行的生物化学反应过程中所消耗的溶解氧的数量。以毫克/升或百分率、ppm表示。它是反映水中有机污染物含量的一个综合指标。如果进行生物氧化的时间为五天就称为五日生化需氧量（BOD5）。生化需氧量是重要的水质污染参数。废水、废水处理厂出水和受污染的水中,微生物利用有机物生长繁殖时需要的氧量，是可降解（可以为微生物利用的）有机物的氧当量。",
            "chla": "叶绿素a（Chla）指植物光合作用中的重要光合色素。通过测定浮游植物叶绿素，可掌握水体的初级生产情况，在环境监测中，可将叶绿素a含量作为湖泊富营养化指标之一。",
            "ss": "悬浮物（suspended solids），简称为SS。指悬浮在水中的固体物质，包括不溶于水中的无机物、有机物及泥砂、黏土、微生物等。水中悬浮物含量是衡量水污染程度的指标之一。悬浮物是造成水浑浊的主要原因。水体中的有机悬浮物沉积后易厌氧发酵，使水质恶化。",
            "turbidity": '浊度（turbidity），是指溶液对光线通过时所产生的阻碍程度，它包括悬浮物对光的散射和溶质分子对光的吸收。水的浊度不仅与水中悬浮物质的含量有关，而且与它们的大小、形状及折射系数等有关。浑浊度的单位是用"度"来表示的。浑浊度是水体物理性状指标之一。它表征水中悬浮物质等阻碍光线透过的程度。 一般来说，水中的不溶解物质越多，浑浊度也越高。浑浊度是由于水中存在颗粒物质如黏土、污泥、胶体颗粒、浮游生物及其他微生物而形成，用以表示水的清澈或浑浊程度，是衡量水质良好程度的重要指标之一。',
            "do": "溶解氧（dissolved oxygen，DO）,指溶解在水中的空气中的分子态氧，以每升水里氧气的毫克数表示。水中溶解氧的量与其和大气接触面的大小有关，接触面越大含溶解氧愈多，又随水温升高而减少，随氧分压升高而增加。在正常状态下，地面水中溶解氧应接近饱和状态，溶解氧的含量能够反映出水体的污染程度，是用于衡最水体污染的一个重要指标。越是干净的水，所含溶解氧就越多，而污染越厉害，水中的溶解氧就越少。水中生物所需的氧气全靠溶解氧来供应，有机物的分解和氧化还原反应等都需溶解氧，所以溶解氧是水体实现自净的重要条件。",
            "bga": "蓝绿藻（BGA）是一种原核生物，在富营养化水体中大量繁殖形成水华。蓝绿藻含量是评价水体富营养化程度和生态健康状况的重要指标。",
        }

        water_quality_chapter = {
            "chapter_num": 4,
            "title": "水质参数反演结果",
            "content": "根据云端内置的水质AI大模型对选定的水体参数进行反演，并依据《地表水环境质量标准》（GB 3838-2002）对水质进行划分。",
            "sections": [],
        }
        # 为每个指标创建section
        indicators = [
            col
            for col in pred_data.columns
            if col not in ["index", "latitude", "longitude"]
        ]
        for indicator in indicators:
            # 获取该指标的所有反演值
            values = []
            min_val = 0
            max_val = 0

            if isinstance(pred_data, pd.DataFrame) and indicator in pred_data.columns:
                # 安全地获取数值并过滤无效值
                values = pred_data[indicator].dropna().tolist()
                if values:  # 确保有有效值
                    valid_values = [
                        float(v)
                        for v in values
                        if str(v).strip() and str(v).lower() != "nan"
                    ]
                    if valid_values:
                        min_val = min(valid_values)
                        max_val = max(valid_values)

            # 获取指标对应的图片路径
            indicator_maps_dict = maps.get(indicator, {})
            
            # 判断是否为定量模式：有实测数据或配置为定量模式
            is_quantitative_mode = not measure_data.empty or visualization_mode == "quantitative"

            section = {
                "name": indicator,
                "items": [
                    {
                        "type": "text",
                        "content": INDICATOR_DESCRIPTIONS.get(
                            indicator,
                            f"{indicator}是水质监测的重要指标之一，其含量变化反映了水体的污染状况。",
                        ),
                    },
                    {
                        "type": "image",
                        "path": indicator_maps_dict.get("distribution", ""),
                        "caption": f"AeroSpot航点水质指标{indicator}分布图",
                    },
                    {
                        "type": "image",
                        "path": indicator_maps_dict.get("interpolation", ""),
                        "caption": f"AeroSpot以点带面反演{indicator}水质指标",
                    },
                    {
                        "type": "image",
                        "path": indicator_maps_dict.get("level", "skip"),
                        "caption": f"AeroSpot分析{indicator}水质等级分布",
                    },
                    {
                        "type": "text",
                        "content": (
                            # 定量模式且有有效数据时显示完整描述
                            f"从反演结果可知，区域内{indicator}的数值分布范围为 {min_val:.3f} ~ {max_val:.3f} mg/L，空间分布差异显著。" +
                            (f"根据《GB 3838-2002地表水环境质量标准》可知，整体水质为{get_water_quality_grade(indicator, valid_values)}。"
                             if indicator in INDICATOR_GRADE_CONFIG else "")
                            if is_quantitative_mode and valid_values else ""
                        ),
                    },
                ],
            }
            water_quality_chapter["sections"].append(section)
            logging.info(f"已添加 {indicator} 的水质分析")

        report_structure["chapters"].append(water_quality_chapter)
        logging.info(
            f"已添加第4章：水质参数反演结果，包含 {len(water_quality_chapter['sections'])} 个指标分析"
        )

    else:
        logging.warning("未找到合并数据，跳过第4章生成")

    # 添加第5章：疑似污染源标记
    if pollution_source:
        pollution_source_chapter = {
            "chapter_num": 5,
            "title": "疑似污染源标记",
            "content": [
                "在高光谱水质监测中，根据机载高光谱相机采集数据和相应水质指标反演结果，标识出一些疑似污染源点位。这些点位可能是与水质异常相关的区域，提示可能存在的污染物质，并识别可能的污染来源。这些点位可能受到多种因素影响，包括但不限于：",
                "- 工业排放：附近工业活动可能导致废水排放，其中可能含有化学物质或颗粒物，对水体产生负面影响。",
                "- 农业活动：农业用地周边可能存在农药、化肥等农业排放物的输入，对水质产生一定的压力。",
                "- 城市污水排放：城市污水系统的排放口可能导致有机物、氮、磷等物质输入水体，影响水体的营养状态。",
                "- 土壤侵蚀：陡峭坡地、裸露土地等可能引发土壤侵蚀，将泥沙等颗粒物质输送到水体中。",
                "高光谱技术能够在数据中识别出异常的光谱反演特征，这些特征往往与化学需氧量、总氮、总磷、氨氮、高锰酸盐指数等水质指标相关。因此，疑似污染源点位的标定有助于进一步的现场调查和采样分析，以验证是否存在污染物质，并识别可能的污染来源。",
                "为了维护水体生态平衡和保护水资源，下一步的工作将包括深入的现场研究，针对这些疑似污染源点位进行详细的水质监测和污染因素溯源，为环保决策提供科学依据。",
            ],
            "sections": [],
        }

        # 为每个检测到的污染源指标创建section
        for indicator, source_points in pollution_source.items():
            if source_points:  # 只有当有污染源点位时才添加该指标的section
                section = {
                    "name": indicator,
                    "items": [
                        {
                            "type": "text",
                            "content": f"该指标共检测出{len(source_points)}处疑似污染源，其点位坐标及高清图像如下。",
                        },
                        {
                            "type": "table",
                            "name": f"{indicator}疑似污染源信息",
                            "headers": ["序号", "经度", "纬度"],
                            "data": source_points,
                        },
                    ],
                }
                pollution_source_chapter["sections"].append(section)

        # 只有当有sections时才添加这一章
        if pollution_source_chapter["sections"]:
            report_structure["chapters"].append(pollution_source_chapter)
        logging.info("已添加第5章：疑似污染源标记")
    else:
        logging.warning("缺少污染源数据，跳过第5章生成")

    # 保存报告结构到JSON文件
    try:
        with open(report_structure_file, "w", encoding="utf-8") as f:
            json.dump(report_structure, f, ensure_ascii=False, indent=2)
        logging.info(f"报告结构已保存到: {report_structure_file}")
    except Exception as e:
        logging.error(f"保存报告结构时出错: {str(e)}")

    # 保存更新后的数据到同路径下
    try:
        updated_data_file = os.path.join(
            os.path.dirname(report_structure_file), "updated_data.json"
        )

        def convert_df_to_length(obj):
            if isinstance(obj, pd.DataFrame):
                return len(obj)
            elif isinstance(obj, dict):
                return {k: convert_df_to_length(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_df_to_length(i) for i in obj]
            else:
                return obj

        serializable_data = convert_df_to_length(updated_data)
        with open(updated_data_file, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)

        logging.info(f"更新后的数据已保存到: {updated_data_file}")
    except Exception as e:
        logging.error(f"保存更新后的数据时出错: {str(e)}")

    return report_structure_file
