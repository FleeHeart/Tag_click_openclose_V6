import os
import customtkinter as ctk
from PIL import Image, ImageTk
from logger import logger
from core.auto_click_manager import AutoClickManager
from ui.ctk_function_panel import CTkFunctionPanel
from ui.ctk_log_panel import CTkLogPanel
from core.browser_connector import BrowserConnector

# 设置外观模式和颜色主题
ctk.set_appearance_mode("System")  # 模式: "System" (默认), "Dark", "Light"
ctk.set_default_color_theme("blue")  # 主题: "blue" (默认), "green", "dark-blue"

class CTkAutoClickerMainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题和大小
        self.title("网页自动化点击系统")
        self.geometry("900x750")
        self.minsize(850, 700)
        
        # 获取应用程序目录的绝对路径
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_path = os.path.join(os.path.dirname(self.app_dir), 'app.log')
        
        # 创建浏览器连接器和自动点击管理器
        self.browser_connector = BrowserConnector()
        self.auto_click_manager = AutoClickManager(self.browser_connector)
        
        # 创建主布局
        self._create_ui()
        
        # 记录系统启动
        logger.info("系统已启动")
        
    def _create_ui(self):
        # 创建标题栏
        self.title_frame = ctk.CTkFrame(self, corner_radius=0, height=60)
        self.title_frame.pack(fill="x")
        
        # 标题和版本信息
        title_container = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        title_container.pack(side="left", padx=20, pady=10)
        
        # 应用图标和标题
        icon_label = ctk.CTkLabel(title_container, text="🚀", font=ctk.CTkFont(size=22, weight="bold"))
        icon_label.pack(side="left")
        
        title_label = ctk.CTkLabel(title_container, text="网页自动化点击系统", 
                                 font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(side="left", padx=10)
        
        version_label = ctk.CTkLabel(title_container, text="V5.0", 
                                   font=ctk.CTkFont(size=11))
        version_label.pack(side="left", padx=5)
        
        # 状态信息和主题切换
        control_container = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        control_container.pack(side="right", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(control_container, text="准备就绪", 
                                       font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=10)
        
        # 主题切换按钮
        self.theme_button = ctk.CTkButton(
            control_container, 
            text="🌙", 
            width=40, 
            command=self.toggle_theme,
            font=ctk.CTkFont(size=14)
        )
        self.theme_button.pack(side="left")
        
        # 创建选项卡控件
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 添加选项卡
        self.tabview.add("功能")
        self.tabview.add("日志")
        
        # 创建功能页面和日志页面
        self.functions_page = CTkFunctionPanel(self.tabview.tab("功能"), self.auto_click_manager)
        self.log_page = CTkLogPanel(self.tabview.tab("日志"))
        
        # 设置默认选项卡
        self.tabview.set("功能")
        
        # 创建底部状态栏
        self.status_bar = ctk.CTkFrame(self, height=25, corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")
        
        status_text = ctk.CTkLabel(
            self.status_bar, 
            text="就绪 - 点击「连接到已打开的Edge浏览器」开始使用",
            font=ctk.CTkFont(size=10)
        )
        status_text.pack(side="left", padx=10)
        
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def toggle_theme(self):
        """切换主题"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        
        # 更新按钮文本
        self.theme_button.configure(text="☀️" if new_mode == "Light" else "🌙")
    
    def on_close(self):
        """关闭窗口时的处理"""
        logger.info("系统正在关闭...")

        # 停止自动投放
        self.auto_click_manager.stop_auto_delivery()

        # 关闭浏览器
        self.auto_click_manager.close_browser()

        logger.info("系统已关闭")
        
        # 销毁窗口
        self.destroy()