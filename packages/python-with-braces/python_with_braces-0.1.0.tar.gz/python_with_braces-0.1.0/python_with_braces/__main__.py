#!/usr/bin/env python3
"""
Python With Braces - 主模块入口点

这个文件允许用户通过 `python -m python_with_braces` 命令来运行Python With Braces工具。
"""

import sys

# 导入并执行主函数
if __name__ == "__main__":
    from python_with_braces.core import main
    sys.exit(main())