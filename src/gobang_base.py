import tkinter as tk

class GobangBase:
    """五子棋游戏基类，包含所有游戏模式共享的核心功能"""
    def __init__(self, root):
        """初始化游戏
        
        Args:
            root: Tkinter根窗口对象
        """
        self.root = root
        self.root.title("五子棋")
        self.root.resizable(False, False)
        
        # 棋盘参数
        self.board_size = 15  # 15x15棋盘
        self.cell_size = 40   # 每个格子大小
        self.margin = 30      # 棋盘边距
        
        # 颜色定义
        self.bg_color = "#E6B889"  # 棋盘背景色
        self.line_color = "#000000"  # 线条颜色
        self.black_stone = "#000000"  # 黑棋
        self.white_stone = "#FFFFFF"  # 白棋
        
        # 游戏状态
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]  # 0:空, 1:黑, 2:白
        self.current_player = 1  # 1:黑棋, 2:白棋
        self.game_over = False
        self.last_move = None  # 上一步落子位置 (x, y)
        
        # 创建画布
        self.canvas = tk.Canvas(
            root, 
            width=self.board_size * self.cell_size + 2 * self.margin, 
            height=self.board_size * self.cell_size + 2 * self.margin,
            bg=self.bg_color
        )
        self.canvas.pack()
        
        # 绘制棋盘
        self.draw_board()
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_click)
        
        # 添加按钮区域
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)
        
        # 添加重置按钮
        self.reset_button = tk.Button(self.button_frame, text="重置游戏", command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        # 添加返回主菜单按钮
        self.back_button = tk.Button(self.button_frame, text="返回主菜单", command=self.back_to_menu)
        self.back_button.pack(side=tk.LEFT, padx=10)
        
        # 显示当前玩家
        self.status_var = tk.StringVar()
        self.status_var.set("当前玩家: 黑棋")
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Arial", 12))
        self.status_label.pack()
    
    def draw_board(self):
        """绘制棋盘，包括横线、竖线和星位点"""
        
        # 绘制横线
        for i in range(self.board_size):
            y = self.margin + i * self.cell_size
            self.canvas.create_line(
                self.margin, y, 
                self.margin + (self.board_size - 1) * self.cell_size, y,
                fill=self.line_color
            )
        
        # 绘制竖线
        for i in range(self.board_size):
            x = self.margin + i * self.cell_size
            self.canvas.create_line(
                x, self.margin, 
                x, self.margin + (self.board_size - 1) * self.cell_size,
                fill=self.line_color
            )
        
        # 绘制星位点
        star_points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for x, y in star_points:
            center_x = self.margin + x * self.cell_size
            center_y = self.margin + y * self.cell_size
            self.canvas.create_oval(
                center_x - 5, center_y - 5, 
                center_x + 5, center_y + 5,
                fill=self.line_color
            )
    
    def on_click(self, event):
        """处理鼠标点击事件，包括计算点击位置、落子、检查胜负和切换玩家
        
        Args:
            event: 鼠标点击事件对象
        """
        if self.game_over:
            return
        
        # 计算点击位置对应的棋盘坐标
        x = (event.x - self.margin + self.cell_size // 2) // self.cell_size
        y = (event.y - self.margin + self.cell_size // 2) // self.cell_size
        
        # 检查位置是否有效
        if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[y][x] == 0:
            # 落子
            self.board[y][x] = self.current_player
            # 记录上一步落子位置
            self.last_move = (x, y)
            # 重新绘制棋盘和所有棋子，以清除之前的标记并绘制新标记
            self.redraw_board()
            
            # 检查胜负
            if self.check_win(x, y, self.current_player):
                winner = "黑棋" if self.current_player == 1 else "白棋"
                self.status_var.set(f"游戏结束! {winner}获胜!")
                self.game_over = True
                return
            
            # 切换玩家
            self.current_player = 2 if self.current_player == 1 else 1
            
            # 更新状态显示
            current_player_text = "黑棋" if self.current_player == 1 else "白棋"
            self.status_var.set(f"当前玩家: {current_player_text}")
    
    def draw_stone(self, x, y, player):
        """绘制棋子
        
        Args:
            x: 棋子的横坐标
            y: 棋子的纵坐标
            player: 玩家编号（1为黑棋，2为白棋）
        """
        center_x = self.margin + x * self.cell_size
        center_y = self.margin + y * self.cell_size
        color = self.black_stone if player == 1 else self.white_stone
        
        self.canvas.create_oval(
            center_x - self.cell_size // 2 + 2, 
            center_y - self.cell_size // 2 + 2, 
            center_x + self.cell_size // 2 - 2, 
            center_y + self.cell_size // 2 - 2,
            fill=color, outline=self.line_color
        )
        
        # 标记上一步落子位置
        if self.last_move == (x, y):
            # 为黑棋标记红色小点，为白棋标记红色小点，使用红色确保在两种颜色棋子上都清晰可见
            mark_color = "#FF0000"  # 红色标记
            mark_outline = "#FFFFFF" if player == 1 else "#000000"  # 黑棋用白色边框，白棋用黑色边框
            self.canvas.create_oval(
                center_x - 10, center_y - 10, 
                center_x + 10, center_y + 10,
                fill=mark_color, outline=mark_outline, width=3
            )
    
    def check_win(self, x, y, player):
        """检查是否获胜
        
        Args:
            x: 最后落子的横坐标
            y: 最后落子的纵坐标
            player: 玩家编号（1为黑棋，2为白棋）
            
        Returns:
            bool: 是否获胜
        """
        # 检查四个方向：横向、纵向、左上到右下、右上到左下
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1  # 当前位置已经有一个棋子
            
            # 向正方向检查
            nx, ny = x + dx, y + dy
            while 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[ny][nx] == player:
                count += 1
                nx += dx
                ny += dy
            
            # 向反方向检查
            nx, ny = x - dx, y - dy
            while 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[ny][nx] == player:
                count += 1
                nx -= dx
                ny -= dy
            
            # 五连子获胜
            if count >= 5:
                return True
        
        return False
    
    def redraw_board(self):
        """重新绘制棋盘和所有棋子，清除之前的标记"""
        # 清空画布并重新绘制棋盘
        self.canvas.delete("all")
        self.draw_board()
        
        # 重新绘制所有棋子
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.board[y][x] != 0:
                    self.draw_stone(x, y, self.board[y][x])
    
    def reset_game(self):
        """重置游戏，清空棋盘并重新开始"""
        # 清空棋盘
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.last_move = None  # 清空上一步落子位置
        
        # 清空画布并重新绘制棋盘
        self.canvas.delete("all")
        self.draw_board()
        
        # 更新状态
        self.status_var.set("当前玩家: 黑棋")
    
    def back_to_menu(self):
        """返回主菜单，销毁当前窗口并重新启动应用"""
        self.root.destroy()
        import subprocess
        import sys
        subprocess.Popen([sys.executable, "main.py"])
        sys.exit()