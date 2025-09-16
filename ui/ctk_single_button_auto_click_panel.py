import customtkinter as ctk
import os
from logger import logger
from tkinter import messagebox

class CTkSingleButtonAutoClickPanel(ctk.CTkFrame):
    def __init__(self, parent, auto_click_manager, on_back_callback):
        super().__init__(parent)
        self.auto_click_manager = auto_click_manager
        self.on_back_callback = on_back_callback
        self.pack(fill="both", expand=True)
        
        # 初始化标签页存储
        self.browser_tabs = []
        
        # 初始化UI组件
        self._init_ui()
    
    def _init_ui(self):
        # 创建标题区域
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # 返回按钮
        back_button = ctk.CTkButton(
            title_frame,
            text="⬅ 返回",
            font=ctk.CTkFont(size=12),
            width=80,
            command=self.on_back
        )
        back_button.pack(side="left", padx=10)
        
        # 创建标题容器
        title_container = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_container.pack(side="left", padx=10, fill="both", expand=True)
        
        # 创建装饰线
        decoration = ctk.CTkFrame(title_container, width=6, height=40, fg_color="#38BDF8")
        decoration.pack(side="left")
        
        # 创建文本容器
        text_container = ctk.CTkFrame(title_container, fg_color="transparent")
        text_container.pack(side="left", padx=10, fill="both", expand=True)
        
        # 创建标题和副标题
        title_label = ctk.CTkLabel(
            text_container, 
            text="单按钮自动点击", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            text_container, 
            text="设置自动点击的详细参数", 
            font=ctk.CTkFont(size=12)
        )
        subtitle.pack(anchor="w")
        
        # 创建分隔线
        separator = ctk.CTkFrame(self, height=1, fg_color=("#E2E8F0", "#334155"))
        separator.pack(fill="x", padx=20, pady=10)
        
        # 创建滚动容器
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 创建主卡片
        self.main_card = ctk.CTkFrame(self.scrollable_frame)
        self.main_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建标签页选择区域
        self.tabs_frame = ctk.CTkFrame(self.main_card)
        self.tabs_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tabs_label = ctk.CTkLabel(
            self.tabs_frame,
            text="标签页选择:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        tabs_label.pack(anchor="w", padx=10, pady=5)
        
        # 标签页列表容器
        self.tabs_list_frame = ctk.CTkFrame(self.tabs_frame, fg_color="transparent")
        self.tabs_list_frame.pack(fill="x", padx=10, pady=5)
        
        # 刷新标签页按钮
        self.refresh_tabs_button = ctk.CTkButton(
            self.tabs_frame,
            text="刷新标签页列表",
            font=ctk.CTkFont(size=12),
            command=self.refresh_tabs
        )
        self.refresh_tabs_button.pack(fill="x", padx=10, pady=5)
        
        # 创建目标设置区域
        self.target_frame = ctk.CTkFrame(self.main_card)
        self.target_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        target_label = ctk.CTkLabel(
            self.target_frame,
            text="目标设置:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        target_label.pack(anchor="w", padx=10, pady=5)
        
        # 目标URL输入
        url_frame = ctk.CTkFrame(self.target_frame, fg_color="transparent")
        url_frame.pack(fill="x", padx=10, pady=5)
        
        url_label = ctk.CTkLabel(url_frame, text="目标URL模式:")
        url_label.pack(side="left")
        
        self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="输入URL模式，例如: example.com")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=10)
        
        # 目标XPath输入
        xpath_frame = ctk.CTkFrame(self.target_frame, fg_color="transparent")
        xpath_frame.pack(fill="x", padx=10, pady=5)
        
        xpath_label = ctk.CTkLabel(xpath_frame, text="目标XPath:")
        xpath_label.pack(side="left")
        
        self.xpath_entry = ctk.CTkEntry(xpath_frame, placeholder_text="输入XPath，例如: //button[@id='submit']")
        self.xpath_entry.pack(side="left", fill="x", expand=True, padx=10)
        
        # 创建操作区域
        self.action_frame = ctk.CTkFrame(self.main_card)
        self.action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        action_label = ctk.CTkLabel(
            self.action_frame,
            text="操作控制:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        action_label.pack(anchor="w", padx=10, pady=5)
        
        # 间隔设置
        interval_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        interval_frame.pack(fill="x", padx=10, pady=5)
        
        interval_label = ctk.CTkLabel(interval_frame, text="点击间隔(秒):")
        interval_label.pack(side="left")
        
        self.interval_slider = ctk.CTkSlider(
            interval_frame, 
            from_=1, 
            to=10,
            number_of_steps=9,
            command=self.update_interval_label
        )
        self.interval_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.interval_slider.set(3)  # 默认值
        
        self.interval_value_label = ctk.CTkLabel(interval_frame, text="3秒")
        self.interval_value_label.pack(side="left", padx=5)
        
        # 添加随机间隔设置区域
        random_interval_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        random_interval_frame.pack(fill="x", padx=10, pady=10)
        
        # 启用随机间隔复选框
        self.enable_random_interval = ctk.CTkCheckBox(
            random_interval_frame,
            text="启用随机间隔时间",
            command=self.toggle_random_interval
        )
        self.enable_random_interval.pack(anchor="w", padx=10, pady=5)
        
        # 最低和最高间隔输入框
        min_max_frame = ctk.CTkFrame(random_interval_frame, fg_color="transparent")
        min_max_frame.pack(fill="x", padx=10, pady=5)
        
        min_interval_label = ctk.CTkLabel(min_max_frame, text="最低间隔(秒):")
        min_interval_label.pack(side="left")
        
        self.min_interval_entry = ctk.CTkEntry(min_max_frame, width=80, placeholder_text="1")
        self.min_interval_entry.pack(side="left", padx=10)
        self.min_interval_entry.insert(0, "1")
        
        max_interval_label = ctk.CTkLabel(min_max_frame, text="最高间隔(秒):")
        max_interval_label.pack(side="left", padx=(20, 0))
        
        self.max_interval_entry = ctk.CTkEntry(min_max_frame, width=80, placeholder_text="10")
        self.max_interval_entry.pack(side="left", padx=10)
        self.max_interval_entry.insert(0, "10")
        
        # 按钮容器
        buttons_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # 创建控制按钮
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_button = ctk.CTkButton(
            self.control_frame,
            text="开始",
            command=self.start_auto_click
        )
        self.start_button.pack(side="right", padx=5)
        
        # 添加结束按钮
        self.stop_button = ctk.CTkButton(
            self.control_frame,
            text="结束",
            command=self.stop_auto_click,
            state="disabled"
        )
        self.stop_button.pack(side="right", padx=5)
        
        # 测试点击按钮
        self.test_button = ctk.CTkButton(
            buttons_frame,
            text="🔍 测试单次点击",
            font=ctk.CTkFont(size=12),
            command=self.test_click
        )
        self.test_button.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # 初始化标签页列表
        self.refresh_tabs()
    
    def on_back(self):
        """返回上一级菜单"""
        if self.on_back_callback:
            self.on_back_callback()
    
    def update_interval_label(self, value):
        """更新间隔时间标签"""
        interval = int(value)
        self.interval_value_label.configure(text=f"{interval}秒")
        if self.auto_click_manager:
            self.auto_click_manager.delivery_interval = interval
    
    def toggle_random_interval(self):
        """切换随机间隔设置"""
        if self.enable_random_interval.get() == 1:
            # 启用随机间隔时，禁用固定间隔滑块
            self.interval_slider.configure(state="disabled")
        else:
            # 禁用随机间隔时，启用固定间隔滑块
            self.interval_slider.configure(state="normal")
    
    def get_random_interval(self):
        """获取随机间隔时间"""
        try:
            min_interval = float(self.min_interval_entry.get())
            max_interval = float(self.max_interval_entry.get())
            
            # 确保最小值不大于最大值
            if min_interval > max_interval:
                min_interval, max_interval = max_interval, min_interval
                self.min_interval_entry.delete(0, 'end')
                self.min_interval_entry.insert(0, str(min_interval))
                self.max_interval_entry.delete(0, 'end')
                self.max_interval_entry.insert(0, str(max_interval))
            
            # 生成随机间隔时间
            random_interval = random.uniform(min_interval, max_interval)
            return random_interval
        except ValueError:
            # 如果输入无效，返回默认值
            return self.auto_click_manager.delivery_interval if self.auto_click_manager else 3
    
    def refresh_tabs(self):
        """刷新标签页列表"""
        # 清空现有标签页列表
        for widget in self.tabs_list_frame.winfo_children():
            widget.destroy()
        
        self.browser_tabs = []
        
        # 获取所有标签页
        if self.auto_click_manager.is_browser_connected():
            try:
                tabs = self.auto_click_manager.get_all_tabs()
                
                if tabs:
                    # 创建标签页选择器
                    for i, tab in enumerate(tabs):
                        tab_frame = ctk.CTkFrame(self.tabs_list_frame, fg_color="transparent")
                        tab_frame.pack(fill="x", pady=2)
                        
                        # 使用标签页对象的title属性，如果是字典格式
                        if isinstance(tab, dict) and 'title' in tab:
                            tab_title = tab['title']
                            tab_id = tab['id'] if 'id' in tab else None
                        else:
                            tab_title = f"标签页 {i+1}"
                            tab_id = None
                        
                        tab_button = ctk.CTkButton(
                            tab_frame,
                            text=f"{tab_title}",
                            command=lambda idx=i: self.switch_to_tab(idx),
                            anchor="w",
                            height=30
                        )
                        tab_button.pack(fill="x")
                        
                        self.browser_tabs.append(tab)
                else:
                    no_tabs_label = ctk.CTkLabel(
                        self.tabs_list_frame,
                        text="未找到标签页"
                    )
                    no_tabs_label.pack(pady=10)
            except Exception as e:
                logger.error(f"刷新标签页列表时出错: {str(e)}")
                error_label = ctk.CTkLabel(
                    self.tabs_list_frame,
                    text=f"获取标签页失败: {str(e)}"
                )
                error_label.pack(pady=10)
    
    def switch_to_tab(self, index):
        """切换到指定标签页"""
        if 0 <= index < len(self.browser_tabs):
            try:
                if self.auto_click_manager.switch_to_tab_by_index(index):
                    # 根据标签页数据类型获取标签页信息
                    if isinstance(self.browser_tabs[index], dict):
                        tab_info = self.browser_tabs[index]['title'] if 'title' in self.browser_tabs[index] else f"标签页 {index+1}"
                        
                        # 自动填充URL到目标URL模式输入框
                        if 'url' in self.browser_tabs[index] and self.browser_tabs[index]['url'] != "未获取":
                            self.url_entry.delete(0, 'end')
                            self.url_entry.insert(0, self.browser_tabs[index]['url'])
                            # 设置目标标签页URL
                            self.auto_click_manager.set_target_tab_url(self.browser_tabs[index]['url'])
                    else:
                        tab_info = f"标签页 {index+1}"
                        
                    logger.info(f"已切换到{tab_info}")
            except Exception as e:
                logger.error(f"切换标签页失败: {str(e)}")
    
    def toggle_auto_click(self):
        """切换自动点击状态"""
        # 获取目标URL和XPath
        target_url = self.url_entry.get()
        target_xpath = self.xpath_entry.get()
        
        # 设置目标
        self.auto_click_manager.set_target_url(target_url)
        self.auto_click_manager.set_target_xpath(target_xpath)
        
        # 设置随机间隔参数
        if self.enable_random_interval.get() == 1:
            min_interval = self.min_interval_entry.get()
            max_interval = self.max_interval_entry.get()
            self.auto_click_manager.set_random_interval_range(min_interval, max_interval)
            self.auto_click_manager.enable_random_interval = True
        else:
            self.auto_click_manager.enable_random_interval = False

        # 切换自动点击状态
        is_enabled = self.auto_click_manager.toggle_auto_delivery()
        
        if is_enabled:
            self.start_button.configure(
                text="⏹️ 停止自动点击",
                fg_color="#EF4444",  # 红色
                hover_color="#DC2626"
            )
            logger.info("开始自动点击")
        else:
            self.start_button.configure(
                text="▶️ 开始自动点击",
                fg_color="#10B981",  # 绿色
                hover_color="#059669"
            )
            logger.info("停止自动点击")
    
    def test_click(self):
        """测试单次点击"""
        # 获取目标URL和XPath
        target_url = self.url_entry.get()
        target_xpath = self.xpath_entry.get()
        
        # 设置目标
        self.auto_click_manager.set_target_url(target_url)
        self.auto_click_manager.set_target_xpath(target_xpath)
        
        # 执行单次点击
        try:
            result = self.auto_click_manager.perform_click()
            if result:
                logger.info("测试点击成功")
            else:
                logger.warning("测试点击失败")
        except Exception as e:
            logger.error(f"测试点击时发生错误: {str(e)}")

    def start_auto_click(self):
        # 获取目标URL和XPath
        target_url = self.url_entry.get()
        target_xpath = self.xpath_entry.get()

        # 设置目标
        self.auto_click_manager.set_target_url(target_url)
        self.auto_click_manager.set_target_xpath(target_xpath)
        
        # 设置随机间隔参数
        if self.enable_random_interval.get() == 1:
            min_interval = self.min_interval_entry.get()
            max_interval = self.max_interval_entry.get()
            self.auto_click_manager.set_random_interval_range(min_interval, max_interval)
            self.auto_click_manager.enable_random_interval = True
        else:
            self.auto_click_manager.enable_random_interval = False

        # 启动自动点击
        self.auto_click_manager.toggle_auto_delivery()

        # 更新UI状态
        if self.auto_click_manager.auto_delivery_enabled:
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            logger.info("已启动单按钮自动点击")

    # 修复停止方法中的属性错误
    def stop_auto_click(self):
        # 修改前：if self.auto_click_manager.is_auto_delivery_running:
        if self.auto_click_manager.auto_delivery_enabled:
            self.auto_click_manager.stop_auto_delivery()
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.show_statistics()
            logger.info("已停止单按钮自动点击")

    # 添加显示统计方法
    def show_statistics(self):
        # 获取统计数据
        elapsed_time, click_count = self.auto_click_manager.get_statistics()

        # 格式化时间
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        formatted_time = f"{minutes:02d}:{seconds:02d}"

        # 显示统计信息
        messagebox.showinfo(
            "点击统计",
            f"点击时长: {formatted_time}\n累计点击次数: {click_count}"
        )
        logger.info(f"显示点击统计: 时长={formatted_time}, 次数={click_count}")
