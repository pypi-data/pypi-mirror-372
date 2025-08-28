"""
IO工具模块
提供数据文件的读取和保存功能
"""
import os
import logging
import pandas as pd
import re
from typing import Optional

logger = logging.getLogger(__name__)

def read_position_data(pos_file: str) -> pd.DataFrame:
    """读取位置数据文件
    
    Args:
        pos_file: 位置文件路径(POS.TXT)
        
    Returns:
        包含位置数据的DataFrame，失败返回空DataFrame
    """
    position_data = pd.DataFrame()
    try:
        with open(pos_file, 'r', encoding='utf-8') as f:
            data_list = []
            for line in f:
                # 使用正则表达式解析每一行
                match = re.search(r'REFL_(\d+)\.csv\s+latitude:\s+([0-9.]+)\s+longitude:\s+([0-9.]+)\s+height:\s+([0-9.]+)', line)
                if match:
                    sample_id = int(match.group(1))
                    latitude = float(match.group(2))
                    longitude = float(match.group(3))
                    
                    data_list.append({
                        'index': str(sample_id),
                        'latitude': latitude,
                        'longitude': longitude,
                    })
            
            if data_list:
                position_data = pd.DataFrame(data_list)
                position_data.set_index('index', inplace=True)
                logger.info(f"成功读取位置数据，共 {len(position_data)} 条记录")
            else:
                logger.warning("位置文件中没有找到有效数据")

        return position_data
    except Exception as e:
        logger.error(f"读取位置数据失败: {str(e)}")
        return pd.DataFrame()

def read_measure_data(measure_file: str) -> pd.DataFrame:
    """读取人工采样测量数据
    
    Args:
        measure_file: 人工采样数据文件路径
        
    Returns:
        包含人工采样数据的DataFrame，失败返回空DataFrame
    """
    try:
        logger.info(f"开始读取人工采样数据: {measure_file}")
        
        # 根据文件扩展名选择读取方法
        ext = os.path.splitext(measure_file)[1].lower()
        if ext in ['.xlsx', '.xls']:
            measure_df = pd.read_excel(measure_file)
        elif ext == '.csv':
            measure_df = pd.read_csv(measure_file, encoding='utf-8')
        else:
            logger.error(f"不支持的文件格式: {ext}")
            return pd.DataFrame()
        
        # 检查是否包含经纬度列
        required_columns = ['latitude', 'longitude']
        column_mapping = {}  # 用于存储需要重命名的列
        
        # 定义可能的替代列名
        alternate_names = {
            'latitude': ['lat', '纬度', 'Latitude', 'LAT'],
            'longitude': ['lon', 'lng', '经度', 'Longitude', 'LON', 'LNG']
        }
        
        # 检查每个必需的列
        for required_col in required_columns:
            # 如果列不存在，尝试查找替代列名
            if required_col not in measure_df.columns:
                found = False
                for alt_name in alternate_names[required_col]:
                    if alt_name in measure_df.columns:
                        column_mapping[alt_name] = required_col
                        found = True
                        break
                if not found:
                    logger.error(f"找不到{required_col}列或其替代列")
                    return pd.DataFrame()
        
        # 重命名列（如果需要）
        if column_mapping:
            measure_df = measure_df.rename(columns=column_mapping)
            logger.info(f"已重命名列: {column_mapping}")
        
        logger.info(f"成功读取人工采样数据，共 {len(measure_df)} 条记录")
        return measure_df
    except Exception as e:
        logger.error(f"读取人工采样数据失败: {str(e)}")
        return pd.DataFrame()

def merge_data_files(indices_file: str, pos_file: str, output_file: Optional[str] = None) -> pd.DataFrame:
    """合并INDEXS.CSV（水质指标）和POS.TXT（位置信息）文件
    
    Args:
        indices_file: 水质指标文件路径(INDEXS.CSV)
        pos_file: 位置文件路径(POS.TXT)
        output_file: 可选的输出文件路径
        
    Returns:
        合并后的DataFrame，失败返回空DataFrame
    """
    try:
        logger.info(f"开始合并数据文件")
        logger.info(f"指标文件: {indices_file}")
        logger.info(f"位置文件: {pos_file}")
        
        # 读取指标文件
        indices_df = pd.read_csv(indices_file, encoding='utf-8', header=0, index_col=0)
        logger.info(f"指标文件包含 {len(indices_df)} 行数据")
        
        # 读取位置文件
        pos_df = read_position_data(pos_file)
        logger.info(f"位置文件包含 {len(pos_df)} 行数据")
        
        # 确保索引类型一致
        logger.info(f"pos_df索引类型: {pos_df.index.dtype}, indices_df索引类型: {indices_df.index.dtype}")
        # 将两个DataFrame的索引都转换为字符串类型
        pos_df.index = pos_df.index.astype(str)
        indices_df.index = indices_df.index.astype(str)
        logger.info("已将两个DataFrame的索引统一转换为字符串类型")
        
                # 检查两个文件的行数是否匹配
        if len(indices_df) != len(pos_df):
            logger.warning(f"指标文件和位置文件的行数不匹配: {len(indices_df)} vs {len(pos_df)}")
            
            logger.warning("尝试通过索引交集对齐指标文件和位置文件的数据")
            common_index = indices_df.index.intersection(pos_df.index)
            if len(common_index) == 0:
                logger.error("指标文件和位置文件没有共同的索引，无法合并")
                return pd.DataFrame()
            indices_df = indices_df.loc[common_index]
            pos_df = pos_df.loc[common_index]
            logger.info(f"通过索引交集对齐后，数据行数为: {len(common_index)}")
            
        # 合并数据
        merged_df = pd.concat([pos_df, indices_df], axis=1)
        logger.info(f"合并后的数据包含 {len(merged_df)} 行和 {len(merged_df.columns)} 列")
        
        # 可选：保存到输出文件
        if output_file:
            merged_df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"合并数据已保存到: {output_file}")
        
        return merged_df
    except Exception as e:
        logger.error(f"合并数据文件时出错: {str(e)}")
        return pd.DataFrame() 