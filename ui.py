import tkinter as tk
from tkinter import ttk
from tkinter import font 
import webbrowser

from storage import load_data
from script_manager import ScriptManager
from endpoint_manager import EndpointManager
from config import VERSION

class App:
    def __init__(self, root: tk.Tk):
        """
        Initialize the main application window and its components.
        
        :param root: The root Tkinter window.
        """
        self.BINO_LOGO = f"""
         _   _         
        | |_| |___ ___ 
        | . |_|   | . |
        |___|_|_|_|___|
        /////{VERSION}////
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
        self.style.configure("TNotebook", background="white")  # Background behind tabs
        self.style.configure("TNotebook.Tab", font=("Silkscreen", 9), padding=[5, 2], borderwidth=1)  
        self.style.map("TNotebook.Tab", background=[("selected", "#c0c0c0"), ("active", "#d9d9d9")])

        # Load saved data (scripts, endpoints, etc.)
        self.data = load_data()

        # Create the main layout frames
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Sidebar (left panel) for navigation
        self.sidebar_frame = tk.Frame(self.main_frame, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 0))

        # Main content area (right panel)
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Notebook widget for "Scripts" and "Endpoints" tabs
        self.notebook = ttk.Notebook(self.sidebar_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 7))

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
        self.footer_frame = tk.Frame(root, height=30, bg="#c0c0c0")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)  

        # Footer content (left: copyright, right: GitHub link)
        self.footer_content = tk.Frame(self.footer_frame, bg="#c0c0c0")
        self.footer_content.pack(fill=tk.X, padx=10)  

        # Copyright label on the left
        self.footer_label = tk.Label(self.footer_content, text=f"© 2025 B!NO - All rights reserved", font=("Silkscreen", 8), bg="#c0c0c0")
        self.footer_label.pack(side=tk.LEFT)

        # Clickable GitHub link on the right
        self.github_label = tk.Label(self.footer_content, text="GitHub", font=("Silkscreen", 8), fg="blue", bg="#c0c0c0", cursor="hand2")
        self.github_label.pack(side=tk.RIGHT)

        # Bind click event to open GitHub repository
        self.github_label.bind("<Button-1>", self.open_github)

    def open_github(self, event):
        """Open the GitHub repository link in the default web browser."""
        webbrowser.open("https://github.com/Ilya-Guyduk/bino")
