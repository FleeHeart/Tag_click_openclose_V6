from logger import logger
import sys
import traceback
import os
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from ui.ctk_main_window import CTkAutoClickerMainWindow
from logger import logger

def main():
    print("开始启动程序...")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python版本: {sys.version}")
    print(f"CustomTkinter版本: {ctk.__version__}")
    
    try:
        # 设置外观模式和默认颜色主题
        ctk.set_appearance_mode("System")  # 系统模式，自动适应系统主题
        ctk.set_default_color_theme("blue")  # 默认蓝色主题
        
        print("创建主窗口...")
        app = CTkAutoClickerMainWindow()
        
        print("显示窗口并启动主循环...")
        app.mainloop()
    except Exception as e:
        error_msg = f"程序运行失败: {str(e)}"
        print(error_msg)
        print("详细错误信息:")
        traceback.print_exc()
        
        # 记录错误到日志
        if 'logger' in sys.modules:
            logger.error(error_msg)
            logger.error(traceback.format_exc())
        
        # 使用简单的消息框显示错误
        try:
            CTkMessagebox(
                title="程序崩溃",
                message=error_msg,
                icon="cancel"
            )
        except Exception as dialog_error:
            print(f"无法显示错误对话框: {str(dialog_error)}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
