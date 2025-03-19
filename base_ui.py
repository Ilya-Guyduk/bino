"""module docstring"""

import tkinter as tk
from tkinter import font
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
import os

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
        self.app = app
        self.init_font()

    def setup_listbox(self, container, bind_command, add_button_command):
        """Создает листбокс и кнопку"""
        self.listbox = tk.Listbox(container)
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

    def create_form_container(self):
        """Создаёт контейнер и рамку формы"""
        container = tk.Frame(self.app.content_frame)
        container.pack(fill="x", padx=7, pady=(0, 5))
        container.columnconfigure(0, weight=1)

        frame = tk.Frame(container, relief="groove", borderwidth=2, bg="#C0C0C0")
        frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        logo_label = tk.Label(frame, text=self.app.bino_logo, font=("Courier", 10, "bold"), bg="#C0C0C0", anchor="e")
        logo_label.pack(side=tk.RIGHT, anchor="ne", padx=5)

        return container, frame

    def clear_content_frame(self):
        """Очистка основного контентного фрейма."""
        for widget in self.app.content_frame.winfo_children():
            widget.destroy()

    def buttons_frame(self, container):
        buttons_frame = tk.Frame(container)
        buttons_frame.grid(row=0, column=1, sticky="ne")

        return buttons_frame

    def create_button(self, buttons_frame, user_text, user_command):
        """
        Создаёт кнопки на основе переданного списка.
        
        :param container: Родительский виджет для кнопок
        :param buttons_data: Список кортежей (Название, Функция)
        """

        def on_enter(e):
            e.widget.config(bg="gray80")

        def on_leave(e):
            e.widget.config(bg="SystemButtonFace")

        btn = tk.Button(buttons_frame, text=user_text, font=("Silkscreen", 9), command=user_command)
        btn.pack(fill="x", pady=0)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn
