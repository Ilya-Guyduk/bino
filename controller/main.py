"""
UI module for the B!NO application.

This module defines the `App` class, which initializes the main application window
using Tkinter. It manages the user interface layout, styling, and interactions.

Features:
- Sidebar with script and endpoint management tabs.
- Footer with copyright information and a GitHub link.
- Uses ttk styling for better appearance.
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import webbrowser
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
import os

from controller.file import FileStorage
from controller.controller import FormHandler

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
        add_font_resource_ex = windll.gdi32.AddFontResourceExA
    elif isinstance(fontpath, unicode):
        pathbuf = create_unicode_buffer(fontpath)
        add_font_resource_ex = windll.gdi32.AddFontResourceExW
    else:
        raise TypeError('fontpath must be of type str or unicode')

    flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
    num_fonts_added = add_font_resource_ex(byref(pathbuf), flags, 0)
    return bool(num_fonts_added)

class App:
    """
    Main application class that initializes and manages the UI components.
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the main application window and its components.

        :param root: The root Tkinter window.
        """


        # Configure the main application window
        self.root = root
        self.root.title("B!NO")  # Set window title
        self.root.geometry("650x600")  # Set default window size

        # Setup UI styling
        self.style = ttk.Style()
        self.style.theme_use("classic")  # Use a classic theme for better compatibility
        self._create_menu_bar()
        self._init_font()

        # Configure notebook (tab container) styles
        self.style.configure("TNotebook",
                             background="#f2ceae",
                             borderwidth=1,
                             relief="solid"
                             )  # Background behind tabs

        self.style.configure("TNotebook.Tab",
                             font=("Silkscreen", 9),
                             padding=[4, 2],
                             background="#fdbf1c",
                             borderwidth=1,
                             relief="solid")

        self.style.map("TNotebook.Tab", background=[("selected", "#f37600"), ("active", "#31b7c3")])

        # Load saved data (scripts, endpoints, etc.)
        self.storage = FileStorage()
        self.data = self.storage.data

        # Create the main layout frames
        self.main_frame = tk.Frame(root, bg="#f2ceae")
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Sidebar (left panel) for navigation
        self.sidebar_frame = tk.Frame(self.main_frame, width=200, bg="#f2ceae")
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, pady=(4, 5), padx=(4, 5))

        # Main content area (right panel)
        self.content_frame = tk.Frame(self.main_frame, bg="#f2ceae")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(4, 5), padx=(0, 4))

        # Notebook widget for "Scripts" and "Endpoints" tabs
        self.notebook = ttk.Notebook(self.sidebar_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create individual tab frames
        self.scripts_frame = tk.Frame(self.notebook)
        self.endpoints_frame = tk.Frame(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(self.scripts_frame, text="Scripts")
        self.notebook.add(self.endpoints_frame, text="Endpoints")

        # Managers for handling scripts and endpoints
        self.scripts_manager = FormHandler(self, "scripts")
        self.endpoints_manager = FormHandler(self, "endpoints")

        # Footer section (bottom of the window)
        self.footer_frame = tk.Frame(root, height=30, bg="#d5a78d")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Footer content (left: copyright, right: GitHub link)
        self.footer_content = tk.Frame(self.footer_frame, bg="#d5a78d")
        self.footer_content.pack(fill=tk.X, padx=10)

        # Copyright label on the left
        self.footer_label = tk.Label(
            self.footer_content,
            text="© 2025 B!NO - All rights reserved",
            font=("Silkscreen", 8),
            bg="#d5a78d",
        )
        self.footer_label.pack(side=tk.LEFT)

        # Clickable GitHub link on the right
        self.github_label = tk.Label(
            self.footer_content,
            text="GitHub",
            font=("Silkscreen", 8),
            fg="blue",
            bg="#d5a78d",
            cursor="hand2",
        )
        self.github_label.pack(side=tk.RIGHT)

        # Bind click event to open GitHub repository
        self.github_label.bind("<Button-1>", self.open_github)

    @staticmethod
    def open_github(_event):
        """
        Open the GitHub repository link in the default web browser.

        :param _event: Unused event parameter from Tkinter.
        """
        webbrowser.open("https://github.com/Ilya-Guyduk/bino")

    def _init_font(self):
        font_path = "fonts/Silkscreen-Regular.ttf"

        if loadfont(font_path):  # Попытка загрузить шрифт
            self.custom_font = tkfont.Font(family="Silkscreen", size=12)
        else:
            print("Ошибка загрузки шрифта")
            self.custom_font = tkfont.Font(family="Courier", size=12)

    def _create_menu_bar(self):
        """
        Creates a top menu bar with File, Edit, and Help menus.
        """
        menu_bar = tk.Menu(self.root, tearoff=0, bg="#f2ceae")

        # --- File Menu ---
        file_menu = tk.Menu(menu_bar, tearoff=0, bg="#f2ceae")
        file_menu.add_command(label="New", command=lambda: print("New clicked"))
        file_menu.add_command(label="Open", command=lambda: print("Open clicked"))
        file_menu.add_command(label="Save", command=lambda: print("Save clicked"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="Storage", menu=file_menu)

        # --- Edit Menu ---
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=lambda: print("Undo clicked"))
        edit_menu.add_command(label="Redo", command=lambda: print("Redo clicked"))
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # --- Help Menu ---
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: print("This is B!NO v1.0"))
        help_menu.add_command(label="GitHub", command=lambda: self.open_github(None))
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Attach the menu bar to the root window
        self.root.config(menu=menu_bar)
