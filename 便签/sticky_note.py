import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime
import logging  # 导入logging模块

class StickyNote:
    def __init__(self):
        # 首先设置日志
        self.setup_logging()
        
        logging.info("开始初始化便签程序")
        try:
            # 创建主窗口
            self.root = tk.Tk()
            self.root.title("便签")
            logging.debug("主窗口创建成功")
            
            # 基本窗口设置
            self.root.geometry("250x300")
            self.root.configure(bg='#ffffd0')
            logging.debug("窗口基本设置完成")
            
            # 创建UI组件
            self.create_ui()
            logging.debug("UI组件创建完成")
            
            # 加载内容
            self.load_content()
            
        except Exception as e:
            logging.error(f"初始化失败: {e}")
            raise

    def create_ui(self):
        logging.debug("开始创建UI组件")
        try:
            # 创建标题栏框架
            self.title_frame = tk.Frame(self.root, bg='#e6e6b8', height=25)
            self.title_frame.pack(fill='x', pady=0)
            self.title_frame.pack_propagate(False)
            
            # 添加标题栏按钮
            self.pin_button = tk.Button(self.title_frame, text="📌", 
                                      command=self.toggle_topmost,
                                      relief='raised', bd=0, bg='#e6e6b8')
            self.pin_button.pack(side='left', padx=3)
            
            # 添加透明度滑块
            self.opacity_scale = ttk.Scale(self.title_frame, 
                                         from_=0.3, to=1.0, 
                                         orient='horizontal', 
                                         length=40,
                                         command=self.change_opacity)
            self.opacity_scale.set(1.0)
            self.opacity_scale.pack(side='right', padx=3)
            
            # 创建文本区域
            self.text_area = tk.Text(self.root, wrap='word', bg='#ffffd0',
                                    relief='flat', font=('Arial', 10))
            self.text_area.pack(expand=True, fill='both', padx=2, pady=(0, 2))
            
            # 绑定事件
            self.title_frame.bind('<Button-1>', self.get_pos)
            self.title_frame.bind('<B1-Motion>', self.move_window)
            self.text_area.bind('<KeyRelease>', self.auto_save)
            
            # 其他UI组件...
            logging.debug("UI组件创建完成")
            
        except Exception as e:
            logging.error(f"创建UI组件时出错: {e}")
            raise

    def load_content(self):
        logging.info("开始加载便签内容")
        try:
            if os.path.exists('note_content.txt'):
                logging.debug("找到内容文件")
                with open('note_content.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                    logging.debug(f"读取到内容，长度: {len(content)}")
                    self.text_area.insert('1.0', content)
            else:
                logging.warning("内容文件不存在，将创建新文件")
                with open('note_content.txt', 'w', encoding='utf-8') as f:
                    f.write('')
        except Exception as e:
            logging.error(f"加载内容时出错: {e}")

    def auto_save(self, event=None):
        logging.debug("开始自动保存")
        try:
            content = self.text_area.get('1.0', 'end-1c')
            with open('note_content.txt', 'w', encoding='utf-8') as f:
                f.write(content)
            logging.debug(f"内容已保存，长度: {len(content)}")
        except Exception as e:
            logging.error(f"自动保存���出错: {e}")

    def change_opacity(self, value):
        logging.debug(f"设置透明度: {value}")
        try:
            self.root.attributes('-alpha', float(value))
        except Exception as e:
            logging.error(f"设置透明度时出错: {e}")

    def get_pos(self, event):
        self.x = event.x
        self.y = event.y
        
    def move_window(self, event):
        new_x = self.root.winfo_x() + (event.x - self.x)
        new_y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{new_x}+{new_y}")
        
    def toggle_topmost(self):
        current_state = self.root.attributes('-topmost')
        self.root.attributes('-topmost', not current_state)
        self.pin_button.configure(relief='sunken' if not current_state else 'raised')

    def setup_logging(self):
        try:
            # 确保日志目录存在
            log_dir = os.path.dirname("便签/sticky_note.log")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 配置日志
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('便签/sticky_note.log', encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            logging.info("=== 便签程序启动 ===")
            
        except Exception as e:
            print(f"设置日志时出错: {e}")
            raise
            
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    note = StickyNote()
    note.run() 