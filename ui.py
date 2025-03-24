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
import webbrowser

from storage import load_data
from script_manager import ScriptManager
from endpoint_manager import EndpointManager



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
        self.root.geometry("800x600")  # Set default window size

        # Setup UI styling
        self.style = ttk.Style()
        self.style.theme_use("classic")  # Use a classic theme for better compatibility

        # Configure button styles (TButton)
        self.style.configure("TButton", font=("Silkscreen", 9), background="#d3d3d3", foreground="black")
        self.style.map("TButton", background=[("active", "#a9a9a9")])  # Change background color on hover

        # Configure notebook (tab container) styles
        self.style.configure("TNotebook", background="#f2ceae", borderwidth=1, relief="solid")  # Background behind tabs
        self.style.configure("TNotebook.Tab", font=("Silkscreen", 9), padding=[4, 2], background="#fdbf1c", borderwidth=1, relief="solid")
        self.style.map("TNotebook.Tab", background=[("selected", "#f37600"), ("active", "#31b7c3")])

        # Load saved data (scripts, endpoints, etc.)
        self.data = load_data()

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
        self.scripts_manager = ScriptManager(self)
        self.endpoints_manager = EndpointManager(self)

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
