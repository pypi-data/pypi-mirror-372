"""
数值计算安全工具模块
提供数值稳定性保护和安全计算函数
"""
import math
import numpy as np
from typing import Union, Optional
from functools import wraps


class NumericalSafety:
    """数值稳定性保护工具类"""
    
    # 常用的数值阈值
    MACHINE_EPS = np.finfo(float).eps
    SAFE_EPS = MACHINE_EPS * 1000
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, 
                   default: float = 0.0, eps: float = None) -> float:
        """
        安全除法，避免除零错误
        
        Args:
            numerator: 分子
            denominator: 分母
            default: 当除法不可行时的默认值
            eps: 判断零值的阈值
            
        Returns:
            除法结果或默认值
        """
        if eps is None:
            eps = NumericalSafety.SAFE_EPS
        
        if not (math.isfinite(numerator) and math.isfinite(denominator)):
            return default
        
        if abs(denominator) < eps:
            return default
        
        result = numerator / denominator
        return result if math.isfinite(result) else default
    
    @staticmethod
    def safe_sqrt(x: float, eps: float = None) -> float:
        """
        安全的平方根计算
        
        Args:
            x: 输入值
            eps: 负数阈值
            
        Returns:
            平方根值
        """
        if eps is None:
            eps = NumericalSafety.SAFE_EPS
        
        if not math.isfinite(x):
            return 0.0
        
        if x < -eps:
            return 0.0
        
        return math.sqrt(max(0.0, x))
    
    @staticmethod
    def safe_log(x: float, eps: float = None) -> Optional[float]:
        """
        安全的对数计算
        
        Args:
            x: 输入值
            eps: 最小正值阈值
            
        Returns:
            对数值或None
        """
        if eps is None:
            eps = NumericalSafety.SAFE_EPS
        
        if not math.isfinite(x) or x <= eps:
            return None
        
        result = math.log(x)
        return result if math.isfinite(result) else None
    
    @staticmethod
    def safe_acos(x: float) -> float:
        """安全的反余弦计算"""
        if not math.isfinite(x):
            return 0.0
        return math.acos(max(-1.0, min(1.0, x)))
    
    @staticmethod
    def safe_asin(x: float) -> float:
        """安全的反正弦计算"""
        if not math.isfinite(x):
            return 0.0
        return math.asin(max(-1.0, min(1.0, x)))
    
    @staticmethod
    def is_valid_number(x: Union[float, int]) -> bool:
        """检查数字是否有效（非NaN且有限）"""
        try:
            return math.isfinite(float(x))
        except (ValueError, TypeError, OverflowError):
            return False
    
    @staticmethod
    def clamp(x: float, min_val: float, max_val: float) -> float:
        """将数值限制在指定范围内"""
        if not math.isfinite(x):
            return min_val
        return max(min_val, min(max_val, x))
    
    @staticmethod
    def safe_power(base: float, exponent: float, eps: float = None) -> float:
        """
        安全的幂运算
        
        Args:
            base: 底数
            exponent: 指数
            eps: 判断零的阈值
            
        Returns:
            幂运算结果
        """
        if eps is None:
            eps = NumericalSafety.SAFE_EPS
        
        if not (math.isfinite(base) and math.isfinite(exponent)):
            return 0.0
        
        # 特殊情况处理
        if abs(base) < eps:
            return 0.0 if exponent > 0 else 1.0
        
        if base < 0 and abs(exponent % 1) > eps:
            # 负数的非整数幂
            return 0.0
        
        try:
            result = base ** exponent
            return result if math.isfinite(result) else 0.0
        except (ValueError, OverflowError, ZeroDivisionError):
            return 0.0
    
    @staticmethod
    def relative_error(predicted: float, actual: float, 
                      abs_threshold: float = None) -> Optional[float]:
        """
        安全的相对误差计算
        
        Args:
            predicted: 预测值
            actual: 实际值
            abs_threshold: 绝对值阈值
            
        Returns:
            相对误差或None
        """
        if abs_threshold is None:
            abs_threshold = NumericalSafety.SAFE_EPS
        
        if not (NumericalSafety.is_valid_number(predicted) and 
                NumericalSafety.is_valid_number(actual)):
            return None
        
        if abs(actual) < abs_threshold:
            return None
        
        return NumericalSafety.safe_divide(
            predicted - actual, actual, default=None
        )


def validate_numeric_inputs(*param_names):
    """
    验证数值输入的装饰器
    
    Args:
        param_names: 需要验证的参数名列表
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查位置参数
            for i, param_name in enumerate(param_names):
                if i < len(args):
                    val = args[i]
                    if not NumericalSafety.is_valid_number(val):
                        raise ValueError(f"参数 {param_name} 包含无效数值: {val}")
            
            # 检查关键字参数
            for param_name in param_names:
                if param_name in kwargs:
                    val = kwargs[param_name]
                    if not NumericalSafety.is_valid_number(val):
                        raise ValueError(f"参数 {param_name} 包含无效数值: {val}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def safe_operation(default_return=None, log_errors=True):
    """
    安全操作装饰器，捕获数值计算异常
    
    Args:
        default_return: 异常时的默认返回值
        log_errors: 是否记录错误日志
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ZeroDivisionError, ValueError, OverflowError, 
                    FloatingPointError) as e:
                if log_errors:
                    import logging
                    logger = logging.getLogger(func.__module__)
                    logger.warning(f"数值计算异常在 {func.__name__}: {str(e)}")
                return default_return
        return wrapper
    return decorator


# 常用的安全数学函数
@safe_operation(default_return=0.0)
def safe_sqrt(x):
    """安全的平方根函数"""
    return NumericalSafety.safe_sqrt(x)


@safe_operation(default_return=0.0)
def safe_divide(a, b):
    """安全的除法函数"""
    return NumericalSafety.safe_divide(a, b)


@safe_operation(default_return=None)
def safe_log(x):
    """安全的对数函数"""
    return NumericalSafety.safe_log(x)


# 向量化版本的安全函数
def safe_divide_vectorized(numerator, denominator, default=0.0, eps=None):
    """向量化的安全除法"""
    if eps is None:
        eps = NumericalSafety.SAFE_EPS
    
    num = np.asarray(numerator)
    den = np.asarray(denominator)
    
    # 检查有效性
    valid_mask = (np.isfinite(num) & np.isfinite(den) & 
                  (np.abs(den) >= eps))
    
    result = np.full_like(num, default, dtype=float)
    result[valid_mask] = num[valid_mask] / den[valid_mask]
    
    return result


def safe_relative_error_vectorized(predicted, actual, abs_threshold=None):
    """向量化的安全相对误差计算"""
    if abs_threshold is None:
        abs_threshold = NumericalSafety.SAFE_EPS
    
    pred = np.asarray(predicted)
    act = np.asarray(actual)
    
    # 检查有效性
    valid_mask = (np.isfinite(pred) & np.isfinite(act) & 
                  (np.abs(act) >= abs_threshold))
    
    result = np.full_like(pred, np.nan, dtype=float)
    result[valid_mask] = ((pred[valid_mask] - act[valid_mask]) / 
                         act[valid_mask] * 100)
    
    return result