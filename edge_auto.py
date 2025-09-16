from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import logger
import time
import os
import subprocess
import platform

class EdgeAutoClicker:
    def __init__(self):
        self.driver = None
        # 不再自动初始化浏览器
        # self.setup_driver()
        
    def setup_driver(self):
        try:
            # 配置Edge选项
            edge_options = Options()
            edge_options.add_argument("--start-maximized")  # 最大化窗口
            edge_options.add_argument("--disable-extensions")  # 禁用扩展
            
            # 设置Edge驱动
            service = Service()
            
            # 创建Edge驱动
            self.driver = webdriver.Edge(service=service, options=edge_options)
            logger.info("Edge浏览器已启动")
        except Exception as e:
            logger.error(f"启动Edge浏览器失败: {str(e)}")
            self.driver = None
    
    def connect_to_existing_browser(self, debugger_address="localhost:9222", max_retries=5):
        """连接到已打开的Edge浏览器"""
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    logger.info(f"尝试第 {retry_count} 次重新连接浏览器...")
                    time.sleep(2)  # 重试前等待两秒
                
                # 检查调试端口是否可访问
                self._check_debug_port(debugger_address)

                edge_options = Options()
                edge_options.add_experimental_option("debuggerAddress", debugger_address)
                edge_options.add_argument("--no-sandbox")
                edge_options.add_argument("--disable-dev-shm-usage")
                edge_options.add_argument("--disable-gpu")  # 禁用GPU加速
                edge_options.add_argument("--disable-extensions")  # 禁用扩展

                # 尝试创建驱动连接到现有浏览器
                logger.info(f"正在尝试连接到浏览器，调试地址: {debugger_address}")
                service = Service()
                self.driver = webdriver.Edge(service=service, options=edge_options)
                logger.info("Edge驱动实例创建成功")

                # 验证连接是否成功
                if self.driver:
                    # 增加等待时间，确保浏览器连接稳定
                    time.sleep(1)
                    
                    current_url = self.driver.current_url
                    logger.info(f"已成功连接到现有Edge浏览器: {debugger_address}")
                    logger.info(f"当前浏览器页面URL: {current_url}")
                    return True
                else:
                    logger.error("创建浏览器驱动失败")
                    if retry_count < max_retries:
                        retry_count += 1
                        continue
                    return False
            except Exception as e:
                error_msg = str(e)
                logger.error(f"连接到现有Edge浏览器失败: {error_msg}")
                
                # 清理无效的driver实例
                self.driver = None
                
                # 判断是否需要重试
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                return False
        
        return False
    
    def _check_debug_port(self, debugger_address):
        """检查调试端口是否可访问"""
        try:
            try:
                host, port = debugger_address.split(':')
                port = int(port)
            except ValueError:
                logger.error(f"调试地址格式错误: {debugger_address}，应为 host:port 格式")
                raise ConnectionError(f"调试地址格式错误: {debugger_address}，应为 host:port 格式")
                
            # 检查端口是否在有效范围内
            if port <= 0 or port > 65535:
                logger.error(f"端口号无效: {port}，应在1-65535范围内")
                raise ConnectionError(f"端口号无效: {port}，应在1-65535范围内")
                
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(15)  # 增加超时时间到15秒，提高连接成功率
                result = s.connect_ex((host, port))
                if result != 0:
                    error_message = f"无法连接到调试端口 {debugger_address}，请确保Edge浏览器已启用远程调试"
                    logger.warning(error_message)
                    # 提供更详细的错误信息
                    if result == 10061:  # 连接被拒绝
                        error_message = "连接被拒绝，请确保已使用远程调试模式启动浏览器"
                        logger.warning("连接被拒绝，请确保已使用 msedge --remote-debugging-port=9222 启动浏览器")
                        raise ConnectionError("连接被拒绝，请确保已使用远程调试模式启动浏览器。\n\n启动方法：\n1. 关闭所有Edge浏览器窗口\n2. 按Win+R打开运行对话框\n3. 输入: msedge --remote-debugging-port=9222\n4. 按回车启动浏览器")
                    elif result == 10060:  # 连接超时
                        error_message = "连接到调试端口超时，请确保浏览器已启动并启用了远程调试"
                        logger.warning(error_message)
                        raise ConnectionError("连接到调试端口超时，请确保浏览器已启动并启用了远程调试。\n\n启动方法：\n1. 关闭所有Edge浏览器窗口\n2. 按Win+R打开运行对话框\n3. 输入: msedge --remote-debugging-port=9222\n4. 按回车启动浏览器")
                    else:
                        # 其他错误码
                        error_message = f"连接到调试端口失败（错误码: {result}），请确保浏览器已启动并启用了远程调试"
                        logger.warning(error_message)
                        raise ConnectionError(f"连接到调试端口失败（错误码: {result}），请确保浏览器已启动并启用了远程调试。\n\n启动方法：\n1. 关闭所有Edge浏览器窗口\n2. 按Win+R打开运行对话框\n3. 输入: msedge --remote-debugging-port=9222\n4. 按回车启动浏览器")
                else:
                    logger.info(f"成功连接到调试端口 {debugger_address}")
        except ConnectionError:
            # 直接向上传递ConnectionError异常
            raise
        except Exception as e:
            error_message = f"检查调试端口时出错: {str(e)}"
            logger.warning(error_message)
            raise ConnectionError(f"检查调试端口时出错: {str(e)}，请确保浏览器已正确启动并启用远程调试")
    
    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Edge浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭Edge浏览器时出错: {str(e)}")
            self.driver = None
    
    def find_element(self, by, value, timeout=10):
        """查找元素，支持多种定位方式"""
        if not self.driver:
            logger.error("浏览器未初始化或未连接")
            return None
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))  # 修改为等待元素可点击
            )
            logger.info(f"找到可点击元素: {by}, {value}")
            return element
        except Exception as e:
            logger.error(f"查找可点击元素失败: {by}, {value}, 错误: {str(e)}")
            return None
    
    def click_element(self, by, value, timeout=10):
        """点击元素"""
        element = self.find_element(by, value, timeout)
        if element:
            try:
                element.click()
                logger.info(f"点击元素: {by}, {value}")
                return True
            except Exception as e:
                logger.error(f"点击元素失败: {by}, {value}, 错误: {str(e)}")
        return False
    
    def input_text(self, by, value, text, timeout=10):
        """输入文本"""
        element = self.find_element(by, value, timeout)
        if element:
            try:
                element.clear()
                element.send_keys(text)
                logger.info(f"输入文本到元素: {by}, {value}")
                return True
            except Exception as e:
                logger.error(f"输入文本失败: {by}, {value}, 错误: {str(e)}")
        return False
    
    def get_current_url(self):
        """获取当前页面URL"""
        if not self.driver:
            logger.error("浏览器未初始化或未连接")
            return None
        try:
            url = self.driver.current_url
            logger.info(f"当前页面URL: {url}")
            return url
        except Exception as e:
            logger.error(f"获取当前URL失败: {str(e)}")
            # 尝试重新连接浏览器
            if "no such window" in str(e) or "web view not found" in str(e):
                logger.info("尝试重新连接浏览器...")
                if self.connect_to_existing_browser():
                    try:
                        url = self.driver.current_url
                        logger.info(f"重新连接后获取URL: {url}")
                        return url
                    except Exception as re:
                        logger.error(f"重新连接后获取URL仍失败: {str(re)}")
            return None
    
    def refresh_page(self):
        """刷新页面"""
        if not self.driver:
            logger.error("浏览器未初始化或未连接")
            return False
        try:
            self.driver.refresh()
            logger.info("页面已刷新")
            return True
        except Exception as e:
            logger.error(f"刷新页面失败: {str(e)}")
            return False

# 创建全局自动化对象
auto_clicker = EdgeAutoClicker()