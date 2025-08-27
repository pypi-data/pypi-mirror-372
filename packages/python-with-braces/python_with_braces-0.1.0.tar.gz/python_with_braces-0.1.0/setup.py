#!/usr/bin/env python3
"""
Python With Braces - 打包配置文件
"""

from setuptools import setup, find_packages
import io
import os
import sys

# 确保Python版本兼容性
if sys.version_info < (3, 6):
    sys.exit("Python With Braces 需要 Python 3.6 或更高版本")

# 获取当前目录
HERE = os.path.abspath(os.path.dirname(__file__))

# 读取README.md内容作为项目描述
with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# 读取模块版本（从文件中获取或硬编码）
version = '0.1.0'

setup(
    name='python_with_braces',
    version=version,
    description='让Python支持大括号语法的预处理器 (PWB)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Python With Braces Team',
    author_email='contact@pythonwithbraces.com',
    url='https://github.com/pythonwithbraces/python_with_braces',  # 可以替换为实际的项目URL
    license='MIT',  # 选择适合的许可证
    keywords='python, braces, syntax, preprocessor, PWB',
    packages=find_packages(),  # 查找所有包
    package_data={
        '': ['README.md', 'LICENSE', 'requirements.txt'],
        'tests': ['*.py'],
        'python_with_braces': ['*.py'],
    },
    data_files=[
        ('', ['README.md', 'LICENSE', 'requirements.txt'])
    ],
    install_requires=[
        # 这个项目没有外部依赖
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'python_with_braces=python_with_braces.core:main',
            'python-with-braces=python_with_braces.core:main',
            'pwb=python_with_braces.core:main',  # 简短别名
        ],
    },
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False,
)