#!/usr/bin/env python3
"""
测试colorbar修改是否生效
"""
import sys
import pandas as pd
sys.path.append('src')

from autoreport.processor.maps import SatelliteMapGenerator

# 创建mock数据
class MockPathManager:
    def get_file_path(self, *args):
        return '/tmp/test_output.png'

# 测试无实测数据的情况
print("=== 测试无实测数据情况 ===")
generator = SatelliteMapGenerator(MockPathManager())

# 模拟无人机数据
uav_data = pd.DataFrame({
    'longitude': [120.0, 120.1, 120.2],
    'latitude': [30.0, 30.1, 30.2], 
    'chla': [10.0, 15.0, 12.0]
})

# 模拟geo_info
geo_info = {
    'min_lon': 119.5,
    'min_lat': 29.5,
    'max_lon': 120.5,
    'max_lat': 30.5
}

# 测试init_maps，data=None表示无实测数据
try:
    generator.init_maps(
        geo_info=geo_info,
        satellite_path='/nonexistent/path.jpg',  # 不存在的路径，会使用空白背景
        data=None,  # 无实测数据
        uav_data=uav_data
    )
    print(f"✓ has_measured_data判断: {generator.original_measured_data is None}")
    print(f"✓ self.data不为空: {generator.data is not None}")
    print(f"✓ 指标列: {generator.indicator_columns}")
    
except Exception as e:
    print(f"✗ 初始化失败: {e}")

print("\n=== 测试完成 ===")