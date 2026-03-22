import socket
import threading
from gobang_base import GobangBase

class GobangNetwork(GobangBase):
    """网络对战模式，支持主机和客户端两种角色"""

    def __init__(self, root, game_mode, layout="vertical"):
        """初始化网络对战游戏
        
        Args:
            root: Tkinter根窗口对象
            game_mode: 游戏模式，"network_host"表示主机，"network_client"表示客户端
            layout: 布局类型，"vertical"、"horizontal"或"grid"
        """

        super().__init__(root, layout=layout)
        self.game_mode = game_mode
        self.socket = None
        self.connected = False
        
        # 初始化网络模式
        if game_mode == "network_host":
            self.start_host()
        elif game_mode == "network_client":
            self.start_client()
    
    def on_click(self, event):
        """处理鼠标点击事件，包括检查回合、计算点击位置、落子、检查胜负、发送落子信息和切换玩家
        
        Args:
            event: 鼠标点击事件对象
        """

        if self.game_over:
            return
        
        # 检查是否是当前玩家的回合
        is_my_turn = False
        if self.game_mode == "network_host" and self.current_player == 1:
            is_my_turn = True
        elif self.game_mode == "network_client" and self.current_player == 2:
            is_my_turn = True
        
        if not is_my_turn:
            self.status_var.set("当前不是您的回合")
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
                winner = "您" if ((self.game_mode == "network_host" and self.current_player == 1) or 
                                (self.game_mode == "network_client" and self.current_player == 2)) else "对方"
                self.status_var.set(f"游戏结束! {winner}获胜!")
                self.game_over = True
                return
            
            # 发送落子位置
            if self.connected:
                try:
                    self.socket.send(f"MOVE:{x},{y}".encode())
                except:
                    self.status_var.set("网络连接已断开")
                    self.connected = False
            
            # 切换玩家
            self.current_player = 2 if self.current_player == 1 else 1
            
            # 更新状态显示
            current_player_text = "黑棋" if self.current_player == 1 else "白棋"
            if (self.game_mode == "network_host" and self.current_player == 1) or \
               (self.game_mode == "network_client" and self.current_player == 2):
                current_player_text += "（您）"
            else:
                current_player_text += "（对方）"
            self.status_var.set(f"当前玩家: {current_player_text}")
    
    def start_host(self):
        """开始作为主机，创建服务器并等待客户端连接
        
        Returns:
            None
        """

        self.status_var.set("正在创建游戏...")
        
        # 创建服务器
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", 12345))
        server.listen(1)
        
        # 显示主机信息
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        self.status_var.set(f"主机已创建\nIP: {ip}\n端口: 12345\n等待连接...\n您是: 黑方")
        
        # 接受连接的线程
        def accept_connection():
            try:
                self.socket, addr = server.accept()
                self.connected = True
                self.status_var.set(f"已连接: {addr}\n当前玩家: 黑棋（您）")
                # 开始接收消息
                threading.Thread(target=self.receive_messages, daemon=True).start()
            except:
                self.status_var.set("创建游戏失败")
        
        threading.Thread(target=accept_connection, daemon=True).start()
    
    def start_client(self):
        """开始作为客户端，连接到主机
        
        Returns:
            None
        """

        self.status_var.set("正在连接...\n您是: 白方")
        
        # 创建客户端
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 简单实现：连接到本地主机
        try:
            self.socket.connect(("127.0.0.1", 12345))
            self.connected = True
            self.status_var.set("已连接到主机\n当前玩家: 黑棋（对方）")
            # 开始接收消息
            threading.Thread(target=self.receive_messages, daemon=True).start()
            # 游戏开始时是黑棋（主机）先下，所以当前玩家为1
            self.current_player = 1
        except:
            self.status_var.set("连接失败，请检查主机是否开启\n您是: 白方")
    
    def receive_messages(self):
        """接收网络消息，处理对方落子和连接状态
        
        Returns:
            None
        """

        while self.connected:
            try:
                message = self.socket.recv(1024).decode()
                if not message:
                    break
                
                if message.startswith("MOVE:"):
                    # 处理对方落子
                    move = message[5:].split(",")
                    x, y = int(move[0]), int(move[1])
                    if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[y][x] == 0:
                        # 落子
                        opponent_player = 2 if self.current_player == 1 else 1
                        self.board[y][x] = opponent_player
                        self.draw_stone(x, y, opponent_player)
                        
                        # 检查胜负
                        if self.check_win(x, y, opponent_player):
                            winner = "对方" if opponent_player != self.current_player else "您"
                            self.status_var.set(f"游戏结束! {winner}获胜!")
                            self.game_over = True
                        else:
                            # 切换玩家
                            self.current_player = opponent_player
                            current_player_text = "黑棋" if self.current_player == 1 else "白棋"
                            if (self.game_mode == "network_host" and self.current_player == 1) or \
                               (self.game_mode == "network_client" and self.current_player == 2):
                                current_player_text += "（您）"
                            else:
                                current_player_text += "（对方）"
                            self.status_var.set(f"当前玩家: {current_player_text}")
            except:
                self.connected = False
                self.status_var.set("网络连接已断开")
                break
    
    def reset_game(self):
        """重置游戏，清空棋盘并重新开始
        
        Returns:
            None
        """

        super().reset_game()
        if self.game_mode == "network_host":
            self.status_var.set("当前玩家: 黑棋（您）")
        elif self.game_mode == "network_client":
            self.status_var.set("当前玩家: 黑棋（对方）")
            self.current_player = 1