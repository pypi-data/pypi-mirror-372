# 数据处理模块 (processor/data)

数据处理模块是AeroSpotReportV2项目的核心组件，负责对航测数据和实测数据进行处理、分析和匹配。该模块采用模块化设计，将不同功能拆分为独立的子模块，提高了代码的可维护性和可扩展性。

## 模块结构

```
processor/data/
├── __init__.py       # 模块初始化，导出核心类和函数
├── processor.py      # 数据处理器核心类
├── standardizer.py   # 数据标准化功能
├── analyzer.py       # 数据分析功能
├── matcher.py        # 数据匹配功能
└── utils.py          # 辅助功能函数
```

## 核心功能

### 数据处理器 (processor.py)

`DataProcessor` 类是数据处理的核心，提供了以下主要功能：

- `process_data`: 处理航测数据，标准化列名和指标名称，计算统计信息
- `match_and_analyze_data`: 匹配和分析航测数据与实测数据的关系

### 数据标准化 (standardizer.py)

提供数据标准化相关功能：

- `standardize_column_names`: 标准化列名，将经纬度相关列统一为标准格式
- `standardize_indicator_names`: 标准化指标名称，统一不同表示的水质指标名称

### 数据分析 (analyzer.py)

提供数据分析相关功能：

- `calculate_statistics`: 计算每个指标的基本统计信息（最小值、最大值、均值、标准差等）
- `generate_data_summary`: 生成数据摘要，包括样本数量、指标列表、地理范围等
- `analyze_errors`: 分析原始航测数据和新反演数据相对于实测数据的误差

### 数据匹配 (matcher.py)

提供航测数据与实测数据的匹配功能：

- `find_common_indicators`: 查找航测数据与实测数据的共同指标
- `match_nearest_points`: 为每个实测点找到最近的航测点
- `handle_invalid_values`: 处理无效值和缺失数据
- `match_and_analyze_data`: 匹配和分析航测数据与实测数据

### 辅助功能 (utils.py)

提供辅助功能函数：

- `get_indicator_unit`: 根据指标名称获取相应的单位

## 使用示例

```python
from processor.data import DataProcessor

# 初始化数据处理器
data_processor = DataProcessor(config={})

# 处理航测数据
processed_data = data_processor.process_data(merged_data)

# 匹配和分析航测数据与实测数据
result = data_processor.match_and_analyze_data(
    merged_data=processed_data['processed_data'],
    measure_data=measure_data,
    ref_data=ref_data
)
```

## 数据流程

1. **数据加载**：从CSV、TXT等格式文件加载原始数据
2. **数据标准化**：统一列名和指标名称格式
3. **统计分析**：计算基本统计信息
4. **数据匹配**：将航测数据与实测数据进行地理位置匹配
5. **模型建立**：基于匹配的数据建立新的反演模型
6. **误差分析**：分析原始数据和新反演数据与实测数据的误差

## 注意事项

- 输入数据必须包含经纬度信息（latitude, longitude）
- 标准化过程会改变原始列名，请在之后的处理中使用标准化后的列名
- 数据匹配基于地理距离计算，确保经纬度数据准确
- 误差分析会自动处理无效值和缺失数据 