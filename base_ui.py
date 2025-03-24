"""module docstring"""

import tkinter as tk
from tkinter import font
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
import os

from storage import save_data
from config import VERSION
from interpreters.python import PythonInterpreter
from interpreters.bash import BashInterpreter
from connectors.ssh import SshConnector
from connectors.PostgreSQL import PostgresConnector

FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20

def loadfont(fontpath, private=True, enumerable=False):
    '''
    Makes fonts located in file `fontpath` available to the font system.
    '''
    # Проверим, существует ли файл
    if not os.path.exists(fontpath):
        print(f"Шрифт не найден по пути: {fontpath}")
        return False

    # Преобразуем путь в байты для ctypes
    if isinstance(fontpath, str):
        pathbuf = create_string_buffer(fontpath.encode('utf-8'))  # Преобразуем в байтовую строку
        AddFontResourceEx = windll.gdi32.AddFontResourceExA
    elif isinstance(fontpath, unicode):
        pathbuf = create_unicode_buffer(fontpath)
        AddFontResourceEx = windll.gdi32.AddFontResourceExW
    else:
        raise TypeError('fontpath must be of type str or unicode')

    flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
    numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)
    return bool(numFontsAdded)

class BaseUI:
    """class docstring"""
    def __init__(self, app):
        self.bino_logo = (
            " _   _         \n"
            "| |_| |___ ___ \n"
            "| . |_|   | . |\n"
            "|___|_|_|_|___|\n"
            f"/////{VERSION}////"
        )
        self.app = app
        self.init_font()

    def setup_listbox(self, container, bind_command, add_button_command):
        """Создает листбокс и кнопку"""
        self.listbox = tk.Listbox(container, selectbackground="#f37600", selectforeground="black")
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", bind_command)
        self.add_button = self.create_button(container, "Add", add_button_command)
        self.add_button.pack(fill=tk.X)

    def init_font(self):
        font_path = "fonts/Silkscreen-Regular.ttf"

        if loadfont(font_path):  # Попытка загрузить шрифт
            self.custom_font = tk.font.Font(family="Silkscreen", size=12)
        else:
            print("Ошибка загрузки шрифта")
            self.custom_font = tk.font.Font(family="Courier", size=12)
    
    def open_options_window(self,parent_name, opt_type):
        """Открывает окно для выбора опций эндпоинта."""
        self.connectors = {
            "ssh": SshConnector(),
            "PostgreSQL": PostgresConnector()
        }
        self.interpreters = {
            "python": PythonInterpreter(),
            "bash": BashInterpreter()
        }

        options_window = tk.Toplevel()
        options_window.title(f"Options")
        container, frame = self.create_form_container(parent=options_window)

        if opt_type == "connector":
            parent_data = self.app.data["endpoints"][parent_name]
            ch_type = parent_data["type"]
            self.point_data = self.connectors
        elif opt_type == "interpreter":
            parent_data = self.app.data["scripts"][parent_name]
            ch_type = parent_data["interpreter"]
            self.point_data = self.interpreters
        
        options_vars = {}
        for i, option in enumerate(self.point_data[ch_type].available_options):
            var = tk.BooleanVar(value=parent_data.get("options", {}).get(option, False))
            chk = tk.Checkbutton(frame, text=option, variable=var, bg="#C0C0C0")
            chk.pack(anchor="w")
            options_vars[option] = var

        def save_options():
            # Сохраняем изменения
            if "options" not in parent_data:
                parent_data["options"] = {}
            for opt, var in options_vars.items():
                parent_data["options"][opt] = var.get()
            save_data(self.app.data)
            options_window.destroy()

        button_container = self.buttons_frame(container)
        save_btn = self.create_button(button_container, "Save", save_options)
        save_btn.grid(row=len(options_vars), column=0, pady=10)  # Также grid()

    def create_form_container(self, parent=None):
        """Создаёт контейнер и рамку формы"""
        if parent is None:
            parent = self.app.content_frame
        container = tk.Frame(parent, bg="#f2ceae")
        container.pack(fill="x", padx=(0, 0), pady=(0, 0))
        container.columnconfigure(0, weight=1)

        frame = tk.Frame(container, relief="groove", borderwidth=2, bg="#d5a78d")
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        logo_label = tk.Label(frame, text=self.bino_logo, font=("Courier", 10, "bold"), bg="#d5a78d", anchor="e")
        logo_label.pack(side=tk.RIGHT, anchor="ne", padx=5)

        return container, frame

    def clear_content_frame(self):
        """Очистка основного контентного фрейма."""
        for widget in self.app.content_frame.winfo_children():
            widget.destroy()

    def buttons_frame(self, container):
        buttons_frame = tk.Frame(container, bg="#f2ceae")
        buttons_frame.grid(row=0, column=1, sticky="ne")

        return buttons_frame

    def create_button(self, buttons_frame, user_text, user_command):
        """
        Создаёт кнопки на основе переданного списка.
        
        :param container: Родительский виджет для кнопок
        :param buttons_data: Список кортежей (Название, Функция)
        """

        def on_enter(e):
            e.widget.config(bg="#d5a78d")

        def on_leave(e):
            e.widget.config(bg="#ffffff")

        btn = tk.Button(buttons_frame, text=user_text, font=("Silkscreen", 9), bg="#ffffff", command=user_command)
        btn.pack(fill="x", pady=(2,0))
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn
