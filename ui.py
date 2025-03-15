import tkinter as tk
from tkinter import ttk
from storage import load_data
from script_manager import ScriptManager
from endpoint_manager import EndpointManager
from tkinter import font as tkFont

class App:
    def __init__(self, root):
        self.BINO_LOGO = r"""
         _   _         
        | |_| |___ ___ 
        | . |_|   | . |
        |___|_|_|_|___|
        /////v0.0.1////
        """
        # Устанавливаем окно приложения
        self.root = root
        self.root.title("B!NO")  # Заголовок окна
        self.root.geometry("800x600")  # Размер окна
        #self.root.add_option

        # Настройка стиля интерфейса
        self.style = ttk.Style()
        self.style.theme_use("classic")  # Используем классическую тему

        # Конфигурация кнопок (TButton)
        self.style.configure("TButton", font=("Silkscreen", 9), padding=4, background="#d3d3d3", foreground="black")  # Изменён фон на светло-серый
        self.style.map("TButton", background=[("active", "#a9a9a9")])  # Изменён цвет при наведении на кнопки на серый

        # Конфигурация меток (TLabel)
        self.style.configure("TLabel", font=("Silkscreen", 9), background="#f0f0f0", foreground="black")  # Лёгкий серый фон для меток

        # Конфигурация вкладок в блокноте (TNotebook)
        self.style.configure("TNotebook.Tab", background="#f0f0f0", foreground="black", padding=[5, 2], font=("Silkscreen", 8))  # Белые вкладки с чёрным текстом
        self.style.map("TNotebook.Tab", background=[("selected", "#c0c0c0"), ("active", "#d9d9d9")])  # Выделение вкладки в светло-серый цвет

        # Загрузка данных
        self.data = load_data()

        # Фрейм для сайдбара (левой панели)
        self.sidebar_frame = tk.Frame(root, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 0), pady=(0, 7))  # Расположение на левой стороне окна

        # Фрейм для основного контента (правой панели)
        self.content_frame = tk.Frame(root)
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
