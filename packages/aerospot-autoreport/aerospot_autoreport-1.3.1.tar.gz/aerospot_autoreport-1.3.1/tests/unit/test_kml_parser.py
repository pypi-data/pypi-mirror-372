#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KML解析器测试用例
"""

import os
import tempfile
import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from autoreport.utils.kml import (
    KMLParser, 
    create_kml_boundary_mask,
    get_kml_boundary_bounds,
    validate_kml_file,
    parse_kml_boundary
)


class TestKMLParser:
    """KML解析器测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建测试用的KML内容
        self.test_kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Placemark>
            <name>Test Polygon</name>
            <Polygon>
                <outerBoundaryIs>
                    <LinearRing>
                        <coordinates>
                            120.0,30.0,0 120.1,30.0,0 120.1,30.1,0 120.0,30.1,0 120.0,30.0,0
                        </coordinates>
                    </LinearRing>
                </outerBoundaryIs>
            </Polygon>
        </Placemark>
    </Document>
</kml>"""
        
        # 创建临时KML文件
        self.temp_kml_file = tempfile.NamedTemporaryFile(mode='w', suffix='.kml', delete=False)
        self.temp_kml_file.write(self.test_kml_content)
        self.temp_kml_file.close()
        
    def teardown_method(self):
        """清理测试环境"""
        if os.path.exists(self.temp_kml_file.name):
            os.unlink(self.temp_kml_file.name)
    
    def test_kml_parser_initialization(self):
        """测试KML解析器初始化"""
        parser = KMLParser(self.temp_kml_file.name)
        
        assert parser.kml_path == self.temp_kml_file.name
        assert parser.tree is not None
        assert parser.root is not None
    
    def test_kml_parser_file_not_found(self):
        """测试KML文件不存在的情况"""
        with pytest.raises(FileNotFoundError):
            KMLParser("non_existent_file.kml")
    
    def test_extract_coordinates(self):
        """测试坐标提取功能"""
        parser = KMLParser(self.temp_kml_file.name)
        coordinates = parser.extract_coordinates()
        
        assert len(coordinates) == 1
        assert len(coordinates[0]) == 5  # 5个坐标点（首尾相同）
        
        # 检查第一个坐标点
        assert coordinates[0][0] == (120.0, 30.0)
        assert coordinates[0][1] == (120.1, 30.0)
        assert coordinates[0][2] == (120.1, 30.1)
        assert coordinates[0][3] == (120.0, 30.1)
        assert coordinates[0][4] == (120.0, 30.0)
    
    def test_get_bounding_box(self):
        """测试边界框获取功能"""
        parser = KMLParser(self.temp_kml_file.name)
        bbox = parser.get_bounding_box()
        
        assert bbox is not None
        min_lon, min_lat, max_lon, max_lat = bbox
        
        assert min_lon == 120.0
        assert min_lat == 30.0
        assert max_lon == 120.1
        assert max_lat == 30.1
    
    def test_parse_coordinates_text(self):
        """测试坐标文本解析"""
        parser = KMLParser(self.temp_kml_file.name)
        
        # 测试正常坐标文本
        coords_text = "120.0,30.0,0 120.1,30.0,0 120.1,30.1,0"
        coords = parser._parse_coordinates_text(coords_text)
        
        assert len(coords) == 3
        assert coords[0] == (120.0, 30.0)
        assert coords[1] == (120.1, 30.0)
        assert coords[2] == (120.1, 30.1)
        
        # 测试空字符串
        coords_empty = parser._parse_coordinates_text("")
        assert len(coords_empty) == 0
        
        # 测试无效格式
        coords_invalid = parser._parse_coordinates_text("invalid,format")
        assert len(coords_invalid) == 0


class TestKMLBoundaryFunctions:
    """KML边界功能测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建测试用的KML内容
        self.test_kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Placemark>
            <name>Test Polygon</name>
            <Polygon>
                <outerBoundaryIs>
                    <LinearRing>
                        <coordinates>
                            120.0,30.0,0 120.1,30.0,0 120.1,30.1,0 120.0,30.1,0 120.0,30.0,0
                        </coordinates>
                    </LinearRing>
                </outerBoundaryIs>
            </Polygon>
        </Placemark>
    </Document>
</kml>"""
        
        # 创建临时KML文件
        self.temp_kml_file = tempfile.NamedTemporaryFile(mode='w', suffix='.kml', delete=False)
        self.temp_kml_file.write(self.test_kml_content)
        self.temp_kml_file.close()
        
    def teardown_method(self):
        """清理测试环境"""
        if os.path.exists(self.temp_kml_file.name):
            os.unlink(self.temp_kml_file.name)
    
    def test_create_kml_boundary_mask(self):
        """测试KML边界掩码创建"""
        # 创建测试网格
        lon_range = np.linspace(119.9, 120.2, 10)
        lat_range = np.linspace(29.9, 30.2, 10)
        grid_lon, grid_lat = np.meshgrid(lon_range, lat_range)
        
        # 创建边界掩码
        mask = create_kml_boundary_mask(grid_lon, grid_lat, self.temp_kml_file.name)
        
        assert mask.shape == grid_lon.shape
        assert isinstance(mask, np.ndarray)
        assert mask.dtype == bool
        
        # 应该有一些点在边界内
        assert np.any(mask)
    
    def test_get_kml_boundary_bounds(self):
        """测试KML边界范围获取"""
        bounds = get_kml_boundary_bounds(self.temp_kml_file.name)
        
        assert bounds is not None
        min_lon, min_lat, max_lon, max_lat = bounds
        
        assert min_lon == 120.0
        assert min_lat == 30.0
        assert max_lon == 120.1
        assert max_lat == 30.1
    
    def test_validate_kml_file(self):
        """测试KML文件验证"""
        # 测试有效文件
        assert validate_kml_file(self.temp_kml_file.name) is True
        
        # 测试不存在的文件
        assert validate_kml_file("non_existent_file.kml") is False
    
    def test_parse_kml_boundary_backward_compatibility(self):
        """测试向后兼容的KML边界解析函数"""
        boundary = parse_kml_boundary(self.temp_kml_file.name)
        
        assert boundary is not None
        assert len(boundary) == 5  # 5个坐标点
        
        # 检查第一个坐标点
        assert boundary[0] == (120.0, 30.0)
    
    def test_kml_boundary_mask_with_invalid_file(self):
        """测试无效KML文件的边界掩码创建"""
        # 创建测试网格
        lon_range = np.linspace(119.9, 120.2, 5)
        lat_range = np.linspace(29.9, 30.2, 5)
        grid_lon, grid_lat = np.meshgrid(lon_range, lat_range)
        
        # 使用不存在的文件
        mask = create_kml_boundary_mask(grid_lon, grid_lat, "non_existent_file.kml")
        
        # 应该返回全True掩码
        assert np.all(mask)
    
    def test_get_kml_boundary_bounds_with_invalid_file(self):
        """测试无效KML文件的边界范围获取"""
        bounds = get_kml_boundary_bounds("non_existent_file.kml")
        
        assert bounds is None


class TestKMLIntegration:
    """KML集成测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建更复杂的KML内容（包含多个图形）
        self.complex_kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Placemark>
            <name>Polygon 1</name>
            <Polygon>
                <outerBoundaryIs>
                    <LinearRing>
                        <coordinates>
                            120.0,30.0,0 120.05,30.0,0 120.05,30.05,0 120.0,30.05,0 120.0,30.0,0
                        </coordinates>
                    </LinearRing>
                </outerBoundaryIs>
            </Polygon>
        </Placemark>
        <Placemark>
            <name>Polygon 2</name>
            <Polygon>
                <outerBoundaryIs>
                    <LinearRing>
                        <coordinates>
                            120.1,30.1,0 120.15,30.1,0 120.15,30.15,0 120.1,30.15,0 120.1,30.1,0
                        </coordinates>
                    </LinearRing>
                </outerBoundaryIs>
            </Polygon>
        </Placemark>
    </Document>
</kml>"""
        
        # 创建临时KML文件
        self.temp_kml_file = tempfile.NamedTemporaryFile(mode='w', suffix='.kml', delete=False)
        self.temp_kml_file.write(self.complex_kml_content)
        self.temp_kml_file.close()
        
    def teardown_method(self):
        """清理测试环境"""
        if os.path.exists(self.temp_kml_file.name):
            os.unlink(self.temp_kml_file.name)
    
    def test_multiple_polygons_extraction(self):
        """测试多个多边形的提取"""
        parser = KMLParser(self.temp_kml_file.name)
        coordinates = parser.extract_coordinates()
        
        assert len(coordinates) == 2  # 应该有两个多边形
        assert len(coordinates[0]) == 5  # 每个多边形5个点
        assert len(coordinates[1]) == 5
    
    def test_multiple_polygons_bounding_box(self):
        """测试多个多边形的边界框"""
        parser = KMLParser(self.temp_kml_file.name)
        bbox = parser.get_bounding_box()
        
        assert bbox is not None
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # 边界框应该包含所有多边形
        assert min_lon == 120.0
        assert min_lat == 30.0
        assert max_lon == 120.15
        assert max_lat == 30.15
    
    def test_multiple_polygons_mask_creation(self):
        """测试多个多边形的掩码创建"""
        # 创建测试网格
        lon_range = np.linspace(119.9, 120.2, 20)
        lat_range = np.linspace(29.9, 30.2, 20)
        grid_lon, grid_lat = np.meshgrid(lon_range, lat_range)
        
        # 创建边界掩码
        mask = create_kml_boundary_mask(grid_lon, grid_lat, self.temp_kml_file.name)
        
        assert mask.shape == grid_lon.shape
        assert isinstance(mask, np.ndarray)
        assert mask.dtype == bool
        
        # 应该有一些点在边界内（两个多边形的并集）
        assert np.any(mask)
        
        # 掩码中True的点数应该合理（不会是全部或全无）
        true_count = np.sum(mask)
        total_count = mask.size
        assert 0 < true_count < total_count


if __name__ == "__main__":
    pytest.main([__file__])