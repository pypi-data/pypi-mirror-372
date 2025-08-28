#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源下载模块
提供网络资源下载功能，支持阿里云OSS认证
"""
import os
import logging
import requests
import oss2
import time
from urllib.parse import urlparse, parse_qsl, unquote
from typing import Optional, Tuple
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class ResourceDownloader:
    """资源下载器类"""
    
    def __init__(self, path_manager=None):
        """初始化资源下载器
        
        Args:
            path_manager: 路径管理器对象
        """
        self.path_manager = path_manager
        self.timeout = 30  # 下载超时时间（秒）
        self.max_retries = 3  # 最大重试次数
        
        # 阿里云OSS配置，从环境变量获取
        self.oss_access_key_id = os.environ.get('OSS_ACCESS_KEY_ID')
        self.oss_access_key_secret = os.environ.get('OSS_ACCESS_KEY_SECRET')
        self.oss_endpoint = os.environ.get('OSS_ENDPOINT', 'oss-cn-shanghai.aliyuncs.com')
        if not all([self.oss_access_key_id, self.oss_access_key_secret, self.oss_endpoint]):
            raise ValueError('OSS配置缺失，请在.env文件或环境变量中设置OSS_ACCESS_KEY_ID、OSS_ACCESS_KEY_SECRET和OSS_ENDPOINT')
    
    def download(self, url: str, resource_type: str = 'downloads') -> Optional[str]:
        """下载资源
        
        Args:
            url: 资源URL
            resource_type: 资源类型，用于确定保存目录
            
        Returns:
            下载后的文件路径，失败返回None
        """
        try:
            logger.info(f"开始下载资源: {url}")
            
            # 解析URL获取文件名
            parsed_url = urlparse(url)
            filename = os.path.basename(unquote(parsed_url.path))
            
            if not filename:
                logger.warning(f"无法从URL解析文件名: {url}")
                filename = f"download_{hash(url) % 10000}.dat"
        
            # 下载文件路径都是默认的downloads
            if self.path_manager:
                save_path = self.path_manager.get_file_path(resource_type, filename)
            else:
                save_dir = os.path.join(os.getcwd(), resource_type)
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, filename)
            
            # 创建保存目录
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # 尝试使用不同方法下载
            # 1. 如果是OSS URL，尝试OSS SDK下载
            # 2. 如果OSS下载失败，尝试直接HTTP请求
            if 'aliyuncs.com' in url or 'oss-' in url:
                try:
                    return self._download_from_oss(url, save_path)
                except Exception as e:
                    logger.warning(f"OSS下载失败，尝试普通HTTP下载: {str(e)}")
            
            # 普通HTTP下载
            for retry in range(self.max_retries):
                try:
                    # 设置请求头来模拟浏览器
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=self.timeout, stream=True, allow_redirects=True)
                    response.raise_for_status()
                    
                    # 获取文件大小
                    total_size = int(response.headers.get('content-length', 0))
                    
                    # 写入文件
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    logger.info(f"资源下载完成: {save_path}")
                    return save_path
                except requests.exceptions.RequestException as e:
                    logger.warning(f"HTTP下载失败 (尝试 {retry+1}/{self.max_retries}): {str(e)}")
                    if retry == self.max_retries - 1:
                        raise
                    time.sleep(1)  # 重试前等待一秒
            
            logger.error("所有下载方法均失败")
            return None
            
        except Exception as e:
            logger.error(f"下载资源失败: {str(e)}")
            return None
    
    
    def _download_from_oss(self, url: str, save_path: str) -> Optional[str]:
        """从阿里云OSS下载资源
        
        Args:
            url: OSS资源URL
            save_path: 保存路径
            
        Returns:
            保存的文件路径，失败返回None
        """
        # 检查凭证是否存在
        if not self.oss_access_key_id or not self.oss_access_key_secret:
            logger.error("OSS凭证未设置，请在环境变量中设置OSS_ACCESS_KEY_ID和OSS_ACCESS_KEY_SECRET")
            return self._download_directly(url, save_path)
        
        # 从URL中提取bucket和object信息
        bucket_name, object_key = self._parse_oss_url(url)
        
        if not bucket_name or not object_key:
            logger.error(f"无法从URL解析出bucket和object信息: {url}")
            return self._download_directly(url, save_path)
        
        logger.info(f"从OSS下载: bucket={bucket_name}, object={object_key}")
        
        # 尝试不同的方法下载
        try:
            # 方法1: 使用OSS SDK直接下载
            auth = oss2.Auth(self.oss_access_key_id, self.oss_access_key_secret)
            bucket = oss2.Bucket(auth, self.oss_endpoint, bucket_name)
            
            # 检查对象是否存在
            if bucket.object_exists(object_key):
                bucket.get_object_to_file(object_key, save_path)
                logger.info(f"使用OSS SDK下载成功: {save_path}")
                return save_path
            else:
                logger.warning(f"OSS对象不存在: {object_key}")
                
                # 尝试替换斜杠方向
                alternate_key = object_key.replace('\\', '/')
                if alternate_key != object_key and bucket.object_exists(alternate_key):
                    bucket.get_object_to_file(alternate_key, save_path)
                    logger.info(f"使用替换斜杠后的路径下载成功: {save_path}")
                    return save_path
                
                # 尝试通过请求直接URL参数中的对象
                return self._download_directly(url, save_path)
        except oss2.exceptions.ServerError as e:
            logger.error(f"OSS服务器错误: {str(e)}")
            return self._download_directly(url, save_path)
        except oss2.exceptions.ClientError as e:
            logger.error(f"OSS客户端错误: {str(e)}")
            return self._download_directly(url, save_path)
        except Exception as e:
            logger.error(f"OSS下载出错: {str(e)}")
            return self._download_directly(url, save_path)
    
    def _download_directly(self, url: str, save_path: str) -> Optional[str]:
        """直接通过HTTP请求下载
        
        Args:
            url: 资源URL
            save_path: 保存路径
            
        Returns:
            保存的文件路径，失败返回None
        """
        try:
            logger.info(f"尝试直接HTTP下载: {url}")
            
            # 设置请求头来模拟浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            # 如果URL中有OSSAccessKeyId和Signature参数，说明是预签名URL，直接使用
            # 否则尝试使用我们的凭据生成新的签名
            parsed_url = urlparse(url)
            query_params = dict(parse_qsl(parsed_url.query))
            
            if 'OSSAccessKeyId' in query_params and 'Signature' in query_params:
                # 直接使用预签名URL
                response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
            else:
                # 尝试生成新的签名URL
                bucket_name, object_key = self._parse_oss_url(url)
                if bucket_name and object_key and self.oss_access_key_id and self.oss_access_key_secret:
                    try:
                        auth = oss2.Auth(self.oss_access_key_id, self.oss_access_key_secret)
                        bucket = oss2.Bucket(auth, self.oss_endpoint, bucket_name)
                        signed_url = bucket.sign_url('GET', object_key, 60)  # 1分钟有效期
                        response = requests.get(signed_url, headers=headers, timeout=self.timeout, stream=True)
                    except Exception as e:
                        logger.warning(f"生成签名URL失败，使用原始URL: {str(e)}")
                        response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
                else:
                    # 直接使用原始URL
                    response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
            
            response.raise_for_status()
            
            # 写入文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"HTTP下载成功: {save_path}")
            return save_path
        
        except Exception as e:
            logger.error(f"HTTP下载失败: {str(e)}")
            return None
    
    def _parse_oss_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """解析OSS URL，提取bucket和object信息
        
        Args:
            url: OSS资源URL
            
        Returns:
            (bucket_name, object_key)元组
        """
        try:
            parsed_url = urlparse(url)
            
            # 尝试从主机名中提取bucket信息
            host_parts = parsed_url.netloc.split('.')
            if len(host_parts) >= 1 and ('aliyuncs.com' in parsed_url.netloc or 'oss-' in parsed_url.netloc):
                bucket_name = host_parts[0]
                
                # 处理路径中的对象名
                object_key = parsed_url.path
                if object_key.startswith('/'):
                    object_key = object_key[1:]  # 移除开头的斜杠
                
                # URL解码
                object_key = unquote(object_key)
                
                # 从查询参数中尝试获取key
                query_params = dict(parse_qsl(parsed_url.query))
                if 'key' in query_params:
                    object_key = unquote(query_params['key'])
                
                # 处理编码的反斜杠
                # OSS对象键可能包含%5C (编码的反斜杠)
                # 有些系统使用反斜杠分隔路径，但OSS标准是正斜杠
                if '%5C' in object_key:
                    object_key = object_key.replace('%5C', '/')
                elif '\\' in object_key:
                    # 保持原始路径格式以便直接使用
                    # 但OSS API可能需要正斜杠
                    pass
                
                logger.debug(f"解析的对象键: {object_key}")
                return bucket_name, object_key
            
            return None, None
        except Exception as e:
            logger.error(f"解析OSS URL时出错: {str(e)}")
            return None, None
    
    def generate_presigned_url(self, bucket_name: str, object_key: str, expires: int = 3600) -> Optional[str]:
        """生成预签名URL
        
        Args:
            bucket_name: 存储桶名称
            object_key: 对象键
            expires: 过期时间（秒），默认1小时
            
        Returns:
            预签名URL，失败返回None
        """
        try:
            # 检查凭证是否存在
            if not self.oss_access_key_id or not self.oss_access_key_secret:
                logger.error("OSS凭证未设置，请在环境变量中设置OSS_ACCESS_KEY_ID和OSS_ACCESS_KEY_SECRET")
                return None
            
            # 创建OSS认证
            auth = oss2.Auth(self.oss_access_key_id, self.oss_access_key_secret)
            bucket = oss2.Bucket(auth, self.oss_endpoint, bucket_name)
            
            # 生成签名URL
            url = bucket.sign_url('GET', object_key, expires)
            
            logger.info(f"生成OSS预签名URL成功, 过期时间: {expires}秒")
            return url
            
        except Exception as e:
            logger.error(f"生成预签名URL失败: {str(e)}")
            return None 