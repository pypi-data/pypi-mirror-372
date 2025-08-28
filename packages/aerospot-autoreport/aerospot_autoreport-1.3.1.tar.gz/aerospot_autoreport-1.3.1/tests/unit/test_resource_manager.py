"""
资源管理器单元测试
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from autoreport.core.resource_manager import ResourceManager
from autoreport.core.exceptions import DownloadError
from autoreport.utils.path import PathManager


class TestResourceManager:
    """资源管理器测试类"""
    
    @pytest.fixture
    def path_manager(self, temp_dir):
        """创建路径管理器"""
        return PathManager(temp_dir)
    
    @pytest.fixture
    def resource_manager(self, path_manager):
        """创建资源管理器"""
        return ResourceManager(path_manager, cache_enabled=True)
    
    def test_init_with_cache_enabled(self, path_manager):
        """测试启用缓存的初始化"""
        rm = ResourceManager(path_manager, cache_enabled=True)
        assert rm.cache_enabled is True
        assert os.path.exists(rm.cache_dir)
    
    def test_init_without_cache(self, path_manager):
        """测试禁用缓存的初始化"""
        rm = ResourceManager(path_manager, cache_enabled=False)
        assert rm.cache_enabled is False
    
    def test_generate_cache_key(self, resource_manager):
        """测试缓存键生成"""
        url = "http://example.com/test.jpg"
        key = resource_manager._generate_cache_key(url)
        assert isinstance(key, str)
        assert len(key) > 0
        
        # 相同URL应该生成相同的键
        key2 = resource_manager._generate_cache_key(url)
        assert key == key2
    
    def test_get_cache_path(self, resource_manager):
        """测试获取缓存路径"""
        cache_key = "test_key"
        resource_type = "logo"
        
        cache_path = resource_manager._get_cache_path(cache_key, resource_type)
        assert cache_path.endswith('.png')  # logo类型默认为png
        assert 'global_cache' in cache_path
    
    def test_is_cache_valid(self, resource_manager, temp_dir):
        """测试缓存有效性检查"""
        # 创建一个测试缓存文件
        cache_file = os.path.join(temp_dir, "test_cache.txt")
        with open(cache_file, 'w') as f:
            f.write("test content")
        
        # 新文件应该是有效的
        assert resource_manager._is_cache_valid(cache_file) is True
        
        # 不存在的文件应该是无效的
        assert resource_manager._is_cache_valid("/non/existent/file") is False
    
    @patch('autoreport.core.resource_manager.ResourceManager._download_to_cache')
    def test_get_resource_with_cache_hit(self, mock_download, resource_manager, temp_dir):
        """测试缓存命中的资源获取"""
        # 创建模拟的缓存文件
        cache_file = os.path.join(temp_dir, "cached_resource.jpg")
        with open(cache_file, 'wb') as f:
            f.write(b"cached content")
        
        # 模拟缓存路径返回
        with patch.object(resource_manager, '_get_cache_path', return_value=cache_file):
            with patch.object(resource_manager, '_is_cache_valid', return_value=True):
                result = resource_manager.get_resource("http://example.com/test.jpg", "satellite")
                
                # 应该返回缓存文件路径
                assert result == cache_file
                # 不应该调用下载
                mock_download.assert_not_called()
    
    @patch('autoreport.core.resource_manager.ResourceManager._download_to_cache')
    def test_get_resource_with_cache_miss(self, mock_download, resource_manager, temp_dir):
        """测试缓存未命中的资源获取"""
        # 设置下载返回路径
        download_path = os.path.join(temp_dir, "downloaded_resource.jpg")
        mock_download.return_value = download_path
        
        # 模拟缓存未命中
        with patch.object(resource_manager, '_is_cache_valid', return_value=False):
            result = resource_manager.get_resource("http://example.com/test.jpg", "satellite")
            
            # 应该调用下载
            mock_download.assert_called_once()
            assert result == download_path
    
    def test_clean_expired_cache(self, resource_manager, temp_dir):
        """测试清理过期缓存"""
        # 创建一个旧文件
        old_file = os.path.join(resource_manager.cache_dir, "old_cache.txt")
        os.makedirs(resource_manager.cache_dir, exist_ok=True)
        
        with open(old_file, 'w') as f:
            f.write("old content")
        
        # 修改文件时间为过期
        old_time = os.path.getmtime(old_file) - resource_manager.cache_ttl - 1
        os.utime(old_file, (old_time, old_time))
        
        # 清理过期缓存
        resource_manager._clean_expired_cache()
        
        # 旧文件应该被删除
        assert not os.path.exists(old_file)
    
    def test_get_resource_type_extension(self, resource_manager):
        """测试获取资源类型扩展名"""
        assert resource_manager._get_resource_type_extension("logo") == ".png"
        assert resource_manager._get_resource_type_extension("satellite") == ".jpg"
        assert resource_manager._get_resource_type_extension("wayline") == ".jpg"
        assert resource_manager._get_resource_type_extension("measure_data") == ".csv"
        assert resource_manager._get_resource_type_extension("file") == ".zip"
        assert resource_manager._get_resource_type_extension("unknown") == ".bin"