# Tag_click_openclose_V6 开发与使用注意事项

## 网页自动化点击系统
一个基于Python和CustomTkinter开发的桌面应用程序，通过Selenium实现对Edge浏览器的自动化控制。

### 功能介绍
- 连接到已打开的Edge浏览器并访问指定网页
- 自动点击指定的标签元素
- 支持XPath和CSS选择器两种定位元素的方式
- 实时日志显示
- 可配置的自动投放间隔（支持固定间隔和随机间隔）
- 多标签页支持，可以在多个标签页之间切换并执行操作
- 现代化用户界面，支持系统主题自适应

### 环境要求
- Python 3.7或更高版本
- Windows系统
- CustomTkinter
- CTkMessagebox
- Selenium
- Microsoft Edge浏览器
- Edge WebDriver（与浏览器版本匹配）

### 详细依赖包版本信息
- Python: 3.7+
- CustomTkinter: 5.2.2
- CTkMessagebox: 2.7
- Selenium: 4.16.0

### 安装步骤
1.确保已安装Python 3.7和pip包管理工具
2.安装CustomTkinter： pip install customtkinter
3.安装CTkMessagebox： pip install CTkMessagebox
4.安装Selenium： pip install selenium
5.下载Edge浏览器驱动： Microsoft Edge WebDriver
请确保下载的驱动版本与您安装的Edge浏览器版本完全匹配
6.将下载的驱动解压并添加到系统环境变量中，或在程序中指定驱动路径

### 使用说明
1. 启动浏览器远程调试模式：先关闭所有的Edge浏览器，按下 Win + R ，输入 msedge --remote-debugging-port=9222 ，按下回车键启动Edge浏览器远程调试模式。
2. 运行 main.py 文件，启动应用程序，在文件夹中双击打开即可
3. 启动程序后，点击"连接到已打开的Edge浏览器"按钮，程序会自动连接到已打开的Edge浏览器实例。
4. 输入要工作的网页URL，复制需要工作的网页的网址，粘贴到输入框中。
5. 默认是XPath定位元素的方式，也可以选择CSS选择器的方式。
6. 输入要点击的标签元素的定位表达式，在需要工作的页面按'F12'，打开开发者工具，然后点击左上角的'元素'选项卡，在页面中点击需要点击的标签元素，会在开发者工具中显示对应的HTML代码，复制该代码的定位表达式，例如： //button[text()='点击我'] 。
7. 点击“开始自动投放”按钮，程序会自动点击添加的标签元素。
8. 可以在设置中配置投放间隔，支持固定间隔和随机间隔两种模式。

### 项目结构
- main.py ：程序主入口文件
- core/ ：核心功能模块
  - browser_connector.py ：浏览器连接相关功能
  - auto_click_manager.py ：自动点击管理功能
- ui/ ：用户界面模块
  - ctk_main_window.py ：主窗口界面
  - ctk_function_panel.py ：功能面板
  - ctk_log_panel.py ：日志显示面板
  - ctk_single_button_auto_click_panel.py ：单按钮自动点击面板
  - ctk_multi_button_random_click_panel.py ：多按钮随机点击面板
- utils/ ：工具类模块
  - ui_utils.py ：UI相关工具函数
- logger.py ：日志功能模块
- app.log ：应用程序日志文件

### 常见问题解答
1. 连接浏览器失败
   - 请确保已正确启动Edge浏览器的远程调试模式
   - 检查Edge WebDriver是否与浏览器版本匹配
   - 确认驱动路径是否正确配置
2. 元素定位失败
   - 检查XPath或CSS选择器表达式是否正确
   - 确认目标元素确实存在于当前页面
   - 可能需要添加等待时间，确保页面完全加载
3. 程序崩溃或无响应
   - 检查 app.log 文件查看详细错误信息
   - 确保所有依赖包已正确安装
   - 尝试以管理员身份运行程序

### 注意事项
- 使用前请确保已关闭所有正在运行的Edge浏览器实例
- 远程调试模式下的浏览器请勿用于敏感操作
- 程序运行过程中请勿关闭浏览器窗口
- 长时间运行可能会导致内存占用增加，建议定期重启程序