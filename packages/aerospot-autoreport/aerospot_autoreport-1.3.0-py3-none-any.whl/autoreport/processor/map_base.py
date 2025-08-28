"""
通用地图绘制基础设施
提供所有领域共用的绘图功能和工具
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from PIL import Image
import matplotlib.image as mpimg
from datetime import datetime
import cv2
from scipy.interpolate import RBFInterpolator, griddata
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches
from scipy.spatial import ConvexHull, Delaunay
from scipy.ndimage import gaussian_filter
from matplotlib.path import Path

# 设置matplotlib参数
plt.rcParams.update({'font.size': 48})
plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)


def calculate_dynamic_layout(img_width, img_height, has_right_element=False, font_size=48, right_element_type='colorbar'):
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
    layout_info = {'hide_axis': True}
    
    # 根据长宽比调整布局 - 确保标题和右侧元素不超出范围，有右侧元素时保持对称留白
    if has_right_element:
        # 根据右侧元素类型确定空间分配
        if right_element_type == 'colorbar':
            # colorbar占用空间较小，减少右侧预留空间
            colorbar_space_factor = 0.5  # 减少50%的右侧空间
        else:  # legend
            # legend占用空间较大，保持原有空间
            colorbar_space_factor = 1.0
        
        # 有右侧元素时，确保左右留白对称
        if aspect_ratio > 2.0:  # 极窄长图像
            left = 0.03
            right_margin = 0.03  # 右侧留白与左侧相同
            right_element_width = 0.15 * colorbar_space_factor  # 右侧元素（图例/colorbar）占用宽度
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
        'global': int(base_font_size * size_factor),
        'title': int(base_font_size * size_factor * 0.9),  # 减小标题字体
        'axis_label': int(base_font_size * size_factor),
        'tick_label': int(base_font_size * size_factor * 0.85),
        'colorbar_label': int(base_font_size * size_factor),
        'colorbar_tick': int(base_font_size * size_factor * 0.85),
        'legend': int(base_font_size * size_factor * 0.75)  # 也减小图例字体
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
    main_ax.set_xlabel('')
    main_ax.set_ylabel('')
    
    # 隐藏刻度标签
    main_ax.tick_params(axis='both', which='major', 
                       labelleft=False, labelbottom=False,
                       left=False, bottom=False, 
                       top=False, right=False)


def read_satellite(img_path):
    """读取卫星图像"""
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
    min_lon = data['longitude'].min()
    max_lon = data['longitude'].max()
    min_lat = data['latitude'].min()
    max_lat = data['latitude'].max()
    
    # 为边界添加一些余量
    lon_margin = (max_lon - min_lon) * 0.05
    lat_margin = (max_lat - min_lat) * 0.05
    
    geo_bounds = [
        min_lon - lon_margin,
        min_lat - lat_margin,
        max_lon + lon_margin,
        max_lat + lat_margin
    ]
    
    logger.info(f"数据地理边界: 经度 {geo_bounds[0]} - {geo_bounds[2]}, 纬度 {geo_bounds[1]} - {geo_bounds[3]}")
    
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
        geo_bounds[3]   # max_lat
    ]
    
    # 检查点是否在地理边界内（添加小的容差来处理浮点数精度问题）
    tolerance = 1e-6  # 约0.1米的容差
    is_inside = (min_lon - tolerance <= lon <= max_lon + tolerance) and (min_lat - tolerance <= lat <= max_lat + tolerance)
    
    # 计算图像上的相对坐标
    x_ratio = (lon - min_lon) / (max_lon - min_lon) if max_lon > min_lon else 0.5
    y_ratio = 1.0 - (lat - min_lat) / (max_lat - min_lat) if max_lat > min_lat else 0.5  # 图像文件第一行对应最北端
    
    # 转换为像素坐标
    x = int(x_ratio * image_width)
    y = int(y_ratio * image_height)
    
    return x, y, is_inside


def parse_geo_bounds(geo_bounds):
    """从配置中解析地理边界"""
    try:
        # 尝试从config中获取四个角的坐标
        # 获取坐标字符串
        ne = geo_bounds.get('north_east', '').split(',')
        sw = geo_bounds.get('south_west', '').split(',')
        se = geo_bounds.get('south_east', '').split(',')
        nw = geo_bounds.get('north_west', '').split(',')
        
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


# 边界检测算法
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
            for j in range(i+1, len(points)):
                dist = np.sqrt(np.sum((points[i] - points[j])**2))
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
        min_area_threshold = np.finfo(float).eps * 100 * max_edge ** 2
        
        if area > min_area_threshold:
            circumradius = (a * b * c) / (4 * area)
            
            # 检查circumradius是否有效
            if np.isfinite(circumradius) and circumradius < alpha:
                for i in range(3):
                    edge = (simplex[i], simplex[(i+1) % 3])
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


def enhanced_interpolation_with_neighborhood(all_data, grid_resolution=200, method='linear', 
                                           neighborhood_radius=2, boundary_method='alpha_shape', indicator_col=None, 
                                           fixed_bounds=None):
    """
    基于智能边界的高分辨率插值，包含邻域分析
    all_data: 包含所有文件数据的DataFrame
    grid_resolution: 网格分辨率
    method: 插值方法
    neighborhood_radius: 邻域分析半径(像素)
    boundary_method: 边界检测方法 ('alpha_shape')
    indicator_col: 指标列名，如果为None则使用第一个非坐标列
    fixed_bounds: 固定的地理边界范围 [min_lon, min_lat, max_lon, max_lat]，如果提供则使用此范围而不是数据边界
    返回: 插值结果、网格坐标、边界掩码、边界点
    """
    # 提取坐标和数值 - 适配maps.py的数据格式
    if 'longitude' in all_data.columns and 'latitude' in all_data.columns:
        points = all_data[['longitude', 'latitude']].values
    else:
        points = all_data[['lon', 'lat']].values
    
    # 获取指标列
    if indicator_col is not None:
        if indicator_col not in all_data.columns:
            raise ValueError(f"指定的指标列 {indicator_col} 不存在")
        values = all_data[indicator_col].values
    else:
        # 获取指标列（排除坐标列）
        coord_cols = ['longitude', 'latitude', 'lon', 'lat', 'index']
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
        if boundary_method == 'alpha_shape':
            boundary_points = compute_alpha_shape(points)
        else:  # 默认使用凸包
            boundary_points = compute_convex_hull(points)
    else:
        # 根据选择的方法计算边界（原有逻辑）
        if boundary_method == 'alpha_shape':
            boundary_points = compute_alpha_shape(points)
            # 确定经纬度范围（基于Alpha Shape）
            lon_min, lon_max = boundary_points[:, 0].min(), boundary_points[:, 0].max()
            lat_min, lat_max = boundary_points[:, 1].min(), boundary_points[:, 1].max()
        else:  # 默认使用凸包
            boundary_points = compute_convex_hull(points)
            lon_min, lon_max = boundary_points[:, 0].min(), boundary_points[:, 0].max()
            lat_min, lat_max = boundary_points[:, 1].min(), boundary_points[:, 1].max()
        
        # 只在使用数据边界时才添加边界扩展
        lon_range = lon_max - lon_min
        lat_range = lat_max - lat_min
        margin_factor = 0.01  # 减少到1%边界扩展，避免边缘效应
        
        lon_min -= lon_range * margin_factor
        lon_max += lon_range * margin_factor
        lat_min -= lat_range * margin_factor
        lat_max += lat_range * margin_factor
    
    # 创建高分辨率插值网格
    grid_lat, grid_lon = np.mgrid[lat_min:lat_max:grid_resolution*1j, 
                                 lon_min:lon_max:grid_resolution*1j]
    
    # 执行插值
    grid_values = griddata(points, values, (grid_lon, grid_lat), method=method)
    
    # 创建边界掩码
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
            indices = distance_transform_edt(nan_mask, return_distances=False, return_indices=True)
            temp_values[nan_mask] = temp_values[tuple(indices[:, nan_mask])]
        
        # 应用高斯滤波
        smoothed_values = gaussian_filter(temp_values, sigma=neighborhood_radius)
        
        # 应用掩码，只保留边界内的平滑结果
        grid_values[valid_mask] = smoothed_values[valid_mask]
    
    return grid_values, grid_lon, grid_lat, boundary_mask, boundary_points