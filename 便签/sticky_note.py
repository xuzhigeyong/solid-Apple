import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime

class StickyNote:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("便签")
        
        # 基本窗口设置
        self.root.geometry("250x300")
        self.root.configure(bg='#ffffd0')  # 淡黄色背景
        
        # 创建标题栏框架
        self.title_frame = tk.Frame(self.root, bg='#e6e6b8', height=25)
        self.title_frame.pack(fill='x', pady=0)
        self.title_frame.pack_propagate(False)
        
        # 添加透明度滑块
        self.opacity_scale = ttk.Scale(self.title_frame, 
                                     from_=0.3, 
                                     to=1.0, 
                                     orient='horizontal', 
                                     length=40,
                                     command=self.change_opacity)
        self.opacity_scale.set(1.0)
        self.opacity_scale.pack(side='right', padx=3)
        
        # 置顶按钮
        self.pin_button = tk.Button(self.title_frame, 
                                  text="📌", 
                                  bg='#e6e6b8',
                                  command=self.toggle_topmost, 
                                  borderwidth=0)
        self.pin_button.pack(side='right', padx=3)
        
        # 文本区域
        self.text_area = tk.Text(self.root, 
                                wrap='word', 
                                bg='#ffffd0',
                                borderwidth=0, 
                                font=('Arial', 12))
        self.text_area.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 绑定事件
        self.title_frame.bind('<B1-Motion>', self.move_window)
        self.title_frame.bind('<Button-1>', self.get_pos)
        self.text_area.bind('<KeyRelease>', self.auto_save)
        
        # 设置窗口属性（移到最后）
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 1.0)
        
        # 加载保存的内容
        self.load_content()
        
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
        
    def change_opacity(self, value):
        """改变窗口透明度"""
        try:
            self.root.attributes('-alpha', float(value))
        except Exception as e:
            print(f"设置透明度时出错: {e}")
            
    def auto_save(self, event=None):
        try:
            content = self.text_area.get('1.0', 'end-1c')
            with open('note_content.txt', 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"保存内容时出错: {e}")
            
    def load_content(self):
        try:
            if os.path.exists('note_content.txt'):
                with open('note_content.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_area.insert('1.0', content)
            else:
                with open('note_content.txt', 'w', encoding='utf-8') as f:
                    f.write('')
        except Exception as e:
            print(f"加载内容时出错: {e}")
            
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    note = StickyNote()
    note.run() 