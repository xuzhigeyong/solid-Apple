import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime
import logging
import uuid

class StickyNote:
    def __init__(self, note_id=None, manager=None, title=None, content=None):
        self.manager = manager
        self.note_id = note_id or str(uuid.uuid4())
        self.title = title or "新建便签"
        self.content = content or ""
        
        self.setup_logging()
        logging.info(f"初始化便签 {self.note_id}")
        
        # 创建窗口但默认不显示
        self.root = tk.Toplevel(manager.root if manager else None)
        self.root.title("便签")
        self.root.geometry("250x300")
        self.root.configure(bg='#ffffd0')
        
        # 创建UI组件
        self.create_ui()
        
        # 加载内容
        if title:
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, title)
        if content:
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', content)
            
        # 默认隐藏窗口
        self.root.withdraw()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """处理窗口关闭事件"""
        self.root.withdraw()  # 隐藏而不是销毁
        
    def show(self):
        """显示便签"""
        if not self.root.winfo_viewable():
            self.root.deiconify()
            self.root.lift()
        else:
            # 如果已经可见，则闪烁提示
            self.flash_window()
            
    def flash_window(self):
        """窗口闪烁效果"""
        current_alpha = self.root.attributes('-alpha')
        def flash_cycle(count=0):
            if count < 6:  # 闪烁3次
                new_alpha = 0.3 if count % 2 == 0 else 1.0
                self.root.attributes('-alpha', new_alpha)
                self.root.after(100, lambda: flash_cycle(count + 1))
            else:
                self.root.attributes('-alpha', current_alpha)
        flash_cycle()

    def create_ui(self):
        logging.debug("开始创建UI组件")
        try:
            # 创建标题栏框架
            self.title_frame = tk.Frame(self.root, bg='#e6e6b8', height=25)
            self.title_frame.pack(fill='x', pady=0)
            self.title_frame.pack_propagate(False)
            
            # 添加标题输入框
            self.title_entry = tk.Entry(self.title_frame, bg='#e6e6b8', 
                                      relief='flat', width=20)
            self.title_entry.insert(0, self.title)
            self.title_entry.pack(side='left', padx=3)
            
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
            self.title_entry.bind('<KeyRelease>', self.auto_save)
            
            # 添加按钮
            self.new_button = tk.Button(self.title_frame, text="➕", 
                                      command=self.create_new_note,
                                      relief='raised', bd=0, bg='#e6e6b8')
            self.new_button.pack(side='left', padx=3)
            
            self.delete_button = tk.Button(self.title_frame, text="❌", 
                                         command=self.delete_note,
                                         relief='raised', bd=0, bg='#e6e6b8')
            self.delete_button.pack(side='left', padx=3)
            
            self.list_button = tk.Button(self.title_frame, text="📋", 
                                       command=self.show_note_list,
                                       relief='raised', bd=0, bg='#e6e6b8')
            self.list_button.pack(side='left', padx=3)
            
        except Exception as e:
            logging.error(f"创建UI组件时出错: {e}")
            raise

    def auto_save(self, event=None):
        if self.manager:
            self.manager.save_notes()

    def change_opacity(self, value):
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

    def create_new_note(self):
        if self.manager:
            self.manager.create_note()

    def delete_note(self):
        if self.manager:
            self.manager.delete_note(self.note_id)
        self.root.destroy()

    def show_note_list(self):
        if self.manager:
            self.manager.root.deiconify()
            self.manager.root.lift()

    def setup_logging(self):
        try:
            os.makedirs('便签', exist_ok=True)
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('便签/sticky_note.log', encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
        except Exception as e:
            print(f"设置日志时出错: {e}")
            raise

class StickyNoteManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("便签管理器")
        self.root.geometry("400x500")
        self.notes = {}
        
        # 确保数据目录存在
        os.makedirs('data', exist_ok=True)
        
        # 创建管理界面
        self.create_manager_ui()
        
        # 加载便签
        self.load_notes()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_manager_ui(self):
        # 创建顶部工具栏
        self.toolbar = tk.Frame(self.root)
        self.toolbar.pack(fill='x', padx=5, pady=5)
        
        # 添加新建便签按钮
        tk.Button(self.toolbar, text="新建便签", 
                 command=self.create_note).pack(side='left', padx=5)
        
        # 添加搜索框
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_notes)
        tk.Entry(self.toolbar, textvariable=self.search_var, 
                width=20).pack(side='right', padx=5)
        tk.Label(self.toolbar, text="搜索：").pack(side='right')
        
        # 创建便签列表框架
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建滚动条
        scrollbar = tk.Scrollbar(self.list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # 创建画布和内部框架用于滚动
        self.canvas = tk.Canvas(self.list_frame)
        self.notes_frame = tk.Frame(self.canvas)
        
        # 配置滚动
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.canvas.yview)
        
        # 放置画布和���签框架
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.notes_frame, anchor='nw')
        
        # 绑定调整大小事件
        self.notes_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def filter_notes(self, *args):
        search_text = self.search_var.get().lower()
        self.update_notes_list(search_text)

    def create_note(self, note_data=None):
        note = StickyNote(
            manager=self,
            note_id=note_data.get('id') if note_data else None,
            title=note_data.get('title') if note_data else None,
            content=note_data.get('content', '') if note_data else None
        )
        
        self.notes[note.note_id] = note
        
        if note_data:
            x, y = note_data.get('position', (100, 100))
            note.root.geometry(f"+{x}+{y}")
            note.opacity_scale.set(note_data.get('opacity', 1.0))
            note.root.attributes('-topmost', note_data.get('topmost', False))
            
        self.save_notes()
        return note

    def delete_note(self, note_id):
        if note_id in self.notes:
            self.notes[note_id].root.destroy()  # 真正销毁窗口
            del self.notes[note_id]
            self.save_notes()
        self.update_notes_list()

    def save_notes(self):
        data = {}
        for note_id, note in self.notes.items():
            data[note_id] = {
                'id': note.note_id,
                'title': note.title_entry.get(),
                'content': note.text_area.get('1.0', 'end-1c'),
                'position': (note.root.winfo_x(), note.root.winfo_y()),
                'opacity': note.opacity_scale.get(),
                'topmost': note.root.attributes('-topmost'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
        with open('data/notes.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        self.update_notes_list()

    def load_notes(self):
        try:
            if os.path.exists('data/notes.json'):
                with open('data/notes.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for note_data in data.values():
                    self.create_note(note_data)
            else:
                self.create_note()
        except Exception as e:
            logging.error(f"加载便签数据时出错: {e}")
            self.create_note()

    def update_notes_list(self, search_text=''):
        for widget in self.notes_frame.winfo_children():
            widget.destroy()
            
        for note_id, note in self.notes.items():
            title = note.title_entry.get() or "无标题"
            content = note.text_area.get('1.0', 'end-1c')
            
            if search_text and search_text not in title.lower() and \
               search_text not in content.lower():
                continue
                
            note_frame = tk.Frame(self.notes_frame, relief='solid', bd=1)
            note_frame.pack(fill='x', padx=5, pady=2)
            
            info_frame = tk.Frame(note_frame)
            info_frame.pack(side='left', fill='x', expand=True, padx=5, pady=5)
            
            tk.Label(info_frame, text=title, font=('Arial', 10, 'bold'), 
                    anchor='w').pack(fill='x')
            
            preview = content[:50] + "..." if len(content) > 50 else content
            tk.Label(info_frame, text=preview, anchor='w', 
                    wraplength=250).pack(fill='x')
            
            button_frame = tk.Frame(note_frame)
            button_frame.pack(side='right', padx=5, pady=5)
            
            # 修改打开按钮的行为
            tk.Button(button_frame, text="打开", 
                     command=lambda n=note: n.show()).pack(side='top', pady=2)
            tk.Button(button_frame, text="删除", 
                     command=lambda id=note_id: self.delete_note(id)).pack(
                         side='top', pady=2)

    def on_closing(self):
        """处理管理器窗口关闭事件"""
        # 保存所有便签
        self.save_notes()
        # 销毁所有窗口
        for note in self.notes.values():
            note.root.destroy()
        # 关闭主窗口
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    manager = StickyNoteManager()
    manager.run()