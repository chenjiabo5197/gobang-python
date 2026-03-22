from gobang_base import GobangBase

class GobangMultiplayer(GobangBase):
    """双人游戏模式，本地对战"""

    def __init__(self, root, layout="vertical"):
        """初始化双人游戏
        
        Args:
            root: Tkinter根窗口对象
            layout: 布局类型，"vertical"、"horizontal"或"grid"
        """

        super().__init__(root, layout=layout)
    
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
            self.draw_stone(x, y, self.current_player)
            
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