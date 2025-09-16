import os
import wx  # 添加 wx 导入
from utils.ui_utils import create_gradient_button, current_theme

class LogPanel(wx.Panel):
    def __init__(self, parent, log_path):
        super().__init__(parent)
        self.log_path = log_path
        self.SetBackgroundColour(current_theme['bg_color'])
        self.page_layout = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.page_layout)

        # 创建标题区域
        title_panel = wx.Panel(self)
        title_panel.SetBackgroundColour(current_theme['bg_color'])
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 添加装饰线
        decoration = wx.Panel(title_panel, size=(5, 30))
        decoration.SetBackgroundColour(current_theme['accent_blue'])
        title_sizer.Add(decoration, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # 添加标题和图标
        title_text = wx.StaticText(title_panel, label=" 系统日志")
        title_text.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title_text.SetForegroundColour(current_theme['text_primary'])
        title_sizer.Add(title_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        
        # 添加图标
        icon_text = wx.StaticText(title_panel, label="📋")
        icon_text.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        title_sizer.Add(icon_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        
        title_panel.SetSizer(title_sizer)
        self.page_layout.Add(title_panel, 0, wx.EXPAND | wx.ALL, 15)
        
        # 添加分隔线
        separator = wx.Panel(self, size=(-1, 1))
        separator.SetBackgroundColour(current_theme['border_color'])
        self.page_layout.Add(separator, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)

        # 创建卡片式容器
        self.log_card = wx.Panel(self)
        self.log_card.SetBackgroundColour(current_theme['card_bg'])
        self.log_layout = wx.BoxSizer(wx.VERTICAL)
        self.log_card.SetSizer(self.log_layout)
        
        # 添加阴影效果
        def on_log_card_paint(event):
            dc = wx.PaintDC(self.log_card)
            gc = wx.GraphicsContext.Create(dc)
            width, height = self.log_card.GetSize()
            
            # 绘制圆角矩形
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, width, height, 10)
            gc.SetBrush(wx.Brush(current_theme['card_bg']))
            
            # 添加细微的边框
            gc.SetPen(wx.Pen(current_theme['border_color'], 1))
            gc.StrokePath(path)
            
            event.Skip()
            
        self.log_card.Bind(wx.EVT_PAINT, on_log_card_paint)

        # 创建日志文本框
        self.log_text = wx.TextCtrl(self.log_card, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.log_text.SetFont(wx.Font(11, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.log_text.SetBackgroundColour(wx.Colour(245, 245, 245))
        self.log_layout.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 15)

        # 创建刷新按钮
        button_panel = wx.Panel(self.log_card)
        button_panel.SetBackgroundColour(current_theme['card_bg'])
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        refresh_button = create_gradient_button(
            button_panel, 
            "🔄 刷新日志",
            size=(-1, 40)
        )
        refresh_button.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        refresh_button.Bind(wx.EVT_BUTTON, self.refresh_log)
        button_sizer.Add(refresh_button, 1, wx.EXPAND)
        
        button_panel.SetSizer(button_sizer)
        self.log_layout.Add(button_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        # 添加卡片到页面布局
        self.page_layout.Add(self.log_card, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)

        # 添加状态信息面板
        status_panel = wx.Panel(self)
        status_panel.SetBackgroundColour(current_theme['bg_color'])
        status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 添加状态图标 - 使用更协调的颜色
        status_icon = wx.StaticText(status_panel, label="ℹ️")
        status_icon.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        status_icon.SetForegroundColour(current_theme['text_secondary'])  # 改为次要文本颜色，更协调
        status_sizer.Add(status_icon, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # 添加状态文本
        status_text = wx.StaticText(status_panel, label=f"日志文件路径: {os.path.basename(self.log_path)}")
        status_text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        status_text.SetForegroundColour(current_theme['text_secondary'])
        status_sizer.Add(status_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        
        status_panel.SetSizer(status_sizer)
        self.page_layout.Add(status_panel, 0, wx.LEFT | wx.BOTTOM, 20)

        # 初始刷新日志
        self.refresh_log()

    def refresh_log(self, event=None):
        """刷新日志显示"""
        try:
            # 清空日志文本框
            self.log_text.Clear()

            # 读取日志文件
            if os.path.exists(self.log_path):
                try:
                    # 首先尝试使用UTF-8编码
                    with open(self.log_path, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                        self.log_text.SetValue(log_content)
                except UnicodeDecodeError:
                    try:
                        # 如果UTF-8失败，尝试使用GBK编码（中文Windows常用）
                        with open(self.log_path, 'r', encoding='gbk') as f:
                            log_content = f.read()
                            self.log_text.SetValue(log_content)
                    except UnicodeDecodeError:
                        # 如果GBK也失败，使用二进制模式读取并跳过错误
                        with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()
                            self.log_text.SetValue(log_content + "\n\n[警告: 日志文件包含无法识别的字符，部分内容可能显示不正确]")
            else:
                self.log_text.SetValue(f"日志文件不存在: {self.log_path}")

            # 滚动到最后一行
            self.log_text.SetInsertionPointEnd()
        except Exception as e:
            self.log_text.SetValue(f"读取日志失败: {str(e)}")
            print(f"读取日志失败: {str(e)}")