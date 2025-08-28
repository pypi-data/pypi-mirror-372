"""
配置验证器单元测试
"""
import pytest
from autoreport.core.config_validator import ConfigValidator
from autoreport.core.exceptions import ConfigValidationError


class TestConfigValidator:
    """配置验证器测试类"""
    
    def test_validate_config_success(self, sample_config):
        """测试配置验证成功"""
        is_valid, errors = ConfigValidator.validate_config(sample_config)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_config_missing_company_info(self):
        """测试缺少公司信息"""
        config = {"domain": "water_quality"}
        is_valid, errors = ConfigValidator.validate_config(config)
        assert is_valid is False
        assert "缺少必要的配置项: company_info" in errors
    
    def test_validate_config_missing_company_fields(self):
        """测试缺少公司字段"""
        config = {
            "company_info": {
                "name": "测试公司"
                # 缺少其他必要字段
            }
        }
        is_valid, errors = ConfigValidator.validate_config(config)
        assert is_valid is False
        assert any("公司信息缺少" in error for error in errors)
    
    def test_validate_config_invalid_url(self):
        """测试无效URL"""
        config = {
            "company_info": {
                "name": "测试公司",
                "address": "测试地址",
                "email": "test@example.com",
                "phone": "123-456-7890",
                "profile": "测试简介",
                "logo_path": "invalid_url",
                "wayline_img": "http://example.com/wayline.jpg",
                "satellite_img": "http://example.com/satellite.jpg",
                "file_url": "http://example.com/data.zip",
                "measure_data": "http://example.com/measure.csv"
            }
        }
        is_valid, errors = ConfigValidator.validate_config(config)
        assert is_valid is False
        assert any("无效的URL" in error for error in errors)
    
    def test_clean_config(self, sample_config):
        """测试配置清理"""
        # 添加一些需要清理的字段
        sample_config["company_info"]["extra_field"] = "should_be_removed"
        
        cleaned_config = ConfigValidator.clean_config(sample_config)
        assert "extra_field" not in cleaned_config.get("company_info", {})
    
    def test_validate_geo_bounds(self):
        """测试地理边界验证"""
        # 有效边界
        valid_bounds = {
            "north_east": [31.0, 121.0],
            "south_west": [30.0, 120.0]
        }
        is_valid, errors = ConfigValidator.validate_geo_bounds(valid_bounds)
        assert is_valid is True
        assert len(errors) == 0
        
        # 无效边界（东北角在西南角的南边）
        invalid_bounds = {
            "north_east": [30.0, 121.0],
            "south_west": [31.0, 120.0]
        }
        is_valid, errors = ConfigValidator.validate_geo_bounds(invalid_bounds)
        assert is_valid is False
        assert len(errors) > 0