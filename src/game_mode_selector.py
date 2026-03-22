import tkinter as tk
from gobang_single import GobangSingle
from gobang_multiplayer import GobangMultiplayer
from gobang_network import GobangNetwork

class GameModeSelector:
    """游戏模式选择器，用于选择单人游戏、双人游戏或网络对战"""

    def __init__(self, root):
        """初始化游戏模式选择器
        
        Args:
            root: Tkinter根窗口对象
        """

        self.root = root
        self.root.title("五子棋 - 游戏模式选择")
        self.root.resizable(False, False)
        
        # 设置窗口大小
        window_width = 400
        window_height = 400
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建标题
        title_label = tk.Label(root, text="五子棋", font=("Arial", 24, "bold"))
        title_label.pack(pady=20)
        
        # 创建布局选择区域
        layout_frame = tk.Frame(root)
        layout_frame.pack(pady=10)
        
        layout_label = tk.Label(layout_frame, text="选择布局:", font=("Arial", 12))
        layout_label.pack(side=tk.LEFT, padx=10)
        
        self.layout_var = tk.StringVar(value="vertical")
        
        vertical_btn = tk.Radiobutton(layout_frame, text="垂直布局", variable=self.layout_var, value="vertical")
        vertical_btn.pack(side=tk.LEFT, padx=5)
        
        horizontal_btn = tk.Radiobutton(layout_frame, text="水平布局", variable=self.layout_var, value="horizontal")
        horizontal_btn.pack(side=tk.LEFT, padx=5)
        
        grid_btn = tk.Radiobutton(layout_frame, text="网格布局", variable=self.layout_var, value="grid")
        grid_btn.pack(side=tk.LEFT, padx=5)
        
        # 创建按钮容器
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)
        
        # 创建游戏模式按钮
        single_player_btn = tk.Button(
            self.button_frame, 
            text="单人游戏（对战电脑）", 
            width=25, 
            height=2, 
            font=("Arial", 12),
            command=self.start_single_player
        )
        single_player_btn.pack(pady=10)
        
        local_multiplayer_btn = tk.Button(
            self.button_frame, 
            text="双人游戏（本地）", 
            width=25, 
            height=2, 
            font=("Arial", 12),
            command=self.start_local_multiplayer
        )
        local_multiplayer_btn.pack(pady=10)
        
        network_multiplayer_btn = tk.Button(
            self.button_frame, 
            text="双人游戏（网络对战）", 
            width=25, 
            height=2, 
            font=("Arial", 12),
            command=self.start_network_multiplayer
        )
        network_multiplayer_btn.pack(pady=10)
        
        # 创建退出游戏按钮
        exit_btn = tk.Button(
            self.button_frame, 
            text="退出游戏", 
            width=25, 
            height=2, 
            font=("Arial", 12),
            command=self.exit_game
        )
        exit_btn.pack(pady=10)
    
    def start_single_player(self):
        """开始单人游戏，创建GobangSingle实例
        
        Returns:
            None
        """

        self.root.destroy()
        root = tk.Tk()
        game = GobangSingle(root, layout=self.layout_var.get())
        root.mainloop()
    
    def start_local_multiplayer(self):
        """开始本地双人游戏，创建GobangMultiplayer实例
        
        Returns:
            None
        """

        self.root.destroy()
        root = tk.Tk()
        game = GobangMultiplayer(root, layout=self.layout_var.get())
        root.mainloop()
    
    def start_network_multiplayer(self):
        """开始网络对战，创建NetworkSetupWindow实例
        
        Returns:
            None
        """

        self.root.destroy()
        root = tk.Tk()
        network_window = NetworkSetupWindow(root, layout=self.layout_var.get())
        root.mainloop()
    
    def exit_game(self):
        """退出游戏，关闭主窗口
        
        Returns:
            None
        """
        self.root.destroy()

class NetworkSetupWindow:
    """网络对战设置窗口，用于选择创建主机或加入客户端"""

    def __init__(self, root, layout="vertical"):
        """初始化网络对战设置窗口
        
        Args:
            root: Tkinter根窗口对象
            layout: 布局类型，"vertical"、"horizontal"或"grid"
        """
        self.root = root
        self.root.title("五子棋 - 网络对战设置")
        self.root.resizable(False, False)
        self.layout = layout
        
        # 设置窗口大小
        window_width = 400
        window_height = 250
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建标题
        title_label = tk.Label(root, text="网络对战设置", font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        # 创建按钮容器
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        # 创建主机和客户端按钮
        host_btn = tk.Button(
            button_frame, 
            text="创建游戏（主机）", 
            width=20, 
            height=2, 
            font=("Arial", 12),
            command=self.create_host
        )
        host_btn.pack(pady=10)
        
        client_btn = tk.Button(
            button_frame, 
            text="加入游戏（客户端）", 
            width=20, 
            height=2, 
            font=("Arial", 12),
            command=self.join_client
        )
        client_btn.pack(pady=10)
        
        # 返回按钮
        back_btn = tk.Button(root, text="返回", command=self.go_back)
        back_btn.pack(pady=10)
    
    def create_host(self):
        """创建主机，创建GobangNetwork实例并设置为network_host模式
        
        Returns:
            None
        """

        self.root.destroy()
        root = tk.Tk()
        game = GobangNetwork(root, game_mode="network_host", layout=self.layout)
        root.mainloop()
    
    def join_client(self):
        """加入客户端，创建GobangNetwork实例并设置为network_client模式
        
        Returns:
            None
        """

        self.root.destroy()
        root = tk.Tk()
        game = GobangNetwork(root, game_mode="network_client", layout=self.layout)
        root.mainloop()
    
    def go_back(self):
        """返回游戏模式选择，创建GameModeSelector实例
        
        Returns:
            None
        """

        self.root.destroy()
        root = tk.Tk()
        selector = GameModeSelector(root)
        root.mainloop()