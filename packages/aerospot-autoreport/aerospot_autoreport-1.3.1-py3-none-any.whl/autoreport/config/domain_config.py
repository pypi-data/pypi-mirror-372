"""
领域配置常量
定义系统支持的领域和默认配置
"""

# 默认领域配置
DEFAULT_DOMAIN = "water_quality"

# 支持的领域列表（按优先级排序）
SUPPORTED_DOMAINS = [
    "water_quality",  # 水质监测（默认）
    "agriculture",    # 农业监测
]

# 领域元数据
DOMAIN_METADATA = {
    "water_quality": {
        "display_name": "水质监测",
        "description": "用于水体环境质量监测和分析",
        "default_indicators": ["nh3n", "tp", "cod", "turbidity", "chla"],
        "required_dependencies": ["autowaterqualitymodeler"],
    },
    "agriculture": {
        "display_name": "农业监测", 
        "description": "用于农作物和土壤环境监测分析",
        "default_indicators": ["nitrogen", "phosphorus", "potassium", "ph", "moisture"],
        "required_dependencies": [],
    }
}

def get_default_domain() -> str:
    """获取默认领域"""
    return DEFAULT_DOMAIN

def get_supported_domains() -> list:
    """获取支持的领域列表"""
    return SUPPORTED_DOMAINS.copy()

def get_domain_metadata(domain: str) -> dict:
    """获取领域元数据"""
    return DOMAIN_METADATA.get(domain, {})

def is_domain_supported(domain: str) -> bool:
    """检查领域是否受支持"""
    return domain in SUPPORTED_DOMAINS

def get_fallback_domain() -> str:
    """获取备用领域（如果指定领域不可用）"""
    return DEFAULT_DOMAIN