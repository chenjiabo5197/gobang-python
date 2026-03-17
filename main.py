import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from game_mode_selector import GameModeSelector

"""五子棋游戏主入口，创建游戏模式选择器"""

if __name__ == "__main__":
    """创建主窗口并启动游戏模式选择器"""
    root = tk.Tk()
    selector = GameModeSelector(root)
    root.mainloop()