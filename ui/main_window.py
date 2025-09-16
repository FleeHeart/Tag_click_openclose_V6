import wx  # 添加 wx 模块导入
import wx.adv
import os  # 添加 os 模块导入
from ui.function_panel import FunctionPanel
from ui.log_panel import LogPanel
from logger import logger  # 修正导入路径
from core.auto_click_manager import AutoClickManager
from utils.ui_utils import apply_modern_style, current_theme, toggle_theme, ThemeChangeEvent, EVT_THEME_CHANGE

class AutoClickerMainWindow(wx.Frame):
    def __init__(self):
        super().__init__(None, title="网页自动化点击系统", size=(900, 750))
        # 获取应用程序目录的绝对路径
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_path = os.path.join(os.path.dirname(self.app_dir), 'app.log')

        # 设置最小尺寸
        self.SetMinSize((850, 700))

        # 创建自动点击管理器
        self.auto_click_manager = AutoClickManager()

        # 创建主面板
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(current_theme['bg_color'])

        # 创建主布局
        self.main_layout = wx.BoxSizer(wx.VERTICAL)

        # 创建标题栏 - 更现代的风格，使用渐变背景
        title_panel = wx.Panel(self.panel)
        # 使用渐变色背景，在绘制事件中实现
        title_panel.SetBackgroundColour(current_theme['accent_blue'])
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 添加应用图标
        icon_text = wx.StaticText(title_panel, label="🚀")
        icon_text.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        icon_text.SetForegroundColour(wx.WHITE)
        title_sizer.Add(icon_text, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 15)

        # 添加标题文本 - 更现代的字体和颜色
        title_text = wx.StaticText(title_panel, label="网页自动化点击系统")
        title_font = wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(wx.WHITE)
        title_sizer.Add(title_text, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)

        # 添加版本信息 - 更现代的字体和颜色
        version_text = wx.StaticText(title_panel, label="V4.0")
        version_text.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        version_text.SetForegroundColour(wx.Colour(240, 240, 255, 200))  # 半透明白色
        title_sizer.Add(version_text, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 8)

        # 添加弹性空间
        title_sizer.AddStretchSpacer()

        # 添加主题切换按钮 - 更现代的样式
        theme_button = wx.ToggleButton(title_panel, label="🌙", size=(40, 40), style=wx.BORDER_NONE)
        theme_button.SetBackgroundColour(wx.Colour(255, 255, 255, 30))  # 半透明白色
        theme_button.SetForegroundColour(wx.WHITE)
        theme_button.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        theme_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_theme_toggle)
        title_sizer.Add(theme_button, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 15)

        # 添加状态信息 - 更现代的字体和颜色
        self.status_text = wx.StaticText(title_panel, label="准备就绪")
        self.status_text.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.status_text.SetForegroundColour(wx.WHITE)
        title_sizer.Add(self.status_text, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 20)
        
        # 添加渐变背景绘制
        def on_paint_title(event):
            dc = wx.PaintDC(title_panel)
            gc = wx.GraphicsContext.Create(dc)
            width, height = title_panel.GetSize()
            
            # 创建渐变画笔
            start_color = current_theme.get('gradient_start', wx.Colour(56, 189, 248))
            end_color = current_theme.get('accent_blue', wx.Colour(14, 165, 233))
            brush = gc.CreateLinearGradientBrush(0, 0, width, 0, start_color, end_color)
            
            # 绘制渐变矩形
            gc.SetBrush(brush)
            gc.DrawRectangle(0, 0, width, height)
            
            event.Skip()
            
        title_panel.Bind(wx.EVT_PAINT, on_paint_title)

        title_panel.SetSizer(title_sizer)
        self.main_layout.Add(title_panel, 0, wx.EXPAND)

        # 创建选项卡控件 - 更现代的风格
        self.notebook = wx.Notebook(self.panel, style=wx.NB_TOP)
        self.notebook.SetBackgroundColour(current_theme['card_bg'])
        self.notebook.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        # 创建功能页面和日志页面
        self.functions_page = FunctionPanel(self.notebook, self.auto_click_manager)
        self.log_page = LogPanel(self.notebook, self.log_path)

        # 添加选项卡
        self.notebook.AddPage(self.functions_page, "功能")
        self.notebook.AddPage(self.log_page, "日志")
        
        # 自定义选项卡外观 - 使用更简单的方法实现底部指示器
        def on_notebook_paint(event):
            # 获取当前选中的选项卡
            selected_tab = self.notebook.GetSelection()
            
            if selected_tab != wx.NOT_FOUND:
                # 绘制选项卡底部的指示器
                dc = wx.PaintDC(self.notebook)
                gc = wx.GraphicsContext.Create(dc)
                
                # 获取选项卡区域 - 使用notebook的尺寸和选项卡数量来估算
                notebook_width = self.notebook.GetSize().GetWidth()
                tab_count = self.notebook.GetPageCount()
                if tab_count > 0:
                    # 估算每个选项卡的宽度
                    tab_width = notebook_width / tab_count
                    x = selected_tab * tab_width
                    y = 30  # 选项卡标题区域的高度
                    
                    # 创建渐变画笔 - 使用更协调的颜色
                    start_color = current_theme.get('border_color', wx.Colour(226, 232, 240))
                    end_color = current_theme.get('text_secondary', wx.Colour(100, 116, 139))
                    brush = gc.CreateLinearGradientBrush(x, y, x + tab_width, y, start_color, end_color)
                    
                    # 绘制底部指示器
                    gc.SetBrush(brush)
                    gc.DrawRectangle(x, y, tab_width, 3)
            
            event.Skip()
        
        self.notebook.Bind(wx.EVT_PAINT, on_notebook_paint)
        
        # 选项卡切换时重绘
        def on_page_changed(event):
            self.notebook.Refresh()
            event.Skip()
            
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, on_page_changed)

        # 添加选项卡到主布局，减小边距使布局更紧凑
        self.main_layout.Add(self.notebook, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        self.panel.SetSizer(self.main_layout)

        # 创建底部状态栏 - 现代风格
        status_bar = self.CreateStatusBar()
        status_bar.SetBackgroundColour(current_theme['card_bg'])
        status_bar.SetStatusText("就绪 - 点击「连接到已打开的Edge浏览器」开始使用")
        status_bar.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        status_bar.SetForegroundColour(current_theme['text_secondary'])

        # 绑定关闭事件
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # 绑定选项卡切换事件
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_changed)

        # 绑定主题变更事件
        self.Bind(EVT_THEME_CHANGE, self.on_theme_change)

        # 应用现代风格
        apply_modern_style(self.panel)

        # 记录系统启动
        logger.info("系统已启动")

        # 显示窗口
        self.Center()
        self.Show()

    def on_theme_toggle(self, event):
        """切换主题"""
        toggle_theme()
        # 发送主题变更事件
        wx.PostEvent(self, ThemeChangeEvent())

    def on_theme_change(self, event):
        """处理主题变更"""
        # 更新界面颜色
        self.panel.SetBackgroundColour(current_theme['bg_color'])
        self.notebook.SetBackgroundColour(current_theme['card_bg'])
        # 重新应用样式
        apply_modern_style(self.panel)
        # 刷新日志页面
        self.log_page.Refresh()
        # 更新状态栏
        status_bar = self.GetStatusBar()
        status_bar.SetBackgroundColour(current_theme['card_bg'])
        status_bar.SetForegroundColour(current_theme['text_secondary'])
        # 刷新窗口
        self.Refresh()

    def on_tab_changed(self, event):
        """处理选项卡切换事件"""
        page_idx = event.GetSelection()
        page_name = self.notebook.GetPageText(page_idx)
        logger.debug(f"切换到选项卡: {page_name}")

        # 如果切换到日志页面，刷新日志内容
        if page_name == "日志":
            self.log_page.refresh_log()

        event.Skip()

    def on_close(self, event):
        """关闭窗口时的处理"""
        logger.info("系统正在关闭...")

        # 停止自动投放
        self.auto_click_manager.stop_auto_delivery()

        # 关闭浏览器
        self.auto_click_manager.close_browser()

        # 接受关闭事件
        event.Skip()

        logger.info("系统已关闭")