"""
pytest配置文件
"""
import os
import sys
import pytest
import tempfile
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
def sample_config():
    """示例配置"""
    return {
        "domain": "water_quality",
        "data_root": "./test_output/",
        "company_info": {
            "name": "测试公司",
            "address": "测试地址",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "profile": "测试简介",
            "logo_path": "http://example.com/logo.png",
            "wayline_img": "http://example.com/wayline.jpg",
            "satellite_img": "http://example.com/satellite.jpg",
            "file_url": "http://example.com/data.zip",
            "measure_data": "http://example.com/measure.csv"
        },
        "domain_config": {
            "enabled_indicators": ["nh3n", "tp", "cod"],
            "quality_standards": "GB_3838_2002"
        }
    }

@pytest.fixture
def sample_data():
    """示例数据"""
    import pandas as pd
    return pd.DataFrame({
        'lat': [30.5, 30.6, 30.7],
        'lon': [120.1, 120.2, 120.3],
        'nh3n': [0.5, 0.8, 1.2],
        'tp': [0.02, 0.03, 0.05],
        'cod': [15, 20, 25]
    })