"""
Main entry point for the Tkinter-based application.

This script initializes the main application window and handles resource path resolution,
ensuring compatibility when packaged into an executable using PyInstaller.

Features:
- Resolves resource paths correctly for both development and packaged execution.
- Initializes the Tkinter-based UI.
- Loads application icons dynamically.

Usage:
Run this script to start the application.
"""

import sys
import os
from tkinter import Tk
from controller.main import App


def resource_path(relative_path: str) -> str:
    """
    Resolve the absolute path to a resource, handling cases where the application 
    is packaged into an executable with PyInstaller.
    
    If the application is running as a bundled executable, it retrieves resources 
    from the PyInstaller `_MEIPASS` temporary directory safely using `getattr`.
    
    :param relative_path: The relative path to the resource file.
    :return: The absolute path to the resource.
    """
    try:
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"Error in resource_path: {e}")
        return relative_path


if __name__ == "__main__":
    # Initialize the main Tkinter application window
    root = Tk()
    # Create an instance of the App class, passing the root window
    app = App(root)
    # Set the application icon (use absolute path resolution for packaged executables)
    root.iconbitmap(resource_path("icon.ico"))
    # Start the Tkinter event loop
    root.mainloop()
