import customtkinter as ctk
import os
import random
from logger import logger
from core.browser_connector import BrowserConnector
import threading
from selenium.webdriver.common.by import By
import time


class AutoClickManager:
    def __init__(self, browser_connector):
        self.browser_connector = browser_connector
        self.auto_delivery_enabled = False
        self.auto_delivery_timer = None
        self.delivery_interval = 3  # 固定间隔时间（秒）
        self.enable_random_interval = False  # 是否启用随机间隔
        self.min_random_interval = 1  # 最小随机间隔时间（秒）
        self.max_random_interval = 5  # 最大随机间隔时间（秒）
        self.retry_count = 0
        self.target_xpath = ""
        self.target_xpaths = []  # 新增：存储多个XPath
        self.target_selector = ""
        self.target_url = ""
        self.locator_type = "xpath"
        self.target_tab_url = ""
        self.start_time = None
        self.click_count = 0

    def connect_to_browser(self, driver_path=None, max_retries=3):
        """连接到浏览器，增强版"""
        try:
            logger.info("开始连接到Edge浏览器")
            if driver_path:
                logger.info(f"使用指定的驱动路径: {driver_path}")
            
            # 调用改进后的连接方法
            result = self.browser_connector.connect_to_existing_browser(
                driver_path=driver_path, 
                max_retries=max_retries
            )
            
            logger.info("浏览器连接成功")
            return result
                
        except ConnectionError as ce:
            error_msg = str(ce)
            logger.error(f"浏览器连接错误: {error_msg}")
            raise
            
        except RuntimeError as re:
            error_msg = str(re)
            logger.error(f"浏览器运行时错误: {error_msg}")
            raise
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"连接浏览器时发生未知错误: {error_msg}")
            raise

    def is_browser_connected(self):
        return self.browser_connector.is_connected()

    def get_current_url(self):
        return self.browser_connector.get_current_url()

    def close_browser(self):
        self.browser_connector.close_driver()

    def set_target_url(self, url):
        self.target_url = url

    def set_target_xpath(self, xpath, locator_type=None):
        self.target_xpath = xpath
        self.target_xpaths = [xpath]  # 同步到多XPath列表
        if locator_type:
            self.locator_type = locator_type

    # 新增：设置多个XPath
    def set_target_xpaths(self, xpaths):
        self.target_xpaths = xpaths
        # 同时设置第一个XPath为默认的单XPath（保持兼容性）
        if xpaths:
            self.target_xpath = xpaths[0]

    def set_locator_type(self, locator_type):
        self.locator_type = locator_type
        
    def set_target_tab_url(self, tab_url):
        """设置目标标签页URL模式"""
        self.target_tab_url = tab_url
        
    def get_all_tabs(self):
        """获取所有标签页信息"""
        return self.browser_connector.get_all_tabs()
        
    def switch_to_tab(self, url_pattern):
        """切换到指定URL模式的标签页"""
        return self.browser_connector.switch_to_tab_by_url(url_pattern)
        
    def switch_to_tab_by_index(self, index):
        """根据索引切换到指定标签页"""
        return self.browser_connector.switch_to_tab_by_index(index)

    def get_delivery_interval(self):
        return self.delivery_interval

    def toggle_auto_delivery(self):
        self.auto_delivery_enabled = not self.auto_delivery_enabled

        if self.auto_delivery_enabled:
            # 重置统计数据
            self.start_time = time.time()
            self.click_count = 0
            logger.info("重置点击统计数据")
            # 修复调用时缺少参数的问题
            self.start_auto_delivery(
                target_url=self.target_url,
                xpath=self.target_xpath,
                interval=self.delivery_interval,
                random_interval=self.enable_random_interval,
                min_interval=self.min_random_interval,
                max_interval=self.max_random_interval
            )
        else:
            self.stop_auto_delivery()

        return self.auto_delivery_enabled

    def set_random_interval_range(self, min_interval, max_interval):
        """设置随机间隔时间范围"""
        try:
            self.min_random_interval = float(min_interval)
            self.max_random_interval = float(max_interval)
            
            # 确保最小值不大于最大值
            if self.min_random_interval > self.max_random_interval:
                self.min_random_interval, self.max_random_interval = self.max_random_interval, self.min_random_interval
        except ValueError:
            # 如果输入无效，使用默认值
            self.min_random_interval = 1
            self.max_random_interval = 5
            logger.warning("无效的随机间隔时间范围，使用默认值(1-5秒)")
    
    def get_next_interval(self):
        """获取下一次点击的间隔时间"""
        if self.enable_random_interval:
            # 生成随机间隔时间
            interval = random.uniform(self.min_random_interval, self.max_random_interval)
            logger.info(f"下次点击将在 {interval:.2f} 秒后执行(随机间隔)")
            return interval
        else:
            # 使用固定间隔时间
            interval = self.delivery_interval
            logger.info(f"下次点击将在 {interval} 秒后执行(固定间隔)")
            return interval

    def stop_auto_delivery(self):
        if self.auto_delivery_timer:
            self.auto_delivery_timer.cancel()
            logger.info("自动投放已停止")
            self.auto_delivery_timer = None
            
    def perform_click(self):
        """执行点击操作"""
        try:
            if self.locator_type == "xpath" and self.target_xpath:
                logger.info(f"使用XPath定位: {self.target_xpath}")
                return self.browser_connector.click_element(By.XPATH, self.target_xpath, timeout=10)
            elif self.locator_type == "css" and self.target_selector:
                logger.info(f"使用CSS选择器定位: {self.target_selector}")
                return self.browser_connector.click_element(By.CSS_SELECTOR, self.target_selector, timeout=10)
            else:
                logger.error("未设置有效的定位方式和路径")
                return False
        except Exception as e:
            logger.error(f"执行点击操作时出错: {str(e)}")
            return False

    # 新增：执行随机点击操作
    def perform_random_click(self):
        """从多个XPath中随机选择一个执行点击操作"""
        if not self.target_xpaths:
            logger.error("未设置有效的XPath列表")
            return False
        
        # 随机选择一个XPath
        selected_xpath = random.choice(self.target_xpaths)
        logger.info(f"随机选择XPath: {selected_xpath}")
        
        try:
            return self.browser_connector.click_element(By.XPATH, selected_xpath, timeout=10)
        except Exception as e:
            logger.error(f"执行随机点击操作时出错: {str(e)}")
            return False

    def start_auto_delivery(self, target_url, xpath, interval, random_interval=False, min_interval=0, max_interval=0):
        # 如果未启用自动投放，则直接返回
        if not self.auto_delivery_enabled:
            return

        try:
            # 初始化开始时间（如果尚未初始化）
            if self.start_time is None:
                self.start_time = time.time()
                logger.info("开始记录点击统计数据")

            # 检查浏览器连接状态
            if not self.browser_connector.is_connected():
                logger.warning("浏览器未连接，尝试重新连接...")
                try:
                    # 使用重试机制重新连接浏览器
                    if not self.browser_connector.connect_to_existing_browser(max_retries=2):
                        logger.error("重新连接浏览器失败")
                        self.auto_delivery_enabled = False
                        return
                except Exception as e:
                    logger.error(f"自动投放过程中重新连接浏览器失败: {str(e)}")
                    self.auto_delivery_enabled = False
                    return

            # 检查目标网址
            if not self.target_url:
                logger.error("未设置目标网址")
                self.auto_delivery_enabled = False
                return
                
            # 获取当前页面URL用于调试
            try:
                current_url = self.browser_connector.get_current_url()
                logger.info(f"当前页面URL: {current_url}")
                
                # 如果设置了目标标签页URL模式，且当前URL不包含目标模式，则尝试切换标签页
                if self.target_tab_url and (not current_url or self.target_tab_url not in current_url):
                    logger.info(f"尝试切换到包含 {self.target_tab_url} 的标签页")
                    if not self.browser_connector.switch_to_tab_by_url(self.target_tab_url):
                        logger.warning(f"未找到包含 {self.target_tab_url} 的标签页，将在当前标签页操作")
                    else:
                        # 切换标签页后重新获取URL
                        current_url = self.browser_connector.get_current_url()
                        logger.info(f"切换后的页面URL: {current_url}")
            except Exception as url_error:
                logger.warning(f"获取或切换URL时出错: {str(url_error)}")
                # 继续执行，不因URL错误而中断自动点击

            logger.info(f"执行自动投放点击，定位方式: {self.locator_type}")

            # 尝试点击目标元素
            if len(self.target_xpaths) > 1:
                # 多个XPath时使用随机点击
                success = self.perform_random_click()
            else:
                # 单个XPath时使用普通点击
                success = self.perform_click()

            if success:
                logger.info("自动投放点击成功")
                # 增加点击计数
                self.click_count += 1
                logger.info(f"当前点击次数: {self.click_count}")
                # 重置重试计数
                self.retry_count = 0
            else:
                self.retry_count += 1
                logger.warning(f"自动投放点击失败，第{self.retry_count}次重试")
                # 如果连续失败5次，暂停
                if self.retry_count >= 5:
                    logger.error("连续5次点击失败，暂停自动投放")
                    self.auto_delivery_enabled = False
                    return
        except Exception as e:
            logger.error(f"自动投放执行错误: {str(e)}")
            # 发生异常时增加重试计数
            self.retry_count += 1
            if self.retry_count >= 5:
                logger.error("连续5次错误，暂停自动投放")
                self.auto_delivery_enabled = False
                return

        # 设置下一次点击
        # 如果启用了随机间隔，每次都重新生成随机间隔
        if self.enable_random_interval:
            delay = self.get_next_interval()
        else:
            # 实现指数退避策略，最多延迟到30秒
            base_interval = self.get_next_interval()
            delay = min(base_interval * (2 ** min(self.retry_count, 5)), 30)

        # 使用threading.Timer替代wx.CallLater
        if self.auto_delivery_timer:
            self.auto_delivery_timer.cancel()
        # 修复递归调用时缺少参数的问题
        self.auto_delivery_timer = threading.Timer(delay, lambda: self.start_auto_delivery(
            target_url=self.target_url,
            xpath=self.target_xpath,
            interval=self.delivery_interval,
            random_interval=self.enable_random_interval,
            min_interval=self.min_random_interval,
            max_interval=self.max_random_interval
        ))
        self.auto_delivery_timer.daemon = True  # 设置为守护线程，主线程结束时自动结束
        self.auto_delivery_timer.start()

    def get_statistics(self):
        if self.start_time is None:
            return 0, 0
        elapsed_time = time.time() - self.start_time
        return elapsed_time, self.click_count