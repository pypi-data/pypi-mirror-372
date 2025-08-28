"""
卫星图像生成模块
提供基于卫星图像和指标数据生成可视化地图的功能

新功能特性：
1. 增强插值算法：集成Alpha Shape边界检测，支持复杂水域形状
2. 纯净版热力图：支持透明背景SVG格式输出
   - SVG格式：矢量图形，可无限缩放，文件更小，适合报告嵌入
3. 国标分级：自动应用GB 3838-2002水质标准分级
4. 智能边界：三种边界检测算法（Alpha Shape、凸包回退、KML边界）

输出文件类型：
- distribution: 散点分布图
- interpolation: 带装饰的插值热力图（卫星底图+坐标轴+标题）
- clean_interpolation_svg: 纯净版插值热力图（透明背景SVG，无装饰元素）
- level: 国标等级分布图（仅支持国标指标）

使用示例：
# 生成透明背景SVG版本
generate_clean_interpolation_map(data, 'cod', 'output.svg', transparent_bg=True, output_format='svg')

# 使用预计算插值数据
result = generate_clean_interpolation_map(data, 'cod', 'output.svg', precomputed_interpolation=cached_data)
"""

import logging
import os
from datetime import datetime
from typing import List, Optional

import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap, Normalize
from matplotlib.path import Path
from PIL import Image
from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging
from scipy.interpolate import RBFInterpolator, griddata
from scipy.ndimage import gaussian_filter
from scipy.spatial import ConvexHull, Delaunay

plt.rcParams.update({"font.size": 48})
plt.rcParams["font.family"] = "SimHei"  # 替换为你选择的字体
plt.rcParams["axes.unicode_minus"] = False

# ================== 克里金插值配置 ==================

# 全局插值方法设置 - 修改此处可切换不同克里金方法进行对比测试
# 可选值: 'auto', 'universal_kriging', 'ordinary_kriging_spherical', 'ordinary_kriging_exponential'
GLOBAL_KRIGING_METHOD = "ordinary_kriging_spherical"  # 🎯 当前使用：普通克里金球形模型

KRIGING_CONFIG = {
    "universal_kriging": {
        "variogram_model": "gaussian",  # 高斯模型：平滑过渡，无明确影响范围
        "drift_terms": ["regional_linear"],  # 区域线性趋势建模
        "description": "泛克里金-高斯模型（适合连续环境数据，支持趋势建模）",
        "enforce_positive": True,  # 强制插值结果为正数
        "transform_method": "log",  # 负数处理方法: 'log', 'clip', 'none'
    },
    "ordinary_kriging_spherical": {
        "variogram_model": "spherical",  # 球形模型：有明确影响范围和渐变特性
        "n_closest_points": 12,  # 搜索最近12个点（ArcGIS默认）
        "search_radius_factor": 0.3,  # 搜索半径为数据范围的30%
        "description": "普通克里金-球形模型（类似ArcGIS，有明确空间影响范围）",
        "enforce_positive": True,  # 强制插值结果为正数
        "transform_method": "clip",  # 负数处理方法: 直接截断
    },
    "ordinary_kriging_exponential": {
        "variogram_model": "exponential",  # 指数模型：快速衰减，适合局部变化
        "n_closest_points": 8,  # 搜索最近8个点
        "search_radius_factor": 0.25,  # 搜索半径为数据范围的25%
        "description": "普通克里金-指数模型（适合快速变化数据，局部影响强）",
        "enforce_positive": True,  # 强制插值结果为正数
        "transform_method": "clip",  # 负数处理方法: 直接截断
    },
}

# 变差函数模型特点说明:
# - Gaussian: 平滑过渡，无明确影响范围，适合连续渐变的环境数据
# - Spherical: 有明确影响范围，在范围内线性增长后趋于稳定，最常用
# - Exponential: 快速衰减，适合有强烈局部变化的数据
#
# 搜索策略说明:
# - n_closest_points: 每个插值点使用的最近邻点数（类似ArcGIS中的"最小点数"）
# - search_radius_factor: 搜索半径相对于数据分布范围的比例
#
# 负数处理方法说明:
# - 'log': 对数变换（适合环境数据，保持相对变化），要求所有数据>0
# - 'clip': 直接截断负值为0（简单有效，但可能影响数据分布）
# - 'none': 不处理负数（保持原始插值结果）


def transform_data_for_kriging(values, method="log"):
    """
    为克里金插值预处理数据，处理负数或零值

    Args:
        values: 原始数据值
        method: 变换方法 ('log', 'clip', 'none')

    Returns:
        transformed_values: 变换后的数据
        transform_params: 变换参数（用于逆变换）
    """
    values = np.array(values)

    if method == "log":
        # 对数变换，适合环境数据（如水质指标）
        min_val = np.min(values)
        if min_val <= 0:
            # 如果有负数或零值，添加偏移量使所有值为正
            offset = abs(min_val) + 1e-6
            logger.info(f"检测到负数或零值，添加偏移量: {offset:.6f}")
        else:
            offset = 0

        transformed_values = np.log(values + offset)
        transform_params = {"method": "log", "offset": offset}

    elif method == "clip":
        # 简单截断，不进行数据变换
        transformed_values = values.copy()
        transform_params = {"method": "clip"}

    else:  # method == 'none'
        # 不处理
        transformed_values = values.copy()
        transform_params = {"method": "none"}

    return transformed_values, transform_params


def inverse_transform_data(values, transform_params):
    """
    对插值结果进行逆变换

    Args:
        values: 插值结果
        transform_params: 变换参数

    Returns:
        original_scale_values: 逆变换后的数据
    """
    method = transform_params["method"]

    if method == "log":
        # 指数逆变换
        offset = transform_params["offset"]
        result = np.exp(values) - offset
        # 确保结果为正数
        result = np.maximum(result, 1e-10)
        return result

    elif method == "clip":
        # 截断负值
        return np.maximum(values, 0)

    else:  # method == 'none'
        return values


logger = logging.getLogger(__name__)


def calculate_dynamic_layout(
    img_width,
    img_height,
    has_right_element=False,
    font_size=48,
    right_element_type="colorbar",
):
    """
    根据图像尺寸动态计算布局参数（隐藏坐标轴后的简化版本）

    Args:
        img_width: 图像宽度（像素）
        img_height: 图像高度（像素）
        has_right_element: 是否有右侧元素（图例或colorbar，影响右侧空间需求）
        font_size: 字体大小（影响所需边距）
        right_element_type: 右侧元素类型，'colorbar' 或 'legend'

    Returns:
        tuple: (left, bottom, width, height, layout_info) 布局参数和配置信息
    """
    aspect_ratio = img_height / img_width

    # 布局配置信息（简化版，因为隐藏了坐标轴）
    layout_info = {"hide_axis": True}

    # 根据长宽比调整布局 - 确保标题和右侧元素不超出范围，有右侧元素时保持对称留白
    if has_right_element:
        # 根据右侧元素类型确定空间分配
        if right_element_type == "colorbar":
            # colorbar占用空间较小，减少右侧预留空间
            colorbar_space_factor = 0.5  # 减少50%的右侧空间
        else:  # legend
            # legend占用空间较大，保持原有空间
            colorbar_space_factor = 1.0

        # 有右侧元素时，确保左右留白对称
        if aspect_ratio > 2.0:  # 极窄长图像
            left = 0.03
            right_margin = 0.03  # 右侧留白与左侧相同
            right_element_width = (
                0.15 * colorbar_space_factor
            )  # 右侧元素（图例/colorbar）占用宽度
            width = 1.0 - left - right_margin - right_element_width
            bottom = 0.05
            height = 0.82
        elif aspect_ratio > 1.5:  # 窄长图像
            left = 0.03
            right_margin = 0.03
            right_element_width = 0.12 * colorbar_space_factor
            width = 1.0 - left - right_margin - right_element_width
            bottom = 0.06
            height = 0.84
        elif aspect_ratio < 0.5:  # 极宽扁图像
            left = 0.04
            right_margin = 0.04
            right_element_width = 0.10 * colorbar_space_factor
            width = 1.0 - left - right_margin - right_element_width
            bottom = 0.10
            height = 0.75
        elif aspect_ratio < 0.7:  # 宽扁图像
            left = 0.04
            right_margin = 0.04
            right_element_width = 0.10 * colorbar_space_factor
            width = 1.0 - left - right_margin - right_element_width
            bottom = 0.08
            height = 0.80
        else:  # 接近正方形
            left = 0.04
            right_margin = 0.04
            right_element_width = 0.10 * colorbar_space_factor
            width = 1.0 - left - right_margin - right_element_width
            bottom = 0.08
            height = 0.82
    else:
        # 无右侧元素时的布局
        if aspect_ratio > 2.0:  # 极窄长图像
            left = 0.02
            bottom = 0.05
            width = 0.96
            height = 0.82
        elif aspect_ratio > 1.5:  # 窄长图像
            left = 0.02
            bottom = 0.06
            width = 0.96
            height = 0.84
        elif aspect_ratio < 0.5:  # 极宽扁图像
            left = 0.03
            bottom = 0.10
            width = 0.94
            height = 0.75
        elif aspect_ratio < 0.7:  # 宽扁图像
            left = 0.03
            bottom = 0.08
            width = 0.94
            height = 0.80
        else:  # 接近正方形
            left = 0.03
            bottom = 0.08
            width = 0.94
            height = 0.82

    # 确保布局参数在合理范围内
    left = max(left, 0.01)
    bottom = max(bottom, 0.04)
    width = max(width, 0.50)
    height = max(height, 0.60)

    # 确保总布局不会超出边界（为标题和图例预留空间）
    if left + width > 0.95:
        width = 0.95 - left
    if bottom + height > 0.88:
        height = 0.88 - bottom

    return left, bottom, width, height, layout_info


def calculate_adaptive_font_sizes(img_width, img_height, base_font_size=48):
    """
    根据图像尺寸计算自适应字体大小

    Args:
        img_width: 图像宽度
        img_height: 图像高度
        base_font_size: 基础字体大小

    Returns:
        dict: 各种文本的字体大小
    """
    # 计算图像面积相对于基准尺寸的比例
    base_area = 800 * 600  # 基准图像尺寸
    current_area = img_width * img_height
    size_factor = min(1.2, max(0.6, (current_area / base_area) ** 0.3))

    return {
        "global": int(base_font_size * size_factor),
        "title": int(base_font_size * size_factor * 0.9),  # 减小标题字体
        "axis_label": int(base_font_size * size_factor),
        "tick_label": int(base_font_size * size_factor * 0.85),
        "colorbar_label": int(base_font_size * size_factor),
        "colorbar_tick": int(base_font_size * size_factor * 0.85),
        "legend": int(base_font_size * size_factor * 0.75),  # 也减小图例字体
    }


def setup_axis_labels_and_ticks(main_ax, font_sizes, layout_info):
    """
    隐藏坐标轴信息，只保留标题和图例

    Args:
        main_ax: matplotlib轴对象
        font_sizes: 字体大小字典
        layout_info: 布局配置信息
    """
    # 隐藏所有坐标轴标签和刻度
    main_ax.set_xlabel("")
    main_ax.set_ylabel("")

    # 隐藏刻度标签
    main_ax.tick_params(
        axis="both",
        which="major",
        labelleft=False,
        labelbottom=False,
        left=False,
        bottom=False,
        top=False,
        right=False,
    )


# ================== 国标分级映射表（GB 3838-2002） ==================
INDICATOR_GRADE_CONFIG = {
    # COD（化学需氧量，mg/L）
    "cod": {
        "thresholds": [15, 15, 20, 30, 40],
        "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
        "colors": ["#1E90FF", "#00FF7F", "#FFFF00", "#FFA500", "#FF0000", "#8B0000"],
    },
    # 氨氮 NH3-N（mg/L）
    "nh3n": {
        "thresholds": [0.15, 0.5, 1.0, 1.5, 2.0],
        "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
        "colors": ["#1E90FF", "#00FF7F", "#FFFF00", "#FFA500", "#FF0000", "#8B0000"],
    },
    # 总磷 TP（mg/L）
    "tp": {
        "thresholds": [0.02, 0.1, 0.2, 0.3, 0.4],
        "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
        "colors": ["#1E90FF", "#00FF7F", "#FFFF00", "#FFA500", "#FF0000", "#8B0000"],
    },
    # 总氮 TN（mg/L）
    "tn": {
        "thresholds": [0.2, 0.5, 1.0, 1.5, 2.0],
        "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
        "colors": ["#1E90FF", "#00FF7F", "#FFFF00", "#FFA500", "#FF0000", "#8B0000"],
    },
    # 溶解氧 DO（mg/L，越高越好，分级反向）
    "do": {
        "thresholds": [2, 3, 5, 6, 7.5],  # 劣五类, Ⅴ类, Ⅳ类, Ⅲ类, Ⅱ类, Ⅰ类
        "labels": ["劣五类", "Ⅴ类", "Ⅳ类", "Ⅲ类", "Ⅱ类", "Ⅰ类"],
        "colors": ["#8B0000", "#FF0000", "#FFA500", "#FFFF00", "#00FF7F", "#1E90FF"],
        "reverse": True,
    },
    # 高锰酸盐指数 CODMn（mg/L）
    "codmn": {
        "thresholds": [2, 4, 6, 10, 15],
        "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
        "colors": ["#1E90FF", "#00FF7F", "#FFFF00", "#FFA500", "#FF0000", "#8B0000"],
    },
    # 五日生化需氧量 BOD5（mg/L）
    "bod5": {
        "thresholds": [3, 3, 4, 6, 10],
        "labels": ["Ⅰ类", "Ⅱ类", "Ⅲ类", "Ⅳ类", "Ⅴ类", "劣五类"],
        "colors": ["#1E90FF", "#00FF7F", "#FFFF00", "#FFA500", "#FF0000", "#8B0000"],
    },
}


def get_indicator_grade_config(indicator):
    """
    获取指标的国标分级配置（阈值、标签、颜色）
    支持标准化名称（如do、cod、nh3n、tp、tn、ph、turbidity、chla）
    """
    key = indicator.lower()
    return INDICATOR_GRADE_CONFIG.get(key)


# ================== 增强插值算法（从heatmap_generator.py集成） ==================


def compute_convex_hull(points):
    """
    计算散点数据的凸包，返回凸包顶点坐标
    points: 二维数组，每行为一个点的坐标 (lon, lat)
    返回: 凸包顶点坐标数组
    """
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]
    return hull_points


def compute_alpha_shape(points, alpha=None):
    """
    计算Alpha Shape边界，能够处理凹陷形状
    points: 二维数组，每行为一个点的坐标 (lon, lat)
    alpha: Alpha参数，控制边界的"紧密度"，None时自动计算
    返回: 边界点的坐标数组
    """
    if len(points) < 3:
        return points

    # 计算Delaunay三角剖分
    tri = Delaunay(points)

    # 自动计算alpha值
    if alpha is None:
        # 基于点之间的平均距离来估算alpha
        distances = []
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                dist = np.sqrt(np.sum((points[i] - points[j]) ** 2))
                distances.append(dist)

        # 使用距离的某个百分位数作为alpha
        alpha = np.percentile(distances, 30)  # 与heatmap_generator保持一致

    # 找到边界边
    boundary_edges = []

    # 遍历所有三角形
    for simplex in tri.simplices:
        # 计算三角形的外接圆半径
        triangle_points = points[simplex]

        # 计算边长
        a = np.linalg.norm(triangle_points[1] - triangle_points[0])
        b = np.linalg.norm(triangle_points[2] - triangle_points[1])
        c = np.linalg.norm(triangle_points[0] - triangle_points[2])

        # 检查退化边（数值稳定性保护）
        min_edge_length = np.finfo(float).eps * 100
        if min(a, b, c) < min_edge_length:
            continue  # 跳过退化三角形

        # 半周长
        s = (a + b + c) / 2

        # 数值稳定的面积计算（海伦公式）
        area_squared = s * (s - a) * (s - b) * (s - c)

        # 检查负数（由于数值误差可能出现）
        if area_squared <= 0:
            continue  # 跳过退化三角形

        area = np.sqrt(area_squared)

        # 使用相对阈值而不是绝对阈值
        max_edge = max(a, b, c)
        min_area_threshold = np.finfo(float).eps * 100 * max_edge**2

        if area > min_area_threshold:
            circumradius = (a * b * c) / (4 * area)

            # 检查circumradius是否有效
            if np.isfinite(circumradius) and circumradius < alpha:
                for i in range(3):
                    edge = (simplex[i], simplex[(i + 1) % 3])
                    boundary_edges.append(edge)

    # 找到只出现一次的边（边界边）
    edge_count = {}
    for edge in boundary_edges:
        edge_sorted = tuple(sorted(edge))
        edge_count[edge_sorted] = edge_count.get(edge_sorted, 0) + 1

    # 只保留出现一次的边
    true_boundary_edges = [edge for edge, count in edge_count.items() if count == 1]

    if not true_boundary_edges:
        # 如果没有找到边界，回退到凸包
        return compute_convex_hull(points)

    # 构建边界路径
    boundary_points = []
    remaining_edges = list(true_boundary_edges)

    if remaining_edges:
        # 从第一条边开始
        current_edge = remaining_edges.pop(0)
        boundary_points.extend([current_edge[0], current_edge[1]])

        # 尝试连接后续边
        while remaining_edges:
            last_point = boundary_points[-1]
            found_next = False

            for i, edge in enumerate(remaining_edges):
                if edge[0] == last_point:
                    boundary_points.append(edge[1])
                    remaining_edges.pop(i)
                    found_next = True
                    break
                elif edge[1] == last_point:
                    boundary_points.append(edge[0])
                    remaining_edges.pop(i)
                    found_next = True
                    break

            if not found_next:
                # 如果无法连接，尝试新的起始点
                if remaining_edges:
                    next_edge = remaining_edges.pop(0)
                    boundary_points.extend([next_edge[0], next_edge[1]])

    # 转换为坐标数组
    boundary_coords = points[boundary_points]

    return boundary_coords


def create_convex_hull_mask(grid_lon, grid_lat, hull_points):
    """
    创建凸包掩码，标记网格中哪些点在凸包内
    grid_lon, grid_lat: 网格坐标
    hull_points: 凸包顶点坐标
    返回: 布尔掩码数组
    """
    # 将网格坐标转换为点集
    points = np.column_stack((grid_lon.ravel(), grid_lat.ravel()))

    # 创建凸包路径
    hull_path = Path(hull_points)

    # 检查每个网格点是否在凸包内
    mask = hull_path.contains_points(points)

    # 重新塑形为网格形状
    mask = mask.reshape(grid_lon.shape)

    return mask


def kriging_interpolation(points, values, grid_lon, grid_lat, method="auto"):
    """
    使用克里金插值方法，支持多种配置

    Args:
        points: 数据点坐标 (N, 2) [lon, lat]
        values: 数据值 (N,)
        grid_lon, grid_lat: 插值网格
        method: 插值方法 ('auto', 'universal_kriging', 'ordinary_kriging_spherical', 'ordinary_kriging_exponential')

    Returns:
        grid_values: 插值结果
    """
    x = points[:, 0]  # 经度
    y = points[:, 1]  # 纬度
    z = values

    # 数据点数量检查
    if len(x) < 3:
        logger.warning("数据点少于3个，使用线性插值")
        return griddata(points, values, (grid_lon, grid_lat), method="linear")

    # 计算数据范围（用于搜索半径）
    x_range = np.max(x) - np.min(x)
    y_range = np.max(y) - np.min(y)
    data_range = np.sqrt(x_range**2 + y_range**2)

    # 根据method参数决定尝试顺序
    if method == "linear":
        # 直接使用scipy线性插值
        logger.info("使用scipy线性插值方法")
        return griddata(points, values, (grid_lon, grid_lat), method="linear")
    elif method == "auto":
        # 自动模式：按优先级尝试
        methods_to_try = [
            "universal_kriging",
            "ordinary_kriging_spherical",
            "ordinary_kriging_exponential",
        ]
    elif method in KRIGING_CONFIG:
        # 指定方法
        methods_to_try = [method]
    else:
        logger.warning(f"未知的插值方法: {method}，使用自动模式")
        methods_to_try = [
            "universal_kriging",
            "ordinary_kriging_spherical",
            "ordinary_kriging_exponential",
        ]

    # 依次尝试不同的克里金方法
    for method_name in methods_to_try:
        config = KRIGING_CONFIG[method_name]

        try:
            logger.info(f"尝试{config['description']}...")

            # 数据预处理：防止负数
            if config.get("enforce_positive", False):
                transform_method = config.get("transform_method", "clip")
                z_transformed, transform_params = transform_data_for_kriging(
                    z, transform_method
                )
                logger.info(f"使用{transform_method}方法处理数据，确保正数插值结果")
            else:
                z_transformed = z
                transform_params = {"method": "none"}

            if method_name == "universal_kriging":
                # 泛克里金
                kriging_obj = UniversalKriging(
                    x,
                    y,
                    z_transformed,
                    variogram_model=config["variogram_model"],
                    drift_terms=config["drift_terms"],
                    verbose=False,
                    enable_plotting=False,
                    exact_values=True,
                    pseudo_inv=False,
                )
                z_pred, ss = kriging_obj.execute("grid", grid_lon[0, :], grid_lat[:, 0])

            else:
                # 普通克里金（球形或指数模型）
                kriging_obj = OrdinaryKriging(
                    x,
                    y,
                    z_transformed,
                    variogram_model=config["variogram_model"],
                    verbose=False,
                    enable_plotting=False,
                    exact_values=True,
                    pseudo_inv=False,
                )

                # 计算搜索半径
                search_radius = data_range * config["search_radius_factor"]

                # 执行插值（使用搜索策略）
                z_pred, ss = kriging_obj.execute(
                    "grid",
                    grid_lon[0, :],
                    grid_lat[:, 0],
                    backend="loop",
                    n_closest_points=config["n_closest_points"],
                )

                logger.info(
                    f"搜索半径: {search_radius:.6f}, 最近点数: {config['n_closest_points']}"
                )

            # 逆变换回原始尺度
            z_pred = inverse_transform_data(z_pred, transform_params)

            # 统计插值结果范围
            valid_mask = ~np.isnan(z_pred)
            if np.any(valid_mask):
                min_val, max_val = (
                    np.min(z_pred[valid_mask]),
                    np.max(z_pred[valid_mask]),
                )
                negative_count = np.sum(z_pred[valid_mask] < 0)
                logger.info(
                    f"{config['description']}成功，网格大小: {z_pred.shape}, 值范围: [{min_val:.3f}, {max_val:.3f}], 负值数量: {negative_count}"
                )
            else:
                logger.info(f"{config['description']}成功，网格大小: {z_pred.shape}")

            return z_pred

        except Exception as e:
            logger.warning(f"{config['description']}失败: {str(e)}")
            continue

    # 所有克里金方法都失败，回退到线性插值
    logger.warning("所有克里金方法失败，回退到线性插值")
    return griddata(points, values, (grid_lon, grid_lat), method="linear")


def enhanced_interpolation_with_neighborhood(
    all_data,
    grid_resolution=200,
    method="linear",
    neighborhood_radius=2,
    boundary_method="alpha_shape",
    indicator_col=None,
    fixed_bounds=None,
    kml_boundary_path=None,
    satellite_info=None,
):
    """
    基于智能边界的高分辨率插值，包含邻域分析
    all_data: 包含所有文件数据的DataFrame
    grid_resolution: 网格分辨率
    method: 插值方法
    neighborhood_radius: 邻域分析半径(像素)
    boundary_method: 边界检测方法 ('alpha_shape', 'kml')
    indicator_col: 指标列名，如果为None则使用第一个非坐标列
    fixed_bounds: 固定的地理边界范围 [min_lon, min_lat, max_lon, max_lat]，如果提供则使用此范围而不是数据边界
    kml_boundary_path: KML边界文件路径，当boundary_method='kml'时使用
    返回: 插值结果、网格坐标、边界掩码、边界点
    """
    # 提取坐标和数值 - 适配maps.py的数据格式
    if "longitude" in all_data.columns and "latitude" in all_data.columns:
        points = all_data[["longitude", "latitude"]].values
    else:
        points = all_data[["lon", "lat"]].values

    # 获取指标列
    if indicator_col is not None:
        if indicator_col not in all_data.columns:
            raise ValueError(f"指定的指标列 {indicator_col} 不存在")
        values = all_data[indicator_col].values
    else:
        # 获取指标列（排除坐标列）
        coord_cols = ["longitude", "latitude", "lon", "lat", "index"]
        value_cols = [col for col in all_data.columns if col not in coord_cols]

        if len(value_cols) == 0:
            raise ValueError("未找到有效的指标数据列")

        # 使用第一个指标列的数据
        values = all_data[value_cols[0]].values

    # 根据是否提供固定边界决定使用范围
    if fixed_bounds is not None:
        # 使用固定的地理边界（如卫星图边界）
        lon_min, lat_min, lon_max, lat_max = fixed_bounds
        # 仍然计算数据边界用于边界检测
        if boundary_method == "alpha_shape":
            boundary_points = compute_alpha_shape(points)
        elif boundary_method == "kml":
            # KML边界方法，完全替代alpha_shape
            if kml_boundary_path and os.path.exists(kml_boundary_path):
                from ..utils.kml import get_kml_boundary_points

                boundary_points = get_kml_boundary_points(kml_boundary_path)
                if boundary_points is not None:
                    # 像alpha_shape一样计算经纬度范围
                    lon_min, lon_max = (
                        boundary_points[:, 0].min(),
                        boundary_points[:, 0].max(),
                    )
                    lat_min, lat_max = (
                        boundary_points[:, 1].min(),
                        boundary_points[:, 1].max(),
                    )
                    logger.info(f"使用KML边界点: {len(boundary_points)} 个点")
                else:
                    logger.warning("无法从KML文件获取边界点，回退到alpha_shape")
                    boundary_points = compute_alpha_shape(points)
                    lon_min, lon_max = (
                        boundary_points[:, 0].min(),
                        boundary_points[:, 0].max(),
                    )
                    lat_min, lat_max = (
                        boundary_points[:, 1].min(),
                        boundary_points[:, 1].max(),
                    )
            else:
                logger.warning(
                    f"KML文件不存在或路径无效: {kml_boundary_path}，回退到alpha_shape"
                )
                boundary_points = compute_alpha_shape(points)
                lon_min, lon_max = (
                    boundary_points[:, 0].min(),
                    boundary_points[:, 0].max(),
                )
                lat_min, lat_max = (
                    boundary_points[:, 1].min(),
                    boundary_points[:, 1].max(),
                )
        else:  # 默认使用凸包
            boundary_points = compute_convex_hull(points)
    else:
        # 根据选择的方法计算边界（原有逻辑）
        if boundary_method == "alpha_shape":
            boundary_points = compute_alpha_shape(points)
            # 确定经纬度范围（基于Alpha Shape）
            lon_min, lon_max = boundary_points[:, 0].min(), boundary_points[:, 0].max()
            lat_min, lat_max = boundary_points[:, 1].min(), boundary_points[:, 1].max()
        elif boundary_method == "kml":
            # KML边界方法，完全替代alpha_shape
            if kml_boundary_path and os.path.exists(kml_boundary_path):
                from ..utils.kml import get_kml_boundary_points

                boundary_points = get_kml_boundary_points(kml_boundary_path)
                if boundary_points is not None:
                    # 像alpha_shape一样计算经纬度范围
                    lon_min, lon_max = (
                        boundary_points[:, 0].min(),
                        boundary_points[:, 0].max(),
                    )
                    lat_min, lat_max = (
                        boundary_points[:, 1].min(),
                        boundary_points[:, 1].max(),
                    )
                    logger.info(f"使用KML边界点: {len(boundary_points)} 个点")
                else:
                    logger.warning("无法从KML文件获取边界点，回退到alpha_shape")
                    boundary_points = compute_alpha_shape(points)
                    lon_min, lon_max = (
                        boundary_points[:, 0].min(),
                        boundary_points[:, 0].max(),
                    )
                    lat_min, lat_max = (
                        boundary_points[:, 1].min(),
                        boundary_points[:, 1].max(),
                    )
            else:
                logger.warning(
                    f"KML文件不存在或路径无效: {kml_boundary_path}，回退到alpha_shape"
                )
                boundary_points = compute_alpha_shape(points)
                lon_min, lon_max = (
                    boundary_points[:, 0].min(),
                    boundary_points[:, 0].max(),
                )
                lat_min, lat_max = (
                    boundary_points[:, 1].min(),
                    boundary_points[:, 1].max(),
                )
        else:  # 默认使用凸包
            boundary_points = compute_convex_hull(points)
            lon_min, lon_max = boundary_points[:, 0].min(), boundary_points[:, 0].max()
            lat_min, lat_max = boundary_points[:, 1].min(), boundary_points[:, 1].max()

        # 只在使用数据边界时才添加边界扩展（KML方法不需要扩展）
        if boundary_method != "kml":
            lon_range = lon_max - lon_min
            lat_range = lat_max - lat_min
            margin_factor = 0.01  # 减少到1%边界扩展，避免边缘效应

            lon_min -= lon_range * margin_factor
            lon_max += lon_range * margin_factor
            lat_min -= lat_range * margin_factor
            lat_max += lat_range * margin_factor

    # 创建高分辨率插值网格 - 保持实际地理比例
    lon_range = lon_max - lon_min
    lat_range = lat_max - lat_min
    aspect_ratio = lon_range / lat_range

    # 智能分辨率选择策略
    if satellite_info is not None:
        # 策略1：基于底图长宽比的适配插值（性能优先）
        img_width, img_height, _ = satellite_info
        aspect_ratio = img_width / img_height

        # 固定较长边为800像素，保持长宽比
        target_max_dimension = 800
        if aspect_ratio >= 1:
            # 宽图
            lon_pixels = target_max_dimension
            lat_pixels = int(target_max_dimension / aspect_ratio)
        else:
            # 高图
            lat_pixels = target_max_dimension
            lon_pixels = int(target_max_dimension * aspect_ratio)

        logger.info(
            f"使用长宽比适配插值：底图{img_width}x{img_height}(比例{aspect_ratio:.2f}) → 插值{lon_pixels}x{lat_pixels}"
        )

        # 简单的范围限制
        lat_pixels = min(max(lat_pixels, 50), 1000)
        lon_pixels = min(max(lon_pixels, 50), 1000)
    else:
        # 策略2：基于地理精度的插值（回退方案）
        desired_resolution = 0.00003  # 3米/像素
        lat_pixels = int(np.ceil(lat_range / desired_resolution))
        lon_pixels = int(np.ceil(lon_range / desired_resolution))
        logger.info(f"使用地理精度插值：3米/像素，插值{lon_pixels}x{lat_pixels}")

        # 地理精度插值使用保守的限制
        lat_pixels = min(max(lat_pixels, 50), 2000)
        lon_pixels = min(max(lon_pixels, 50), 2000)

    logger.info(
        f"创建插值网格: {lat_pixels} x {lon_pixels} (长宽比: {aspect_ratio:.3f})"
    )

    # 这里的`*1j`是numpy的复数语法，表示生成等间隔的复数个点（即像素数），
    # 例如lat_pixels*1j表示在纬度方向生成lat_pixels个点，lon_pixels*1j表示在经度方向生成lon_pixels个点。
    # 这种写法常用于np.mgrid，等价于np.linspace(start, stop, num)，但能直接生成网格。
    # 这里的j没有实际的虚数意义，只是numpy规定用来指定采样点数的语法糖。
    grid_lat, grid_lon = np.mgrid[
        lat_min : lat_max : lat_pixels * 1j, lon_min : lon_max : lon_pixels * 1j
    ]

    # 执行插值
    # 对于KML边界方法，需要确保插值能够覆盖整个KML区域
    if (
        boundary_method == "kml"
        and kml_boundary_path
        and os.path.exists(kml_boundary_path)
    ):
        # 在KML边界上添加虚拟数据点，确保插值覆盖整个边界
        from ..utils.kml import get_kml_boundary_points

        kml_boundary_points = get_kml_boundary_points(kml_boundary_path)

        if kml_boundary_points is not None:
            # 在KML边界上均匀采样点
            n_boundary_points = min(50, len(kml_boundary_points))  # 限制边界点数量
            if len(kml_boundary_points) > n_boundary_points:
                # 均匀采样边界点
                indices = np.linspace(
                    0, len(kml_boundary_points) - 1, n_boundary_points, dtype=int
                )
                sampled_boundary_points = kml_boundary_points[indices]
            else:
                sampled_boundary_points = kml_boundary_points

            # 为每个边界点找到在KML范围内的最近真实数据点的值
            from matplotlib.path import Path
            from scipy.spatial.distance import cdist

            # 首先筛选出在KML范围内的真实数据点
            kml_polygon_path = Path(kml_boundary_points)
            points_inside_mask = kml_polygon_path.contains_points(points)

            if np.any(points_inside_mask):
                # 获取在KML范围内的数据点
                points_inside_kml = points[points_inside_mask]
                values_inside_kml = values[points_inside_mask]

                # 计算边界点到KML范围内真实数据点的距离
                distances = cdist(sampled_boundary_points, points_inside_kml)

                # 找到每个边界点在KML范围内的最近真实数据点
                nearest_indices = np.argmin(distances, axis=1)

                # 使用KML范围内最近真实数据点的值作为边界虚拟点的值
                boundary_values = values_inside_kml[nearest_indices]

                logger.info(
                    f"从 {len(points_inside_kml)} 个KML范围内的真实数据点中选择最近点作为边界值"
                )
            else:
                # 如果没有真实数据点在KML范围内，使用全局最近点（回退策略）
                logger.warning("没有真实数据点在KML范围内，使用全局最近点作为边界值")
                distances = cdist(sampled_boundary_points, points)
                nearest_indices = np.argmin(distances, axis=1)
                boundary_values = values[nearest_indices]
            extended_points = np.vstack([points, sampled_boundary_points])
            extended_values = np.concatenate([values, boundary_values])

            logger.info(f"添加 {len(sampled_boundary_points)} 个KML边界虚拟点进行插值")

            # 使用扩展的数据集进行克里金插值
            grid_values = kriging_interpolation(
                extended_points,
                extended_values,
                grid_lon,
                grid_lat,
                method=GLOBAL_KRIGING_METHOD,
            )
        else:
            # 如果无法获取KML边界点，使用克里金插值
            grid_values = kriging_interpolation(
                points, values, grid_lon, grid_lat, method=GLOBAL_KRIGING_METHOD
            )
    else:
        # 非KML方法使用克里金插值
        grid_values = kriging_interpolation(
            points, values, grid_lon, grid_lat, method=GLOBAL_KRIGING_METHOD
        )

    # 创建边界掩码
    if boundary_method == "kml":
        # KML方法使用专门的KML边界掩码
        if kml_boundary_path and os.path.exists(kml_boundary_path):
            from ..utils.kml import create_kml_boundary_mask

            boundary_mask = create_kml_boundary_mask(
                grid_lon, grid_lat, kml_boundary_path
            )
        else:
            boundary_mask = np.ones_like(grid_lon, dtype=bool)
    else:
        # alpha_shape, convex_hull 使用凸包掩码逻辑
        if boundary_points is not None:
            boundary_mask = create_convex_hull_mask(grid_lon, grid_lat, boundary_points)
        else:
            boundary_mask = np.ones_like(grid_lon, dtype=bool)

    # 将边界外的区域设为NaN
    grid_values[~boundary_mask] = np.nan

    # 邻域分析：使用高斯滤波平滑插值结果
    # 只对有效数据进行滤波，避免NaN填充为0导致边界数值偏低
    valid_mask = ~np.isnan(grid_values)
    if np.any(valid_mask):
        # 创建临时数组，使用边界值填充而不是0
        temp_values = np.copy(grid_values)
        nan_mask = np.isnan(temp_values)

        # 如果有NaN值，使用最近邻有效值填充
        if np.any(nan_mask):
            from scipy.ndimage import distance_transform_edt

            # 找到最近的有效值
            indices = distance_transform_edt(
                nan_mask, return_distances=False, return_indices=True
            )
            temp_values[nan_mask] = temp_values[tuple(indices[:, nan_mask])]

        # 应用高斯滤波
        smoothed_values = gaussian_filter(temp_values, sigma=neighborhood_radius)

        # 应用掩码，只保留边界内的平滑结果
        grid_values[valid_mask] = smoothed_values[valid_mask]

    return grid_values, grid_lon, grid_lat, boundary_mask, boundary_points


class SatelliteMapGenerator:
    """卫星图像生成器类"""

    def __init__(self, path_manager):
        """
        初始化卫星图像生成器

        Args:
            satellite_image_path: 卫星图像文件路径
            geo_bounds: 地理边界坐标 [min_lon, min_lat, max_lon, max_lat]
        """
        self.path_manager = path_manager
        self.satellite_geo_bounds = {}
        self.kml_boundary_path = None

    def init_maps(
        self,
        geo_info: dict,
        satellite_path: str,
        data: pd.DataFrame,
        uav_data: pd.DataFrame,
        kml_boundary_path: Optional[str] = None,
        visualization_mode: str = "quantitative",
    ) -> Optional[str]:
        """
        生成指标卫星图

        Args:
            geo_info: 地理信息字典，包含边界坐标等
            satellite_path: 卫星图像文件路径
            data: 包含指标数据的DataFrame
            uav_data: 无人机数据的DataFrame
            kml_boundary_path: KML边界文件路径（可选）

        Returns:
            Optional[str]: 生成的图像文件路径，失败返回None
        """
        # 获取卫星地图边界
        self.satellite_geo_bounds = parse_geo_bounds(geo_info)
        # 获取卫星底图宽、高、读取的图像对象
        self.satellite_info = read_satellite(satellite_path)
        # 存储KML边界文件路径
        self.kml_boundary_path = kml_boundary_path
        # 存储可视化模式
        self.visualization_mode = visualization_mode

        # 获取所有水质指标名称
        if data is not None:
            self.indicator_columns = [
                col
                for col in data.columns
                if col not in ["index", "latitude", "longitude"]
            ]
        elif uav_data is not None:
            logger.info("使用无人机数据生成指标卫星图")
            self.indicator_columns = [
                col
                for col in uav_data.columns
                if col not in ["index", "latitude", "longitude"]
            ]
        else:
            logger.error("实测数据 和 无人机数据 不能同时为空")
            raise ValueError("实测数据 和 无人机数据 不能同时为空")

        logging.info(f"检测到的水质指标: {', '.join(self.indicator_columns)}")

        # 获取数据的地理边界
        self.data_geo_bounds = (
            get_data_geo_bounds(data)
            if data is not None
            else get_data_geo_bounds(uav_data)
        )
        # 保存原始实测数据状态，用于判断是否有实测数据
        self.original_measured_data = data
        # 接收反演值数据，如果无实测值，这里传入的data为None，用无人机数据代替
        self.data = data if data is not None else uav_data

        # 初始化水体掩膜（暂时设为None，在实际使用中可以从配置或数据中获取）
        self.water_mask = None

        if data is not None:
            # 检查多少点位在卫星图外
            points_outside, self.all_points_outside = self.check_points_in_bounds()
            if self.all_points_outside:
                logger.error(
                    "所有点位都在卫星图外，可能是为传递实测数据，或者是实测数据和飞行任务范围偏差太大。"
                )
        else:
            self.all_points_outside = False
            logger.warning("未传递实测数据，将只生成卫星底图。")

    def _determine_colorbar_mode(self):
        """
        判断colorbar显示模式
        
        Returns:
            str: "quantitative" 或 "qualitative"
        """
        # 检查是否有实测数据
        has_measured_data = (
            self.original_measured_data is not None
            and not self.original_measured_data.empty
        )
        
        if has_measured_data:
            # 有实测数据时，强制使用定量模式（数值显示）
            return "quantitative"
        else:
            # 无实测数据时，根据配置决定
            return self.visualization_mode

    def generate_indicator_map(self):
        if not self.all_points_outside:
            logging.info("开始生成各指标反演结果分布图...")

        save_paths = dict()
        for indicator in self.indicator_columns:
            save_paths[indicator] = {}
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 检查指标是否支持国标分级
            grade_cfg = get_indicator_grade_config(indicator)
            supports_grading = grade_cfg is not None

            # 检查是否有实测数据（基于原始传入的data参数，而不是self.data）
            has_measured_data = (
                self.original_measured_data is not None
                and not self.original_measured_data.empty
            )
            
            # 获取当前指标的colorbar模式
            colorbar_mode = self._determine_colorbar_mode()

            # 添加调试信息
            logger.info(
                f"{indicator} - 实测数据状态: has_measured_data={has_measured_data}"
            )
            logger.info(
                f"{indicator} - colorbar模式: {colorbar_mode}"
            )
            logger.info(
                f"{indicator} - original_measured_data is None: {self.original_measured_data is None}"
            )

            # 判断是否为定量模式：有实测数据或配置为定量模式
            is_quantitative_mode = has_measured_data or self.visualization_mode == "quantitative"
            
            # 根据是否支持国标分级和是否为定量模式决定生成哪些类型的图
            if supports_grading and is_quantitative_mode:
                map_types = [
                    "distribution",
                    "interpolation",
                    "clean_interpolation_svg",
                    "level",
                ]
                logger.info(f"{indicator} 支持国标分级且为定量模式，将生成完整的图表集（包括等级图）")
            elif is_quantitative_mode:
                map_types = ["distribution", "interpolation", "clean_interpolation_svg"]
                logger.info(f"{indicator} 为定量模式但不支持国标分级，跳过等级图生成")
            else:
                # 定性模式时，只生成散点图和插值图，不生成等级图
                map_types = ["distribution", "interpolation", "clean_interpolation_svg"]
                logger.info(
                    f"{indicator} 为定性模式，跳过等级图生成，colorbar将显示相对高低"
                )

            for type in map_types:
                # 根据类型设置文件扩展名
                if type == "clean_interpolation_svg":
                    map_filename = f"{indicator}_clean_transparent_{timestamp}.svg"
                else:
                    map_filename = f"{indicator}_{type}_{timestamp}.png"

                save_path = self.path_manager.get_file_path("maps", map_filename)

                if type == "distribution":
                    result = generate_distribution_indicator_map(
                        self.data,
                        indicator,
                        self.satellite_info,
                        save_path,
                        self.satellite_geo_bounds,
                        self.data_geo_bounds,
                        self.all_points_outside,
                        colorbar_mode,
                    )
                elif type == "interpolation":
                    # 生成带装饰的插值热力图
                    result, interpolation_data = generate_interpolation_indicator_map(
                        self.data,
                        indicator,
                        self.satellite_info,
                        save_path,
                        self.satellite_geo_bounds,
                        self.data_geo_bounds,
                        self.all_points_outside,
                        self.water_mask,
                        kml_boundary_path=self.kml_boundary_path,
                        colorbar_mode=colorbar_mode,
                    )
                    # 保存插值数据和网格坐标
                    if interpolation_data:
                        self.interpolation_cache = (
                            interpolation_data  # 缓存插值结果供clean版本使用
                        )
                        self.Z, self.grid_lon, self.grid_lat = interpolation_data
                    else:
                        self.interpolation_cache = None
                        self.Z = None
                elif type == "clean_interpolation_svg":
                    # 生成透明背景SVG版纯净插值热力图，优先使用缓存的插值结果
                    precomputed = getattr(self, "interpolation_cache", None)
                    result, _ = generate_clean_interpolation_map(
                        self.data,
                        indicator,
                        save_path,
                        grid_resolution=300,  # 恢复原值（此参数实际未使用）
                        transparent_bg=True,
                        output_format="svg",
                        satellite_info=self.satellite_info,
                        kml_boundary_path=self.kml_boundary_path,
                        precomputed_interpolation=precomputed,
                    )
                elif type == "level":
                    # 使用插值数据生成国标等级图
                    result = generate_level_indicator_map(
                        indicator,
                        self.satellite_info,
                        save_path,
                        self.satellite_geo_bounds,
                        self.data_geo_bounds,
                        self.all_points_outside,
                        self.Z,
                        getattr(self, "grid_lon", None),
                        getattr(self, "grid_lat", None),
                    )
                    # 清理插值数据
                    self.Z = None
                    self.grid_lon = None
                    self.grid_lat = None

                if result and result != "skip":
                    save_paths[indicator][type] = result
                    logging.info(
                        f"{indicator} 指标{type}图创建成功，保存路径: {result}"
                    )
                elif result == "skip":
                    logging.info(f"{indicator} 指标{type}图跳过生成（不支持国标分级）")
                else:
                    logging.warning(f"{indicator} 指标{type}图创建失败!")

        return save_paths

    def check_points_in_bounds(self):
        """检查数据点是否在卫星图像范围内

        Returns:
            tuple: (超出范围的点数, 是否所有点都在范围内)
        """
        points_outside = 0
        all_points_outside = False

        # 记录边界信息用于调试
        min_lon, min_lat, max_lon, max_lat = self.satellite_geo_bounds
        logger.debug(
            f"卫星图边界: 经度 {min_lon:.6f} - {max_lon:.6f}, 纬度 {min_lat:.6f} - {max_lat:.6f}"
        )

        # 记录数据范围
        data_min_lon, data_max_lon = (
            self.data["longitude"].min(),
            self.data["longitude"].max(),
        )
        data_min_lat, data_max_lat = (
            self.data["latitude"].min(),
            self.data["latitude"].max(),
        )
        logger.debug(
            f"数据范围: 经度 {data_min_lon:.6f} - {data_max_lon:.6f}, 纬度 {data_min_lat:.6f} - {data_max_lat:.6f}"
        )

        for idx, row in self.data.iterrows():
            lat, lon = row["latitude"], row["longitude"]
            _, _, is_inside = geo_to_image_coords(
                lat,
                lon,
                self.satellite_info[0],  # img_width
                self.satellite_info[1],  # img_height
                self.satellite_geo_bounds,
            )
            if not is_inside:
                points_outside += 1
                logger.debug(f"点位超出范围: ({lat:.6f}, {lon:.6f})")

        if points_outside > 0:
            logger.warning(
                f"有 {points_outside}/{len(self.data)} 个数据点超出卫星图像范围"
            )

        if points_outside == len(self.data):
            all_points_outside = True

        return points_outside, all_points_outside


# 创建单个以点带面图 - 使用增强插值算法
def generate_interpolation_indicator_map(
    data,
    indicator,
    satellite_info,
    save_path,
    satellite_geo_bounds,
    data_geo_bounds,
    all_points_outside,
    water_mask,
    kml_boundary_path=None,
    colorbar_mode="quantitative",
):
    """生成插值热力图 - 使用heatmap_generator的增强插值算法

    Args:
        data: 包含经纬度和指标值的数据框
        indicator: 要绘制的指标名称
        satellite_info: 卫星图像信息元组 (宽度, 高度, 图像对象)
        save_path: 保存路径
        satellite_geo_bounds: 卫星图像地理边界
        data_geo_bounds: 数据地理边界
        all_points_outside: 是否所有点都在卫星图像范围外
        water_mask: 水体掩膜
        kml_boundary_path: KML边界文件路径（可选）
    """
    # 解包卫星数据信息
    img_width, img_height, img_obj = satellite_info

    # 计算自适应字体大小和布局参数
    font_sizes = calculate_adaptive_font_sizes(img_width, img_height)
    left, bottom, width, height, layout_info = calculate_dynamic_layout(
        img_width,
        img_height,
        has_right_element=True,
        font_size=font_sizes["global"],
        right_element_type="colorbar",
    )  # 插值图有colorbar
    layout_params = [left, bottom, width, height]

    # 重新设置字体参数确保生效
    plt.rcParams.update({"font.size": font_sizes["global"]})
    plt.rcParams["font.family"] = "SimHei"
    plt.rcParams["axes.unicode_minus"] = False

    # 准备数据用于增强插值算法
    prepared_data = data.copy()
    prepared_data["longitude"] = data["longitude"]
    prepared_data["latitude"] = data["latitude"]
    prepared_data[indicator] = data[indicator]

    # 使用增强插值算法生成插值数据
    try:
        # 决定使用的边界方法
        boundary_method = (
            "kml"
            if kml_boundary_path and os.path.exists(kml_boundary_path)
            else "alpha_shape"
        )

        # 根据边界方法决定插值范围
        # 所有边界方法都使用相同的逻辑：根据数据是否在卫星图内决定插值范围
        interpolation_bounds = None if all_points_outside else satellite_geo_bounds

        grid_values, grid_lon, grid_lat, boundary_mask, boundary_points = (
            enhanced_interpolation_with_neighborhood(
                prepared_data,
                grid_resolution=300,  # 保留兼容性，但优先使用satellite_info
                method="linear",
                neighborhood_radius=3,
                boundary_method=boundary_method,
                indicator_col=indicator,
                fixed_bounds=interpolation_bounds,
                kml_boundary_path=kml_boundary_path,
                satellite_info=satellite_info,  # 新增：智能分辨率选择
            )
        )
    except Exception as e:
        logger.error(f"增强插值算法失败: {str(e)}，回退到原始算法")
        # 回退到原始RBF插值
        geo_bounds = data_geo_bounds if all_points_outside else satellite_geo_bounds
        x = np.linspace(geo_bounds[0], geo_bounds[2], img_width)
        y = np.linspace(geo_bounds[1], geo_bounds[3], img_height)
        X, Y = np.meshgrid(x, y)

        points = np.column_stack((data["longitude"], data["latitude"]))
        values = data[indicator].values

        try:
            rbf = RBFInterpolator(points, values, kernel="thin_plate_spline")
            grid_points = np.column_stack((X.flatten(), Y.flatten()))
            grid_values = rbf(grid_points).reshape(X.shape)
            grid_lon, grid_lat = X, Y
        except Exception as e2:
            logger.error(f"RBF插值也失败: {str(e2)}")
            return None, None

    # 应用水体掩膜 - 暂时禁用，Alpha Shape边界检测已足够精确
    # if water_mask is not None and not all_points_outside:
    #     try:
    #         if water_mask.shape != grid_values.shape:
    #             from scipy.ndimage import zoom
    #             zoom_factor = (grid_values.shape[0]/water_mask.shape[0], grid_values.shape[1]/water_mask.shape[1])
    #             resampled_mask = zoom(water_mask, zoom_factor, order=0)
    #             grid_values = np.where(resampled_mask > 0, grid_values, np.nan)
    #             logger.info(f"水体掩膜已调整大小，从{water_mask.shape}到{grid_values.shape}")
    #         else:
    #             grid_values = np.where(water_mask > 0, grid_values, np.nan)
    #     except Exception as e:
    #         logger.warning(f"应用水体掩膜失败: {str(e)}")

    # 计算显示范围
    geo_bounds = data_geo_bounds if all_points_outside else satellite_geo_bounds

    # 创建图形
    if all_points_outside:
        # 对于没有卫星图像的情况
        fig = plt.figure(figsize=(12, 8))
        main_ax = fig.add_subplot(111)
        main_ax.add_patch(
            plt.Rectangle(
                (geo_bounds[0], geo_bounds[1]),
                geo_bounds[2] - geo_bounds[0],
                geo_bounds[3] - geo_bounds[1],
                facecolor="lightgray",
            )
        )
        dpi = 300
    else:
        # 有卫星图像的情况
        dpi = 100.0
        figsize = (img_width / dpi, img_height / dpi)
        fig = plt.figure(figsize=figsize, dpi=dpi, frameon=True)
        main_ax = fig.add_axes(layout_params)

        # 显示卫星图像
        main_ax.imshow(
            img_obj,
            extent=[geo_bounds[0], geo_bounds[2], geo_bounds[1], geo_bounds[3]],
            aspect="auto",
            origin="upper",
        )  # 卫星图像使用origin='upper'

    # 设置坐标范围（保持数据正确显示）
    main_ax.set_xlim(geo_bounds[0], geo_bounds[2])
    main_ax.set_ylim(geo_bounds[1], geo_bounds[3])

    # 隐藏坐标轴信息
    setup_axis_labels_and_ticks(main_ax, font_sizes, layout_info)

    # 计算原始数据范围，确保与散点图colorbar范围一致
    original_values = data[indicator].values
    vmin, vmax = np.min(original_values), np.max(original_values)

    # 绘制插值热力图，使用插值网格的实际地理边界确保GPS对齐
    # 获取插值网格的实际地理范围，而不是使用卫星图边界
    grid_lon_min, grid_lon_max = grid_lon.min(), grid_lon.max()
    grid_lat_min, grid_lat_max = grid_lat.min(), grid_lat.max()

    im = main_ax.imshow(
        grid_values,
        extent=[grid_lon_min, grid_lon_max, grid_lat_min, grid_lat_max],
        aspect="auto",
        origin="lower",
        cmap="jet",
        interpolation="bilinear",
        vmin=vmin,
        vmax=vmax,
    )

    # 设置坐标范围，确保与其他图一致
    main_ax.set_xlim(geo_bounds[0], geo_bounds[2])
    main_ax.set_ylim(geo_bounds[1], geo_bounds[3])  # 标准地理坐标，南到北

    # 不绘制边界和原始数据点，保持插值图的纯净效果

    # 添加颜色条，调整位置和大小
    cbar = fig.colorbar(im, ax=main_ax, fraction=0.04, pad=0.02)
    cbar.set_label(indicator, fontsize=font_sizes["colorbar_label"])

    # 先设置字体样式
    cbar.ax.tick_params(labelsize=font_sizes["colorbar_tick"])

    # 根据colorbar模式决定显示方式
    if colorbar_mode == "qualitative":
        # 定性模式时，只显示"低"和"高"
        cbar.set_ticks([vmin, vmax])
        cbar.set_ticklabels(["低", "高"])

    # 添加网格线
    main_ax.grid(True, linestyle="--", alpha=0.3)

    # 移除图例（因为不显示数据点和边界）

    # 移除纵横比调整，保持与distribution图一致的显示效果

    # 保持与distribution图一致的坐标范围设置，确保底图完整显示
    # 移除之前错误的网格范围设置，保持卫星图的原始地理边界

    # 设置标题
    title = f"水质监测数据 - {indicator} (增强插值热力图)"
    if not all_points_outside:
        title += " - 卫星底图"
    main_ax.set_title(title, fontsize=font_sizes["title"], pad=30)

    # 保存图像
    if not all_points_outside:
        plt.savefig(save_path, dpi=dpi, bbox_inches=None, pad_inches=0)
    else:
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    logger.info(f"增强插值图已保存至: {save_path}")

    plt.clf()
    plt.cla()
    plt.close()

    return save_path, (grid_values, grid_lon, grid_lat)


# 创建纯净版插值图
def generate_clean_interpolation_map(
    data,
    indicator,
    save_path,
    grid_resolution=200,
    transparent_bg=True,
    output_format="png",
    satellite_info=None,
    kml_boundary_path=None,
    precomputed_interpolation=None,
):
    """生成纯净版插值热力图SVG，无装饰元素

    Args:
        data: 包含经纬度和指标值的数据框
        indicator: 要绘制的指标名称
        save_path: 保存路径（自动转换为.svg格式）
        grid_resolution: 网格分辨率（当无预计算数据时使用）
        transparent_bg: 是否使用透明背景
        output_format: 输出格式（固定为'svg'，保持兼容性）
        satellite_info: 卫星图像信息元组 (宽度, 高度, 图像对象)，用于保持尺寸一致
        kml_boundary_path: KML边界文件路径（可选）
        precomputed_interpolation: 预计算的插值结果 (grid_values, grid_lon, grid_lat)，如果提供则跳过插值计算
    """
    try:
        # 检查是否有预计算的插值结果
        if precomputed_interpolation is not None:
            # 使用预计算的插值结果，确保与generate_interpolation_indicator_map完全一致
            grid_values, grid_lon, grid_lat = precomputed_interpolation
            logger.info("使用预计算的插值结果，确保与主插值图完全一致")
        else:
            # 重新计算插值，使用与generate_interpolation_indicator_map完全相同的参数
            logger.info("重新计算插值（与主插值图使用相同参数）")

            # 准备数据
            prepared_data = data.copy()
            prepared_data["longitude"] = data["longitude"]
            prepared_data["latitude"] = data["latitude"]
            prepared_data[indicator] = data[indicator]

            # 决定使用的边界方法
            boundary_method = (
                "kml"
                if kml_boundary_path and os.path.exists(kml_boundary_path)
                else "alpha_shape"
            )

            # 执行增强插值 - 使用与generate_interpolation_indicator_map相同的参数
            grid_values, grid_lon, grid_lat, boundary_mask, boundary_points = (
                enhanced_interpolation_with_neighborhood(
                    prepared_data,
                    grid_resolution=300,  # 保留兼容性，但优先使用satellite_info
                    method="linear",
                    neighborhood_radius=3,
                    boundary_method=boundary_method,
                    indicator_col=indicator,
                    fixed_bounds=None,
                    kml_boundary_path=kml_boundary_path,
                    satellite_info=satellite_info,  # 新增：智能分辨率选择
                )
            )

        # 计算实际的经纬度范围
        lon_min, lon_max = grid_lon.min(), grid_lon.max()
        lat_min, lat_max = grid_lat.min(), grid_lat.max()

        # 计算原始数据范围，确保与interpolation图colorbar范围完全一致
        original_values = data[indicator].values
        vmin, vmax = np.min(original_values), np.max(original_values)
        logger.info(f"使用原始数据范围作为colorbar: [{vmin:.3f}, {vmax:.3f}]")

        # 确保保存路径为SVG格式
        if not save_path.lower().endswith(".svg"):
            save_path = save_path.replace(".png", ".svg")

        # 创建纯净图形，尺寸与其他图的卫星底图部分保持一致
        if satellite_info is not None:
            img_width, img_height, _ = satellite_info
            dpi = 100.0
            # 计算卫星底图的实际尺寸（其他图的axes区域是85% x 80%）
            satellite_fig_width = img_width / dpi
            satellite_fig_height = img_height / dpi
            # Clean图直接使用卫星图的宽高比，但保持合适的显示尺寸
            figsize = (satellite_fig_width * 0.85, satellite_fig_height * 0.8)
        else:
            # 如果没有卫星图信息，使用默认尺寸
            figsize = (10, 8)

        fig, ax = plt.subplots(figsize=figsize)

        # 设置透明背景
        if transparent_bg:
            fig.patch.set_alpha(0.0)  # 设置figure背景透明
            ax.patch.set_alpha(0.0)  # 设置axes背景透明

        # 使用imshow绘制热力图，使用与interpolation图相同的colorbar范围
        im = ax.imshow(
            grid_values,
            cmap="jet",
            aspect="auto",
            extent=[lon_min, lon_max, lat_min, lat_max],
            origin="lower",
            interpolation="bilinear",
            vmin=vmin,
            vmax=vmax,
        )

        # 移除所有装饰元素
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_title("")
        ax.axis("off")

        # 根据中心纬度调整纵横比
        mean_lat = (lat_min + lat_max) / 2
        ax.set_aspect(1 / np.cos(np.deg2rad(mean_lat)), adjustable="box")

        # 紧密布局，移除边距
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # SVG格式保存参数
        save_kwargs = {
            "format": "svg",
            "bbox_inches": "tight",
            "pad_inches": 0,
            "edgecolor": "none",
        }

        if transparent_bg:
            save_kwargs["facecolor"] = "none"  # 透明背景
            save_kwargs["transparent"] = True  # 启用透明度支持
        else:
            save_kwargs["facecolor"] = "white"  # 白色背景

        # 保存纯净图像
        plt.savefig(save_path, **save_kwargs)

        format_desc = f"{'透明' if transparent_bg else '白色'}背景的SVG"
        logger.info(f"纯净版插值图({format_desc})已保存至: {save_path}")

        plt.clf()
        plt.cla()
        plt.close()

        return save_path, grid_values

    except Exception as e:
        logger.error(f"生成纯净版插值图失败: {str(e)}")
        return None, None


# 创建单个散点图
def generate_distribution_indicator_map(
    data,
    indicator,
    satellite_info,
    save_path,
    satellite_geo_bounds,
    data_geo_bounds,
    all_points_outside,
    colorbar_mode="quantitative",
):
    """创建单个散点图

    Args:
        colorbar_mode: colorbar显示模式，"quantitative"(数值)或"qualitative"(高低)
    """
    logger.info(f"散点图 {indicator} - colorbar_mode参数: {colorbar_mode}")
    # 解包卫星数据信息
    img_width, img_height, img_obj = satellite_info

    # 计算自适应字体大小和布局参数
    font_sizes = calculate_adaptive_font_sizes(img_width, img_height)
    left, bottom, width, height, layout_info = calculate_dynamic_layout(
        img_width,
        img_height,
        has_right_element=True,
        font_size=font_sizes["global"],
        right_element_type="colorbar",
    )  # 散点图有colorbar
    layout_params = [left, bottom, width, height]

    # 重新设置字体参数确保生效
    plt.rcParams.update({"font.size": font_sizes["global"]})
    plt.rcParams["font.family"] = "SimHei"
    plt.rcParams["axes.unicode_minus"] = False

    # 默认点大小
    point_size = 20

    # 判断用白色底图还是卫星底图
    if all_points_outside:
        geo_bounds = data_geo_bounds
        img_width = 1200
        img_height = int(
            img_width
            * (geo_bounds[3] - geo_bounds[1])
            / (geo_bounds[2] - geo_bounds[0])
        )

        # 对于没有卫星图像的情况，使用更灵活的布局
        fig = plt.figure(figsize=(12, 8))
        main_ax = fig.add_subplot(111)

        # 添加空白背景
        main_ax.add_patch(
            plt.Rectangle(
                (geo_bounds[0], geo_bounds[1]),
                geo_bounds[2] - geo_bounds[0],
                geo_bounds[3] - geo_bounds[1],
                facecolor="lightgray",
            )
        )
    else:
        geo_bounds = satellite_geo_bounds
        # 固定的DPI值
        dpi = 100.0
        # 根据图像尺寸计算figsize (英寸)
        figsize = (img_width / dpi, img_height / dpi)

        # 创建figure
        fig = plt.figure(figsize=figsize, dpi=dpi, frameon=True)

        # 创建具有精确尺寸的主要轴，减少边距，增大图像区域
        main_ax = fig.add_axes(layout_params)

        # 显示卫星图像，使用正确的origin参数
        main_ax.imshow(
            img_obj,
            extent=[geo_bounds[0], geo_bounds[2], geo_bounds[1], geo_bounds[3]],
            aspect="auto",
            origin="upper",
        )  # 卫星图像使用origin='upper'

    # 设置坐标范围
    main_ax.set_xlim(geo_bounds[0], geo_bounds[2])
    main_ax.set_ylim(geo_bounds[1], geo_bounds[3])  # 标准地理坐标，南到北

    # 隐藏坐标轴信息
    setup_axis_labels_and_ticks(main_ax, font_sizes, layout_info)

    # 准备绘制数据点
    values = data[indicator].values
    norm = Normalize(vmin=min(values), vmax=max(values))

    # 根据数据点数量调整点大小，增大基础点大小
    adaptive_point_size = point_size * 10.0  # 将基础点大小显著增大
    if len(data) > 100:
        adaptive_point_size = max(
            60, int(point_size * 10.0 * 100 / len(data))
        )  # 确保最小点大小为60

    # 准备数据
    x = data["longitude"].values
    y = data["latitude"].values
    z = data[indicator].values

    mappable = main_ax.scatter(x, y, c=z, cmap="jet", s=adaptive_point_size, alpha=0.8)

    # 添加颜色条
    cbar = fig.colorbar(mappable, ax=main_ax, fraction=0.04, pad=0.02)
    cbar.set_label(indicator, fontsize=font_sizes["colorbar_label"])

    # 先设置字体样式
    cbar.ax.tick_params(labelsize=font_sizes["colorbar_tick"])

    # 根据colorbar模式决定显示方式
    logger.info(
        f"散点图 {indicator} - colorbar设置: colorbar_mode={colorbar_mode}"
    )
    if colorbar_mode == "qualitative":
        # 定性模式时，只显示"低"和"高"
        logger.info(f"散点图 {indicator} - 设置colorbar为'低'和'高'显示")
        cbar.set_ticks([norm.vmin, norm.vmax])
        cbar.set_ticklabels(["低", "高"])
    else:
        logger.info(f"散点图 {indicator} - 使用默认数值colorbar")

    title = f"水质监测数据 - {indicator} (散点图)"

    if not all_points_outside:
        title += " - 卫星底图"
    main_ax.set_title(title, fontsize=font_sizes["title"], pad=30)

    # 添加网格线
    main_ax.grid(True, linestyle="--", alpha=0.3)

    # 保存图像
    if not all_points_outside:
        # 保持原始分辨率，减少白边
        plt.savefig(save_path, dpi=dpi, bbox_inches=None, pad_inches=0)
    else:
        # 对于生成的图像优化布局
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight", pad_inches=0)

    # plt.savefig(save_path, dpi=300, bbox_inches='tight')

    logger.info(f"图像已保存至: {save_path}")

    plt.clf()  # 清除当前 figure 的内容（保持 figure 对象）
    plt.cla()  # 清除当前 axes 的内容（保持 axes 对象）
    plt.close()  # 关闭当前 figure，推荐用于循环中防止内存累积
    return save_path


def read_satellite(img_path):
    if os.path.exists(img_path):
        try:
            # 读取卫星图像
            satellite_img = Image.open(img_path)
            img_width, img_height = satellite_img.size
            # 读取原始图像
            original_img = mpimg.imread(img_path)[:, :, :3]

            return [img_width, img_height, original_img]
        except Exception as e:
            logger.error(f"读取或处理卫星图像失败: {str(e)},将使用空白背景绘制点...")
            return [None, None, None]
    else:
        logger.warning(f"找不到卫星图像 {img_path}，将使用空白背景")
        return [None, None, None]


def get_data_geo_bounds(data: pd.DataFrame) -> List[float]:
    """
    获取数据的地理边界坐标

    Args:
        data: 包含经纬度数据的DataFrame

    Returns:
        List[float]: 地理边界坐标 [min_lon, min_lat, max_lon, max_lat]
    """
    min_lon = data["longitude"].min()
    max_lon = data["longitude"].max()
    min_lat = data["latitude"].min()
    max_lat = data["latitude"].max()

    # 为边界添加一些余量
    lon_margin = (max_lon - min_lon) * 0.05
    lat_margin = (max_lat - min_lat) * 0.05

    geo_bounds = [
        min_lon - lon_margin,
        min_lat - lat_margin,
        max_lon + lon_margin,
        max_lat + lat_margin,
    ]

    logger.info(
        f"数据地理边界: 经度 {geo_bounds[0]} - {geo_bounds[2]}, 纬度 {geo_bounds[1]} - {geo_bounds[3]}"
    )

    return geo_bounds


def geo_to_image_coords(lat, lon, image_width, image_height, geo_bounds):
    """
    将经纬度坐标转换为图像坐标

    参数:
        lat, lon: 经纬度坐标
        image_width, image_height: 图像尺寸
        geo_bounds: 图像边界经纬度 [min_lon, min_lat, max_lon, max_lat]

    返回:
        x, y: 图像坐标
        is_inside: 是否在图像范围内
    """
    min_lon, min_lat, max_lon, max_lat = [
        geo_bounds[0],  # min_lon
        geo_bounds[1],  # min_lat
        geo_bounds[2],  # max_lon
        geo_bounds[3],  # max_lat
    ]

    # 检查点是否在地理边界内（添加小的容差来处理浮点数精度问题）
    tolerance = 1e-6  # 约0.1米的容差
    is_inside = (min_lon - tolerance <= lon <= max_lon + tolerance) and (
        min_lat - tolerance <= lat <= max_lat + tolerance
    )

    # 计算图像上的相对坐标
    x_ratio = (lon - min_lon) / (max_lon - min_lon) if max_lon > min_lon else 0.5
    y_ratio = (
        1.0 - (lat - min_lat) / (max_lat - min_lat) if max_lat > min_lat else 0.5
    )  # 图像文件第一行对应最北端

    # 转换为像素坐标
    x = int(x_ratio * image_width)
    y = int(y_ratio * image_height)

    return x, y, is_inside


def parse_geo_bounds(geo_bounds):
    """从配置中解析地理边界"""
    try:
        # 尝试从config中获取四个角的坐标
        # 获取坐标字符串
        ne = geo_bounds.get("north_east", "").split(",")
        sw = geo_bounds.get("south_west", "").split(",")
        se = geo_bounds.get("south_east", "").split(",")
        nw = geo_bounds.get("north_west", "").split(",")

        if len(ne) != 2 or len(sw) != 2 or len(se) != 2 or len(nw) != 2:
            logging.warning("地理坐标格式不正确，使用默认边界")
            return None

        # 转换为浮点数
        ne_lon, ne_lat = float(ne[0]), float(ne[1])
        sw_lon, sw_lat = float(sw[0]), float(sw[1])
        se_lon, se_lat = float(se[0]), float(se[1])
        nw_lon, nw_lat = float(nw[0]), float(nw[1])

        # 求最大最小经纬度范围
        min_lon = min(sw_lon, nw_lon)
        max_lon = max(ne_lon, se_lon)
        min_lat = min(sw_lat, se_lat)
        max_lat = max(ne_lat, nw_lat)

        return [min_lon, min_lat, max_lon, max_lat]
    except Exception as e:
        logging.error(f"解析地理边界失败: {str(e)}")
        return None


def generate_level_indicator_map(
    indicator,
    satellite_info,
    save_path,
    satellite_geo_bounds,
    data_geo_bounds,
    all_points_outside,
    Z,
    grid_lon=None,
    grid_lat=None,
):
    """
    根据二维指标值Z和分级标准，绘制水质等级分布图
    使用插值数据并应用国标分级标准
    """
    # 解包卫星数据信息
    img_width, img_height, img_obj = satellite_info

    # 计算自适应字体大小和布局参数
    font_sizes = calculate_adaptive_font_sizes(img_width, img_height)
    left, bottom, width, height, layout_info = calculate_dynamic_layout(
        img_width,
        img_height,
        has_right_element=True,
        font_size=font_sizes["global"],
        right_element_type="legend",
    )  # level图有图例
    layout_params = [left, bottom, width, height]

    # 重新设置字体参数确保生效
    plt.rcParams.update({"font.size": font_sizes["global"]})
    plt.rcParams["font.family"] = "SimHei"
    plt.rcParams["axes.unicode_minus"] = False
    # 检查是否支持该指标的国标分级
    grade_cfg = get_indicator_grade_config(indicator)
    if grade_cfg is None:
        logger.warning(f"未找到{indicator}的国标分级标准，跳过水质等级图生成")
        return "skip"

    if Z is None:
        logger.error(f"插值数据Z为空，无法生成{indicator}的等级图")
        return None

    # 获取分级配置
    grade_labels = grade_cfg["labels"]
    grade_thresholds = grade_cfg["thresholds"]
    grade_colors = grade_cfg["colors"]
    is_reverse = grade_cfg.get("reverse", False)

    # 创建插值数据的副本用于分级处理
    Z_processed = Z.copy()

    # 处理反向分级（如溶解氧，数值越高等级越好）
    if is_reverse:
        Z_processed = -Z_processed
        # 反转阈值、标签和颜色
        grade_thresholds = [-t for t in grade_thresholds[::-1]]
        grade_labels = grade_labels[::-1]
        grade_colors = grade_colors[::-1]

    # 执行分级
    grade_map = np.digitize(Z_processed, bins=grade_thresholds, right=True).astype(
        float
    )
    # digitize返回0~len(bins)，调整为1~len(bins)+1的类别编号
    grade_map = grade_map + 1

    # 保持NaN区域
    nan_mask = np.isnan(Z_processed)
    grade_map[nan_mask] = np.nan

    # 计算显示范围
    geo_bounds = data_geo_bounds if all_points_outside else satellite_geo_bounds

    # 创建图形
    if all_points_outside:
        fig = plt.figure(figsize=(12, 8))
        main_ax = fig.add_subplot(111)
        main_ax.add_patch(
            plt.Rectangle(
                (geo_bounds[0], geo_bounds[1]),
                geo_bounds[2] - geo_bounds[0],
                geo_bounds[3] - geo_bounds[1],
                facecolor="lightgray",
            )
        )
        dpi = 300
    else:
        dpi = 100.0
        figsize = (img_width / dpi, img_height / dpi)
        fig = plt.figure(figsize=figsize, dpi=dpi, frameon=True)
        main_ax = fig.add_axes(layout_params)

        # 显示卫星图像
        main_ax.imshow(
            img_obj,
            extent=[geo_bounds[0], geo_bounds[2], geo_bounds[1], geo_bounds[3]],
            aspect="auto",
            origin="upper",
        )  # 卫星图像使用origin='upper'

    # 设置坐标范围（保持数据正确显示）
    main_ax.set_xlim(geo_bounds[0], geo_bounds[2])
    main_ax.set_ylim(geo_bounds[1], geo_bounds[3])

    # 隐藏坐标轴信息
    setup_axis_labels_and_ticks(main_ax, font_sizes, layout_info)

    # 创建分级颜色图
    cmap = ListedColormap(grade_colors)
    bounds = list(range(1, len(grade_labels) + 2))
    norm = BoundaryNorm(bounds, cmap.N)

    # 绘制等级图，使用实际的网格坐标确保GPS对齐
    if grid_lon is not None and grid_lat is not None:
        # 使用插值网格的实际地理范围，确保GPS坐标对齐
        grid_lon_min, grid_lon_max = grid_lon.min(), grid_lon.max()
        grid_lat_min, grid_lat_max = grid_lat.min(), grid_lat.max()
        extent = [grid_lon_min, grid_lon_max, grid_lat_min, grid_lat_max]
    else:
        # 回退到使用地理边界
        extent = [geo_bounds[0], geo_bounds[2], geo_bounds[1], geo_bounds[3]]

    im = main_ax.imshow(
        grade_map,
        extent=extent,
        aspect="auto",
        origin="lower",
        cmap=cmap,
        norm=norm,
    )

    # 添加图例，模仿colorbar的样式和位置
    patches = [
        mpatches.Patch(color=grade_colors[i], label=grade_labels[i])
        for i in range(len(grade_labels))
    ]
    legend = main_ax.legend(
        handles=patches,
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        fontsize=font_sizes["legend"],
        frameon=True,
        fancybox=False,
        shadow=False,
        ncol=1,
        columnspacing=0.5,
        handlelength=1.5,
        handletextpad=0.5,
    )

    # 添加网格线
    main_ax.grid(True, linestyle="--", alpha=0.3)

    # 设置标题
    title = f"水质监测数据 - {indicator} (国标等级分布图)"
    if not all_points_outside:
        title += " - 卫星底图"
    main_ax.set_title(title, fontsize=font_sizes["title"], pad=30)

    # 保存图像
    if not all_points_outside:
        plt.savefig(save_path, dpi=dpi, bbox_inches=None, pad_inches=0)
    else:
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    logger.info(f"国标等级图已保存至: {save_path}")

    plt.clf()
    plt.cla()
    plt.close()

    return save_path
