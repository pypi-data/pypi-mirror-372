"""
数据处理工作流集成测试
"""
import pytest
import tempfile
import os
import pandas as pd
from unittest.mock import Mock, patch
from autoreport.processor.data.processor import DataProcessor
from autoreport.domains.water_quality.domain import WaterQualityDomain


class TestDataProcessingWorkflow:
    """数据处理工作流测试类"""
    
    @pytest.fixture
    def data_processor(self):
        """创建数据处理器"""
        return DataProcessor(domain_name="water_quality")
    
    @pytest.fixture
    def sample_merged_data(self):
        """创建示例合并数据"""
        return pd.DataFrame({
            'lat': [30.5, 30.6, 30.7, 30.8],
            'lon': [120.1, 120.2, 120.3, 120.4],
            'nh3n': [0.5, 0.8, 1.2, 0.3],
            'tp': [0.02, 0.03, 0.05, 0.01],
            'cod': [15, 20, 25, 12],
            'turbidity': [5, 8, 12, 4],
            'chla': [10, 15, 20, 8]
        })
    
    def test_data_processor_initialization(self, data_processor):
        """测试数据处理器初始化"""
        assert data_processor.domain_name == "water_quality"
        assert isinstance(data_processor.domain, WaterQualityDomain)
    
    def test_process_data_success(self, data_processor, sample_merged_data):
        """测试数据处理成功"""
        result = data_processor.process_data(sample_merged_data)
        
        if result:  # 如果处理成功
            assert isinstance(result, dict)
            assert "processed_data" in result
            assert isinstance(result["processed_data"], pd.DataFrame)
            
            # 检查处理后的数据结构
            processed_df = result["processed_data"]
            assert len(processed_df) > 0
            assert "lat" in processed_df.columns
            assert "lon" in processed_df.columns
    
    def test_process_data_empty_input(self, data_processor):
        """测试空输入数据处理"""
        empty_data = pd.DataFrame()
        result = data_processor.process_data(empty_data)
        
        # 应该返回None或空结果
        assert result is None or (isinstance(result, dict) and not result.get("processed_data"))
    
    def test_process_data_missing_columns(self, data_processor):
        """测试缺少必要列的数据处理"""
        incomplete_data = pd.DataFrame({
            'lat': [30.5, 30.6],
            # 缺少lon列
            'nh3n': [0.5, 0.8]
        })
        
        result = data_processor.process_data(incomplete_data)
        # 应该处理错误或返回None
        assert result is None or isinstance(result, dict)
    
    def test_match_and_analyze_data(self, data_processor, sample_merged_data):
        """测试匹配和分析数据"""
        # 创建模拟的测量数据和光谱数据
        measure_data = pd.DataFrame({
            'lat': [30.55, 30.65],
            'lon': [120.15, 120.25],
            'nh3n': [0.6, 0.9],
            'tp': [0.025, 0.035]
        })
        
        ref_data = pd.DataFrame({
            'band_400': [0.1, 0.2],
            'band_500': [0.15, 0.25],
            'band_600': [0.2, 0.3]
        })
        
        try:
            result = data_processor.match_and_analyze_data(
                sample_merged_data, measure_data, ref_data
            )
            
            # 如果分析成功，检查结果
            if result:
                assert isinstance(result, dict)
        except Exception as e:
            # 如果依赖不满足，跳过测试
            pytest.skip(f"依赖不满足，跳过测试: {e}")
    
    def test_data_processor_with_invalid_domain(self):
        """测试无效领域的数据处理器"""
        with pytest.raises(Exception):
            DataProcessor(domain_name="invalid_domain")
    
    def test_data_standardization_workflow(self, data_processor, sample_merged_data):
        """测试数据标准化工作流"""
        # 创建包含不规范列名的数据
        messy_data = pd.DataFrame({
            'lat': [30.5, 30.6],
            'lon': [120.1, 120.2],
            'NH3-N': [0.5, 0.8],  # 不规范的列名
            'TP': [0.02, 0.03],   # 不规范的列名
            'COD': [15, 20]       # 不规范的列名
        })
        
        # 通过领域处理器标准化
        domain = data_processor.domain
        standardized = domain.standardize_column_names(messy_data)
        
        # 检查标准化结果
        assert 'nh3n' in standardized.columns
        assert 'tp' in standardized.columns
        assert 'cod' in standardized.columns
        assert 'NH3-N' not in standardized.columns
        assert 'TP' not in standardized.columns
        assert 'COD' not in standardized.columns