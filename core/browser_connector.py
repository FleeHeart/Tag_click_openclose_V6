from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import logger  # 修正导入路径
import socket
import time

class BrowserConnector:
    def __init__(self):
        self.driver = None
        self.target_tab_url = None  # 存储目标标签页的URL

    def connect_to_existing_browser(self, debugger_address="localhost:9222", driver_path=None, max_retries=3):
        """连接到已打开的Edge浏览器
        
        Args:
            debugger_address: Edge浏览器的调试地址，默认为localhost:9222
            driver_path: msedgedriver的路径，**必须提供此路径**
            max_retries: 连接失败时的最大重试次数
        """
        # 关闭任何现有的连接
        if self.driver:
            logger.info("关闭现有浏览器连接以确保干净的连接状态")
            self.close_driver()
        
        # 检查驱动路径是否提供
        if not driver_path:
            error_msg = "未提供msedgedriver路径，请使用'选择msedgedriver路径'按钮指定驱动位置"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # 检查调试端口是否可访问
        logger.info(f"检查调试端口 {debugger_address} 是否可访问")
        self._check_debug_port(debugger_address)  # 如果端口不可访问，会抛出ConnectionError

        # 设置Edge浏览器选项
        edge_options = Options()
        edge_options.add_experimental_option("debuggerAddress", debugger_address)
        
        # 创建服务对象
        try:
            logger.info(f"使用指定的驱动路径: {driver_path}")
            service = Service(executable_path=driver_path)
            
            # 禁用自动下载驱动，使用静默模式
            service.creation_flags = 0x08000000  # CREATE_NO_WINDOW
        except Exception as e:
            error_msg = str(e)
            logger.error(f"创建服务对象失败: {error_msg}")
            raise RuntimeError(f"创建服务对象失败: {error_msg}")
        
        # 尝试连接，带重试机制
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                logger.info(f"正在连接到浏览器，调试地址: {debugger_address} (尝试 {retry_count+1}/{max_retries})")
                self.driver = webdriver.Edge(service=service, options=edge_options)
                logger.info("Edge驱动实例创建成功")
                
                # 立即验证连接是否成功
                current_url = self.driver.current_url
                logger.info(f"已成功连接到Edge浏览器，当前URL: {current_url}")
                return True
                
            except Exception as e:
                error_msg = str(e).lower()
                logger.error(f"连接到浏览器失败: {error_msg}")
                self.driver = None  # 确保驱动实例被清理
                last_error = e
                
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"{retry_count}秒后重试...")
                    time.sleep(1)
        
        # 达到最大重试次数后仍失败
        logger.error(f"达到最大重试次数({max_retries})，连接失败")
        
        # 根据错误类型提供具体的错误信息
        error_msg = str(last_error).lower()
        if "cannot find msedgedriver" in error_msg:
            raise RuntimeError("找不到msedgedriver，请确保提供的路径正确")
        elif "version of microsoft edge webdriver" in error_msg:
            raise RuntimeError("Edge浏览器版本与驱动不匹配，请更新Edge浏览器或下载匹配的驱动")
        elif "chrome not reachable" in error_msg:
            raise ConnectionError("无法连接到Edge浏览器，请确保浏览器已启动且远程调试已启用")
        elif "invalid session id" in error_msg:
            raise ConnectionError("浏览器会话无效，请重新启动浏览器并确保远程调试已启用")
        elif "session not created" in error_msg:
            raise RuntimeError("无法创建浏览器会话，可能是驱动版本与浏览器不兼容")
        else:
            raise ConnectionError(f"连接到浏览器失败: {str(last_error)}")


    def _check_debug_port(self, debugger_address):
        """检查调试端口是否可访问
        
        如果端口不可访问，会抛出ConnectionError异常
        如果端口可访问，返回True
        """
        # 解析调试地址
        try:
            host, port = debugger_address.split(':')
            port = int(port)
        except ValueError:
            error_msg = f"调试地址格式错误: {debugger_address}，应为 host:port 格式"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
            
        # 检查端口是否在有效范围内
        if port <= 0 or port > 65535:
            error_msg = f"端口号无效: {port}，应在1-65535范围内"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
            
        # 尝试连接到端口
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)  # 设置3秒超时，足够检测端口是否开放
                logger.info(f"正在检查端口 {host}:{port} 是否开放")
                result = s.connect_ex((host, port))
                
                if result != 0:
                    # 根据错误码提供具体信息
                    if result == 10061:  # 连接被拒绝
                        error_msg = "调试端口连接被拒绝，请确保已使用命令启动浏览器: msedge --remote-debugging-port=9222"
                    elif result == 10060:  # 连接超时
                        error_msg = "调试端口连接超时，请确保已使用命令启动浏览器: msedge --remote-debugging-port=9222"
                    else:
                        error_msg = f"调试端口连接失败(错误码:{result})，请使用命令启动浏览器: msedge --remote-debugging-port=9222"
                    
                    logger.error(error_msg)
                    raise ConnectionError(error_msg)
                
                logger.info(f"成功连接到调试端口 {debugger_address}")
                return True
                
        except socket.error as sock_err:
            error_msg = f"调试端口连接错误: {str(sock_err)}，请使用命令启动浏览器: msedge --remote-debugging-port=9222"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except Exception as e:
            error_msg = f"检查调试端口时出错: {str(e)}，请确保浏览器已正确启动并启用远程调试"
            logger.error(error_msg)
            raise ConnectionError(error_msg)

    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Edge浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭Edge浏览器时出错: {str(e)}")
            self.driver = None

    def is_connected(self):
        return self.driver is not None

    def find_element(self, by, value, timeout=10):
        """查找元素，支持多种定位方式"""
        if not self.driver:
            logger.error("浏览器未初始化或未连接")
            return None

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            logger.info(f"找到可点击元素: {by}, {value}")
            return element
        except Exception as e:
            logger.error(f"查找可点击元素失败: {by}, {value}, 错误: {str(e)}")
            return None

    def click_element(self, by, value, timeout=10):
        """点击元素，添加反检测措施"""
        element = self.find_element(by, value, timeout)
        if element:
            try:
                # 添加随机延迟，模拟人类思考时间
                import random
                time.sleep(random.uniform(0.3, 1.5))

                # 模拟鼠标移动到元素（带随机偏移）
                action = webdriver.ActionChains(self.driver)
                # 随机偏移量，模拟人类点击不精确性
                x_offset = random.randint(-5, 5)
                y_offset = random.randint(-5, 5)
                action.move_to_element_with_offset(element, x_offset, y_offset)
                action.pause(random.uniform(0.1, 0.5))  # 悬停片刻
                action.click()
                action.perform()

                logger.info(f"点击元素: {by}, {value} (带反检测措施)")
                return True
            except Exception as e:
                logger.error(f"点击元素失败: {by}, {value}, 错误: {str(e)}")
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
            error_msg = str(e)
            logger.error(f"获取当前URL失败: {error_msg}")
            
            # 处理各种可能的错误情况
            if "no such window" in error_msg or "web view not found" in error_msg:
                logger.info("尝试重新连接浏览器...")
                try:
                    if self.connect_to_existing_browser():
                        try:
                            url = self.driver.current_url
                            logger.info(f"重新连接后获取URL: {url}")
                            return url
                        except Exception as re:
                            logger.error(f"重新连接后获取URL仍失败: {str(re)}")
                except Exception as conn_error:
                    logger.error(f"重新连接浏览器失败: {str(conn_error)}")
            elif "chrome not reachable" in error_msg.lower():
                logger.error("浏览器无法访问，可能已关闭或崩溃")
                self.driver = None  # 重置驱动状态
            elif "invalid session id" in error_msg.lower():
                logger.error("会话ID无效，浏览器可能已关闭")
                self.driver = None  # 重置驱动状态
            return None
            
    def get_all_tabs(self):
        """获取所有标签页的句柄、标题和URL"""
        if not self.driver:
            logger.error("浏览器未初始化或未连接")
            return []
            
        try:
            # 获取当前窗口句柄和所有窗口句柄
            try:
                current_handle = self.driver.current_window_handle
                window_handles = self.driver.window_handles
            except Exception as e:
                error_msg = str(e).lower()
                logger.error(f"获取窗口句柄失败: {error_msg}")
                
                # 处理会话失效的情况
                if "invalid session id" in error_msg or "no such window" in error_msg:
                    logger.error("浏览器会话已失效，尝试重新连接")
                    self.driver = None
                    try:
                        if self.connect_to_existing_browser():
                            # 重新获取句柄
                            current_handle = self.driver.current_window_handle
                            window_handles = self.driver.window_handles
                        else:
                            return []
                    except Exception as conn_error:
                        logger.error(f"重新连接浏览器失败: {str(conn_error)}")
                        return []
                else:
                    return []
            
            # 获取标签页信息，包括标题和URL
            tabs = []
            original_handle = current_handle
            
            for handle in window_handles:
                try:
                    # 切换到标签页获取标题和URL
                    self.driver.switch_to.window(handle)
                    title = self.driver.title
                    url = self.driver.current_url
                    
                    tabs.append({
                        'id': handle,
                        'handle': handle,
                        'title': title,  # 获取实际标题
                        'url': url,  # 获取实际URL
                        'is_current': handle == original_handle
                    })
                except Exception as tab_error:
                    logger.warning(f"获取标签页信息失败: {str(tab_error)}")
                    tabs.append({
                        'id': handle,
                        'handle': handle,
                        'title': f"标签页 {len(tabs)+1}",
                        'url': "未获取",
                        'is_current': handle == original_handle
                    })
            
            # 切回原始标签页
            try:
                self.driver.switch_to.window(original_handle)
            except Exception as switch_error:
                logger.warning(f"切回原始标签页失败: {str(switch_error)}")
                    
            return tabs
        except Exception as e:
            logger.error(f"获取标签页信息失败: {str(e)}")
            return []
    
    def switch_to_tab_by_url(self, url_pattern):
        """根据URL模式切换到指定标签页"""
        if not self.driver:
            logger.error("浏览器未初始化或未连接")
            return False
            
        try:
            self.target_tab_url = url_pattern
            
            # 获取当前窗口句柄和所有窗口句柄
            try:
                current_handle = self.driver.current_window_handle
                window_handles = self.driver.window_handles
            except Exception as e:
                error_msg = str(e).lower()
                logger.error(f"获取窗口句柄失败: {error_msg}")
                
                # 处理会话失效的情况
                if "invalid session id" in error_msg or "no such window" in error_msg:
                    logger.error("浏览器会话已失效，尝试重新连接")
                    self.driver = None
                    try:
                        if self.connect_to_existing_browser():
                            current_handle = self.driver.current_window_handle
                            window_handles = self.driver.window_handles
                        else:
                            return False
                    except Exception as conn_error:
                        logger.error(f"重新连接浏览器失败: {str(conn_error)}")
                        return False
                else:
                    return False
            
            # 首先检查当前标签页是否匹配URL模式，避免不必要的切换
            try:
                current_url = self.driver.current_url
                if url_pattern in current_url:
                    logger.info(f"当前标签页已匹配URL模式: {url_pattern}")
                    return True
            except Exception as url_error:
                logger.warning(f"获取当前URL失败: {str(url_error)}")
            
            # 如果当前标签页不匹配，尝试查找匹配的标签页
            found = False
            target_handle = None
            
            # 遍历所有标签页，但不立即切换，先找到目标标签页
            for handle in window_handles:
                if handle == current_handle:
                    continue  # 跳过当前标签页，因为已经检查过了
                    
                try:
                    # 切换到标签页并获取URL
                    self.driver.switch_to.window(handle)
                    tab_url = self.driver.current_url
                    
                    # 检查URL是否匹配模式
                    if url_pattern in tab_url:
                        logger.info(f"找到匹配URL模式的标签页: {tab_url}")
                        found = True
                        target_handle = handle
                        break
                except Exception as tab_error:
                    logger.warning(f"访问标签页 {handle} 失败: {str(tab_error)}")
                    continue
            
            # 如果没有找到匹配的标签页，切回原标签页
            if not found:
                logger.warning(f"未找到包含 {url_pattern} 的标签页，切回原标签页")
                try:
                    if current_handle in window_handles:
                        self.driver.switch_to.window(current_handle)
                        logger.info("已切回原标签页")
                    else:
                        # 如果原句柄无效，切换到第一个可用标签页
                        self.driver.switch_to.window(window_handles[0])
                        logger.info("原标签页无效，已切换到第一个标签页")
                except Exception as switch_error:
                    logger.error(f"切换回原标签页失败: {str(switch_error)}")
                    return False
                return False
                
            return True
        except Exception as e:
            logger.error(f"切换标签页失败: {str(e)}")
            return False
            
    def switch_to_tab_by_index(self, index):
        """根据索引切换到指定标签页"""
        if not self.driver:
            logger.error("浏览器未初始化或未连接")
            return False
            
        try:
            # 获取所有窗口句柄
            try:
                handles = self.driver.window_handles
                # 记录当前句柄，以便切换失败时可以回到原来的标签页
                current_handle = self.driver.current_window_handle
            except Exception as e:
                error_msg = str(e).lower()
                logger.error(f"获取窗口句柄失败: {error_msg}")
                
                # 处理会话失效的情况
                if "invalid session id" in error_msg or "no such window" in error_msg:
                    logger.error("浏览器会话已失效，尝试重新连接")
                    self.driver = None
                    try:
                        if self.connect_to_existing_browser():
                            handles = self.driver.window_handles
                            current_handle = self.driver.current_window_handle
                        else:
                            return False
                    except Exception as conn_error:
                        logger.error(f"重新连接浏览器失败: {str(conn_error)}")
                        return False
                else:
                    return False
            
            # 检查索引是否有效
            if 0 <= index < len(handles):
                target_handle = handles[index]
                
                # 如果目标标签页就是当前标签页，则不需要切换
                if target_handle == current_handle:
                    logger.info(f"已经在目标标签页 {index+1}")
                    return True
                    
                try:
                    # 使用try-except块保护切换操作
                    self.driver.switch_to.window(target_handle)
                    logger.info(f"已切换到第 {index+1} 个标签页")
                    
                    # 不主动获取URL，避免可能的连接问题
                    return True
                except Exception as switch_error:
                    logger.error(f"切换到标签页 {target_handle} 失败: {str(switch_error)}")
                    
                    # 尝试切回原标签页
                    try:
                        if current_handle in handles:
                            self.driver.switch_to.window(current_handle)
                            logger.info("已切回原标签页")
                    except Exception as restore_error:
                        logger.error(f"切回原标签页失败: {str(restore_error)}")
                        
                    return False
            else:
                logger.warning(f"标签页索引 {index} 超出范围，共有 {len(handles)} 个标签页")
                return False
        except Exception as e:
            logger.error(f"切换标签页失败: {str(e)}")
            return False
            
    def switch_to_tab_by_id(self, tab_id):
        """根据标签页ID切换到指定标签页"""
        if not self.driver:
            logger.error("浏览器未初始化或未连接")
            return False
            
        try:
            # 在Chrome/Edge中，tab_id通常是window handle
            if tab_id in self.driver.window_handles:
                self.driver.switch_to.window(tab_id)
                logger.info(f"已切换到标签页ID {tab_id}: {self.driver.current_url}")
                return True
            else:
                logger.warning(f"未找到ID为 {tab_id} 的标签页")
                return False
        except Exception as e:
            logger.error(f"切换到标签页ID {tab_id} 失败: {str(e)}")