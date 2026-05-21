import random
from gobang_base import GobangBase

class GobangSingle(GobangBase):
    """单人游戏模式，对战电脑AI"""
    def __init__(self, root, layout="vertical", difficulty="easy"):
        """初始化单人游戏
        
        Args:
            root: Tkinter根窗口对象
            layout: 布局类型，"vertical"、"horizontal"或"grid"
            difficulty: 难度等级，"easy"、"medium"或"hard"
        """
        super().__init__(root, layout=layout)
        self.difficulty = difficulty
        self.status_var.set(f"当前玩家: 黑棋（您）\n难度: {self.get_difficulty_text()}")
    
    def get_difficulty_text(self):
        """获取难度的中文描述
        
        Returns:
            str: 难度的中文描述
        """
        if self.difficulty == "easy":
            return "简单"
        elif self.difficulty == "medium":
            return "中等"
        else:
            return "困难"
    
    def on_click(self, event):
        """处理鼠标点击事件，包括计算点击位置、落子、检查胜负和切换到电脑回合
        
        Args:
            event: 鼠标点击事件对象
        """
        if self.game_over or self.current_player != 1:
            return
        
        x = (event.x - self.margin + self.cell_size // 2) // self.cell_size
        y = (event.y - self.margin + self.cell_size // 2) // self.cell_size
        
        result = self._place_stone(x, y, self.current_player)
        if result == "win":
            self.status_var.set("游戏结束! 您获胜!")
            self.game_over = True
            return
        elif result == "invalid":
            return
        
        self.current_player = 2
        self.status_var.set("当前玩家: 电脑")
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
    
    def random_move(self):
        """简单难度：随机落子
        
        Returns:
            tuple: 落子位置 (x, y)
        """
        empty_positions = []
        
        # 收集所有空位
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.board[y][x] == 0:
                    empty_positions.append((x, y))
        
        # 随机选择一个空位
        if empty_positions:
            return random.choice(empty_positions)
        return None
    
    def medium_move(self):
        """中等难度：基础评估
        
        Returns:
            tuple: 落子位置 (x, y)
        """
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
                    
                    # 综合考虑进攻和防守，中等难度稍微偏向防守
                    total_score = computer_score + player_score * 1.2
                    
                    # 寻找最佳落子点
                    if total_score > best_score:
                        best_score = total_score
                        best_move = (x, y)
        
        return best_move
    
    def hard_move(self):
        """困难难度：高级评估
        
        Returns:
            tuple: 落子位置 (x, y)
        """
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
                    
                    # 综合考虑进攻和防守，困难难度更倾向于进攻
                    total_score = computer_score * 1.5 + player_score
                    
                    # 寻找最佳落子点
                    if total_score > best_score:
                        best_score = total_score
                        best_move = (x, y)
        
        return best_move
    
    def computer_move(self):
        """电脑落子，根据难度等级选择不同的AI策略"""
        if self.game_over or self.current_player != 2:
            return
        
        if self.difficulty == "easy":
            best_move = self.random_move()
        elif self.difficulty == "medium":
            best_move = self.medium_move()
        else:
            best_move = self.hard_move()
        
        if best_move:
            x, y = best_move
            result = self._place_stone(x, y, 2)
            if result == "win":
                self.status_var.set("游戏结束! 电脑获胜!")
                self.game_over = True
                return
            self.current_player = 1
            self.status_var.set(f"当前玩家: 您\n难度: {self.get_difficulty_text()}")
        else:
            self.status_var.set("游戏结束! 平局!")
            self.game_over = True
    
    def undo_move(self):
        """悔棋，取消自己和电脑的上一步棋
        
        Returns:
            bool: 是否成功悔棋
        """
        # 单人游戏中，悔棋需要取消自己和电脑的各一步
        if len(self.move_history) < 2:
            return False
        
        # 弹出电脑的落子状态
        self.move_history.pop()
        # 弹出自己的落子状态
        state = self.move_history.pop()
        
        # 恢复状态
        self.board = state['board']
        self.current_player = state['current_player']
        self.last_black_move = state['last_black_move']
        self.last_white_move = state['last_white_move']
        self.game_over = False
        
        # 重新绘制棋盘
        self.redraw_board()
        
        # 更新状态显示
        self.status_var.set("当前玩家: 黑棋（您）")
        
        return True
    
    def reset_game(self):
        """重置游戏，清空棋盘并重新开始
        
        Returns:
            None
        """
        super().reset_game()
        self.status_var.set("当前玩家: 黑棋（您）")