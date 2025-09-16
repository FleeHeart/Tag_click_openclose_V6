import customtkinter as ctk
import os
from PIL import Image, ImageTk
from logger import logger

class CTkLogPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        # 初始化UI组件
        self._init_ui()
        
        # 刷新日志
        self.refresh_log()
    
    def _init_ui(self):
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
            text="日志记录", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            text_container, 
            text="查看应用程序运行日志", 
            font=ctk.CTkFont(size=12)
        )
        subtitle.pack(anchor="w")
        
        # 创建分隔线
        separator = ctk.CTkFrame(self, height=1, fg_color=("#E2E8F0", "#334155"))
        separator.pack(fill="x", padx=20, pady=10)
        
        # 创建日志区域
        log_container = ctk.CTkFrame(self)
        log_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 创建日志文本框
        self.log_text = ctk.CTkTextbox(log_container, wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建底部控制区域
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # 刷新按钮
        self.refresh_button = ctk.CTkButton(
            control_frame,
            text="🔄 刷新日志",
            font=ctk.CTkFont(size=12),
            command=self.refresh_log
        )
        self.refresh_button.pack(side="left", padx=10)
        
        # 状态信息
        self.status_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        self.status_frame.pack(side="right", padx=10)
        
        # 状态图标
        self.status_icon = ctk.CTkLabel(
            self.status_frame,
            text="✅",
            font=ctk.CTkFont(size=16)
        )
        self.status_icon.pack(side="left")
        
        # 状态文本
        self.status_text = ctk.CTkLabel(
            self.status_frame,
            text="日志已加载",
            font=ctk.CTkFont(size=12)
        )
        self.status_text.pack(side="left", padx=5)
    
    def refresh_log(self):
        """刷新日志内容"""
        try:
            # 清空当前日志
            self.log_text.delete("1.0", "end")
            
            # 获取日志文件路径
            log_file = "app.log"
            
            if os.path.exists(log_file):
                # 尝试以UTF-8读取
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        log_content = f.read()
                except UnicodeDecodeError:
                    # 如果UTF-8失败，尝试GBK
                    try:
                        with open(log_file, "r", encoding="gbk") as f:
                            log_content = f.read()
                    except UnicodeDecodeError:
                        # 如果GBK也失败，使用二进制模式读取并忽略错误
                        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                            log_content = f.read()
                
                # 显示日志内容
                self.log_text.insert("1.0", log_content)
                
                # 滚动到底部
                self.log_text.see("end")
                
                # 更新状态
                self.status_icon.configure(text="✅")
                self.status_text.configure(text="日志已刷新")
                logger.info("日志已刷新")
            else:
                self.log_text.insert("1.0", "日志文件不存在")
                self.status_icon.configure(text="⚠️")
                self.status_text.configure(text="日志文件不存在")
                logger.warning("日志文件不存在")
        except Exception as e:
            self.log_text.insert("1.0", f"加载日志时出错: {str(e)}")
            self.status_icon.configure(text="❌")
            self.status_text.configure(text=f"加载日志出错")
            logger.error(f"加载日志时出错: {str(e)}")