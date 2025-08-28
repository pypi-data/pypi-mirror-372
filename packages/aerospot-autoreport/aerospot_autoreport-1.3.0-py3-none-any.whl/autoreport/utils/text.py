import unicodedata


def is_numeric(char):
    """判断字符是否为数字
    
    Args:
        char: 要判断的字符
        
    Returns:
        是否为数字
    """
    return char.isdigit()

def is_chinese(char: str) -> bool:
    if not char:
        return False
    try:
        name = unicodedata.name(char)
        return 'CJK UNIFIED IDEOGRAPH' in name
    except ValueError:
        return False

# 导出所有符号以保持向后兼容性
__all__ = [
    'is_chinese',
    'is_numeric'
] 