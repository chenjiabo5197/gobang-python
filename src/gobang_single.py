from gobang_base import GobangBase

class GobangSingle(GobangBase):
    """单人游戏模式，对战电脑AI"""
    def __init__(self, root, layout="vertical"):
        """初始化单人游戏
        
        Args:
            root: Tkinter根窗口对象
            layout: 布局类型，"vertical"、"horizontal"或"grid"
        """
        super().__init__(root, layout=layout)
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
    
    def evaluate_position(self, x, y, player):
        """评估指定位置对指定玩家的价值
        
        Args:
            x: 棋盘x坐标
            y: 棋盘y坐标
            player: 玩家编号（1或2）
            
        Returns:
            int: 位置价值分数
        """
        if self.board[y][x] != 0:
            return -1  # 已被占用的位置
        
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # 四个方向
        
        for dx, dy in directions:
            # 计算当前方向上的连续棋子数
            count = 0
            empty = 0
            blocked = 0
            
            # 向正方向搜索
            for i in range(1, 5):
                nx, ny = x + i * dx, y + i * dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    if self.board[ny][nx] == player:
                        count += 1
                    elif self.board[ny][nx] == 0:
                        empty += 1
                        break
                    else:
                        blocked += 1
                        break
                else:
                    blocked += 1
                    break
            
            # 向反方向搜索
            for i in range(1, 5):
                nx, ny = x - i * dx, y - i * dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    if self.board[ny][nx] == player:
                        count += 1
                    elif self.board[ny][nx] == 0:
                        empty += 1
                        break
                    else:
                        blocked += 1
                        break
                else:
                    blocked += 1
                    break
            
            # 根据连续棋子数和阻塞情况计算分数
            if count == 4:
                score += 10000  # 五连
            elif count == 3 and blocked == 0:
                score += 1000   # 活四
            elif count == 3 and blocked == 1:
                score += 100    # 冲四
            elif count == 2 and blocked == 0:
                score += 100    # 活三
            elif count == 2 and blocked == 1:
                score += 10     # 冲三
            elif count == 1 and blocked == 0:
                score += 5      # 活二
        
        return score
    
    def computer_move(self):
        """电脑落子（智能AI），评估棋盘位置并选择最优落子点
        
        Returns:
            None
        """
        if self.game_over or self.current_player != 2:
            return
        
        best_score = -1
        best_move = None
        
        # 评估所有空位
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.board[y][x] == 0:
                    # 评估电脑在此位置落子的价值
                    computer_score = self.evaluate_position(x, y, 2)
                    # 评估玩家在此位置落子的价值（防守）
                    player_score = self.evaluate_position(x, y, 1)
                    
                    # 综合考虑进攻和防守
                    total_score = computer_score * 1.2 + player_score  # 稍微优先进攻
                    
                    # 寻找最佳落子点
                    if total_score > best_score:
                        best_score = total_score
                        best_move = (x, y)
        
        # 如果找到最佳落子点
        if best_move:
            x, y = best_move
            # 落子
            self.board[y][x] = 2
            # 记录上一步落子位置
            self.last_move = (x, y)
            # 重新绘制棋盘和所有棋子，以清除之前的标记并绘制新标记
            self.redraw_board()
            
            # 检查胜负
            if self.check_win(x, y, 2):
                self.status_var.set("游戏结束! 电脑获胜!")
                self.game_over = True
                return
            
            # 切换玩家
            self.current_player = 1
            self.status_var.set("当前玩家: 您")
        else:
            # 如果没有找到空位（理论上不会发生）
            self.status_var.set("游戏结束! 平局!")
            self.game_over = True
    
    def reset_game(self):
        """重置游戏，清空棋盘并重新开始
        
        Returns:
            None
        """
        super().reset_game()
        self.status_var.set("当前玩家: 黑棋（您）")