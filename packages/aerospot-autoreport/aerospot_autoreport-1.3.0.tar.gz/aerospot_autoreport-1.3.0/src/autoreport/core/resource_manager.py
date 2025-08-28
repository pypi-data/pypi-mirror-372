#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AeroSpot自动化报告生成工具的资源管理器"""

import hashlib
import logging
import os
import shutil
import time
from typing import Any, Dict, Optional

from .exceptions import DownloadError
from ..processor.downloader import ResourceDownloader
from ..utils.path import PathManager

logger = logging.getLogger(__name__)

class ResourceManager:
    """资源管理器，负责下载、缓存和管理资源"""
    
    # 默认缓存过期时间（3天，单位：秒）
    DEFAULT_CACHE_TTL = 3 * 24 * 60 * 60
    
    def __init__(self, path_manager: PathManager, cache_enabled: bool = False, cache_ttl: int = DEFAULT_CACHE_TTL):
        """初始化资源管理器
        
        Args:
            path_manager: 路径管理器实例
            cache_enabled: 是否启用缓存
            cache_ttl: 缓存过期时间（秒）
        """
        self.path_manager = path_manager
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.downloader = ResourceDownloader(path_manager)
        
        # 创建全局共享的缓存目录（位于项目根目录）
        # 获取当前时间戳目录的上两级（时间戳目录的父目录的父目录，即项目根目录）
        project_root = os.path.dirname(os.path.dirname(path_manager.get_base_dir()))
        self.cache_dir = os.path.join(project_root, 'global_cache')
        
        # 确保缓存目录存在
        if cache_enabled:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"使用全局缓存目录: {self.cache_dir}")
            
            # 清理过期缓存
            self._clean_expired_cache()
    
    def get_resource(self, url: str, resource_type: str, force_download: bool = False) -> str:
        """获取资源，优先使用缓存
        
        Args:
            url: 资源URL或本地路径
            resource_type: 资源类型标识
            force_download: 是否强制重新下载（忽略缓存）
            
        Returns:
            str: 资源的本地路径
            
        Raises:
            ResourceNotFoundError: 资源未找到
            DownloadError: 下载失败
        """
        # 如果是本地文件路径且存在，直接返回
        if os.path.exists(url):
            logger.info(f"使用本地文件: {url}")
            return url
        
        # 检查是否有有效缓存
        cache_path = None
        use_cache = self.cache_enabled and not force_download
        
        if use_cache:
            cache_path = self._get_cache_path(url, resource_type)
            if os.path.exists(cache_path) and not self._is_cache_expired(cache_path):
                logger.info(f"使用缓存资源: {cache_path}")
                return cache_path
            elif os.path.exists(cache_path):
                logger.info(f"缓存已过期，重新下载: {cache_path}")
                # 删除过期缓存
                os.remove(cache_path)
        
        # 下载资源
        try:
            downloaded_path = self.downloader.download(url)
            if not downloaded_path:
                raise DownloadError(f"资源下载失败: {url}")
            
            # 缓存资源
            if self.cache_enabled and cache_path:
                self._cache_resource(downloaded_path, cache_path)
            
            return downloaded_path
        except Exception as e:
            raise DownloadError(f"获取资源失败: {str(e)}")
    
    def _get_cache_path(self, url: str, resource_type: str) -> str:
        """获取资源的缓存路径
        
        Args:
            url: 资源URL
            resource_type: 资源类型
            
        Returns:
            str: 缓存路径
        """
        # 移除URL中的查询参数部分
        base_url = url.split('?')[0]
        
        # 使用URL的哈希值作为缓存文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # 从URL中提取文件扩展名
        file_ext = os.path.splitext(base_url)[-1]
        if not file_ext and '.' in base_url.split('/')[-1]:
            file_ext = '.' + base_url.split('/')[-1].split('.')[-1]
        
        # 如果无法从URL获取扩展名，使用资源类型作为扩展名
        if not file_ext:
            extension_map = {
                'logo': '.png', 
                'wayline': '.png', 
                'satellite': '.png',
                'measure_data': '.csv',
                'file': '.zip',
                'kml_boundary': '.kml'
            }
            file_ext = extension_map.get(resource_type, '')
        
        cache_filename = f"{resource_type}_{url_hash}{file_ext}"
        return os.path.join(self.cache_dir, cache_filename)
    
    def _cache_resource(self, source_path: str, cache_path: str) -> bool:
        """缓存资源文件
        
        Args:
            source_path: 源文件路径
            cache_path: 缓存路径
            
        Returns:
            bool: 是否成功缓存
        """
        try:
            shutil.copy2(source_path, cache_path)
            logger.info(f"资源已缓存: {cache_path}")
            
            # 更新缓存元数据（创建时间）
            self._update_cache_metadata(cache_path)
            
            return True
        except Exception as e:
            logger.warning(f"缓存资源失败: {str(e)}")
            return False
    
    def _update_cache_metadata(self, cache_path: str) -> None:
        """更新缓存元数据
        
        Args:
            cache_path: 缓存文件路径
        """
        # 创建元数据文件
        meta_path = f"{cache_path}.meta"
        current_time = int(time.time())
        
        try:
            with open(meta_path, 'w') as f:
                f.write(f"created={current_time}\n")
                f.write(f"ttl={self.cache_ttl}\n")
        except Exception as e:
            logger.warning(f"更新缓存元数据失败: {str(e)}")
    
    def _is_cache_expired(self, cache_path: str) -> bool:
        """检查缓存是否过期
        
        Args:
            cache_path: 缓存文件路径
            
        Returns:
            bool: 是否过期
        """
        # 尝试读取元数据
        meta_path = f"{cache_path}.meta"
        current_time = int(time.time())
        
        if not os.path.exists(meta_path):
            # 如果没有元数据文件，使用文件的修改时间
            try:
                file_mtime = os.path.getmtime(cache_path)
                return (current_time - file_mtime) > self.cache_ttl
            except Exception:
                # 如果无法获取修改时间，默认为过期
                return True
        
        try:
            created_time = None
            with open(meta_path, 'r') as f:
                for line in f:
                    if line.startswith('created='):
                        created_time = int(line[8:].strip())
            
            if created_time is None:
                return True
            
            # 检查是否超过TTL
            return (current_time - created_time) > self.cache_ttl
        except Exception:
            # 如果读取元数据失败，默认为过期
            return True
    
    def _clean_expired_cache(self) -> int:
        """清理过期的缓存文件
        
        Returns:
            int: 清理的文件数量
        """
        if not self.cache_enabled or not os.path.exists(self.cache_dir):
            return 0
        
        count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.meta'):
                    continue
                
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path) and self._is_cache_expired(file_path):
                    # 删除缓存文件和元数据
                    try:
                        os.remove(file_path)
                        meta_path = f"{file_path}.meta"
                        if os.path.exists(meta_path):
                            os.remove(meta_path)
                        count += 1
                    except Exception as e:
                        logger.warning(f"删除过期缓存失败: {str(e)}")
            
            if count > 0:
                logger.info(f"已清理{count}个过期缓存文件")
            
            return count
        except Exception as e:
            logger.error(f"清理过期缓存失败: {str(e)}")
            return count
    
    def clear_cache(self, resource_type: Optional[str] = None, force: bool = False) -> int:
        """清除缓存
        
        Args:
            resource_type: 要清除的资源类型，None表示清除所有
            force: 是否强制清除所有缓存（包括未过期的）
            
        Returns:
            int: 清除的文件数量
        """
        if not self.cache_enabled or not os.path.exists(self.cache_dir):
            return 0
        
        count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.meta'):
                    continue
                
                if resource_type and not filename.startswith(f"{resource_type}_"):
                    continue
                
                file_path = os.path.join(self.cache_dir, filename)
                if not os.path.isfile(file_path):
                    continue
                
                # 如果强制清除或缓存过期，则删除
                if force or self._is_cache_expired(file_path):
                    try:
                        os.remove(file_path)
                        meta_path = f"{file_path}.meta"
                        if os.path.exists(meta_path):
                            os.remove(meta_path)
                        count += 1
                    except Exception as e:
                        logger.warning(f"删除缓存失败: {str(e)}")
            
            logger.info(f"已清除{count}个缓存文件")
            return count
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.cache_enabled or not os.path.exists(self.cache_dir):
            return {
                'enabled': False,
                'count': 0,
                'size': 0,
                'expired': 0
            }
        
        total_count = 0
        total_size = 0
        expired_count = 0
        resource_types = {}
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.meta'):
                    continue
                
                file_path = os.path.join(self.cache_dir, filename)
                if not os.path.isfile(file_path):
                    continue
                
                total_count += 1
                try:
                    size = os.path.getsize(file_path)
                    total_size += size
                except Exception as e:
                    logger.error(f"错误：{e}")
                
                # 检查是否过期
                if self._is_cache_expired(file_path):
                    expired_count += 1
                
                # 统计资源类型
                resource_type = filename.split('_')[0] if '_' in filename else 'unknown'
                if resource_type not in resource_types:
                    resource_types[resource_type] = 0
                resource_types[resource_type] += 1
            
            return {
                'enabled': self.cache_enabled,
                'directory': self.cache_dir,
                'count': total_count,
                'size': total_size,
                'expired': expired_count,
                'types': resource_types
            }
        except Exception as e:
            logger.error(f"获取缓存统计信息失败: {str(e)}")
            return {
                'enabled': self.cache_enabled,
                'error': str(e)
            } 