#!/usr/bin/env python3
"""
Python With Braces - 让Python支持大括号语法的预处理器

这个模块允许你编写使用大括号而不是缩进的Python代码。
它会在执行前将大括号语法转换为标准的Python冒号缩进语法。
"""
import sys
import traceback
import builtins

# 确保Python版本兼容性
if sys.version_info < (3, 6):
    sys.exit("Python With Braces 需要 Python 3.6 或更高版本")

# 仅在Python 3.9+中提供的类型注解，但保持向后兼容性
try:
    from typing import Dict, List, Tuple, Any, Optional
except ImportError:
    # 在较低版本的Python中使用通用类型
    Dict = dict
    List = list
    Tuple = tuple
    Any = object
    Optional = object

class PythonWithBraces:
    """Python大括号语法预处理器"""
    
    def __init__(self):
        # 缩进字符串（默认4个空格）
        self.indent_str = '    '
    
    def process_file(self, file_path: str) -> str:
        """处理文件并返回标准Python代码"""
        # 尝试多种常见编码格式，提高兼容性
        encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-16']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    code = f.read()
                return self.process_code(code)
            except UnicodeDecodeError:
                continue
        
        # 如果所有编码都失败，显示错误信息
        print(f"错误: 无法解码文件 '{file_path}'。请检查文件编码格式。")
        raise UnicodeDecodeError("all_encodings", b"", 0, 1, "无法使用任何支持的编码格式解码文件")
    
    def process_code(self, code: str) -> str:
        """将使用大括号的代码转换为标准Python代码"""
        # 步骤1: 处理f-string中的花括号，避免与代码块大括号混淆
        code = self._preserve_fstring_braces(code)
        
        # 步骤2: 处理代码块大括号
        lines = code.split('\n')
        processed_lines = []
        indent_level = 0
        
        for line in lines:
            line_stripped = line.strip()
            
            # 跳过空行和纯注释行
            if not line_stripped or line_stripped.startswith('#'):
                processed_lines.append(line)
                continue
            
            # 处理右大括号（减少缩进）
            if '}' in line_stripped:
                # 计算右大括号数量
                close_braces = line_stripped.count('}')
                # 减少缩进级别
                indent_level = max(0, indent_level - close_braces)
                # 移除右大括号
                line_stripped = line_stripped.replace('}', '').strip()
                # 如果移除后为空，则不添加这一行
                if not line_stripped:
                    continue
            
            # 添加当前行（带正确缩进）
            processed_line = self.indent_str * indent_level + line_stripped
            processed_lines.append(processed_line)
            
            # 处理左大括号（增加缩进）
            if '{' in line_stripped:
                # 计算左大括号数量
                open_braces = line_stripped.count('{')
                # 在当前行中将左大括号替换为冒号
                processed_lines[-1] = processed_lines[-1].replace('{', ':')
                # 增加缩进级别
                indent_level += open_braces
        
        # 步骤3: 恢复f-string中的花括号
        processed_code = '\n'.join(processed_lines)
        processed_code = self._restore_fstring_braces(processed_code)
        
        return processed_code
    
    def _preserve_fstring_braces(self, code: str) -> str:
        """保留f-string中的花括号，避免被错误处理"""
        # 使用字符串处理方法来识别f-string并替换其中的花括号
        result = []
        in_fstring = False
        fstring_quote = None
        fstring_content = []
        
        i = 0
        while i < len(code):
            # 检查是否进入f-string
            if (i < len(code) - 1 and code[i] == 'f' and code[i+1] in ['"', "'"] and not in_fstring):
                in_fstring = True
                fstring_quote = code[i+1]
                result.append('f' + fstring_quote)
                i += 2
                continue
            
            # 检查是否退出f-string
            if (in_fstring and code[i] == fstring_quote and (i == 0 or code[i-1] != '\\')):
                in_fstring = False
                # 处理f-string内容中的花括号
                processed_content = ''.join(fstring_content)
                processed_content = processed_content.replace('{', '<<<BRACE>>>')
                processed_content = processed_content.replace('}', '<<<END_BRACE>>>')
                result.append(processed_content + fstring_quote)
                fstring_content = []
                i += 1
                continue
            
            # 在f-string内部
            if in_fstring:
                fstring_content.append(code[i])
            else:
                # 在f-string外部，直接添加字符
                result.append(code[i])
            
            i += 1
        
        return ''.join(result)
    
    def _restore_fstring_braces(self, code: str) -> str:
        """恢复f-string中的花括号"""
        # 将特殊标记替换回花括号
        restored_code = code.replace('<<<BRACE>>>', '{')
        restored_code = restored_code.replace('<<<END_BRACE>>>', '}')
        return restored_code
    
    def execute_file(self, file_path: str, globals_dict: Dict[str, Any] = None, locals_dict: Dict[str, Any] = None) -> Any:
        """执行使用大括号语法的Python文件"""
        try:
            # 处理文件，转换为标准Python代码
            processed_code = self.process_file(file_path)
            
            # 如果没有提供命名空间，使用默认命名空间
            if globals_dict is None:
                globals_dict = {}
            
            # 确保内置函数可用
            globals_dict.update({
                '__builtins__': builtins,
                '__file__': file_path,
                '__name__': '__main__'
            })
            
            # 执行处理后的代码
            exec(processed_code, globals_dict, locals_dict)
            return globals_dict
        except FileNotFoundError:
            print(f"错误: 找不到文件 '{file_path}'")
            return None
        except IOError as e:
            print(f"文件读取错误: {e}")
            return None
        except Exception as e:
            print(f"执行错误: {e}")
            print("\n转换后的代码:\n", processed_code)
            traceback.print_exc()
            return None
    
    def execute_code(self, code: str, globals_dict: Dict[str, Any] = None, locals_dict: Dict[str, Any] = None) -> Any:
        """执行使用大括号语法的Python代码字符串"""
        try:
            # 处理代码，转换为标准Python代码
            processed_code = self.process_code(code)
            
            # 如果没有提供命名空间，使用默认命名空间
            if globals_dict is None:
                globals_dict = {}
            
            # 确保内置函数可用
            globals_dict.update({
                '__builtins__': builtins,
                '__name__': '__main__'
            })
            
            # 执行处理后的代码
            exec(processed_code, globals_dict, locals_dict)
            return globals_dict
        except Exception as e:
            print(f"执行错误: {e}")
            traceback.print_exc()
            return None

    def validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """验证转换后的代码是否有语法错误"""
        processed_code = self.process_code(code)
        try:
            # 使用Python的ast模块来验证语法
            import ast
            ast.parse(processed_code)
            return True, None
        except SyntaxError as e:
            return False, str(e)

# 创建一个简单的示例文件，演示如何使用大括号语法
EXAMPLE_CODE = """# 这是一个使用大括号语法的Python示例

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

# 定义一个有返回值的函数
def calculate(a, b){
    if a > b{
        return a - b;
    } elif a < b{
        return b - a;
    } else {
        return 0;
    }
}

# 调用带返回值的函数
result = calculate(5, 3);
print(f"结果: {result}");
"""

# 命令行接口
def main():
    """命令行入口函数"""
    # 创建预处理器实例
    processor = PythonWithBraces()
    
    # 处理命令行参数
    if len(sys.argv) < 2 or sys.argv[1] in ('--help', '-h'):
        # 显示帮助信息
        print("Python With Braces (PWB) - 让Python支持大括号语法的预处理器")
        print("\n用法:")
        print("  python-with-braces <filename>  # 执行包含大括号语法的Python文件")
        print("  python-with-braces --help     # 显示帮助信息")
        print("  python-with-braces            # 创建并执行示例文件")
        print("  pwb <filename>                # 简短别名，执行包含大括号语法的Python文件")
        print("  pwb --help                    # 简短别名，显示帮助信息")
        print("  pwb                           # 简短别名，创建并执行示例文件")
        print("\n示例:")
        print("  python-with-braces my_script.braces.py")
        print("  python-with-braces my_code.py")
        print("  pwb my_script.braces.py       # 使用简短别名")
        print("\n注: Python With Braces 的正式简称为 PWB")
        
        if len(sys.argv) < 2:
            # 如果没有提供文件名，创建一个示例文件
            example_file = "example_with_braces.py"
            with open(example_file, 'w', encoding='utf-8') as f:
                f.write(EXAMPLE_CODE)
            
            print(f"\n已创建示例文件: {example_file}")
            print("\n执行示例文件:")
            processor.execute_file(example_file)
        
        return
        
    # 获取文件名
    file_path = sys.argv[1]
    
    try:
        # 执行文件
        print(f"执行文件: {file_path}")
        processor.execute_file(file_path)
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{file_path}'")
        print("请检查文件路径是否正确，或使用 --help 查看用法")
        sys.exit(1)
    except Exception as e:
        print(f"执行时出错: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()