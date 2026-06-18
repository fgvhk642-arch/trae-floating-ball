import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import random
import threading
import time
import base64
import json
from io import BytesIO
try:
    from PIL import Image, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

try:
    from trae_utils import find_and_launch_trae
    HAS_TRAE_UTILS = True
except ImportError:
    HAS_TRAE_UTILS = False
    def find_and_launch_trae():
        return None

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    
    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tip_window, text=self.text, background="#ffffe0",
                        relief="solid", borderwidth=1, font=("Segoe UI", 9))
        label.pack()
    
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class ScreenCapture:
    def __init__(self, callback):
        self.callback = callback
        self.start_x = 0
        self.start_y = 0
        self.rect = None
        self.corner_box = None
        self.size_label = None
        
    def start_capture(self):
        if not HAS_PIL:
            messagebox.showwarning("提示", "请安装 Pillow 库以使用截图功能：\npip install Pillow")
            return
            
        self.root = tk.Toplevel()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.2)
        self.root.attributes("-topmost", True)
        self.root.configure(bg='black')
        
        self.canvas = tk.Canvas(self.root, cursor="cross", bg='black', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.header_frame = tk.Frame(self.root, bg='white')
        self.header_frame.pack(fill=tk.X, pady=50)
        
        self.screenshot_btn = tk.Button(self.header_frame, text="✂️ 截图提问", 
                                        font=("微软雅黑", 12), bg='#667eea', fg='white',
                                        borderwidth=0, padx=15, pady=5)
        self.screenshot_btn.pack(side=tk.LEFT, padx=(100, 10))
        
        self.share_btn = tk.Button(self.header_frame, text="📹 共享屏幕语音通话", 
                                   font=("微软雅黑", 12), bg='white', fg='#333',
                                   borderwidth=1, relief='solid', padx=15, pady=5)
        self.share_btn.pack(side=tk.LEFT)
        
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", self.cancel_screenshot)
        
        self.root.focus_force()
        self.root.grab_set()
    
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        if self.corner_box:
            self.canvas.delete(self.corner_box)
        if self.size_label:
            self.size_label.destroy()
            self.size_label = None
        
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='#667eea', width=2, fill='#667eea', stipple='gray50'
        )
    
    def on_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
            
            width = abs(event.x - self.start_x)
            height = abs(event.y - self.start_y)
            
            if self.size_label:
                self.size_label.destroy()
            
            self.size_label = tk.Label(self.root, text=f"{width} × {height}", 
                                       bg='white', fg='#333', font=("微软雅黑", 12))
            label_x = max(0, min(event.x + 10, self.root.winfo_screenwidth() - 100))
            label_y = max(60, min(event.y + 10, self.root.winfo_screenheight() - 30))
            self.size_label.place(x=label_x, y=label_y)
            
            self.draw_corner_box(event.x, event.y)
    
    def draw_corner_box(self, x, y):
        if self.corner_box:
            self.canvas.delete(self.corner_box)
        
        box_size = 30
        self.corner_box = self.canvas.create_rectangle(
            x - box_size, y - box_size, x + box_size, y + box_size,
            outline='#667eea', width=1, fill='white'
        )
        
        cancel_btn = self.canvas.create_text(x - 10, y - 10, text='✕', 
                                            fill='#999', font=("微软雅黑", 14, "bold"))
        confirm_btn = self.canvas.create_text(x + 10, y + 10, text='✓', 
                                             fill='#667eea', font=("微软雅黑", 14, "bold"))
        
        self.corner_box_items = [self.corner_box, cancel_btn, confirm_btn]
        
        self.canvas.tag_bind(cancel_btn, "<Button-1>", self.cancel_screenshot)
        self.canvas.tag_bind(confirm_btn, "<Button-1>", self.confirm_screenshot)
    
    def on_release(self, event):
        if self.rect:
            coords = self.canvas.coords(self.rect)
            width = abs(coords[2] - coords[0])
            height = abs(coords[3] - coords[1])
            
            if width > 5 and height > 5:
                self.show_confirm_buttons()
    
    def show_confirm_buttons(self):
        coords = self.canvas.coords(self.rect)
        x2, y2 = coords[2], coords[3]
        
        if self.corner_box:
            self.canvas.delete(self.corner_box)
        
        box_size = 30
        self.corner_box = self.canvas.create_rectangle(
            x2 - box_size, y2 - box_size, x2 + box_size, y2 + box_size,
            outline='#667eea', width=1, fill='white'
        )
        
        self.cancel_btn = self.canvas.create_text(x2 - 10, y2 - 10, text='✕', 
                                                 fill='#999', font=("微软雅黑", 14, "bold"))
        self.confirm_btn = self.canvas.create_text(x2 + 10, y2 + 10, text='✓', 
                                                  fill='#667eea', font=("微软雅黑", 14, "bold"))
        
        self.canvas.tag_bind(self.cancel_btn, "<Button-1>", self.cancel_screenshot)
        self.canvas.tag_bind(self.confirm_btn, "<Button-1>", self.confirm_screenshot)
    
    def cancel_screenshot(self, event=None):
        self.root.destroy()
    
    def confirm_screenshot(self, event=None):
        if not self.rect:
            return
            
        coords = self.canvas.coords(self.rect)
        if coords[2] - coords[0] < 5 or coords[3] - coords[1] < 5:
            return
            
        self.root.destroy()
        
        x1, y1 = int(coords[0]), int(coords[1])
        x2, y2 = int(coords[2]), int(coords[3])
        
        left, top = min(x1, x2), min(y1, y2)
        right, bottom = max(x1, x2), max(y1, y2)
        
        try:
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            
            buffer = BytesIO()
            screenshot.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            if HAS_PYPERCLIP:
                try:
                    clipboard_buffer = BytesIO()
                    screenshot.convert('RGB').save(clipboard_buffer, format='BMP')
                    clipboard_data = clipboard_buffer.getvalue()[14:]
                    pyperclip.copy(clipboard_data)
                except Exception as e:
                    pass
            
            self.callback(img_base64, screenshot)
        except Exception as e:
            messagebox.showerror("错误", f"截图失败：{str(e)}")

class TraeFloatingBall:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Trae AI 悬浮球")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.ball_size = 60
        self.ball_x = screen_width - self.ball_size - 30
        self.ball_y = screen_height - self.ball_size - 100
        
        self.root.geometry(f"{self.ball_size}x{self.ball_size}+{self.ball_x}+{self.ball_y}")
        
        self.history_file = os.path.join(os.path.expanduser("~"), ".trae_floating_ball_history.json")
        self.chat_history = self.load_chat_history()
        
        self.canvas = tk.Canvas(self.root, width=self.ball_size, height=self.ball_size, highlightthickness=0)
        self.canvas.pack()
        
        self.draw_ball()
        
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.chat_window = None
        self.menu_window = None
        
        self.knowledge_base = {
            "python": {
                "list": "Python列表：[]，支持增删改查，常用方法：append(), extend(), insert(), remove(), pop()",
                "dict": "Python字典：{}，键值对存储，常用方法：get(), keys(), values(), items()",
                "error": "Python错误处理：try...except...finally，捕获特定异常类型"
            },
            "javascript": {
                "array": "JS数组：[]，常用方法：push(), pop(), shift(), unshift(), slice(), splice()",
                "function": "JS函数：function name() {} 或 const name = () => {}",
                "async": "异步处理：async/await, Promise.then(), setTimeout()"
            },
            "git": {
                "basic": "常用命令：git init, git add ., git commit -m 'msg', git push, git pull",
                "branch": "分支操作：git branch, git checkout, git merge, git rebase"
            }
        }
        
        self.root.mainloop()
    
    def load_chat_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def save_chat_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history[-100:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def add_to_history(self, sender, message):
        self.chat_history.append({
            'sender': sender,
            'message': message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        self.save_chat_history()
    
    def draw_ball(self):
        self.canvas.delete("all")
        
        self.canvas.create_oval(0, 0, self.ball_size, self.ball_size, fill="#667eea", outline="")
        self.canvas.create_oval(5, 5, self.ball_size-5, self.ball_size-5, fill="#764ba2", outline="")
        
        self.canvas.create_text(self.ball_size//2, self.ball_size//2, text="T", fill="white", font=("Arial", 24, "bold"))
        
        self.canvas.create_oval(3, 3, 23, 23, fill="#4CAF50", outline="white", width=2)
        self.canvas.create_polygon(10, 8, 10, 18, 18, 13, fill="white")
        
        self.canvas.create_oval(self.ball_size-23, self.ball_size-23, self.ball_size-3, self.ball_size-3, fill="#1976D2", outline="white", width=2)
        self.canvas.create_text(self.ball_size-13, self.ball_size-13, text="≡", fill="white", font=("Arial", 10, "bold"))
    
    def on_left_click(self, event):
        x, y = event.x, event.y
        
        if x <= 23 and y <= 23:
            self.open_trae_app()
            return
        
        if x >= self.ball_size-23 and y >= self.ball_size-23:
            self.toggle_menu()
            return
        
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_right_click(self, event):
        self.toggle_menu()
    
    def toggle_menu(self):
        if self.menu_window is not None and self.menu_window.winfo_exists():
            self.menu_window.destroy()
            self.menu_window = None
        else:
            self.open_menu()
    
    def open_menu(self):
        self.menu_window = tk.Toplevel(self.root)
        self.menu_window.title("功能菜单")
        self.menu_window.overrideredirect(True)
        self.menu_window.wm_attributes("-topmost", True)
        
        x = self.root.winfo_x() - 160
        y = self.root.winfo_y()
        self.menu_window.geometry(f"160x340+{max(0, x)}+{y}")
        
        menu_frame = ttk.Frame(self.menu_window, padding=5)
        menu_frame.pack(fill=tk.BOTH, expand=True)
        
        menu_items = [
            ("打开 Trae", "📱", self.open_trae_app, "启动 Trae 应用程序"),
            ("打开对话窗口", "💬", self.open_chat_window, "打开 AI 助手聊天窗口"),
            ("截图提问", "📷", self.screenshot_question, "截取屏幕区域进行提问"),
            ("代码审查", "💻", self.code_review_action, "分析代码质量和潜在问题"),
            ("错误诊断", "🐛", self.error_diagnosis_action, "定位并解决程序错误"),
            ("代码生成", "📝", self.code_generation_action, "生成各类语言代码"),
            ("知识库", "📚", self.show_knowledge_action, "查询编程知识库"),
            ("隐藏悬浮球", "🙈", self.hide_ball, "暂时隐藏悬浮球到托盘"),
            ("退出", "🚪", self.exit_app, "退出应用程序")
        ]
        
        for text, icon, command, tooltip in menu_items:
            btn = ttk.Button(menu_frame, text=f"{icon} {text}", command=command)
            btn.pack(fill=tk.X, pady=2)
            ToolTip(btn, tooltip)
        
        self.menu_window.bind("<FocusOut>", self.on_menu_focus_out)
    
    def on_menu_focus_out(self, event):
        pass
    
    def close_menu(self):
        if self.menu_window:
            try:
                self.menu_window.destroy()
                self.menu_window = None
            except:
                pass
    
    def on_drag(self, event):
        if self.is_dragging:
            delta_x = event.x - self.drag_start_x
            delta_y = event.y - self.drag_start_y
            
            new_x = self.root.winfo_x() + delta_x
            new_y = self.root.winfo_y() + delta_y
            
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            new_x = max(0, min(new_x, screen_width - self.ball_size))
            new_y = max(0, min(new_y, screen_height - self.ball_size))
            
            self.root.geometry(f"+{new_x}+{new_y}")
    
    def on_release(self, event):
        if self.is_dragging:
            self.is_dragging = False
        else:
            x, y = event.x, event.y
            if not (x <= 23 and y <= 23) and not (x >= self.ball_size-23 and y >= self.ball_size-23):
                self.open_chat_window()
    
    def open_trae_app(self):
        self.close_menu()
        find_and_launch_trae()
    
    def open_chat_window(self):
        self.close_menu()
        
        if self.chat_window is not None and self.chat_window.winfo_exists():
            self.chat_window.lift()
            return
        
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.title("Trae AI 助手")
        self.chat_window.geometry("500x600")
        self.chat_window.wm_attributes("-topmost", True)
        
        x = self.root.winfo_x() - 500 + 60
        y = self.root.winfo_y() - 600
        self.chat_window.geometry(f"500x600+{max(0, x)}+{max(0, y)}")
        
        self.chat_window.protocol("WM_DELETE_WINDOW", self.close_chat_window)
        
        self.create_chat_ui()
    
    def create_chat_ui(self):
        self.chat_window.configure(bg="#f8f9fa")
        
        header = ttk.Frame(self.chat_window)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        logo_label = ttk.Label(header, text="T", font=("Segoe UI", 18, "bold"), background="#667eea", foreground="white", width=4, anchor="center")
        logo_label.pack(side=tk.LEFT, padx=(0, 5))
        
        title_label = ttk.Label(header, text="Trae", font=("Segoe UI", 16, "bold"), foreground="#333")
        title_label.pack(side=tk.LEFT)
        
        toolbar = ttk.Frame(header)
        toolbar.pack(side=tk.RIGHT)
        
        screenshot_btn = ttk.Button(toolbar, text="📷", command=self.screenshot_question, width=3, style="Toolbutton.TButton")
        screenshot_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(screenshot_btn, "截图提问")
        
        minimize_btn = ttk.Button(toolbar, text="—", command=self.minimize_chat, width=3, style="Toolbutton.TButton")
        minimize_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(minimize_btn, "最小化窗口")
        
        close_btn = ttk.Button(toolbar, text="×", command=self.close_chat_window, width=3, style="Toolbutton.TButton")
        close_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(close_btn, "关闭窗口")
        
        self.messages_frame = ttk.Frame(self.chat_window, style="Messages.TFrame")
        self.messages_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.messages_canvas = tk.Canvas(self.messages_frame, bg="#ffffff", highlightthickness=0)
        self.messages_scrollbar = ttk.Scrollbar(self.messages_frame, orient="vertical", command=self.messages_canvas.yview)
        self.messages_scrollbar.pack(side="right", fill="y")
        self.messages_canvas.configure(yscrollcommand=self.messages_scrollbar.set)
        
        self.messages_inner = ttk.Frame(self.messages_canvas)
        self.messages_canvas.create_window((0, 0), window=self.messages_inner, anchor="nw")
        
        if self.chat_history:
            for msg in self.chat_history[-20:]:
                self.add_message(msg['sender'], msg['message'], "user" if msg['sender'] == "我" else "bot")
        else:
            self.add_welcome_message()
        
        input_frame = ttk.Frame(self.chat_window, style="Input.TFrame")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        plus_btn = ttk.Button(input_frame, text="+", command=self.show_quick_menu, width=4)
        plus_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.input_entry = ttk.Entry(input_frame, width=60, font=("Segoe UI", 13))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.focus()
        self.input_entry.insert(0, "发消息或输入\"/\"选择技能")
        self.input_entry.bind("<FocusIn>", self.on_input_focus)
        self.input_entry.bind("<FocusOut>", self.on_input_blur)
        
        send_btn = ttk.Button(input_frame, text="发送", command=self.send_message, style="Send.TButton")
        send_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.input_entry.bind("<Return>", self.on_enter)
        
        self.messages_inner.bind("<Configure>", self.on_messages_configure)
        
        style = ttk.Style()
        style.configure("Toolbutton.TButton", padding=2)
        style.configure("Send.TButton", background="#667eea", foreground="white")
        style.configure("Messages.TFrame", background="#ffffff")
        style.configure("Input.TFrame", background="#ffffff", borderwidth=1, relief="solid")
    
    def add_welcome_message(self):
        welcome_frame = ttk.Frame(self.messages_inner, padding=10)
        welcome_frame.pack(fill=tk.X, padx=10, pady=20)
        
        welcome_text = ttk.Label(welcome_frame, text="你好！我是 Trae，可以帮你：\n\n💻 代码审查\n🐛 错误诊断\n📝 代码生成\n📚 知识库查询\n📷 截图提问\n\n请输入你的问题，或点击右下角按钮选择技能。", 
                                font=("Segoe UI", 13), foreground="#666", justify=tk.LEFT)
        welcome_text.pack()
    
    def add_message(self, sender, message, tag="bot"):
        msg_frame = ttk.Frame(self.messages_inner, padding=10)
        msg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if sender == "我":
            msg_frame.pack(anchor="e")
            bubble = ttk.Label(msg_frame, text=message, font=("Segoe UI", 13), 
                              background="#667eea", foreground="white", 
                              padding=(15, 10), borderwidth=0, relief="flat")
            bubble.config(wraplength=350)
        else:
            msg_frame.pack(anchor="w")
            bubble = ttk.Label(msg_frame, text=message, font=("Segoe UI", 13), 
                              background="#e9ecef", foreground="#333", 
                              padding=(15, 10), borderwidth=0, relief="flat")
            bubble.config(wraplength=350)
        
        bubble.pack()
        self.messages_canvas.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
    
    def add_code_block(self, code, language=""):
        code_frame = ttk.Frame(self.messages_inner, padding=10)
        code_frame.pack(fill=tk.X, padx=10, pady=5, anchor="w")
        
        code_label = ttk.Label(code_frame, text=f"```{language}\n{code}\n```", 
                              font=("Consolas", 11), background="#f8f9fa", 
                              foreground="#0066cc", padding=(15, 10), 
                              borderwidth=1, relief="solid")
        code_label.config(wraplength=400)
        code_label.pack()
        self.messages_canvas.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
    
    def send_message(self):
        message = self.input_entry.get().strip()
        if not message or message == "发消息或输入\"/\"选择技能":
            return
        
        self.add_message("我", message, "user")
        self.add_to_history("我", message)
        self.input_entry.delete(0, tk.END)
        
        thinking_frame = ttk.Frame(self.messages_inner, padding=10)
        thinking_frame.pack(fill=tk.X, padx=10, pady=5, anchor="w")
        thinking_label = ttk.Label(thinking_frame, text="思考中...", font=("Segoe UI", 13), 
                                   background="#e9ecef", foreground="#666", 
                                   padding=(15, 10))
        thinking_label.pack()
        self.thinking_frame = thinking_frame
        
        self.messages_canvas.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
        
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
    
    def on_input_focus(self, event):
        if self.input_entry.get() == "发消息或输入\"/\"选择技能":
            self.input_entry.delete(0, tk.END)
    
    def on_input_blur(self, event):
        if not self.input_entry.get():
            self.input_entry.insert(0, "发消息或输入\"/\"选择技能")
    
    def on_messages_configure(self, event):
        self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
    
    def minimize_chat(self):
        self.chat_window.iconify()
    
    def show_quick_menu(self):
        menu = tk.Menu(self.chat_window, tearoff=0)
        menu.add_command(label="💻 代码审查", command=self.code_review)
        menu.add_command(label="🐛 错误诊断", command=self.error_diagnosis)
        menu.add_command(label="📝 代码生成", command=self.code_generation)
        menu.add_command(label="📚 知识库", command=self.show_knowledge_base)
        menu.add_separator()
        menu.add_command(label="📷 截图提问", command=self.screenshot_question)
        menu.add_command(label="📋 复制内容", command=self.copy_clipboard)
        menu.add_command(label="🗑 清空聊天", command=self.clear_chat)
        menu.add_command(label="🗂️ 清空历史记录", command=self.clear_history)
        menu.post(self.chat_window.winfo_pointerx(), self.chat_window.winfo_pointery())
    
    def process_message(self, message):
        try:
            time.sleep(1)
            response = self.generate_response(message)
            if self.root.winfo_exists():
                self.root.after(0, self.safe_update_response, response)
        except Exception as e:
            if self.root.winfo_exists():
                self.root.after(0, self.show_error, str(e))
    
    def safe_update_response(self, response):
        try:
            self.update_response(response)
        except Exception as e:
            print(f"UI更新错误: {e}")
    
    def show_error(self, error_msg):
        try:
            messagebox.showerror("错误", f"处理消息时发生错误：{error_msg}")
        except Exception:
            print(f"显示错误消息失败: {error_msg}")
    
    def update_response(self, response):
        if hasattr(self, 'thinking_frame') and self.thinking_frame:
            self.thinking_frame.destroy()
            self.thinking_frame = None
        
        self.add_message("Trae", response['text'], "bot")
        self.add_to_history("Trae", response['text'])
        
        if response.get('code'):
            self.add_code_block(response['code'], response.get('language', ''))
            self.add_to_history("Trae", f"```{response.get('language', '')}\n{response['code']}\n```")
    
    def generate_response(self, message):
        msg_lower = message.lower()
        
        if any(word in msg_lower for word in ["审查", "review", "检查", "分析", "代码质量"]):
            return {
                "text": "好的，我来帮你审查代码。请提供要审查的代码片段，我将从以下维度分析：\n\n• 代码可读性和可维护性\n• 安全性（SQL注入、XSS等）\n• 性能优化建议\n• 最佳实践符合度\n• 潜在bug和边界情况\n\n💡 提示：点击左上角🟢绿色按钮打开Trae主应用，获得更强的AI代码审查能力！",
                "code": None
            }
        
        elif any(word in msg_lower for word in ["错误", "error", "bug", "异常", "崩溃", "不工作"]):
            return {
                "text": "我来帮你诊断问题。请提供以下信息：\n\n1. 🔍 完整的错误信息（traceback）\n2. 💻 相关代码片段\n3. 🎯 你期望的结果\n4. ❌ 实际发生的情况\n\n我会帮你定位问题并提供解决方案。\n\n💡 提示：点击左上角🟢绿色按钮打开Trae主应用，获得更强的AI错误诊断能力！",
                "code": None
            }
        
        elif any(word in msg_lower for word in ["生成", "create", "写一个", "做个", "实现"]):
            if "python" in msg_lower or "py" in msg_lower:
                return {
                    "text": "好的，我为你生成Python代码：",
                    "code": "def quick_sort(arr):\n    \"\"\"快速排序算法 - 分治思想\"\"\"\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)\n\n# 使用示例\nif __name__ == \"__main__\":\n    arr = [64, 34, 25, 12, 22, 11, 90]\n    print(\"排序前:\", arr)\n    print(\"排序后:\", quick_sort(arr))",
                    "language": "python"
                }
            elif "javascript" in msg_lower or "js" in msg_lower:
                return {
                    "text": "好的，我为你生成JavaScript代码：",
                    "code": "function debounce(func, wait) {\n    let timeout;\n    return function executedFunction(...args) {\n        const later = () => {\n            clearTimeout(timeout);\n            func(...args);\n        };\n        clearTimeout(timeout);\n        timeout = setTimeout(later, wait);\n    };\n}",
                    "language": "javascript"
                }
            else:
                return {
                    "text": "请告诉我你需要什么语言的代码？我支持：\n\n• Python\n• JavaScript/TypeScript\n• Java\n• C/C++\n• 以及其他主流语言",
                    "code": None
                }
        
        elif any(word in msg_lower for word in ["知识", "help", "帮助", "怎么", "如何", "用法"]):
            return self.search_knowledge_base(message)
        
        else:
            responses = [
                {
                    "text": "你好！我是 Trae AI 助手，可以帮你：\n\n💻 代码审查 - 分析代码质量和潜在问题\n🐛 错误诊断 - 定位并解决程序错误\n📝 代码生成 - 生成各类语言代码片段\n📚 知识库 - 查询编程知识\n📷 截图提问 - 截图分析问题\n\n💡 提示：点击左上角🟢绿色按钮打开Trae主应用，获得完整AI能力！\n\n请告诉我具体需要什么帮助？",
                    "code": None
                },
                {
                    "text": "我来帮你分析这个问题！\n\n常见问题解决步骤：\n1. ✅ 检查代码语法是否正确\n2. 📖 查看官方文档或API参考\n3. 🔍 在Stack Overflow搜索类似问题\n4. 🧪 编写测试用例复现问题\n5. 🔄 尝试最小化复现场景\n\n如果你能提供更多细节（如代码片段、错误信息），我可以给出更具体的建议！\n\n💡 提示：点击左上角🟢绿色按钮打开Trae主应用，获得更强的AI问题解决能力！",
                    "code": None
                },
                {
                    "text": "没问题！让我来帮你解决这个问题。\n\n请提供更多信息：\n• 你正在使用什么编程语言？\n• 你遇到了什么具体问题？\n• 是否有错误信息或代码片段？\n\n我会根据你的具体情况提供针对性的解决方案！\n\n💡 提示：点击左上角🟢绿色按钮打开Trae主应用，获得完整AI对话能力！",
                    "code": None
                }
            ]
            return random.choice(responses)
    
    def search_knowledge_base(self, query):
        query_lower = query.lower()
        
        for language, items in self.knowledge_base.items():
            if language in query_lower:
                for key, value in items.items():
                    if key in query_lower:
                        return {
                            "text": f"找到相关知识：\n{value}",
                            "code": None
                        }
        
        return {
            "text": "我目前掌握的知识包括：\n\n📚 Python：列表、字典、错误处理等\n📚 JavaScript：数组、函数、异步处理等\n📚 Git：基础命令、分支操作等\n\n你想了解哪个方面？或者可以问我具体的编程问题！",
            "code": None
        }
    
    def screenshot_question(self):
        self.close_menu()
        
        self.open_chat_window()
        self.add_message("我", "截图提问", "user")
        self.add_message("Trae", "正在启动截图工具...\n\n请在屏幕上拖动鼠标框选要截取的问题区域", "bot")
        
        self.root.after(200, self.start_screen_capture)
    
    def start_screen_capture(self):
        def on_screenshot_complete(img_base64, screenshot):
            try:
                screenshot.save("temp_screenshot.png")
                self.add_message("Trae", "✅ 截图已完成！正在分析图片内容...\n\n我会根据截图中的内容为你提供帮助。", "bot")
                
                if HAS_PYPERCLIP:
                    try:
                        pyperclip.copy("")
                        screenshot.save(pyperclip.paste(), format='PNG')
                    except:
                        pass
            except Exception as e:
                self.add_message("Trae", f"截图处理失败：{str(e)}", "bot")
        
        self.screen_capture = ScreenCapture(on_screenshot_complete)
        self.screen_capture.start_capture()
    
    def code_review_action(self):
        self.open_chat_window()
        self.root.after(500, self.code_review)
    
    def error_diagnosis_action(self):
        self.open_chat_window()
        self.root.after(500, self.error_diagnosis)
    
    def code_generation_action(self):
        self.open_chat_window()
        self.root.after(500, self.code_generation)
    
    def show_knowledge_action(self):
        self.open_chat_window()
        self.root.after(500, self.show_knowledge_base)
    
    def code_review(self):
        self.add_message("我", "请帮我审查这段代码：", "user")
        self.add_message("Trae", "好的，请粘贴你要审查的代码。我会从以下方面进行分析：\n\n• 代码结构和设计模式\n• 性能和效率\n• 安全性考虑\n• 可读性和维护性\n• 潜在bug和边界情况", "bot")
    
    def error_diagnosis(self):
        self.add_message("我", "我遇到了一个错误：", "user")
        self.add_message("Trae", "请提供以下信息，我来帮你诊断：\n\n1. 🔍 错误信息（完整的traceback）\n2. 💻 相关代码片段\n3. 🎯 你期望的结果\n4. ❌ 实际发生的情况\n5. 🔄 复现步骤\n\n信息越详细，诊断越准确！", "bot")
    
    def code_generation(self):
        self.add_message("我", "帮我生成一段代码：", "user")
        self.add_message("Trae", "请告诉我你需要什么代码：\n\n1. 📝 功能描述\n2. 🎨 编程语言\n3. ⚙️ 特殊要求（性能、风格等）\n\n例如：\n• 写一个Python的快速排序算法\n• 生成JavaScript的防抖函数\n• 实现Java的单例模式", "bot")
    
    def show_knowledge_base(self):
        self.add_message("我", "查看知识库", "user")
        self.add_message("Trae", "📚 当前知识库内容：\n\n🐍 Python\n• 列表操作：append(), extend(), insert(), remove(), pop()\n• 字典操作：get(), keys(), values(), items()\n• 错误处理：try...except...finally\n\n🌐 JavaScript\n• 数组方法：push(), pop(), shift(), slice(), splice()\n• 函数定义：function 和 箭头函数\n• 异步处理：async/await, Promise\n\n📦 Git\n• 基础命令：init, add, commit, push, pull\n• 分支操作：branch, checkout, merge, rebase\n\n想深入了解哪个主题？", "bot")
    
    def copy_clipboard(self):
        content = self.messages_text.get("1.0", tk.END).strip()
        if content:
            if HAS_PYPERCLIP:
                pyperclip.copy(content)
                messagebox.showinfo("提示", "已复制到剪贴板")
            else:
                try:
                    subprocess.run(["powershell", "-command", f"Set-Clipboard -Value '{content}'"], capture_output=True)
                    messagebox.showinfo("提示", "已复制到剪贴板（使用系统命令）")
                except Exception:
                    messagebox.showinfo("提示", "请手动选择并复制内容（Ctrl+C）")
        else:
            messagebox.showinfo("提示", "没有内容可复制")
    
    def clear_chat(self):
        if messagebox.askyesno("确认", "确定要清空聊天记录吗？"):
            self.messages_text.config(state=tk.NORMAL)
            self.messages_text.delete("1.0", tk.END)
            self.messages_text.config(state=tk.DISABLED)
            self.add_message("Trae", "聊天记录已清空。有什么我可以帮你的吗？", "bot")
    
    def clear_history(self):
        if messagebox.askyesno("确认", "确定要清空所有历史记录吗？"):
            self.chat_history = []
            self.save_chat_history()
            messagebox.showinfo("提示", "历史记录已清空")
    
    def hide_ball(self):
        if self.menu_window:
            self.menu_window.destroy()
            self.menu_window = None
        self.root.withdraw()
        messagebox.showinfo("提示", "悬浮球已隐藏\n需要重新启动应用才能再次显示")
    
    def exit_app(self):
        if messagebox.askyesno("确认", "确定要退出 Trae 悬浮球吗？"):
            if self.menu_window:
                self.menu_window.destroy()
            if self.chat_window:
                self.chat_window.destroy()
            self.root.destroy()
    
    def close_chat_window(self):
        if self.chat_window:
            self.chat_window.destroy()
            self.chat_window = None
    
    def on_enter(self, event):
        self.send_message()
        return "break"

if __name__ == "__main__":
    TraeFloatingBall()