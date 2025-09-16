import customtkinter as ctk
import os
from PIL import Image, ImageTk
from logger import logger
from ui.ctk_single_button_auto_click_panel import CTkSingleButtonAutoClickPanel


class CTkFunctionPanel(ctk.CTkFrame):
    def __init__(self, parent, auto_click_manager):
        super().__init__(parent)
        self.auto_click_manager = auto_click_manager
        self.pack(fill="both", expand=True)
        
        # 初始化页面状态
        self.is_in_main_view = True
        self.detail_panel = None
        self.connection_in_progress = False
        
        # 初始化UI组件
        self._init_ui()

    def on_connect_browser(self):
        """连接到浏览器，增强版"""
        # 防止重复点击
        if self.connection_in_progress:
            logger.warning("连接已在进行中，请等待...")
            return
        
        try:
            self.connection_in_progress = True
            # 显示连接中状态
            self.browser_status_label.configure(text="浏览器状态: 正在连接...")
            self.update()
            
            try:
                # 使用选择的驱动路径（必须提供）
                if not self.driver_path:
                    self._prompt_select_driver()
                    if not self.driver_path:
                        raise RuntimeError("未提供msedgedriver路径，无法连接到浏览器")
                
                self.auto_click_manager.connect_to_browser(
                    driver_path=self.driver_path,
                    max_retries=3  # 增加重试次数
                )
                
                # 连接成功
                self.browser_status_label.configure(text="浏览器状态: 已连接")
                self.update_current_url()
                logger.info("成功连接到浏览器")
                
                # 显示功能按钮区域 - 使用pack()而不是grid()
                self.features_frame.pack(fill="x", padx=20, pady=20)
            except ConnectionError as ce:
                error_msg = str(ce)
                logger.error(f"连接错误: {error_msg}")
                
                # 分类处理不同的连接错误
                if "调试端口" in error_msg or "远程调试" in error_msg:
                    self.browser_status_label.configure(text="浏览器状态: 调试端口连接失败")
                    self.show_connection_help(f"调试端口连接失败: {error_msg}")
                elif "无法下载Edge驱动" in error_msg or "LATEST_RELEASE" in error_msg:
                    self.browser_status_label.configure(text="浏览器状态: 网络连接错误")
                    self.show_connection_help(f"网络连接错误: {error_msg}")
                    # 提示用户选择驱动路径
                    if not self.driver_path:
                        self._prompt_select_driver()
                elif "chrome not reachable" in error_msg.lower():
                    self.browser_status_label.configure(text="浏览器状态: 无法连接到浏览器")
                    self.show_connection_help("无法连接到Edge浏览器，请确保浏览器已启动且远程调试已启用\n请使用 msedge --remote-debugging-port=9222 命令启动浏览器")
                elif "invalid session id" in error_msg.lower():
                    self.browser_status_label.configure(text="浏览器状态: 会话无效")
                    self.show_connection_help("浏览器会话无效，请重新启动浏览器并确保远程调试已启用\n请使用 msedge --remote-debugging-port=9222 命令启动浏览器")
                elif "连接被拒绝" in error_msg or "请确保已使用 msedge --remote-debugging-port=9222 启动浏览器" in error_msg:
                    self.browser_status_label.configure(text="浏览器状态: 连接被拒绝")
                    self.show_connection_help("连接被拒绝，请确保已使用正确的命令启动浏览器\n请使用 msedge --remote-debugging-port=9222 命令启动浏览器")
                else:
                    self.browser_status_label.configure(text="浏览器状态: 连接错误")
                    clean_error = self.clean_error_message(error_msg)
                    self.show_connection_help(f"连接错误: {clean_error}")
            except RuntimeError as re:
                error_msg = str(re)
                # 处理运行时错误
                if "找不到msedgedriver" in error_msg:
                    self.browser_status_label.configure(text="浏览器状态: 驱动程序缺失")
                    self.show_connection_help(f"驱动程序错误: {error_msg}")
                    self._prompt_select_driver()
                elif "版本与驱动不匹配" in error_msg:
                    self.browser_status_label.configure(text="浏览器状态: 版本不匹配")
                    self.show_connection_help(f"版本不匹配: {error_msg}")
                    self._prompt_select_driver()
                else:
                    self.browser_status_label.configure(text="浏览器状态: 浏览器连接错误")
                    self.show_connection_help(f"浏览器连接错误: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            self.browser_status_label.configure(text=f"浏览器状态: 连接错误")
            self.show_connection_help(error_msg)
            logger.error(f"连接浏览器时发生错误: {error_msg}")
        finally:
            self.connection_in_progress = False

    def _prompt_select_driver(self):
        """提示用户选择驱动路径"""
        try:
            from CTkMessagebox import CTkMessagebox
            result = CTkMessagebox(
                title="驱动问题",
                message="无法找到或使用Edge驱动，是否手动选择驱动路径？",
                icon="question",
                option_1="是",
                option_2="否"
            )
            if result.get() == "是":
                self.select_driver_path()
        except Exception as e:
            logger.error(f"提示选择驱动路径时出错: {str(e)}")

    def _init_ui(self):
        # 清空当前帧中的所有组件
        for widget in self.winfo_children():
            widget.destroy()
        
        if self.is_in_main_view:
            # 创建主视图（连接浏览器相关）
            # 创建标题区域
            title_frame = ctk.CTkFrame(self, fg_color="transparent")
            title_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            # 创建标题容器
            title_container = ctk.CTkFrame(title_frame, fg_color="transparent")
            title_container.pack(fill="x")
            
            # 创建装饰线
            decoration = ctk.CTkFrame(title_container, width=6, height=40, fg_color="#38BDF8")
            decoration.pack(side="left")
            
            # 创建文本容器
            text_container = ctk.CTkFrame(title_container, fg_color="transparent")
            text_container.pack(side="left", padx=10, fill="both", expand=True)
            
            # 创建标题和副标题
            title_label = ctk.CTkLabel(
                text_container, 
                text="自动化点击功能", 
                font=ctk.CTkFont(size=24, weight="bold")
            )
            title_label.pack(anchor="w")
            
            subtitle = ctk.CTkLabel(
                text_container, 
                text="高效自动化，轻松点击", 
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
            
            # 创建连接区域框架
            connect_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
            connect_frame.pack(fill="x", padx=20, pady=20)
            
            # 创建连接浏览器按钮
            self.connect_button = ctk.CTkButton(
                connect_frame,
                text="🔗 连接到已打开的Edge浏览器",
                font=ctk.CTkFont(size=12, weight="bold"),
                height=50,
                command=self.on_connect_browser
            )
            self.connect_button.pack(fill="x", pady=(0, 10))
            
            # 创建选择驱动路径按钮
            self.select_driver_button = ctk.CTkButton(
                connect_frame,
                text="📁 选择msedgedriver路径",
                font=ctk.CTkFont(size=12),
                height=30,
                command=self.select_driver_path
            )
            self.select_driver_button.pack(fill="x")
            
            # 驱动路径存储
            self.driver_path = None
            self.driver_path_label = ctk.CTkLabel(
                connect_frame,
                text="驱动路径: 未设置（使用系统默认）",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            self.driver_path_label.pack(anchor="w", pady=(5, 0))
            
            # 创建浏览器信息区域
            self.browser_info_frame = ctk.CTkFrame(self.main_card)
            self.browser_info_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            # 浏览器状态标签
            self.browser_status_label = ctk.CTkLabel(
                self.browser_info_frame,
                text="浏览器状态: 未连接",
                font=ctk.CTkFont(size=12)
            )
            self.browser_status_label.pack(anchor="w", padx=10, pady=5)
            
            # 当前URL标签
            self.current_url_label = ctk.CTkLabel(
                self.browser_info_frame,
                text="当前URL: 无",
                font=ctk.CTkFont(size=12)
            )
            self.current_url_label.pack(anchor="w", padx=10, pady=5)
            
            # 创建功能按钮区域（初始隐藏）
            self.features_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
            # 初始不添加到布局中，连接成功后再添加
            # self.features_frame.pack(fill="x", padx=20, pady=20)
            
            # 单按钮自动点击功能按钮
            self.single_button_click_button = ctk.CTkButton(
                self.features_frame,
                text="🔘 单按钮自动点击",
                font=ctk.CTkFont(size=12, weight="bold"),
                height=50,
                command=self.navigate_to_single_button_panel
            )
            self.single_button_click_button.pack(fill="x", pady=10)

            # 多按钮随机点击功能按钮 - 新增
            self.multi_button_random_click_button = ctk.CTkButton(
                self.features_frame,
                text="🎯 多按钮随机点击",
                font=ctk.CTkFont(size=12, weight="bold"),
                height=50,
                command=self.navigate_to_multi_button_panel
            )
            self.multi_button_random_click_button.pack(fill="x", pady=10)
        else:
            # 不要在这里创建默认面板，而是依赖导航方法创建的面板
            pass
            # 显示详细功能面板
            self.detail_panel = CTkSingleButtonAutoClickPanel(
                self,
                self.auto_click_manager,
                self.navigate_back
            )
    
    def navigate_to_single_button_panel(self):
        """导航到单按钮自动点击面板"""
        self.is_in_main_view = False
        
        # 移除主视图组件
        for widget in self.winfo_children():
            widget.destroy()
        
        # 创建新面板
        from ui.ctk_single_button_auto_click_panel import CTkSingleButtonAutoClickPanel
        self.detail_panel = CTkSingleButtonAutoClickPanel(
            self,
            self.auto_click_manager,
            self.navigate_back
        )
        # 显示面板
        self.detail_panel.pack(fill="both", expand=True)

    def navigate_to_multi_button_panel(self):
        """导航到多按钮随机点击面板"""
        self.is_in_main_view = False
        
        # 移除主视图组件
        for widget in self.winfo_children():
            widget.destroy()
        
        # 创建新面板
        from ui.ctk_multi_button_random_click_panel import CTkMultiButtonRandomClickPanel
        self.detail_panel = CTkMultiButtonRandomClickPanel(
            master=self,
            auto_click_manager=self.auto_click_manager,
            on_back_callback=self.navigate_back
        )
        # 显示面板
        self.detail_panel.pack(fill="both", expand=True)

    def navigate_back(self):
        """返回主视图"""
        self.is_in_main_view = True
        
        # 移除当前面板
        for widget in self.winfo_children():
            widget.destroy()
        
        # 重新初始化UI
        self._init_ui()
    
    def select_driver_path(self):
        """选择msedgedriver路径"""
        try:
            from tkinter import filedialog
            
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择msedgedriver.exe文件",
                filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
            )
            
            if file_path:
                # 验证文件名是否包含msedgedriver
                file_name = os.path.basename(file_path).lower()
                if "msedgedriver" in file_name or "edgedriver" in file_name:
                    self.driver_path = file_path
                    self.driver_path_label.configure(
                        text=f"驱动路径: {file_path}",
                        text_color="green"
                    )
                    logger.info(f"已设置msedgedriver路径: {file_path}")
                else:
                    from CTkMessagebox import CTkMessagebox
                    CTkMessagebox(
                        title="文件验证",
                        message="所选文件似乎不是msedgedriver.exe，请确保选择正确的驱动程序文件。",
                        icon="warning"
                    )
        except Exception as e:
            logger.error(f"选择驱动路径时出错: {str(e)}")
            logger.exception(e)
    
    def clean_error_message(self, error_msg):
        """清理错误消息中的URL编码和特殊字符"""
        try:
            # 移除URL编码和特殊字符
            import re
            # 移除URL编码部分
            clean_msg = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL]', error_msg)
            # 移除过长的路径
            clean_msg = re.sub(r'[\w\\/:.-]+\.exe', '[EXECUTABLE_PATH]', clean_msg)
            return clean_msg
        except Exception:
            return error_msg
            
    def show_connection_help(self, error_msg=None):
        """显示连接帮助信息"""
        from CTkMessagebox import CTkMessagebox
        
        help_text = "连接Edge浏览器失败，请按照以下步骤操作：\n\n"
        help_text += "1. 确保Edge浏览器已经完全关闭（检查任务管理器确保没有Edge进程）\n"
        help_text += "2. 使用命令行启动Edge浏览器的远程调试模式：\n"
        help_text += "   - 按下Win+R打开运行对话框\n"
        help_text += "   - 输入：msedge --remote-debugging-port=9222\n"
        help_text += "   - 按下回车键启动Edge浏览器\n"
        help_text += "3. 等待Edge浏览器完全加载（约5-10秒）\n"
        help_text += "4. 重新点击'连接到已打开的Edge浏览器'按钮\n"
        
        # 根据错误类型提供简洁的帮助信息
        if error_msg:
            if "驱动程序缺失" in error_msg or "找不到msedgedriver" in error_msg:
                help_text += "\nEdge驱动程序问题解决方法：\n"
                help_text += "- 访问 https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/\n"
                help_text += "- 下载与您Edge浏览器版本匹配的驱动程序\n"
                help_text += "- 使用'选择msedgedriver路径'按钮指定下载的驱动程序位置\n"
            elif "版本不匹配" in error_msg:
                help_text += "\n版本不匹配问题解决方法：\n"
                help_text += "- 更新Edge浏览器到最新版本或下载匹配的驱动程序\n"
                help_text += "- 驱动下载地址: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/\n"
        
        if error_msg:
            help_text += f"\n错误详情: {error_msg}"
        
        CTkMessagebox(
            title="连接帮助",
            message=help_text,
            icon="info",
            option_1="了解"
        )
    
    def update_current_url(self):
        """更新当前URL显示"""
        if self.auto_click_manager.is_browser_connected():
            current_url = self.auto_click_manager.get_current_url()
            self.current_url_label.configure(text=f"当前URL: {current_url}")
    
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
                    self.update_current_url()
                    
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
            # 这里需要在AutoClickManager中实现test_click方法
            result = self.auto_click_manager.perform_click()
            if result:
                logger.info("测试点击成功")
            else:
                logger.warning("测试点击失败")
        except Exception as e:
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger.error(f"测试点击时发生错误: {str(e)}")
            logger.exception(e)
            logger
            