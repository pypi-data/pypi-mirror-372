#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据提取模块
提供文件解压和数据提取功能

本模块主要用于从压缩文件(主要是ZIP文件)中提取和处理数据。
主要功能包括：
1. 解压ZIP文件到指定目录
2. 获取ZIP文件内容列表
3. 根据模式匹配查找文件
4. 检测并修复文本文件编码
5. 验证ZIP文件完整性
6. 安全路径检查，防止路径穿越攻击
7. 估算解压后的文件大小
8. 清理临时文件
"""
import os
import logging
import zipfile
import tempfile
import shutil
import chardet
from typing import List, Optional

logger = logging.getLogger(__name__)

class DataExtractor:
    """
    数据提取器基类
    
    提供数据提取的基本框架，定义了通用的接口方法。
    子类应该实现具体的提取逻辑。
    
    属性:
        path_manager: 路径管理器对象，提供路径操作功能
        temp_dir: 临时目录路径，用于存放提取的文件
    """
    
    def __init__(self, path_manager=None):
        """初始化数据提取器
        
        Args:
            path_manager: 路径管理器对象，提供路径操作功能。
                          如果为None，则使用系统临时目录。
        """
        self.path_manager = path_manager
        self.temp_dir = tempfile.mkdtemp() if path_manager is None else path_manager.get_path('temp')
    
    def extract(self, file_path: str) -> Optional[str]:
        """提取数据
        
        解压或提取指定文件中的数据。
        
        Args:
            file_path: 数据文件路径
            
        Returns:
            提取后的数据目录路径，失败返回None
            
        注意:
            这是一个抽象方法，子类必须实现具体逻辑。
        """
        raise NotImplementedError("子类必须实现此方法")

class ZipExtractor(DataExtractor):
    """
    ZIP文件提取器
    
    专门用于处理ZIP格式文件的解压和内容提取。
    提供了安全检查、编码修复、文件查找等功能。
    
    属性:
        path_manager: 路径管理器对象
        temp_dir: 临时目录路径
        _extracted_files: 缓存已提取文件列表的字典
        
    示例:
        extractor = ZipExtractor(path_manager)
        extract_dir = extractor.extract("data.zip")
        csv_file = extractor.find_file("data.zip", "data.csv")
    """
    
    def __init__(self, path_manager=None):
        """初始化ZIP文件提取器
        
        Args:
            path_manager: 路径管理器对象，提供路径操作功能。
                          如果为None，则使用系统临时目录。
        """
        super().__init__(path_manager)
        self._extracted_files = {}  # 用于缓存已提取的文件
    
    def extract(self, zip_path: str) -> Optional[str]:
        """解压ZIP文件
        
        将ZIP文件解压到指定目录，并执行安全检查。
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            解压后的目录路径，失败返回None
            
        示例:
            extract_dir = extractor.extract("data.zip")
            if extract_dir:
                print(f"文件已解压到: {extract_dir}")
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(zip_path):
                logger.error(f"ZIP文件不存在: {zip_path}")
                return None
                
            # 检查是否为ZIP文件
            if not zipfile.is_zipfile(zip_path):
                logger.error(f"文件不是有效的ZIP格式: {zip_path}")
                return None
            
            # 创建提取目录 - 使用updated PathManager的'extracted'目录
            zip_name = os.path.splitext(os.path.basename(zip_path))[0]
            
            # 如果路径管理器可用，使用其提供的extracted目录
            if self.path_manager:
                extract_dir = os.path.join(self.path_manager.get_path('extracted'), zip_name)
            else:
                extract_dir = os.path.join(self.temp_dir, zip_name)
                
            os.makedirs(extract_dir, exist_ok=True)
            
            logger.info(f"开始解压ZIP文件: {zip_path} -> {extract_dir}")
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                zip_ref.extractall(extract_dir)
                
                # 存储已提取的文件列表
                self._extracted_files[zip_path] = file_list
                
                logger.info(f"ZIP文件解压完成，共 {len(file_list)} 个文件")
            
            return extract_dir
            
        except zipfile.BadZipFile:
            logger.error(f"无效的ZIP文件: {zip_path}")
            return None
        except Exception as e:
            logger.error(f"解压ZIP文件时出错: {str(e)}")
            return None
    
    def get_extracted_files(self, zip_path: str) -> List[str]:
        """获取已提取的文件列表
        
        获取指定ZIP文件解压后的所有文件路径列表。
        如果文件尚未解压，则尝试读取ZIP文件内容列表。
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            文件路径列表
            
        示例:
            files = extractor.get_extracted_files("data.zip")
            for file in files:
                print(f"- {file}")
        """
        if zip_path in self._extracted_files:
            return self._extracted_files[zip_path]
        
        # 如果没有缓存记录，尝试读取
        if zipfile.is_zipfile(zip_path):
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    self._extracted_files[zip_path] = zip_ref.namelist()
                    return zip_ref.namelist()
            except Exception as e:
                logger.error(f"读取ZIP文件内容列表时出错: {str(e)}")
        
        return []
    
    def find_file(self, zip_path: str, pattern: str) -> Optional[str]:
        """在已提取的文件中查找匹配的文件
        
        根据文件名模式在已解压的文件中查找匹配的文件。
        模式匹配使用部分匹配（包含关系），不区分大小写。
        
        Args:
            zip_path: ZIP文件路径
            pattern: 文件名模式，支持部分匹配
            
        Returns:
            匹配的文件路径，未找到返回None
            
        示例:
            # 查找包含"report"的文件
            report_file = extractor.find_file("data.zip", "report")
            
            # 查找CSV文件
            csv_file = extractor.find_file("data.zip", ".csv")
        """
        files = self.get_extracted_files(zip_path)
        for file in files:
            if pattern.lower() in file.lower():
                # 提取目录 - 使用路径管理器
                zip_name = os.path.splitext(os.path.basename(zip_path))[0]
                if self.path_manager:
                    extract_dir = os.path.join(self.path_manager.get_path('extracted'), zip_name)
                else:
                    extract_dir = os.path.join(self.temp_dir, zip_name)
                    
                return os.path.join(extract_dir, file)
        
        return None
        
    def _is_safe_path(self, path: str) -> bool:
        """检查路径是否安全
        
        防止路径穿越攻击，确保解压路径在目标目录内
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 路径是否安全
        """
        try:
            resolved_path = os.path.abspath(path)
            # 使用路径管理器获取extracted目录
            if self.path_manager:
                extract_root = os.path.abspath(self.path_manager.get_path('extracted'))
            else:
                extract_root = os.path.abspath(self.temp_dir)
                
            common_prefix = os.path.commonpath([resolved_path, extract_root])
            return common_prefix == extract_root
        except Exception:
            return False
            
    def _is_allowed_file(self, filename: str) -> bool:
        """检查文件是否允许解压
        
        根据文件扩展名判断文件是否为安全的文件类型。
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 文件是否允许解压
        """
        ext = os.path.splitext(filename)[1].lower()
        return ext in {'.csv', '.txt', '.json', '.xml', '.jpg', '.png', '.pdf'}
    
    def _detect_encoding(self, file_path: str) -> str:
        """检测文件编码
        
        使用chardet库检测文本文件的编码类型。
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 检测到的编码，如果检测失败则返回utf-8
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(8192)
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception as e:
            logger.warning(f"编码检测失败: {str(e)}")
            return 'utf-8'
    
    def _fix_text_file_encoding(self, file_path: str) -> bool:
        """修复文本文件编码
        
        将文本文件转换为UTF-8编码，便于后续处理。
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功修复
        """
        if not file_path.lower().endswith(('.txt', '.csv')):
            return True
            
        try:
            # 检测编码
            encoding = self._detect_encoding(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 以UTF-8重新写入
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            logger.error(f"修复文件编码失败 {file_path}: {str(e)}")
            return False
    
    def _verify_zip_file(self, zip_path: str) -> bool:
        """验证ZIP文件完整性
        
        检查ZIP文件是否损坏或不完整。
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            bool: 文件是否完整
            
        示例:
            if extractor._verify_zip_file("data.zip"):
                print("ZIP文件完好无损")
            else:
                print("ZIP文件已损坏")
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                result = zip_ref.testzip()
                if result is not None:
                    logger.error(f"ZIP文件损坏，首个损坏文件: {result}")
                    return False
                return True
        except Exception as e:
            logger.error(f"验证ZIP文件失败: {str(e)}")
            return False
    
    def _estimate_uncompressed_size(self, zip_path: str) -> int:
        """估算解压后的总大小
        
        计算ZIP文件解压后将占用的磁盘空间。
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            int: 估算的总大小（字节）
            
        示例:
            size = extractor._estimate_uncompressed_size("data.zip")
            print(f"解压后大小约: {size / 1024 / 1024:.1f} MB")
        """
        try:
            total_size = 0
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for info in zip_ref.infolist():
                    total_size += info.file_size
            return total_size
        except Exception as e:
            logger.error(f"估算解压大小失败: {str(e)}")
            return 0
    
    def cleanup(self, zip_path: str = None):
        """清理解压的临时文件
        
        删除解压过程中生成的临时文件，释放磁盘空间。
        
        Args:
            zip_path: 指定要清理的ZIP文件，如果为None则清理所有
            
        示例:
            # 清理单个ZIP文件的临时文件
            extractor.cleanup("data.zip")
            
            # 清理所有临时文件
            extractor.cleanup()
        """
        # 使用路径管理器获取extracted目录
        if self.path_manager:
            extract_dir = self.path_manager.get_path('extracted')
        else:
            extract_dir = self.temp_dir
        
        if zip_path:
            # 清理指定ZIP文件的解压目录
            extracted_files = self.get_extracted_files(zip_path)
            for extracted_file in extracted_files:
                if os.path.exists(extracted_file):
                    try:
                        if os.path.isfile(extracted_file):
                            os.remove(extracted_file)
                        elif os.path.isdir(extracted_file):
                            shutil.rmtree(extracted_file)
                    except Exception as e:
                        logger.error(f"清理文件失败 {extracted_file}: {str(e)}")
        else:
            # 清理所有解压文件
            try:
                shutil.rmtree(extract_dir)
                os.makedirs(extract_dir, exist_ok=True)
                self._extracted_files.clear()
            except Exception as e:
                logger.error(f"清理解压目录失败: {str(e)}")
        
        logger.info("清理完成")