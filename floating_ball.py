import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import random
from trae_utils import find_and_launch_trae

class FloatingBall:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Trae Floating Ball")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.ball_size = 60
        self.ball_x = screen_width - self.ball_size - 30
        self.ball_y = screen_height - self.ball_size - 100
        
        self.root.geometry(f"{self.ball_size}x{self.ball_size}+{self.ball_x}+{self.ball_y}")
        
        self.canvas = tk.Canvas(self.root, width=self.ball_size, height=self.ball_size, highlightthickness=0)
        self.canvas.pack()
        
        self.canvas.create_oval(0, 0, self.ball_size, self.ball_size, fill="#667eea", outline="")
        self.canvas.create_oval(5, 5, self.ball_size-5, self.ball_size-5, fill="#764ba2", outline="")
        self.canvas.create_text(self.ball_size//2, self.ball_size//2, text="T", fill="white", font=("Arial", 24, "bold"))
        
        self.canvas.create_oval(3, 3, 23, 23, fill="#4CAF50", outline="white", width=2)
        self.canvas.create_polygon(10, 8, 10, 18, 18, 13, fill="white")
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.chat_window = None
        
        self.root.mainloop()
    
    def on_click(self, event):
        x, y = event.x, event.y
        
        if x <= 23 and y <= 23:
            self.open_trae_app()
            return
        
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
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
            if x > 23 or y > 23:
                self.open_chat_window()
    
    def open_trae_app(self):
        find_and_launch_trae()
    
    def open_chat_window(self):
        if self.chat_window is not None and self.chat_window.winfo_exists():
            self.chat_window.lift()
            return
        
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.title("Trae Chat")
        self.chat_window.geometry("420x550")
        self.chat_window.wm_attributes("-topmost", True)
        
        x = self.root.winfo_x() - 420 + 60
        y = self.root.winfo_y() - 550
        self.chat_window.geometry(f"420x550+{x}+{y}")
        
        self.chat_window.protocol("WM_DELETE_WINDOW", self.close_chat_window)
        
        header = ttk.Frame(self.chat_window)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        logo_label = ttk.Label(header, text="T", font=("Arial", 16, "bold"), background="#667eea", foreground="white", width=4, anchor="center")
        logo_label.pack(side=tk.LEFT, padx=(0, 5))
        
        title_label = ttk.Label(header, text="Trae", font=("Arial", 14, "bold"), foreground="#667eea")
        title_label.pack(side=tk.LEFT)
        
        toolbar = ttk.Frame(header)
        toolbar.pack(side=tk.RIGHT)
        
        screenshot_btn = ttk.Button(toolbar, text="📷", command=self.take_screenshot)
        screenshot_btn.pack(side=tk.LEFT, padx=2)
        
        close_btn = ttk.Button(toolbar, text="×", command=self.close_chat_window)
        close_btn.pack(side=tk.LEFT, padx=2)
        
        self.messages_text = tk.Text(self.chat_window, wrap=tk.WORD, state=tk.DISABLED, height=20)
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.add_message("Trae", "你好！我是 Trae，有什么我可以帮助你的吗？")
        
        input_frame = ttk.Frame(self.chat_window)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.input_entry = ttk.Entry(input_frame, width=50)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.focus()
        
        send_btn = ttk.Button(input_frame, text="发送", command=self.send_message)
        send_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.input_entry.bind("<Return>", self.on_enter)
    
    def add_message(self, sender, message):
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.insert(tk.END, f"{sender}: {message}\n\n")
        self.messages_text.config(state=tk.DISABLED)
        self.messages_text.see(tk.END)
    
    def send_message(self):
        message = self.input_entry.get().strip()
        if not message:
            return
        
        self.add_message("我", message)
        self.input_entry.delete(0, tk.END)
        
        responses = [
            "好的，我明白你的需求了。让我来帮你分析一下。",
            "这个问题很有意思！让我仔细思考一下...",
            "谢谢你的提问，我来为你解答。",
            "根据你的描述，我认为可以这样处理：",
            "我理解你的想法，以下是我的建议：",
            "这个问题我需要再想想，让我分析一下。",
            "好的，我来帮你处理这个问题。"
        ]
        
        response = random.choice(responses)
        self.add_message("Trae", response)
    
    def on_enter(self, event):
        self.send_message()
        return "break"
    
    def take_screenshot(self):
        messagebox.showinfo("提示", "截图功能需要安装 pyautogui 库")
    
    def close_chat_window(self):
        if self.chat_window:
            self.chat_window.destroy()
            self.chat_window = None

if __name__ == "__main__":
    FloatingBall()