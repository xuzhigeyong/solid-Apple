import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime
import logging
import uuid  # 新增：用于生成唯一ID

class StickyNote:
    def __init__(self, note_id=None, manager=None):
        # 新增：便签管理器引用和便签ID
        self.manager = manager
        self.note_id = note_id or str(uuid.uuid4())
        
        self.setup_logging()
        logging.info(f"初始化便签 {self.note_id}")
        
        # 修改：总是创建 Toplevel 窗口
        self.root = tk.Toplevel(manager.root if manager else None)
        self.root.title("便签")
        
        # 基本窗口设置
        self.root.geometry("250x300")
        self.root.configure(bg='#ffffd0')
        logging.debug("窗口基本设置完成")
        
        # 创建UI组件
        self.create_ui()
        logging.debug("UI组件创建完成")
        
        # 加载内容
        self.load_content()
        
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
            
            # 新增：添加新建和删除按钮
            self.new_button = tk.Button(self.title_frame, text="➕", 
                                      command=self.create_new_note,
                                      relief='raised', bd=0, bg='#e6e6b8')
            self.new_button.pack(side='left', padx=3)
            
            self.delete_button = tk.Button(self.title_frame, text="❌", 
                                         command=self.delete_note,
                                         relief='raised', bd=0, bg='#e6e6b8')
            self.delete_button.pack(side='left', padx=3)
            
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
            logging.error(f"自动保存时出错: {e}")

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

    def create_new_note(self):
        if self.manager:
            self.manager.create_note()
        else:
            StickyNote()

    def delete_note(self):
        if self.manager:
            self.manager.delete_note(self.note_id)
        self.root.destroy()

    def get_note_data(self):
        return {
            'id': self.note_id,
            'content': self.text_area.get('1.0', 'end-1c'),
            'position': (self.root.winfo_x(), self.root.winfo_y()),
            'opacity': self.opacity_scale.get(),
            'topmost': self.root.attributes('-topmost')
        }

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

# 新增：便签管理器类
class StickyNoteManager:
    def __init__(self):
        # 创建隐藏的主窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口
        self.notes = {}
        self.load_notes()

    def create_note(self, note_data=None):
        note = StickyNote(manager=self)
        self.notes[note.note_id] = note
        if note_data:
            self.restore_note_state(note, note_data)
        self.save_notes()
        return note

    def delete_note(self, note_id):
        if note_id in self.notes:
            del self.notes[note_id]
            self.save_notes()

    def save_notes(self):
        data = {note_id: note.get_note_data() for note_id, note in self.notes.items()}
        with open('notes_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_notes(self):
        try:
            if os.path.exists('notes_data.json'):
                with open('notes_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for note_data in data.values():
                    self.create_note(note_data)
            else:
                self.create_note()  # 创建第一个便签
        except Exception as e:
            logging.error(f"加载便签数据时出错: {e}")
            self.create_note()

    def restore_note_state(self, note, data):
        note.text_area.insert('1.0', data['content'])
        x, y = data['position']
        note.root.geometry(f"+{x}+{y}")
        note.opacity_scale.set(data['opacity'])
        note.root.attributes('-topmost', data['topmost'])

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    manager = StickyNoteManager()
    manager.run() 