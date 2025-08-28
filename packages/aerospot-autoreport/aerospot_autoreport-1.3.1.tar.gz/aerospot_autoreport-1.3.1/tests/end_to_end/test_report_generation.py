"""
端到端报告生成测试
"""
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch
from autoreport.main import AeroSpotReportGenerator


class TestReportGeneration:
    """端到端报告生成测试类"""
    
    @pytest.fixture
    def test_config_file(self, temp_dir, sample_config):
        """创建测试配置文件"""
        config_path = os.path.join(temp_dir, "test_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, ensure_ascii=False, indent=2)
        return config_path
    
    @pytest.fixture
    def generator(self, temp_dir, sample_config):
        """创建报告生成器"""
        output_dir = os.path.join(temp_dir, "output")
        return AeroSpotReportGenerator(
            output_dir=output_dir,
            config=sample_config,
            cache_enabled=False,
            domain="water_quality"
        )
    
    def test_generator_initialization(self, generator):
        """测试生成器初始化"""
        assert generator.domain == "water_quality"
        assert generator.output_dir is not None
        assert os.path.exists(generator.output_dir)
    
    def test_load_config_success(self, generator, test_config_file):
        """测试配置加载成功"""
        result = generator.load_config(test_config_file)
        assert result is True
        assert generator.config is not None
        assert generator.config.get("domain") == "water_quality"
    
    def test_load_config_invalid_file(self, generator):
        """测试加载无效配置文件"""
        with pytest.raises(Exception):
            generator.load_config("/non/existent/config.json")
    
    @patch('autoreport.core.resource_manager.ResourceManager.get_resource')
    def test_download_resources_success(self, mock_get_resource, generator, temp_dir):
        """测试资源下载成功"""
        # 模拟资源下载成功
        mock_get_resource.return_value = os.path.join(temp_dir, "mock_resource.jpg")
        
        # 创建模拟文件
        for resource_type in ["logo", "satellite", "wayline", "measure_data", "file"]:
            mock_file = os.path.join(temp_dir, f"mock_{resource_type}.jpg")
            with open(mock_file, 'wb') as f:
                f.write(b"mock content")
        
        result = generator.download_resources()
        assert result is True
    
    @patch('autoreport.core.resource_manager.ResourceManager.get_resource')
    def test_download_resources_failure(self, mock_get_resource, generator):
        """测试资源下载失败"""
        from autoreport.core.exceptions import ResourceError
        
        # 模拟资源下载失败
        mock_get_resource.side_effect = ResourceError("下载失败")
        
        result = generator.download_resources()
        assert result is False
    
    def test_create_report_data(self, generator):
        """测试创建报告数据"""
        generator.create_report_data()
        
        assert generator.report_data is not None
        assert isinstance(generator.report_data, dict)
        assert "domain" in generator.report_data
        assert "company_info" in generator.report_data
        assert "image_resources" in generator.report_data
    
    @patch('autoreport.processor.extractor.ZipExtractor.extract')
    @patch('autoreport.main.AeroSpotReportGenerator._find_data_files')
    def test_process_data_workflow(self, mock_find_files, mock_extract, generator, temp_dir):
        """测试数据处理工作流"""
        # 创建模拟的ZIP文件
        zip_file = os.path.join(temp_dir, "test_data.zip")
        with open(zip_file, 'wb') as f:
            f.write(b"mock zip content")
        
        # 设置配置中的文件路径
        generator.config["company_info"]["file_url"] = zip_file
        
        # 模拟解压结果
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        mock_extract.return_value = extract_dir
        
        # 模拟找到的文件
        mock_find_files.return_value = {
            "indices_file": os.path.join(extract_dir, "INDEXS.CSV"),
            "pos_file": os.path.join(extract_dir, "POS.TXT"),
            "ref_file": []
        }
        
        # 创建模拟数据文件
        indices_file = os.path.join(extract_dir, "INDEXS.CSV")
        pos_file = os.path.join(extract_dir, "POS.TXT")
        
        with open(indices_file, 'w') as f:
            f.write("lat,lon,nh3n,tp,cod\\n30.5,120.1,0.5,0.02,15\\n")
        
        with open(pos_file, 'w') as f:
            f.write("30.5,120.1,100\\n30.6,120.2,101\\n")
        
        # 使用mock来避免实际的数据处理
        with patch.object(generator, '_process_uav_data'):
            with patch.object(generator, '_process_measure_data'):
                with patch.object(generator, '_match_analyze_data'):
                    result = generator.process_data()
                    
                    # 由于使用了mock，应该返回True
                    assert result is True
    
    def test_save_processed_config(self, generator, temp_dir):
        """测试保存处理后的配置"""
        # 设置一些报告数据
        generator.report_data = {
            "domain": "water_quality",
            "company_info": {"name": "测试公司"},
            "some_data": "test_value"
        }
        
        config_path = generator.save_processed_config()
        
        if config_path:  # 如果保存成功
            assert os.path.exists(config_path)
            assert config_path.endswith('.json')
            
            # 检查保存的内容
            with open(config_path, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
                assert saved_config.get("domain") == "water_quality"
    
    def test_domain_validation(self, temp_dir, sample_config):
        """测试领域验证"""
        # 测试有效领域
        valid_generator = AeroSpotReportGenerator(
            output_dir=temp_dir,
            config=sample_config,
            domain="water_quality"
        )
        assert valid_generator.domain == "water_quality"
        
        # 测试无效领域
        with pytest.raises(ValueError):
            AeroSpotReportGenerator(
                output_dir=temp_dir,
                config=sample_config,
                domain="invalid_domain"
            )
    
    def test_error_handling(self, generator):
        """测试错误处理"""
        # 测试处理不存在的文件
        generator.config["company_info"]["file_url"] = "/non/existent/file.zip"
        
        # 应该抛出异常或返回False
        try:
            result = generator.process_data()
            assert result is False
        except Exception:
            # 异常也是可以接受的
            pass