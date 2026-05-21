import socket
import threading
import tkinter as tk
from tkinter import messagebox
from gobang_base import GobangBase

class GobangNetwork(GobangBase):
    """网络对战模式，支持主机和客户端两种角色"""

    def __init__(self, root, game_mode, layout="vertical", host="127.0.0.1", port=12345, back_callback=None):
        """初始化网络对战游戏

        Args:
            root: Tkinter根窗口对象
            game_mode: 游戏模式，"network_host"表示主机，"network_client"表示客户端
            layout: 布局类型，"vertical"、"horizontal"或"grid"
            host: 客户端模式下要连接的主机IP地址
            port: 客户端模式下要连接的端口号
            back_callback: 返回主菜单的回调函数
        """

        super().__init__(root, layout=layout, back_callback=back_callback)
        self.game_mode = game_mode
        self.socket = None
        self.connected = False
        self.port = port

        if game_mode == "network_host":
            self.start_host()
        elif game_mode == "network_client":
            self.start_client(host, port)
    
    def on_click(self, event):
        """处理鼠标点击事件，包括检查回合、计算点击位置、落子、检查胜负、发送落子信息和切换玩家
        
        Args:
            event: 鼠标点击事件对象
        """

        if self.game_over:
            return
        
        is_my_turn = False
        if self.game_mode == "network_host" and self.current_player == 1:
            is_my_turn = True
        elif self.game_mode == "network_client" and self.current_player == 2:
            is_my_turn = True
        
        if not is_my_turn:
            self.status_var.set("当前不是您的回合")
            return
        
        x = (event.x - self.margin + self.cell_size // 2) // self.cell_size
        y = (event.y - self.margin + self.cell_size // 2) // self.cell_size
        
        result = self._place_stone(x, y, self.current_player)
        if result == "win":
            winner = "您" if ((self.game_mode == "network_host" and self.current_player == 1) or
                            (self.game_mode == "network_client" and self.current_player == 2)) else "对方"
            self.status_var.set(f"游戏结束! {winner}获胜!")
            self.game_over = True
            return
        elif result == "draw":
            self.status_var.set("游戏结束! 平局!")
            self.game_over = True
            return
        elif result == "invalid":
            return
        
        if self.connected:
            try:
                self.socket.send(f"MOVE:{x},{y}".encode())
            except:
                self.status_var.set("网络连接已断开")
                self.connected = False
        
        self.current_player = 2 if self.current_player == 1 else 1
        
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
        try:
            server.bind(("0.0.0.0", self.port))
        except OSError:
            self.status_var.set(f"端口 {self.port} 被占用，请使用其他端口")
            return
        server.listen(1)

        # 显示主机信息
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
        except:
            ip = "无法获取IP"
        self.status_var.set(f"主机已创建\nIP: {ip}\n端口: {self.port}\n等待连接...\n您是: 黑方")
        
        # 接受连接的线程
        def accept_connection():
            try:
                self.socket, addr = server.accept()
                server.close()
                self.connected = True
                self.status_var.set(f"已连接: {addr}\n当前玩家: 黑棋（您）")
                # 开始接收消息
                threading.Thread(target=self.receive_messages, daemon=True).start()
            except:
                self.status_var.set("创建游戏失败")
        
        threading.Thread(target=accept_connection, daemon=True).start()
    
    def start_client(self, host="127.0.0.1", port=12345):
        """开始作为客户端，连接到主机
        
        Args:
            host: 主机IP地址
            port: 主机端口号
        """

        self.status_var.set(f"正在连接 {host}:{port}...\n您是: 白方")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.socket.connect((host, port))
            self.connected = True
            self.status_var.set("已连接到主机\n当前玩家: 黑棋（对方）")
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.current_player = 2  # 客户端为白方
        except:
            self.status_var.set(f"连接失败，请检查主机 {host}:{port} 是否开启\n您是: 白方")
    
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
                    move = message[5:].split(",")
                    x, y = int(move[0]), int(move[1])
                    self.root.after(0, lambda mx=x, my=y: self._handle_remote_move(mx, my))
                elif message == "UNDO_REQUEST":
                    self.root.after(0, self._handle_undo_request)
                elif message == "UNDO_ACCEPTED":
                    self.root.after(0, self._handle_undo_accepted)
                elif message == "UNDO_REJECTED":
                    self.root.after(0, lambda: self.status_var.set("对方拒绝了悔棋请求"))
            except:
                self.connected = False
                self.root.after(0, lambda: self.status_var.set("网络连接已断开"))
                break
    
    def _handle_remote_move(self, x, y):
        """在主线程处理对方落子
        
        Args:
            x: 对方落子的横坐标
            y: 对方落子的纵坐标
        """
        opponent_player = 2 if self.game_mode == "network_host" else 1
        result = self._place_stone(x, y, opponent_player)
        
        if result == "win":
            winner = "对方" if opponent_player != self.current_player else "您"
            self.status_var.set(f"游戏结束! {winner}获胜!")
            self.game_over = True
        elif result == "draw":
            self.status_var.set("游戏结束! 平局!")
            self.game_over = True
        elif result == "placed":
            self.current_player = 2 if opponent_player == 1 else 1  # 切换到本地玩家回合
            current_player_text = "黑棋" if self.current_player == 1 else "白棋"
            if (self.game_mode == "network_host" and self.current_player == 1) or \
               (self.game_mode == "network_client" and self.current_player == 2):
                current_player_text += "（您）"
            else:
                current_player_text += "（对方）"
            self.status_var.set(f"当前玩家: {current_player_text}")
    
    def _handle_undo_request(self):
        """在主线程处理悔棋请求，弹出确认对话框"""
        response = messagebox.askyesno("悔棋请求", "对方请求悔棋，是否同意？")
        
        if response:
            try:
                self.socket.send("UNDO_ACCEPTED".encode())
            except:
                self.status_var.set("网络连接已断开")
                self.connected = False
                return
            super().undo_move()
            current_player_text = "黑棋" if self.current_player == 1 else "白棋"
            if (self.game_mode == "network_host" and self.current_player == 1) or \
               (self.game_mode == "network_client" and self.current_player == 2):
                current_player_text += "（您）"
            else:
                current_player_text += "（对方）"
            self.status_var.set(f"已同意对方悔棋\n当前玩家: {current_player_text}")
        else:
            try:
                self.socket.send("UNDO_REJECTED".encode())
            except:
                self.status_var.set("网络连接已断开")
                self.connected = False
                return
            self.status_var.set("已拒绝对方悔棋")
    
    def _handle_undo_accepted(self):
        """在主线程处理悔棋被接受"""
        super().undo_move()
        current_player_text = "黑棋" if self.current_player == 1 else "白棋"
        if (self.game_mode == "network_host" and self.current_player == 1) or \
           (self.game_mode == "network_client" and self.current_player == 2):
            current_player_text += "（您）"
        else:
            current_player_text += "（对方）"
        self.status_var.set(f"对方已同意悔棋\n当前玩家: {current_player_text}")
    
    def undo_move(self):
        """网络对战中的悔棋，需要对方同意
        
        Returns:
            bool: 是否成功发送悔棋请求
        """
        if not self.connected:
            self.status_var.set("网络连接已断开，无法悔棋")
            return False
        
        if not self.move_history:
            self.status_var.set("没有可悔的棋")
            return False
        
        # 发送悔棋请求
        try:
            self.socket.send("UNDO_REQUEST".encode())
            self.status_var.set("已发送悔棋请求，等待对方同意...")
            return True
        except:
            self.status_var.set("网络连接已断开")
            self.connected = False
            return False
    
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
            self.current_player = 2  # 客户端为白方