"""
水质监测领域的地图配置
包含国标分级、颜色方案等水质专用配置
"""

# 国标分级映射表（GB 3838-2002）
WATER_QUALITY_INDICATOR_CONFIGS = {
    # COD（化学需氧量，mg/L）
    'cod': {
        'thresholds': [15, 20, 30, 40],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000'],
        'unit': 'mg/L',
        'display_name': '化学需氧量',
        'description': '反映水体有机污染程度'
    },
    # 氨氮 NH3-N（mg/L）
    'nh3n': {
        'thresholds': [0.15, 0.5, 1.0, 1.5],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000'],
        'unit': 'mg/L',
        'display_name': '氨氮',
        'description': '反映水体氮污染程度'
    },
    # 总磷 TP（mg/L）
    'tp': {
        'thresholds': [0.02, 0.1, 0.2, 0.3],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000'],
        'unit': 'mg/L',
        'display_name': '总磷',
        'description': '反映水体磷污染程度'
    },
    # 总氮 TN（mg/L）
    'tn': {
        'thresholds': [0.2, 0.5, 1.0, 1.5],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000'],
        'unit': 'mg/L',
        'display_name': '总氮',
        'description': '反映水体氮污染程度'
    },
    # 溶解氧 DO（mg/L，越高越好，分级反向）
    'do': {
        'thresholds': [2, 3, 5, 6],  # Ⅴ~Ⅱ类
        'labels': ['Ⅴ类', 'Ⅳ类', 'Ⅲ类', 'Ⅱ类', 'Ⅰ类'],
        'colors': ['#FF0000', '#FFA500', '#FFFF00', '#00FF7F', '#1E90FF'],
        'reverse': True,
        'unit': 'mg/L',
        'display_name': '溶解氧',
        'description': '反映水体氧气含量'
    },
    # pH
    'ph': {
        'thresholds': [6, 6.5, 8.5, 9],
        'labels': ['Ⅴ类', 'Ⅳ类', 'Ⅲ类', 'Ⅱ类', 'Ⅰ类'],
        'colors': ['#FF0000', '#FFA500', '#FFFF00', '#00FF7F', '#1E90FF'],
        'reverse': True,
        'unit': '',
        'display_name': 'pH值',
        'description': '反映水体酸碱度'
    },
    # 浊度（NTU）
    'turbidity': {
        'thresholds': [1, 3, 10, 20],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000'],
        'unit': 'NTU',
        'display_name': '浊度',
        'description': '反映水体透明度'
    },
    # 叶绿素a（μg/L）
    'chla': {
        'thresholds': [1, 5, 10, 20],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000'],
        'unit': 'μg/L',
        'display_name': '叶绿素a',
        'description': '反映水体富营养化程度'
    },
}

# 水质专用图表配置
WATER_QUALITY_MAP_SETTINGS = {
    'default_colormap': 'jet',
    'boundary_method': 'alpha_shape',
    'grid_resolution': 300,
    'alpha_transparency': 0.8,
    'point_size_base': 60,
    'title_template': '水质监测数据 - {indicator}',
    'supported_map_types': ['distribution', 'interpolation', 'clean_interpolation_png', 'clean_interpolation_svg', 'level']
}

def get_water_quality_indicator_config(indicator: str) -> dict:
    """获取水质指标配置"""
    return WATER_QUALITY_INDICATOR_CONFIGS.get(indicator.lower())

def get_water_quality_map_settings() -> dict:
    """获取水质地图设置"""
    return WATER_QUALITY_MAP_SETTINGS.copy()

def get_supported_indicators() -> list:
    """获取支持的水质指标列表"""
    return list(WATER_QUALITY_INDICATOR_CONFIGS.keys())

def is_water_quality_indicator_supported(indicator: str) -> bool:
    """检查指标是否支持国标分级"""
    return indicator.lower() in WATER_QUALITY_INDICATOR_CONFIGS