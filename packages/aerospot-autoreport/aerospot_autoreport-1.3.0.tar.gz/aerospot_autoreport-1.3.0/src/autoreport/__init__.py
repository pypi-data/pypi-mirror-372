"""
AeroSpot自动化报告生成工具包
==============================

这是一个用于自动生成遥感报告的工具包，主要功能包括：
- 数据下载和处理
- 报告生成
- 资源管理
- 工具函数

主要模块：
- main: 主程序入口
- generator: 报告生成器
- processor: 数据处理模块
- config: 配置管理
- document: 文档生成
- utils: 工具函数
- resources: 资源文件

版本: 动态版本管理
作者: AutoReport Team
"""

# 版本号获取，优先级：包元数据 > _version.py > fallback
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("aerospot-autoreport")
    except PackageNotFoundError:
        # 开发环境或未安装的包，尝试从_version.py获取
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "1.0.0"  # fallback版本
except ImportError:
    # Python < 3.8，使用importlib_metadata
    try:
        from importlib_metadata import version, PackageNotFoundError
        try:
            __version__ = version("aerospot-autoreport")
        except PackageNotFoundError:
            try:
                from ._version import __version__
            except ImportError:
                __version__ = "1.0.0"
    except ImportError:
        # 完全fallback
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "2.0.0"

__author__ = "AutoReport Team"
__email__ = "support@autoreport.com"

# 延迟导入主要的类和函数，避免循环导入
def get_aerospotreportgenerator():
    from .main import AeroSpotReportGenerator
    return AeroSpotReportGenerator

def get_reportgenerator():
    from .generator import ReportGenerator
    return ReportGenerator

# 导出公共接口
__all__ = [
    "get_aerospotreportgenerator",
    "get_reportgenerator",
    "__version__",
    "__author__",
    "__email__"
]