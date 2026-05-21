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