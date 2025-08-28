"""
地理工具模块
提供地理坐标处理功能
"""
import math
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def validate_coordinates(lat: float, lon: float) -> None:
    """
    验证坐标有效性
    
    Args:
        lat: 纬度
        lon: 经度
        
    Raises:
        ValueError: 坐标无效时抛出异常
    """
    if not math.isfinite(lat):
        raise ValueError(f"纬度值无效: {lat}")
    if not math.isfinite(lon):
        raise ValueError(f"经度值无效: {lon}")
    if not (-90 <= lat <= 90):
        raise ValueError(f"纬度必须在-90到90度之间，当前值: {lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"经度必须在-180到180度之间，当前值: {lon}")


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    使用 Haversine 公式计算两个坐标点之间的距离
    
    Args:
        lat1: 第一个点的纬度
        lon1: 第一个点的经度
        lat2: 第二个点的纬度
        lon2: 第二个点的经度
        
    Returns:
        两点之间的距离（单位：米）
        
    Raises:
        ValueError: 坐标值无效时抛出异常
    """
    # 验证输入坐标
    validate_coordinates(lat1, lon1)
    validate_coordinates(lat2, lon2)
    
    # 地球半径（米），使用更精确的WGS84椭球体平均半径
    R = 6371008.8
    
    # 将经纬度转换为弧度
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # 数值稳定的Haversine计算
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    
    # 确保a在[0,1]范围内，避免浮点误差
    a = max(0.0, min(1.0, a))
    
    # 数值稳定的反三角函数计算
    if a < 1e-10:  # 距离很小时使用线性近似
        c = 2 * math.sqrt(a)
    else:
        # 使用数值稳定的atan2
        sqrt_a = math.sqrt(a)
        sqrt_1_minus_a = math.sqrt(1 - a)
        c = 2 * math.atan2(sqrt_a, sqrt_1_minus_a)
    
    distance = R * c
    
    # 确保返回值为非负数
    return max(0.0, distance)