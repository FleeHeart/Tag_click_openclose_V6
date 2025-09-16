import logging
import os
import datetime
import logging  # 添加 logging 模块导入

class Logger:
    def __init__(self, log_file='app.log'):
        # 创建logger对象
        self.logger = logging.getLogger('AutoClicker')
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 创建文件handler，使用GBK编码（适合中文Windows系统）
            file_handler = logging.FileHandler(log_file, encoding='gbk')
            file_handler.setLevel(logging.INFO)
            
            # 创建控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 定义日志格式
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加handler到logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def debug(self, message):
        self.logger.debug(message)

# 创建全局日志对象
logger = Logger()