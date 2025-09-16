import wx  # 添加 wx 模块导入
import math
import colorsys
import wx.lib.newevent

# 创建自定义事件用于主题切换
ThemeChangeEvent, EVT_THEME_CHANGE = wx.lib.newevent.NewEvent()

# 定义主题颜色 - 更现代的配色方案
LIGHT_THEME = {
    'bg_color': wx.Colour(248, 250, 252),  # 更柔和的背景色
    'card_bg': wx.Colour(255, 255, 255),
    'text_primary': wx.Colour(30, 41, 59),  # 更深的主文本色
    'text_secondary': wx.Colour(100, 116, 139),  # 更柔和的次要文本色
    'accent_blue': wx.Colour(56, 189, 248),  # 更鲜亮的蓝色
    'accent_purple': wx.Colour(168, 85, 247),  # 添加紫色调
    'accent_green': wx.Colour(34, 197, 94),  # 更鲜亮的绿色
    'accent_red': wx.Colour(244, 63, 94),  # 更鲜亮的红色
    'accent_orange': wx.Colour(249, 115, 22),  # 添加橙色调
    'border_color': wx.Colour(226, 232, 240),  # 更柔和的边框色
    'highlight_color': wx.Colour(14, 165, 233),  # 高亮色
    'gradient_start': wx.Colour(56, 189, 248),  # 渐变起始色
    'gradient_end': wx.Colour(103, 232, 249)  # 渐变结束色
}

DARK_THEME = {
    'bg_color': wx.Colour(15, 23, 42),  # 更深邃的背景色
    'card_bg': wx.Colour(30, 41, 59),  # 更柔和的卡片背景
    'text_primary': wx.Colour(248, 250, 252),  # 更柔和的主文本色
    'text_secondary': wx.Colour(148, 163, 184),  # 更柔和的次要文本色
    'accent_blue': wx.Colour(56, 189, 248),  # 保持与亮色主题一致
    'accent_purple': wx.Colour(168, 85, 247),  # 添加紫色调
    'accent_green': wx.Colour(34, 197, 94),  # 保持与亮色主题一致
    'accent_red': wx.Colour(244, 63, 94),  # 保持与亮色主题一致
    'accent_orange': wx.Colour(249, 115, 22),  # 添加橙色调
    'border_color': wx.Colour(51, 65, 85),  # 更柔和的边框色
    'highlight_color': wx.Colour(2, 132, 199),  # 高亮色
    'gradient_start': wx.Colour(56, 189, 248),  # 渐变起始色
    'gradient_end': wx.Colour(103, 232, 249)  # 渐变结束色
}

# 当前主题
current_theme = LIGHT_THEME


def toggle_theme():
    """切换主题（亮色/暗色）"""
    global current_theme
    current_theme = DARK_THEME if current_theme == LIGHT_THEME else LIGHT_THEME
    return current_theme


def button_feedback(button):
    """按钮点击反馈动效 - 点击时颜色变化"""
    # 保存原始样式
    original_bg = button.GetBackgroundColour()
    original_fg = button.GetForegroundColour()

    # 更改样式作为反馈
    button.SetBackgroundColour(current_theme['highlight_color'])
    button.SetForegroundColour(wx.WHITE)
    button.Refresh()

    # 恢复原始样式
    def restore_style():
        button.SetBackgroundColour(original_bg)
        button.SetForegroundColour(original_fg)
        button.Refresh()

    wx.CallLater(100, restore_style)


def button_pulse(button):
    """按钮脉动动效 - 颜色变化"""
    if not hasattr(button, 'pulse_state'):
        button.pulse_state = 0
        # 保存原始样式
        button.original_bg = button.GetBackgroundColour()
        button.original_fg = button.GetForegroundColour()

    # 简化脉动效果，直接切换样式
    if button.pulse_state < 6:  # 持续约0.6秒
        if button.pulse_state % 2 == 0:
            button.SetBackgroundColour(current_theme['highlight_color'])
            button.SetForegroundColour(wx.WHITE)
        else:
            button.SetBackgroundColour(button.original_bg)
            button.SetForegroundColour(button.original_fg)
        button.pulse_state += 1
        button.Refresh()
        wx.CallLater(100, lambda: button_pulse(button))
    else:
        # 恢复原始样式
        button.SetBackgroundColour(button.original_bg)
        button.SetForegroundColour(button.original_fg)
        button.Refresh()
        delattr(button, 'pulse_state')
        delattr(button, 'original_bg')
        delattr(button, 'original_fg')


def create_gradient_button(parent, label, start_color=None, end_color=None, size=(-1, 45), radius=10):
    """创建现代渐变按钮"""
    # 使用主题中定义的渐变色，如果没有指定
    if start_color is None:
        start_color = current_theme.get('gradient_start', wx.Colour(56, 189, 248))
    if end_color is None:
        end_color = current_theme.get('gradient_end', wx.Colour(103, 232, 249))
        
    button = wx.Button(parent, label=label, size=size, style=wx.BORDER_NONE)
    button.SetForegroundColour(wx.WHITE)
    # 使用现代无衬线字体
    button.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

    # 创建圆角渐变位图
    width, height = button.GetSize()
    bitmap = wx.Bitmap(width, height)
    dc = wx.MemoryDC(bitmap)
    dc.SetBackground(wx.Brush(current_theme['card_bg']))
    dc.Clear()

    # 绘制渐变背景
    r1, g1, b1 = start_color.Red(), start_color.Green(), start_color.Blue()
    r2, g2, b2 = end_color.Red(), end_color.Green(), end_color.Blue()

    # 绘制圆角矩形
    graphics = wx.GraphicsContext.Create(dc)
    path = graphics.CreatePath()
    path.AddRoundedRectangle(0, 0, width, height, radius)
    brush = graphics.CreateLinearGradientBrush(0, 0, 0, height, start_color, end_color)
    graphics.SetBrush(brush)
    graphics.FillPath(path)

    # 绘制按钮标签
    text_width, text_height = button.GetTextExtent(label)
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    dc.SetTextForeground(wx.WHITE)
    dc.DrawText(label, text_x, text_y)

    dc.SelectObject(wx.NullBitmap)
    button.SetBitmap(bitmap)

    # 添加悬停效果
    def on_enter(event):
        # 高亮颜色
        highlight_start = wx.Colour(min(255, r1 + 30), min(255, g1 + 30), min(255, b1 + 30))
        highlight_end = wx.Colour(min(255, r2 + 30), min(255, g2 + 30), min(255, b2 + 30))

        # 创建高亮渐变位图
        highlight_bitmap = wx.Bitmap(width, height)
        highlight_dc = wx.MemoryDC(highlight_bitmap)
        highlight_dc.SetBackground(wx.Brush(current_theme['card_bg']))
        highlight_dc.Clear()

        graphics = wx.GraphicsContext.Create(highlight_dc)
        path = graphics.CreatePath()
        path.AddRoundedRectangle(0, 0, width, height, radius)
        brush = graphics.CreateLinearGradientBrush(0, 0, 0, height, highlight_start, highlight_end)
        graphics.SetBrush(brush)
        graphics.FillPath(path)

        # 绘制按钮标签
        highlight_dc.SetTextForeground(wx.WHITE)
        highlight_dc.DrawText(label, text_x, text_y)

        highlight_dc.SelectObject(wx.NullBitmap)
        button.SetBitmap(highlight_bitmap)
        button.Refresh()
        event.Skip()

    def on_leave(event):
        button.SetBitmap(bitmap)
        button.Refresh()
        event.Skip()

    button.Bind(wx.EVT_ENTER_WINDOW, on_enter)
    button.Bind(wx.EVT_LEAVE_WINDOW, on_leave)

    return button


def create_modern_text_ctrl(parent, hint="", style=0, size=(-1, 40)):
    """创建现代风格文本输入框"""
    # 创建自定义绘制的面板作为背景
    panel = wx.Panel(parent)
    panel.SetBackgroundColour(current_theme['card_bg'])
    
    # 文本输入框的父窗口应该是 panel，而不是 parent
    text_ctrl = wx.TextCtrl(panel, style=style | wx.BORDER_NONE, size=size)
    text_ctrl.SetHint(hint)
    text_ctrl.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 8)
    panel.SetSizer(sizer)

    # 自定义绘制边框
    def on_paint(event):
        dc = wx.PaintDC(panel)
        gc = wx.GraphicsContext.Create(dc)
        width, height = panel.GetSize()

        # 绘制圆角矩形边框
        path = gc.CreatePath()
        path.AddRoundedRectangle(0, 0, width, height, 8)
        gc.SetPen(wx.Pen(current_theme['border_color'], 1))
        gc.StrokePath(path)

    panel.Bind(wx.EVT_PAINT, on_paint)

    return text_ctrl, panel


def create_rounded_panel(parent, radius=12):
    """创建带圆角的面板"""
    panel = wx.Panel(parent)
    panel.SetBackgroundColour(current_theme['card_bg'])

    # 自定义绘制圆角
    def on_paint(event):
        try:
            dc = wx.PaintDC(panel)
            gc = wx.GraphicsContext.Create(dc)
            width, height = panel.GetSize()

            # 绘制圆角矩形背景
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, width, height, radius)
            gc.SetBrush(wx.Brush(current_theme['card_bg']))
            gc.FillPath(path)

            # 绘制阴影
            shadow_path = gc.CreatePath()
            shadow_path.AddRoundedRectangle(2, 2, width-2, height-2, radius)
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 10), 1))
            gc.StrokePath(shadow_path)
        except RuntimeError:
            # 面板可能已被删除，忽略错误
            pass

    panel.Bind(wx.EVT_PAINT, on_paint)
    return panel


def apply_modern_style(window):
    """应用现代风格到窗口"""
    window.SetBackgroundColour(current_theme['bg_color'])

    # 递归设置所有子窗口的样式
    for child in window.GetChildren():
        if isinstance(child, wx.Panel):
            child.SetBackgroundColour(current_theme['bg_color'])
            apply_modern_style(child)
        elif isinstance(child, wx.Button) and child.GetWindowStyleFlag() & wx.BORDER_SIMPLE:
            # 美化普通按钮
            child.SetWindowStyleFlag(wx.BORDER_NONE)
            child.SetBackgroundColour(current_theme['accent_blue'])
            child.SetForegroundColour(wx.WHITE)
        elif isinstance(child, wx.StaticText):
            # 设置文本颜色
            if child.GetFont().GetWeight() == wx.FONTWEIGHT_BOLD:
                child.SetForegroundColour(current_theme['text_primary'])
            else:
                child.SetForegroundColour(current_theme['text_secondary'])