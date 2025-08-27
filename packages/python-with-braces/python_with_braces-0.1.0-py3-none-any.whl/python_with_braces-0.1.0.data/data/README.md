# Python With Braces (PWB)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个让Python支持大括号语法的预处理器库。正式简称为 **PWB**。

## 功能

这个库允许你编写使用大括号而不是缩进的Python代码，它会在执行前将大括号语法转换为标准的Python冒号缩进语法。例如：

大括号语法（可执行）：
```python
if a == 1{
    print("123");
}
else{
    print("456");
}
```

会被自动转换为标准Python语法并执行。

## 特性

- 支持所有Python控制结构（if/else/elif, for, while, def, class等）
- 正确处理f-string中的花括号
- 提供命令行接口和Python库接口
- 无外部依赖
- 跨平台兼容（Windows, macOS, Linux等）
- 多Python版本支持（Python 3.6+，包括最新的Python 3.13）
- 多编码格式支持（UTF-8, Latin-1, CP1252等）

## 安装

### 使用pip安装

```bash
pip install python_with_braces  # 或简称为 PWB
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/pythonwithbraces/python_with_braces.git
cd python_with_braces

# 安装
pip install -e .
```

## 发布到PyPI（供开发者参考）

要让所有人都能通过`pip install python_with_braces`安装这个库，需要将其发布到Python Package Index (PyPI)。以下是发布步骤：

1. 安装必要的工具：
```bash
pip install build twine
```

2. 构建包：
```bash
python -m build
```

3. 上传到PyPI（需要PyPI账号）：
```bash
python -m twine upload dist/*
```

## 使用方法 (PWB)

PWB 提供两种使用方式：命令行接口和Python库接口。

### 命令行使用

安装后，可以使用`python-with-braces`命令：

```bash
python-with-braces <filename>
```

或者直接使用Python执行：

```bash
python python_with_braces.py <filename>
```

例如，创建一个名为`my_script.py`的文件，内容使用大括号语法，然后执行：

```bash
python-with-braces my_script.py
```

如果不提供文件名，将创建并执行一个示例文件。

### 作为库使用

```python
from python_with_braces import PythonWithBraces

# 创建预处理器实例
processor = PythonWithBraces()

# 执行使用大括号语法的文件
processor.execute_file('my_script.py')

# 执行代码字符串
code = "if a == 1{\n    print(123);\n}"
processor.execute_code(code)

# 仅转换代码（不执行）
standard_python_code = processor.process_code(code)

# 验证代码语法
is_valid, error_msg = processor.validate_syntax(code)
if not is_valid:
    print(f"语法错误: {error_msg}")
```

## 语法规则

使用大括号语法时，请遵循以下规则：

1. 使用`{`代替冒号`:`来标记代码块的开始
2. 使用`}`来标记代码块的结束
3. 语句结尾可以选择性地添加分号`;`（类似其他语言的习惯）
4. 保持缩进可以提高代码可读性，但不是必需的
5. 支持所有Python的控制结构：`if`/`else`/`elif`, `for`, `while`, `def`, `class`等

## API 文档

### PythonWithBraces 类

#### `__init__(self)`
初始化预处理器实例。

#### `process_file(self, file_path: str) -> str`
处理文件并返回标准Python代码。
- `file_path`: 要处理的文件路径
- 返回: 转换后的标准Python代码字符串

#### `process_code(self, code: str) -> str`
将使用大括号的代码转换为标准Python代码。
- `code`: 要处理的代码字符串
- 返回: 转换后的标准Python代码字符串

#### `execute_file(self, file_path: str, globals_dict: Dict[str, Any] = None, locals_dict: Dict[str, Any] = None) -> Any`
执行使用大括号语法的Python文件。
- `file_path`: 要执行的文件路径
- `globals_dict`: 全局命名空间（可选）
- `locals_dict`: 局部命名空间（可选）
- 返回: 全局命名空间字典

#### `execute_code(self, code: str, globals_dict: Dict[str, Any] = None, locals_dict: Dict[str, Any] = None) -> Any`
执行使用大括号语法的Python代码字符串。
- `code`: 要执行的代码字符串
- `globals_dict`: 全局命名空间（可选）
- `locals_dict`: 局部命名空间（可选）
- 返回: 全局命名空间字典

#### `validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]`
验证转换后的代码是否有语法错误。
- `code`: 要验证的代码字符串
- 返回: (是否有效, 错误信息) 的元组

## 示例代码

```python
# 函数定义
def hello_world(){
    print("Hello, World with Braces!");
}

# 调用函数
hello_world();

# 条件语句
a = 1;
if a == 1{
    print("a 等于 1");
} else {
    print("a 不等于 1");
}

# 循环语句
for i in range(5){
    if i % 2 == 0{
        print(f"偶数: {i}");
    } else {
        print(f"奇数: {i}");
    }
}

# 嵌套结构
for i in range(3){
    if i == 0{
        for j in range(2){
            print(f"i={i}, j={j}");
        }
    } elif i == 1{
        print("i=1");
    } else {
        print("i=2");
    }
}

# 类定义
class Person{
    def __init__(self, name, age){
        self.name = name;
        self.age = age;
    }
    
    def greet(self){
        print(f"你好，我是{self.name}，今年{self.age}岁。");
    }
}

# 创建类实例并调用方法
person = Person("张三", 30);
person.greet();
```

## 注意事项

1. 这是一个实验性工具，主要用于教育目的和个人喜好
2. 对于复杂的Python代码（如多行字符串、嵌套引号等）可能存在转换问题
3. 建议在使用前测试代码，确保转换和执行正确

## 贡献指南

欢迎贡献代码！请按照以下步骤：

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件