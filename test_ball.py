import tkinter as tk
import subprocess
import os

class SimpleFloatingBall:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Trae Ball")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.root.geometry("60x60+%d+%d" % (screen_width - 90, screen_height - 160))
        
        self.canvas = tk.Canvas(self.root, width=60, height=60)
        self.canvas.pack()
        
        self.canvas.create_oval(0, 0, 60, 60, fill="#667eea")
        self.canvas.create_text(30, 30, text="T", fill="white", font=("Arial", 24, "bold"))
        
        self.canvas.create_oval(3, 3, 23, 23, fill="#4CAF50")
        self.canvas.create_polygon(10, 8, 10, 18, 18, 13, fill="white")
        
        self.canvas.bind("<Button-1>", self.on_click)
        
        self.root.mainloop()
    
    def on_click(self, event):
        x, y = event.x, event.y
        
        if x <= 23 and y <= 23:
            self.open_trae()
        else:
            print("打开聊天窗口")
    
    def open_trae(self):
        trae_paths = [
            r"C:\Program Files\Trae\Trae.exe",
            r"C:\Program Files (x86)\Trae\Trae.exe",
            os.path.join(os.environ.get('APPDATA', ''), 'Trae', 'Trae.exe'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Trae', 'Trae.exe')
        ]
        
        found = False
        for trae_path in trae_paths:
            if os.path.exists(trae_path):
                subprocess.Popen([trae_path], shell=True)
                found = True
                break
        
        if not found:
            print("未找到 Trae 应用")

if __name__ == "__main__":
    SimpleFloatingBall()