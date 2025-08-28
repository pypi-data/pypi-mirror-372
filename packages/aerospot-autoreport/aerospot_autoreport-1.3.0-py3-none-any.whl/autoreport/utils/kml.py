#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KML文件解析和区域提取工具模块

功能：
1. 解析KML文件中的几何图形
2. 提取多边形/折线的坐标信息
3. 转换为用于地图生成的边界掩码
"""

import os
import logging
from typing import List, Tuple, Optional, Union
import xml.etree.ElementTree as ET
import numpy as np
from matplotlib.path import Path

logger = logging.getLogger(__name__)


class KMLParser:
    """KML文件解析器"""
    
    def __init__(self, kml_path: str):
        """
        初始化KML解析器
        
        Args:
            kml_path: KML文件路径
        """
        self.kml_path = kml_path
        self.tree = None
        self.root = None
        self.namespaces = {
            'kml': 'http://www.opengis.net/kml/2.2',
            'gx': 'http://www.google.com/kml/ext/2.2'
        }
        
        self._parse_kml()
    
    def _parse_kml(self) -> None:
        """解析KML文件"""
        try:
            if not os.path.exists(self.kml_path):
                raise FileNotFoundError(f"KML文件不存在: {self.kml_path}")
            
            self.tree = ET.parse(self.kml_path)
            self.root = self.tree.getroot()
            
            logger.info(f"成功解析KML文件: {self.kml_path}")
            
        except ET.ParseError as e:
            logger.error(f"KML文件解析错误: {str(e)}")
            raise ValueError(f"KML文件格式错误: {str(e)}")
        except Exception as e:
            logger.error(f"解析KML文件时发生错误: {str(e)}")
            raise
    
    def extract_coordinates(self) -> List[List[Tuple[float, float]]]:
        """
        提取KML文件中的坐标信息
        
        Returns:
            List[List[Tuple[float, float]]]: 坐标点列表，每个元素是一个多边形的坐标列表
        """
        coordinate_sets = []
        
        # 查找所有的Polygon和LineString元素
        for coord_element in self.root.iter():
            if coord_element.tag.endswith('coordinates'):
                coordinates_text = coord_element.text
                if coordinates_text:
                    coords = self._parse_coordinates_text(coordinates_text)
                    if coords:
                        coordinate_sets.append(coords)
        
        if not coordinate_sets:
            logger.warning("KML文件中未找到有效的坐标信息")
        else:
            logger.info(f"从KML文件中提取到 {len(coordinate_sets)} 个几何图形的坐标")
        
        return coordinate_sets
    
    def _parse_coordinates_text(self, coordinates_text: str) -> List[Tuple[float, float]]:
        """
        解析坐标文本字符串
        
        Args:
            coordinates_text: 坐标文本，格式为 "lon1,lat1,alt1 lon2,lat2,alt2 ..."
            
        Returns:
            List[Tuple[float, float]]: 坐标点列表 [(lon, lat), ...]
        """
        coords = []
        try:
            # 清理文本，移除多余的空白字符
            coordinates_text = coordinates_text.strip()
            
            # 分割坐标点
            coord_points = coordinates_text.split()
            
            for point in coord_points:
                if point.strip():
                    # 每个点的格式为 "lon,lat,alt" 或 "lon,lat"
                    parts = point.split(',')
                    if len(parts) >= 2:
                        lon = float(parts[0])
                        lat = float(parts[1])
                        coords.append((lon, lat))
                        
        except (ValueError, IndexError) as e:
            logger.error(f"解析坐标文本时出错: {str(e)}")
            logger.debug(f"原始坐标文本: {coordinates_text}")
            
        return coords
    
    def get_bounding_box(self) -> Optional[Tuple[float, float, float, float]]:
        """
        获取KML文件中所有几何图形的边界框
        
        Returns:
            Optional[Tuple[float, float, float, float]]: 边界框 (min_lon, min_lat, max_lon, max_lat)
        """
        all_coordinates = self.extract_coordinates()
        
        if not all_coordinates:
            return None
        
        # 收集所有坐标点
        all_points = []
        for coord_set in all_coordinates:
            all_points.extend(coord_set)
        
        if not all_points:
            return None
        
        # 计算边界框
        lons = [point[0] for point in all_points]
        lats = [point[1] for point in all_points]
        
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)
        
        logger.info(f"KML边界框: 经度 {min_lon:.6f} - {max_lon:.6f}, 纬度 {min_lat:.6f} - {max_lat:.6f}")
        
        return (min_lon, min_lat, max_lon, max_lat)


def create_kml_boundary_mask(grid_lon: np.ndarray, grid_lat: np.ndarray, 
                           kml_path: str) -> np.ndarray:
    """
    基于KML文件创建边界掩码
    
    Args:
        grid_lon: 网格经度数组
        grid_lat: 网格纬度数组
        kml_path: KML文件路径
        
    Returns:
        np.ndarray: 布尔掩码数组，True表示在KML定义的区域内
    """
    try:
        # 解析KML文件
        kml_parser = KMLParser(kml_path)
        coordinate_sets = kml_parser.extract_coordinates()
        
        if not coordinate_sets:
            logger.warning("KML文件中未找到有效的坐标信息，使用全True掩码")
            return np.ones_like(grid_lon, dtype=bool)
        
        # 将网格坐标转换为点集
        points = np.column_stack((grid_lon.ravel(), grid_lat.ravel()))
        
        # 创建组合掩码
        combined_mask = np.zeros(len(points), dtype=bool)
        
        # 对每个几何图形创建掩码
        for i, coords in enumerate(coordinate_sets):
            if len(coords) >= 3:  # 至少需要3个点才能形成有效的多边形
                # 创建多边形路径
                polygon_path = Path(coords)
                
                # 检查每个网格点是否在多边形内
                mask = polygon_path.contains_points(points)
                
                # 使用并集合并掩码
                combined_mask |= mask
                
                logger.info(f"处理第 {i+1} 个几何图形，包含 {len(coords)} 个坐标点")
            else:
                logger.warning(f"第 {i+1} 个几何图形坐标点数量不足，跳过")
        
        # 重新塑形为网格形状
        boundary_mask = combined_mask.reshape(grid_lon.shape)
        
        # 统计掩码信息
        total_points = boundary_mask.size
        valid_points = np.sum(boundary_mask)
        logger.info(f"KML边界掩码创建完成，有效区域占比: {valid_points/total_points:.2%}")
        
        return boundary_mask
        
    except Exception as e:
        logger.error(f"创建KML边界掩码时发生错误: {str(e)}")
        logger.warning("回退到全True掩码")
        return np.ones_like(grid_lon, dtype=bool)


def get_kml_boundary_bounds(kml_path: str) -> Optional[Tuple[float, float, float, float]]:
    """
    获取KML文件定义的边界范围
    
    Args:
        kml_path: KML文件路径
        
    Returns:
        Optional[Tuple[float, float, float, float]]: 边界范围 (min_lon, min_lat, max_lon, max_lat)
    """
    try:
        kml_parser = KMLParser(kml_path)
        return kml_parser.get_bounding_box()
    except Exception as e:
        logger.error(f"获取KML边界范围时发生错误: {str(e)}")
        return None


def get_kml_boundary_points(kml_path: str) -> Optional[np.ndarray]:
    """
    获取KML文件定义的边界点数组，返回与alpha_shape相同格式的numpy数组
    
    Args:
        kml_path: KML文件路径
        
    Returns:
        Optional[np.ndarray]: 边界点坐标数组，形状为(n, 2)，与alpha_shape返回值格式相同
    """
    try:
        kml_parser = KMLParser(kml_path)
        coordinate_sets = kml_parser.extract_coordinates()
        
        if not coordinate_sets:
            logger.warning("KML文件中未找到有效的坐标信息")
            return None
        
        # 选择包含最多点数的几何图形作为边界（通常是主要的多边形）
        max_points_index = 0
        max_points_count = len(coordinate_sets[0])
        
        for i, coords in enumerate(coordinate_sets):
            if len(coords) > max_points_count:
                max_points_count = len(coords)
                max_points_index = i
        
        if max_points_count < 3:
            logger.warning(f"KML文件中的几何图形点数不足以构成有效边界（最多只有{max_points_count}个点）")
            return None
        
        boundary_points = np.array(coordinate_sets[max_points_index])
        logger.info(f"从KML文件第{max_points_index}个几何图形获取到 {len(boundary_points)} 个边界点")
        
        return boundary_points
        
    except Exception as e:
        logger.error(f"获取KML边界点时发生错误: {str(e)}")
        return None


def validate_kml_file(kml_path: str) -> bool:
    """
    验证KML文件是否有效
    
    Args:
        kml_path: KML文件路径
        
    Returns:
        bool: 是否为有效的KML文件
    """
    try:
        kml_parser = KMLParser(kml_path)
        coordinate_sets = kml_parser.extract_coordinates()
        
        # 检查是否有有效的坐标信息
        if not coordinate_sets:
            logger.warning("KML文件中未找到有效的坐标信息")
            return False
        
        # 检查坐标的合理性
        for coord_set in coordinate_sets:
            for lon, lat in coord_set:
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    logger.warning(f"发现无效的坐标: 经度={lon}, 纬度={lat}")
                    return False
        
        logger.info("KML文件验证通过")
        return True
        
    except Exception as e:
        logger.error(f"验证KML文件时发生错误: {str(e)}")
        return False


# 为了向后兼容，保留旧的函数名
def parse_kml_boundary(kml_path: str) -> Optional[List[Tuple[float, float]]]:
    """
    解析KML文件中的边界信息（向后兼容函数）
    
    Args:
        kml_path: KML文件路径
        
    Returns:
        Optional[List[Tuple[float, float]]]: 边界坐标点列表
    """
    try:
        kml_parser = KMLParser(kml_path)
        coordinate_sets = kml_parser.extract_coordinates()
        
        if coordinate_sets:
            # 返回第一个几何图形的坐标
            return coordinate_sets[0]
        
        return None
        
    except Exception as e:
        logger.error(f"解析KML边界时发生错误: {str(e)}")
        return None