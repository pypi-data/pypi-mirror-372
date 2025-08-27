"""
Python With Braces (PWB) - 让Python支持大括号语法的预处理器

这个包允许你编写使用大括号而不是缩进的Python代码。
它会在执行前将大括号语法转换为标准的Python冒号缩进语法。
正式简称为PWB。
"""

import sys

# 确保Python版本兼容性
if sys.version_info < (3, 6):
    raise ImportError("Python With Braces 需要 Python 3.6 或更高版本")

# 版本信息
__version__ = '0.1.0'

# 安全导入核心模块
try:
    from .core import PythonWithBraces
    # 定义包的公共接口
    __all__ = ['PythonWithBraces']
except Exception as e:
    # 如果导入失败，提供有用的错误信息
    print(f"警告: 无法导入PythonWithBraces类: {e}")
    __all__ = []