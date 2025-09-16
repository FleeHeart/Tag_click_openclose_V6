import wx  # 添加 wx 模块导入
import wx.adv  # 添加高级控件支持
from logger import logger
from utils.ui_utils import button_feedback, button_pulse, create_gradient_button, create_modern_text_ctrl, create_rounded_panel, apply_modern_style, current_theme

class FunctionPanel(wx.Panel):
    def __init__(self, parent, auto_click_manager):
        super().__init__(parent)
        self.auto_click_manager = auto_click_manager
        self.SetBackgroundColour(current_theme['bg_color'])
        self.page_layout = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.page_layout)
        
        # 初始化标签页存储
        self.browser_tabs = []

        # 初始化UI组件
        self._init_ui()

    def _init_ui(self):
        # 创建标题区域 - 更现代的设计
        title_panel = wx.Panel(self)
        title_panel.SetBackgroundColour(current_theme['bg_color'])
        title_sizer = wx.BoxSizer(wx.VERTICAL)

        # 创建功能标题 - 更现代的字体和布局
        title_container = wx.Panel(title_panel)
        title_container.SetBackgroundColour(current_theme['bg_color'])
        title_container_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 添加左侧装饰线
        decoration_panel = wx.Panel(title_container, size=(6, 40))
        decoration_panel.SetBackgroundColour(current_theme.get('accent_blue', wx.Colour(56, 189, 248)))
        title_container_sizer.Add(decoration_panel, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # 标题和副标题容器
        text_container = wx.Panel(title_container)
        text_container.SetBackgroundColour(current_theme['bg_color'])
        text_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 创建功能标题 - 更现代的字体和颜色
        title_label = wx.StaticText(text_container, label="自动化点击功能")
        title_font = wx.Font(24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(current_theme['text_primary'])
        text_sizer.Add(title_label, 0, wx.LEFT | wx.TOP, 5)

        # 添加副标题 - 更现代的字体和颜色
        subtitle = wx.StaticText(text_container, label="高效自动化，轻松点击")
        subtitle.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))
        subtitle.SetForegroundColour(current_theme['text_secondary'])
        text_sizer.Add(subtitle, 0, wx.LEFT | wx.BOTTOM, 5)
        
        text_container.SetSizer(text_sizer)
        title_container_sizer.Add(text_container, 1, wx.EXPAND | wx.LEFT, 10)
        
        title_container.SetSizer(title_container_sizer)
        title_sizer.Add(title_container, 0, wx.EXPAND | wx.ALL, 10)
        
        # 添加分隔线
        separator = wx.Panel(title_panel, size=(-1, 1))
        separator.SetBackgroundColour(current_theme['border_color'])
        title_sizer.Add(separator, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        title_panel.SetSizer(title_sizer)
        self.page_layout.Add(title_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        # 创建卡片式容器 - 使用滚动窗口
        self.scroll_win = wx.ScrolledWindow(self, style=wx.VSCROLL | wx.HSCROLL)
        self.scroll_win.SetBackgroundColour(current_theme['bg_color'])
        self.scroll_win.SetScrollRate(10, 10)
        # 设置最小高度，确保能显示所有内容
        self.scroll_win.SetMinSize((-1, 600))

        # 创建滚动窗口的sizer
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_win.SetSizer(self.scroll_sizer)

        self.main_card = create_rounded_panel(self.scroll_win)
        # 增加最小高度，确保所有内容可见
        self.main_card.SetMinSize((-1, 650))
        self.main_layout = wx.BoxSizer(wx.VERTICAL)
        self.main_card.SetSizer(self.main_layout)

        # 将main_card添加到scroll_sizer
        self.scroll_sizer.Add(self.main_card, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 20)

        # 创建连接浏览器按钮 - 使用更现代的渐变按钮
        # 使用主题中定义的渐变色
        self.connect_button = create_gradient_button(
            self.main_card, 
            "连接到已打开的Edge浏览器", 
            size=(-1, 50)  # 增加按钮高度
        )
        # 添加图标
        self.connect_button.SetLabel("🔗 连接到已打开的Edge浏览器")
        self.connect_button.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.connect_button.Bind(wx.EVT_BUTTON, self.on_connect_browser)
        self.main_layout.Add(self.connect_button, 0, wx.EXPAND | wx.ALL, 20)

        # 添加标签页选择区域 - 更现代的卡片式设计
        self.tabs_panel = wx.Panel(self.main_card)
        self.tabs_panel.SetBackgroundColour(current_theme['card_bg'])
        # 添加阴影效果
        def on_tabs_panel_paint(event):
            dc = wx.PaintDC(self.tabs_panel)
            gc = wx.GraphicsContext.Create(dc)
            width, height = self.tabs_panel.GetSize()
            
            # 绘制圆角矩形
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, width, height, 10)
            gc.SetBrush(wx.Brush(current_theme['card_bg']))
            
            # 添加细微的边框
            gc.SetPen(wx.Pen(current_theme['border_color'], 1))
            gc.StrokePath(path)
            
            event.Skip()
            
        self.tabs_panel.Bind(wx.EVT_PAINT, on_tabs_panel_paint)
        
        tabs_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标签页选择标题 - 更现代的设计
        header_panel = wx.Panel(self.tabs_panel)
        header_panel.SetBackgroundColour(current_theme['card_bg'])
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 添加图标
        icon_text = wx.StaticText(header_panel, label="🔖")
        icon_text.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        icon_text.SetForegroundColour(current_theme['accent_blue'])
        header_sizer.Add(icon_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        
        # 标签页选择标题
        tabs_label = wx.StaticText(header_panel, label="选择已打开的标签页")
        tabs_label.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        tabs_label.SetForegroundColour(current_theme['text_primary'])
        header_sizer.Add(tabs_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        
        header_panel.SetSizer(header_sizer)
        tabs_sizer.Add(header_panel, 0, wx.EXPAND | wx.TOP, 15)
        
        # 添加分隔线
        separator = wx.Panel(self.tabs_panel, size=(-1, 1))
        separator.SetBackgroundColour(current_theme['border_color'])
        tabs_sizer.Add(separator, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        # 标签页选择下拉框 - 更现代的设计
        choice_panel = wx.Panel(self.tabs_panel)
        choice_panel.SetBackgroundColour(current_theme['card_bg'])
        choice_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.tabs_choice = wx.Choice(choice_panel, choices=[])
        self.tabs_choice.SetBackgroundColour(current_theme['card_bg'])
        self.tabs_choice.SetForegroundColour(current_theme['text_primary'])
        self.tabs_choice.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.tabs_choice.Bind(wx.EVT_CHOICE, self.on_tab_selected)
        self.tabs_choice.Enable(False)  # 初始状态禁用
        choice_sizer.Add(self.tabs_choice, 1, wx.EXPAND | wx.ALL, 10)
        
        # 刷新标签页按钮 - 更现代的设计
        refresh_button = wx.Button(choice_panel, label="🔄", size=(40, 40), style=wx.BORDER_NONE)
        refresh_button.SetToolTip("刷新标签页列表")
        refresh_button.SetBackgroundColour(wx.Colour(current_theme['accent_blue'].Red(), 
                                                 current_theme['accent_blue'].Green(), 
                                                 current_theme['accent_blue'].Blue(), 
                                                 40))  # 半透明背景
        refresh_button.SetForegroundColour(current_theme['accent_blue'])
        refresh_button.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        refresh_button.Bind(wx.EVT_BUTTON, self.on_refresh_tabs)
        refresh_button.Enable(False)  # 初始状态禁用
        self.refresh_tabs_button = refresh_button
        choice_sizer.Add(refresh_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        choice_panel.SetSizer(choice_sizer)
        tabs_sizer.Add(choice_panel, 0, wx.EXPAND)
        
        self.tabs_panel.SetSizer(tabs_sizer)
        self.main_layout.Add(self.tabs_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        self.tabs_panel.Hide()  # 初始状态隐藏

        # 添加网址输入区域 - 更现代的卡片式设计
        url_card = wx.Panel(self.main_card)
        url_card.SetBackgroundColour(current_theme['card_bg'])
        url_card_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 添加阴影效果
        def on_url_card_paint(event):
            dc = wx.PaintDC(url_card)
            gc = wx.GraphicsContext.Create(dc)
            width, height = url_card.GetSize()
            
            # 绘制圆角矩形
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, width, height, 10)
            gc.SetBrush(wx.Brush(current_theme['card_bg']))
            
            # 添加细微的边框
            gc.SetPen(wx.Pen(current_theme['border_color'], 1))
            gc.StrokePath(path)
            
            event.Skip()
            
        url_card.Bind(wx.EVT_PAINT, on_url_card_paint)
        
        # 网址输入标题 - 更现代的设计
        url_header = wx.Panel(url_card)
        url_header.SetBackgroundColour(current_theme['card_bg'])
        url_header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 添加图标
        url_icon = wx.StaticText(url_header, label="🌐")
        url_icon.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        url_icon.SetForegroundColour(current_theme['accent_blue'])
        url_header_sizer.Add(url_icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        
        # 网址输入标题
        url_label = wx.StaticText(url_header, label="网址")
        url_label.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        url_label.SetForegroundColour(current_theme['text_primary'])
        url_header_sizer.Add(url_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        
        url_header.SetSizer(url_header_sizer)
        url_card_sizer.Add(url_header, 0, wx.EXPAND | wx.TOP, 10)
        
        # 添加分隔线
        url_separator = wx.Panel(url_card, size=(-1, 1))
        url_separator.SetBackgroundColour(current_theme['border_color'])
        url_card_sizer.Add(url_separator, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        # 网址输入框 - 更现代的设计
        self.url_input, url_panel = create_modern_text_ctrl(url_card, "https://example.com")
        self.url_input.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.url_input.Bind(wx.EVT_TEXT, self.on_input_change)
        url_card_sizer.Add(url_panel, 0, wx.EXPAND | wx.ALL, 15)
        
        url_card.SetSizer(url_card_sizer)
        self.main_layout.Add(url_card, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)

        # 添加XPath输入区域 - 更现代的卡片式设计
        xpath_card = wx.Panel(self.main_card)
        xpath_card.SetBackgroundColour(current_theme['card_bg'])
        xpath_card_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 添加阴影效果
        def on_xpath_card_paint(event):
            dc = wx.PaintDC(xpath_card)
            gc = wx.GraphicsContext.Create(dc)
            width, height = xpath_card.GetSize()
            
            # 绘制圆角矩形
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, width, height, 10)
            gc.SetBrush(wx.Brush(current_theme['card_bg']))
            
            # 添加细微的边框
            gc.SetPen(wx.Pen(current_theme['border_color'], 1))
            gc.StrokePath(path)
            
            event.Skip()
            
        xpath_card.Bind(wx.EVT_PAINT, on_xpath_card_paint)
        
        # XPath输入标题 - 更现代的设计
        xpath_header = wx.Panel(xpath_card)
        xpath_header.SetBackgroundColour(current_theme['card_bg'])
        xpath_header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 添加图标
        xpath_icon = wx.StaticText(xpath_header, label="🔍")
        xpath_icon.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        xpath_icon.SetForegroundColour(current_theme['accent_purple'])
        xpath_header_sizer.Add(xpath_icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        
        # XPath输入标题
        xpath_label = wx.StaticText(xpath_header, label="元素选择器")
        xpath_label.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        xpath_label.SetForegroundColour(current_theme['text_primary'])
        xpath_header_sizer.Add(xpath_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        
        # 添加弹性空间
        xpath_header_sizer.AddStretchSpacer()
        
        # 添加定位方式选择 - 更现代的设计
        selector_label = wx.StaticText(xpath_header, label="定位方式:")
        selector_label.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        selector_label.SetForegroundColour(current_theme['text_secondary'])
        xpath_header_sizer.Add(selector_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

        self.selector_choice = wx.Choice(xpath_header, choices=["XPath", "CSS选择器"])
        self.selector_choice.SetSelection(0)
        self.selector_choice.SetBackgroundColour(current_theme['card_bg'])
        self.selector_choice.SetForegroundColour(current_theme['text_primary'])
        self.selector_choice.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.selector_choice.Bind(wx.EVT_CHOICE, self.on_locator_type_change)
        xpath_header_sizer.Add(self.selector_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        
        xpath_header.SetSizer(xpath_header_sizer)
        xpath_card_sizer.Add(xpath_header, 0, wx.EXPAND | wx.TOP, 10)
        
        # 添加分隔线
        xpath_separator = wx.Panel(xpath_card, size=(-1, 1))
        xpath_separator.SetBackgroundColour(current_theme['border_color'])
        xpath_card_sizer.Add(xpath_separator, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        # 美化XPath输入框 - 多行更现代风格
        self.xpath_input, xpath_panel = create_modern_text_ctrl(
            xpath_card, 
            "请输入XPath或CSS选择器",  # 修改默认提示文本
            style=wx.TE_MULTILINE,
            size=(-1, 120)  # 增加高度使其更明显
        )
        self.xpath_input.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.xpath_input.Bind(wx.EVT_TEXT, self.on_input_change)
        xpath_card_sizer.Add(xpath_panel, 0, wx.EXPAND | wx.ALL, 15)
        
        xpath_card.SetSizer(xpath_card_sizer)
        self.main_layout.Add(xpath_card, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)

        # 创建浏览器状态卡片 - 更现代的设计
        status_card = wx.Panel(self.main_card)
        status_card.SetBackgroundColour(current_theme['card_bg'])
        status_card_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 添加阴影效果
        def on_status_card_paint(event):
            dc = wx.PaintDC(status_card)
            gc = wx.GraphicsContext.Create(dc)
            width, height = status_card.GetSize()
            
            # 绘制圆角矩形
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, width, height, 10)
            gc.SetBrush(wx.Brush(current_theme['card_bg']))
            
            # 添加细微的边框
            gc.SetPen(wx.Pen(current_theme['border_color'], 1))
            gc.StrokePath(path)
            
            event.Skip()
            
        status_card.Bind(wx.EVT_PAINT, on_status_card_paint)
        
        # 添加状态图标 - 使用更协调的颜色
        status_icon = wx.StaticText(status_card, label="⚠️")
        status_icon.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        status_icon.SetForegroundColour(wx.Colour(244, 63, 94, 180))  # 使用半透明的红色，更协调
        status_card_sizer.Add(status_icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        
        # 创建浏览器状态标签 - 更现代的设计
        self.browser_status_label = wx.StaticText(status_card, label="未连接到浏览器")
        self.browser_status_label.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.browser_status_label.SetForegroundColour(wx.Colour(244, 63, 94, 180))  # 使用半透明的红色，更协调
        status_card_sizer.Add(self.browser_status_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 10)
        
        status_card.SetSizer(status_card_sizer)
        self.main_layout.Add(status_card, 0, wx.EXPAND | wx.ALL, 20)

        # 将滚动窗口添加到页面布局
        self.page_layout.Add(self.scroll_win, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 15)

        # 创建单独的面板放置自动投放按钮 - 更现代的设计
        button_card = wx.Panel(self)
        button_card.SetBackgroundColour(current_theme['bg_color'])
        
        # 添加阴影效果
        def on_button_card_paint(event):
            dc = wx.PaintDC(button_card)
            gc = wx.GraphicsContext.Create(dc)
            width, height = button_card.GetSize()
            
            # 绘制圆角矩形
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, width, height, 10)
            gc.SetBrush(wx.Brush(current_theme['bg_color']))
            
            event.Skip()
            
        button_card.Bind(wx.EVT_PAINT, on_button_card_paint)
        
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        button_card.SetSizer(button_sizer)

        # 添加自动开关投放按钮 - 更现代的设计
        self.auto_delivery_button = create_gradient_button(
            button_card, 
            "🚀 启用自动投放", 
            size=(-1, 60)  # 增加按钮高度使其更明显
        )
        # 初始状态下禁用按钮，但确保它可见
        self.auto_delivery_button.Enable(False)
        self.auto_delivery_button.Show(True)
        self.auto_delivery_button.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.auto_delivery_button.Bind(wx.EVT_BUTTON, self.on_toggle_auto_delivery)
        # 使用更大的边距，确保按钮更明显
        button_sizer.Add(self.auto_delivery_button, 1, wx.EXPAND | wx.ALL, 15)
        
        # 创建状态标签 - 更现代的设计
        status_panel = wx.Panel(button_card)
        status_panel.SetBackgroundColour(current_theme['bg_color'])
        status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 添加状态图标 - 使用更协调的颜色
        status_icon = wx.StaticText(status_panel, label="✅")
        status_icon.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        status_icon.SetForegroundColour(wx.Colour(34, 197, 94, 180))  # 使用半透明的绿色，更协调
        status_sizer.Add(status_icon, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # 状态文本
        self.status_label = wx.StaticText(status_panel, label="就绪")
        self.status_label.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.status_label.SetForegroundColour(wx.Colour(34, 197, 94, 180))  # 使用半透明的绿色，更协调
        status_sizer.Add(self.status_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        
        status_panel.SetSizer(status_sizer)
        button_sizer.Add(status_panel, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        # 将按钮面板添加到页面布局
        self.page_layout.Add(button_card, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        
        # 确保所有布局正确显示
        self.main_layout.Layout()
        self.scroll_sizer.Layout()
        self.page_layout.Layout()
        self.scroll_win.FitInside()
        self.Refresh()

    def on_connect_browser(self, event):
        # 使用按钮反馈效果
        button_feedback(self.connect_button)
        
        # 查找状态图标
        status_icon = None
        for child in self.browser_status_label.GetParent().GetChildren():
            if isinstance(child, wx.StaticText) and child != self.browser_status_label:
                status_icon = child
                break
        
        # 尝试连接浏览器
        if self.auto_click_manager.connect_to_browser():
            # 更新状态标签 - 使用更协调的颜色
            self.browser_status_label.SetLabel("已连接到浏览器")
            self.browser_status_label.SetForegroundColour(wx.Colour(34, 197, 94, 180))  # 使用半透明的绿色，更协调
            
            # 更新状态图标
            if status_icon:
                status_icon.SetLabel("✅")
                status_icon.SetForegroundColour(wx.Colour(34, 197, 94, 180))  # 使用半透明的绿色，更协调
            
            # 获取当前URL并更新输入框
            current_url = self.auto_click_manager.get_current_url()
            if current_url:
                self.url_input.SetValue(current_url)
            
            # 显示标签页选择面板
            self.tabs_panel.Show()
            
            # 启用标签页选择和刷新按钮
            self.tabs_choice.Enable(True)
            self.refresh_tabs_button.Enable(True)
            
            # 获取并加载标签页列表
            self.load_browser_tabs()
                
            # 确保自动投放按钮可见
            self.auto_delivery_button.Show(True)
            self.auto_delivery_button.Enable(True)
            
            # 重新布局，确保UI正确更新
            self.main_layout.Layout()
            self.scroll_sizer.Layout()
            self.page_layout.Layout()
            self.scroll_win.FitInside()
            self.Refresh()
            logger.info("浏览器连接成功，UI已更新")
            
            # 显示成功消息
            wx.MessageBox("成功连接到Edge浏览器！", "连接成功", wx.OK | wx.ICON_INFORMATION)
        else:
            # 更新状态标签
            self.browser_status_label.SetLabel("连接失败")
            self.browser_status_label.SetForegroundColour(current_theme['accent_red'])
            
            # 更新状态图标
            if status_icon:
                status_icon.SetLabel("⚠️")
                status_icon.SetForegroundColour(current_theme['accent_red'])
                
            # 确保标签页选择面板隐藏
            self.tabs_panel.Hide()
            # 禁用标签页选择和刷新按钮
            self.tabs_choice.Enable(False)
            self.refresh_tabs_button.Enable(False)
            wx.MessageBox("无法连接到浏览器，请确保已打开Edge并启用远程调试\n\n启动命令: msedge.exe --remote-debugging-port=9222", "连接失败", wx.OK | wx.ICON_ERROR)
            
    def load_browser_tabs(self):
        """获取并加载浏览器标签页列表"""
        try:
            # 获取所有标签页
            tabs = self.auto_click_manager.get_all_tabs()
            
            if not tabs:
                logger.warning("未获取到标签页信息")
                return
                
            # 清空当前选项
            self.tabs_choice.Clear()
            
            # 存储标签页信息
            self.browser_tabs = tabs
            
            # 添加标签页选项
            for i, tab in enumerate(tabs):
                # 截取标题，避免过长
                title = tab['title']
                if len(title) > 50:
                    title = title[:47] + "..."
                    
                # 添加到选择框，格式："标题 (URL)"
                url = tab['url']
                if len(url) > 30:
                    url = url[:27] + "..."
                    
                display_text = f"{title} ({url})"
                self.tabs_choice.Append(display_text)
                
                # 如果是当前标签页，选中它
                if tab.get('is_current', False):
                    self.tabs_choice.SetSelection(i)
                    # 更新URL输入框
                    self.url_input.SetValue(tab['url'])
            
            # 如果没有自动选择，则选择第一个
            if self.tabs_choice.GetSelection() == wx.NOT_FOUND and self.tabs_choice.GetCount() > 0:
                self.tabs_choice.SetSelection(0)
                # 更新URL输入框
                if tabs:
                    self.url_input.SetValue(tabs[0]['url'])
                    
            logger.info(f"已加载 {len(tabs)} 个标签页")
        except Exception as e:
            logger.error(f"加载标签页失败: {str(e)}")
            
    def on_refresh_tabs(self, event):
        """刷新标签页列表"""
        button_feedback(self.refresh_tabs_button)
        self.load_browser_tabs()
        
    def on_tab_selected(self, event):
        """标签页选择事件处理"""
        try:
            selected_index = self.tabs_choice.GetSelection()
            if selected_index != wx.NOT_FOUND and 0 <= selected_index < len(self.browser_tabs):
                selected_tab = self.browser_tabs[selected_index]
                
                # 切换到选中的标签页
                if self.auto_click_manager.browser_connector.switch_to_tab_by_id(selected_tab['handle']):
                    # 更新URL输入框
                    self.url_input.SetValue(selected_tab['url'])
                    logger.info(f"已切换到标签页: {selected_tab['title']}")
                else:
                    logger.error(f"切换到标签页失败: {selected_tab['title']}")
        except Exception as e:
            logger.error(f"标签页选择处理失败: {str(e)}")

    def on_toggle_auto_delivery(self, event):
        # 调用反馈动效
        button_feedback(self.auto_delivery_button)
        
        # 切换自动投放状态
        is_enabled = self.auto_click_manager.toggle_auto_delivery()

        # 获取当前设置
        url = self.url_input.GetValue().strip()
        xpath = self.xpath_input.GetValue().strip()
        selector_type = "xpath" if self.selector_choice.GetSelection() == 0 else "css"

        # 查找状态图标
        status_icon = None
        for child in self.auto_delivery_button.GetParent().GetChildren():
            if isinstance(child, wx.Panel):
                for panel_child in child.GetChildren():
                    if isinstance(panel_child, wx.StaticText) and panel_child != self.status_label:
                        status_icon = panel_child
                        break

        if is_enabled:
            # 更新目标URL和XPath
            self.auto_click_manager.set_target_url(url)
            self.auto_click_manager.set_target_xpath(xpath, selector_type)

            self.auto_delivery_button.SetLabel("🛑 关闭自动投放")
            interval = self.auto_click_manager.get_delivery_interval()
            self.status_label.SetLabel(f"自动投放已开启，间隔{interval}秒")
            
            # 更新状态图标
            if status_icon:
                status_icon.SetLabel("🔄")
                status_icon.SetForegroundColour(current_theme['accent_blue'])
            
            logger.info(f"自动投放已开启，间隔{interval}秒")
            # 添加状态变化动效
            button_pulse(self.auto_delivery_button)
        else:
            self.auto_delivery_button.SetLabel("🚀 启用自动投放")
            self.status_label.SetLabel("自动投放已关闭")
            
            # 更新状态图标
            if status_icon:
                status_icon.SetLabel("✅")
                status_icon.SetForegroundColour(current_theme['accent_green'])
                
            logger.info("自动投放已关闭")
            
        # 确保按钮可见
        self.auto_delivery_button.Show(True)
        logger.info("自动投放按钮状态已更新并显示")
            
        # 强制更新UI布局
        self.main_layout.Layout()
        self.scroll_sizer.Layout()
        self.page_layout.Layout()
        self.scroll_win.FitInside()
        self.Refresh()
        logger.info("UI布局已更新")

    def on_locator_type_change(self, event):
        selection = self.selector_choice.GetSelection()
        locator_type = "xpath" if selection == 0 else "css"
        self.auto_click_manager.set_locator_type(locator_type)
        logger.info(f"定位方式已切换为: {locator_type}")

    def on_input_change(self, event):
        self._validate_inputs()
        # 强制更新UI布局，确保自动投放按钮可见
        self.main_layout.Layout()
        self.scroll_sizer.Layout()
        self.page_layout.Layout()
        self.scroll_win.FitInside()
        self.Refresh()

    def on_close_browser(self):
        # 关闭浏览器连接
        self.auto_click_manager.close_browser()
        
        # 更新状态标签
        self.browser_status_label.SetLabel("未连接到浏览器")
        self.browser_status_label.SetForegroundColour(current_theme['accent_red'])
        
        # 停止自动投放
        if self.auto_click_manager.auto_delivery_enabled:
            self.auto_click_manager.toggle_auto_delivery()
            self.auto_delivery_button.SetLabel("启用自动投放")
        
        # 禁用自动投放按钮
        self.auto_delivery_button.Enable(False)
        
        # 隐藏标签页选择面板
        self.tabs_panel.Hide()
        
        # 禁用标签页选择和刷新按钮
        self.tabs_choice.Enable(False)
        self.refresh_tabs_button.Enable(False)
        
        # 清空标签页列表
        self.tabs_choice.Clear()
        self.browser_tabs = []
        
        # 重新布局，确保UI正确更新
        self.main_layout.Layout()
        self.scroll_sizer.Layout()
        self.page_layout.Layout()
        self.scroll_win.FitInside()
        self.Refresh()

    def _validate_inputs(self):
        # 检查浏览器是否已连接
        browser_connected = self.auto_click_manager.is_browser_connected()
        # 检查网址和XPath是否已输入
        url_entered = bool(self.url_input.GetValue().strip())
        xpath_entered = bool(self.xpath_input.GetValue().strip())

        # 更新目标XPath和URL
        if url_entered:
            self.auto_click_manager.set_target_url(self.url_input.GetValue().strip())
        if xpath_entered:
            self.auto_click_manager.set_target_xpath(self.xpath_input.GetValue().strip())

        # 启用/禁用自动投放按钮
        button_should_enable = browser_connected and url_entered and xpath_entered
        self.auto_delivery_button.Enable(button_should_enable)
        # 确保按钮状态更新后可见
        self.auto_delivery_button.Show(True)

        # 更新状态标签
        if not browser_connected:
            self.status_label.SetLabel("未连接到浏览器")
        elif not url_entered:
            self.status_label.SetLabel("请输入网址")
        elif not xpath_entered:
            self.status_label.SetLabel("请输入XPath或CSS选择器")
        else:
            self.status_label.SetLabel("就绪")
            # 如果所有条件满足，确保自动投放按钮可见并记录日志
            logger.info(f"所有条件满足，自动投放按钮已启用: 浏览器={browser_connected}, URL={url_entered}, XPath={xpath_entered}")
            # 强制按钮显示在前面
            self.auto_delivery_button.Raise()

        # 确保所有元素都被添加到布局中并正确显示
        self.main_layout.Layout()
        self.scroll_sizer.Layout()
        self.page_layout.Layout()
        
        # 确保滚动窗口正确显示所有内容
        self.scroll_win.FitInside()
        self.scroll_win.Refresh()
        self.Refresh()