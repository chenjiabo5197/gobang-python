from gobang_base import GobangBase

class GobangSingle(GobangBase):
    """单人游戏模式，对战电脑AI"""
    def __init__(self, root):
        """初始化单人游戏
        
        Args:
            root: Tkinter根窗口对象
        """
        super().__init__(root)
        self.status_var.set("当前玩家: 黑棋（您）")
    
    def on_click(self, event):
        """处理鼠标点击事件，包括计算点击位置、落子、检查胜负和切换到电脑回合
        
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
                self.status_var.set("游戏结束! 您获胜!")
                self.game_over = True
                return
            
            # 切换玩家
            self.current_player = 2
            
            # 更新状态显示
            self.status_var.set("当前玩家: 电脑")
            # 电脑落子
            self.root.after(500, self.computer_move)
    
    def computer_move(self):
        """电脑落子（简单AI），寻找第一个空位进行落子
        
        Returns:
            None
        """
        if self.game_over or self.current_player != 2:
            return
        
        # 简单AI：寻找第一个空位
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.board[y][x] == 0:
                    # 落子
                    self.board[y][x] = 2
                    self.draw_stone(x, y, 2)
                    
                    # 检查胜负
                    if self.check_win(x, y, 2):
                        self.status_var.set("游戏结束! 电脑获胜!")
                        self.game_over = True
                        return
                    
                    # 切换玩家
                    self.current_player = 1
                    self.status_var.set("当前玩家: 您")
                    return
    
    def reset_game(self):
        """重置游戏，清空棋盘并重新开始
        
        Returns:
            None
        """
        super().reset_game()
        self.status_var.set("当前玩家: 黑棋（您）")