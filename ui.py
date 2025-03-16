import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
import webbrowser

from storage import load_data
from script_manager import ScriptManager
from endpoint_manager import EndpointManager
from config import VERSION

class App:
    def __init__(self, root):
        self.BINO_LOGO = f"""
         _   _         
        | |_| |___ ___ 
        | . |_|   | . |
        |___|_|_|_|___|
        /////{VERSION}////
        """
        # Устанавливаем окно приложения
        self.root = root
        self.root.title("B!NO")  # Заголовок окна
        self.root.geometry("800x600")  # Размер окна

        # Настройка стиля интерфейса
        self.style = ttk.Style()
        self.style.theme_use("classic")  # Используем классическую тему

        # Конфигурация кнопок (TButton)
        self.style.configure("TButton", font=("Silkscreen", 9), background="#d3d3d3", foreground="black")  # Изменён фон на светло-серый
        self.style.map("TButton", background=[("active", "#a9a9a9")])  # Изменён цвет при наведении на кнопки на серый

        self.style.configure("TNotebook", background="white")  # Фон за вкладками
        self.style.configure("TNotebook.Tab", font=("Silkscreen", 9), padding=[5, 2], borderwidth=1)  
        self.style.map("TNotebook.Tab", background=[("selected", "#c0c0c0"), ("active", "#d9d9d9")])

        # Загрузка данных
        self.data = load_data()

        # Основной фрейм для всех виджетов
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Фрейм для сайдбара (левой панели)
        self.sidebar_frame = tk.Frame(self.main_frame, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 0), pady=(0, 0))  # Расположение на левой стороне окна

        # Фрейм для основного контента (правой панели)
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # Контент занимает всю оставшуюся часть окна

        # Блокнот для вкладок "Scripts" и "Endpoints"
        self.notebook = ttk.Notebook(self.sidebar_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 7))  # Блокнот растягивается по ширине и высоте

        # Создание вкладок
        self.scripts_frame = tk.Frame(self.notebook)
        self.endpoints_frame = tk.Frame(self.notebook)

        # Добавление вкладок в блокнот
        self.notebook.add(self.scripts_frame, text="Scripts")  # Вкладка для скриптов
        self.notebook.add(self.endpoints_frame, text="Endpoints")  # Вкладка для эндпоинтов

        # Менеджеры для скриптов и эндпоинтов
        self.scripts_manager = ScriptManager(self)  # Менеджер скриптов
        self.endpoints_manager = EndpointManager(self)  # Менеджер эндпоинтов

        # Создание футера
        self.footer_frame = tk.Frame(root, height=30, bg="#c0c0c0")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)  # Размещаем футер внизу

        # Фрейм для содержимого футера (слева копирайт, справа ссылка)
        self.footer_content = tk.Frame(self.footer_frame, bg="#c0c0c0")
        self.footer_content.pack(fill=tk.X, padx=10)  # Добавляем отступы по бокам

        # Лейбл с копирайтом слева
        self.footer_label = tk.Label(self.footer_content, text=f"© 2025 B!NO - All rights reserved", font=("Silkscreen", 8), bg="#c0c0c0")
        self.footer_label.pack(side=tk.LEFT)

        # Лейбл с кликабельной ссылкой на GitHub
        self.github_label = tk.Label(self.footer_content, text="GitHub", font=("Silkscreen", 8), fg="blue", bg="#c0c0c0", cursor="hand2")
        self.github_label.pack(side=tk.RIGHT)

        # Обработчик клика на ссылку
        self.github_label.bind("<Button-1>", self.open_github)

    # Функция для открытия GitHub
    def open_github(self, event):
        webbrowser.open("https://github.com/Ilya-Guyduk/bino")
