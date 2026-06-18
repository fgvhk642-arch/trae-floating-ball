import tkinter as tk
from modules.floating_ball import FloatingBall
from modules.chat_window import ChatWindow
from modules.history_manager import HistoryManager
from modules.ai_service import AIService
from modules.screen_capture import ScreenCapture

def main():
    root = tk.Tk()
    root.title('Trae悬浮助手')
    
    history_manager = HistoryManager()
    ai_service = AIService()
    screen_capture = ScreenCapture(root)
    
    chat_window = ChatWindow(root, history_manager, ai_service, screen_capture)
    floating_ball = FloatingBall(root, chat_window)
    
    root.mainloop()

if __name__ == '__main__':
    main()
