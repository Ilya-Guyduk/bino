from tkinter import Tk
from ui import App
import sys

def resource_path(relative_path):
    """Возвращает путь к файлу внутри .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.iconbitmap(resource_path("icon.ico"))
    root.mainloop()