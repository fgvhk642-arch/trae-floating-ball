import os
import subprocess
from tkinter import messagebox, filedialog

TRAE_CANDIDATE_PATHS = [
    r"C:\Temp\TTT\Trae CN\Trae CN.exe",
    r"C:\Program Files\Trae\Trae.exe",
    r"C:\Program Files (x86)\Trae\Trae.exe",
    os.path.join(os.environ.get('APPDATA', ''), 'Trae', 'Trae.exe'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Trae', 'Trae.exe'),
    os.path.join(os.environ.get('APPDATA', ''), '..', 'Local', 'Trae', 'Trae.exe'),
    r"C:\Users\Public\Trae\Trae.exe",
    r"C:\Trae\Trae.exe",
    os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Trae', 'Trae.exe'),
    os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Roaming', 'Trae', 'Trae.exe'),
    r"C:\Program Files\TraeCN\TraeCN.exe",
    r"C:\Program Files (x86)\TraeCN\TraeCN.exe",
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'TraeCN', 'TraeCN.exe'),
    r"C:\Temp\TTT\Trae CN\Trae.exe",
    os.path.join(os.environ.get('TEMP', r'C:\Temp'), 'TTT', 'Trae CN', 'Trae.exe')
]

def find_and_launch_trae():
    for trae_path in TRAE_CANDIDATE_PATHS:
        if os.path.exists(trae_path):
            try:
                subprocess.Popen([trae_path], shell=True)
                return True
            except Exception:
                continue
    return _prompt_manual_selection()

def _prompt_manual_selection():
    result = messagebox.askyesno(
        "提示",
        "未找到 Trae 应用程序\n\n是否需要手动选择 Trae 的安装路径？"
    )
    if not result:
        return False
    
    file_path = filedialog.askopenfilename(
        title="选择 Trae 应用程序",
        filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
    )
    
    if not file_path:
        return False
    
    try:
        subprocess.Popen([file_path], shell=True)
        messagebox.showinfo("提示", "已成功启动 Trae！")
        return True
    except Exception as e:
        messagebox.showerror("错误", f"启动失败：{str(e)}")
        return False