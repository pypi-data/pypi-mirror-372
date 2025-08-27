#!/usr/bin/env python3
"""
Python With Braces - 贪吃蛇小游戏

这是一个作为彩蛋功能的简单贪吃蛇游戏，支持所有Python平台。
"""
import sys
import random
import time
import os

# 检查是否支持颜色输出
has_colors = False
try:
    # 在Windows上启用ANSI转义序列
    if os.name == 'nt':
        os.system('')  # 这会启用Windows命令提示符的ANSI转义序列支持
    has_colors = True
except:
    pass

# 跨平台键盘输入处理函数
def get_key():
    """获取单个按键输入，支持Windows、Linux和macOS"""
    try:
        # Windows平台
        if os.name == 'nt':
            import msvcrt
            return msvcrt.getch().decode('utf-8').lower()
        # Unix/Linux/macOS平台
        else:
            import termios
            import tty
            # 保存终端设置
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                # 设置终端为字符模式
                tty.setraw(sys.stdin.fileno())
                # 读取单个字符
                ch = sys.stdin.read(1)
                return ch.lower()
            finally:
                # 恢复终端设置
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except:
        # 如果出现任何错误，返回空字符串
        return ''

# 检查是否有按键按下
def is_key_pressed():
    """检查是否有按键按下，支持Windows、Linux和macOS"""
    try:
        # Windows平台
        if os.name == 'nt':
            import msvcrt
            return msvcrt.kbhit()
        # Unix/Linux/macOS平台
        else:
            import select
            # 使用select检查是否有输入可读
            return select.select([sys.stdin], [], [], 0)[0] != []
    except:
        # 如果出现任何错误，返回False
        return False

class SnakeGame:
    """贪吃蛇游戏类"""
    def __init__(self):
        # 设置游戏区域大小
        self.width = 40
        self.height = 20
        # 初始化蛇的位置和方向
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = 'RIGHT'
        self.next_direction = 'RIGHT'
        # 初始化食物位置
        self.food = self._generate_food()
        # 初始化分数和游戏状态
        self.score = 0
        self.game_over = False
        # 游戏速度
        self.speed = 0.15
        
    def _generate_food(self):
        """生成食物位置"""
        while True:
            food = (random.randint(1, self.width-2), random.randint(1, self.height-2))
            # 确保食物不在蛇身上
            if food not in self.snake:
                return food
    
    def _clear_screen(self):
        """清屏"""
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    
    def _display(self):
        """显示游戏界面"""
        self._clear_screen()
        
        # 打印顶部边界
        print('+' + '-' * self.width + '+')
        
        for y in range(self.height):
            line = '|'
            for x in range(self.width):
                # 检查是否是蛇头
                if (x, y) == self.snake[0]:
                    if has_colors:
                        line += '\033[91m@\033[0m'  # 红色蛇头
                    else:
                        line += '@'
                # 检查是否是蛇身
                elif (x, y) in self.snake[1:]:
                    if has_colors:
                        line += '\033[92m#\033[0m'  # 绿色蛇身
                    else:
                        line += '#'
                # 检查是否是食物
                elif (x, y) == self.food:
                    if has_colors:
                        line += '\033[93m*\033[0m'  # 黄色食物
                    else:
                        line += '*'
                # 其他位置显示空格
                else:
                    line += ' '
            line += '|'
            print(line)
        
        # 打印底部边界
        print('+' + '-' * self.width + '+')
        # 打印分数
        print(f'  分数: {self.score}  |  控制: W(上) A(左) S(下) D(右)  |  退出: Q')
        print(f'  提示: 吃到食物加分并增长蛇身，撞到墙壁或自己游戏结束')
    
    def _get_input(self):
        """获取用户输入（跨平台支持）"""
        if is_key_pressed():
            key = get_key()
            # 根据按键改变方向，但不能直接反向
            if key == 'w' and self.direction != 'DOWN':
                self.next_direction = 'UP'
            elif key == 's' and self.direction != 'UP':
                self.next_direction = 'DOWN'
            elif key == 'a' and self.direction != 'RIGHT':
                self.next_direction = 'LEFT'
            elif key == 'd' and self.direction != 'LEFT':
                self.next_direction = 'RIGHT'
            elif key == 'q':
                self.game_over = True
    
    def _move(self):
        """移动蛇"""
        # 更新方向
        self.direction = self.next_direction
        
        # 获取蛇头当前位置
        head_x, head_y = self.snake[0]
        
        # 根据方向计算新的蛇头位置
        if self.direction == 'UP':
            head_y -= 1
        elif self.direction == 'DOWN':
            head_y += 1
        elif self.direction == 'LEFT':
            head_x -= 1
        elif self.direction == 'RIGHT':
            head_x += 1
        
        # 检查是否撞到墙壁
        if head_x <= 0 or head_x >= self.width-1 or head_y <= 0 or head_y >= self.height-1:
            self.game_over = True
            return
        
        # 检查是否撞到自己
        if (head_x, head_y) in self.snake:
            self.game_over = True
            return
        
        # 将新的蛇头添加到蛇的身体
        self.snake.insert(0, (head_x, head_y))
        
        # 检查是否吃到食物
        if (head_x, head_y) == self.food:
            # 吃到食物，加分并生成新的食物，但不删除蛇尾
            self.score += 10
            self.food = self._generate_food()
            # 随着分数增加，游戏速度逐渐加快
            if self.score % 50 == 0 and self.speed > 0.05:
                self.speed -= 0.01
        else:
            # 没吃到食物，删除蛇尾
            self.snake.pop()
    
    def run(self):
        """运行游戏主循环"""
        try:
            print("\n=== 欢迎来到贪吃蛇游戏！===\n")
            print("使用 W A S D 键控制蛇的移动，Q 键退出游戏")
            print("3秒后游戏开始...")
            time.sleep(3)
            
            while not self.game_over:
                self._display()
                self._get_input()
                self._move()
                time.sleep(self.speed)
            
            # 游戏结束
            self._clear_screen()
            print("\n=== 游戏结束！===\n")
            print(f"  你的最终得分: {self.score}\n")
            print("感谢游玩贪吃蛇小游戏！")
        except Exception as e:
            print(f"游戏出错: {e}")
        except KeyboardInterrupt:
            print("\n游戏已中断")

def run_snake_game():
    """运行贪吃蛇游戏（跨平台支持）"""
    try:
        # 运行游戏
        game = SnakeGame()
        game.run()
    except Exception as e:
        # 处理可能的异常
        print(f"游戏启动错误: {e}")
        # 在非交互式环境或不支持直接键盘输入的环境中提供友好提示
        print("\n提示: 贪吃蛇游戏需要在支持直接键盘输入的终端中运行。")
        print("在某些IDE或受限环境中，可能无法正常接收键盘输入。")
        print("建议在原生终端（如Windows命令提示符、Linux终端或macOS终端）中运行此游戏。")

if __name__ == "__main__":
    run_snake_game()