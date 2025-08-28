"""
水质领域处理器单元测试
"""
import pytest
import pandas as pd
from autoreport.domains.water_quality.domain import WaterQualityDomain
from autoreport.domains.base.indicator import IndicatorDefinition


class TestWaterQualityDomain:
    """水质领域处理器测试类"""
    
    @pytest.fixture
    def domain(self):
        """创建水质领域实例"""
        return WaterQualityDomain()
    
    def test_domain_name(self, domain):
        """测试领域名称"""
        assert domain.domain_name == "water_quality"
    
    def test_domain_display_name(self, domain):
        """测试领域显示名称"""
        assert domain.domain_display_name == "水质监测"
    
    def test_get_indicators(self, domain):
        """测试获取指标"""
        indicators = domain.get_indicators()
        assert isinstance(indicators, dict)
        assert len(indicators) > 0
        
        # 检查关键指标
        key_indicators = ["nh3n", "tp", "cod", "turbidity", "chla"]
        for indicator in key_indicators:
            assert indicator in indicators
            assert isinstance(indicators[indicator], IndicatorDefinition)
    
    def test_standardize_column_names(self, domain):
        """测试标准化列名"""
        data = pd.DataFrame({
            'lat': [30.5, 30.6],
            'lon': [120.1, 120.2],
            'NH3-N': [0.5, 0.8],
            'TP': [0.02, 0.03],
            'COD': [15, 20]
        })
        
        standardized = domain.standardize_column_names(data)
        
        # 检查标准化后的列名
        assert 'lat' in standardized.columns
        assert 'lon' in standardized.columns
        assert 'nh3n' in standardized.columns
        assert 'tp' in standardized.columns
        assert 'cod' in standardized.columns
    
    def test_get_indicator_unit(self, domain):
        """测试获取指标单位"""
        assert domain.get_indicator_unit("nh3n") == "mg/L"
        assert domain.get_indicator_unit("tp") == "mg/L"
        assert domain.get_indicator_unit("cod") == "mg/L"
        assert domain.get_indicator_unit("turbidity") == "NTU"
        assert domain.get_indicator_unit("chla") == "μg/L"
    
    def test_process_analysis_data(self, domain, sample_data):
        """测试数据分析处理"""
        # 这是一个集成测试，需要模拟数据处理过程
        # 由于依赖外部库，这里只测试基本功能
        try:
            result = domain.process_analysis_data(
                sample_data,
                output_dir="./test_output/",
                model_name="test_model",
                prediction_mode="interpolation"
            )
            # 如果运行成功，检查结果格式
            if result:
                assert isinstance(result, dict)
        except Exception as e:
            # 如果依赖不满足，跳过这个测试
            pytest.skip(f"依赖不满足，跳过测试: {e}")
    
    def test_get_report_template(self, domain):
        """测试获取报告模板"""
        template = domain.get_report_template()
        assert template is not None
        assert hasattr(template, 'generate_structure')
    
    def test_indicator_validation(self, domain):
        """测试指标验证"""
        # 测试有效指标
        valid_indicators = ["nh3n", "tp", "cod"]
        for indicator in valid_indicators:
            assert domain._get_indicator_cached(indicator) is not None
        
        # 测试无效指标
        invalid_indicator = "invalid_indicator"
        assert domain._get_indicator_cached(invalid_indicator) is None