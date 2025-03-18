from tkinter import Tk
from ui import App
import sys
import os

def resource_path(relative_path: str) -> str:
    """
    Resolve the absolute path to a resource, handling cases where the application 
    is packaged into an executable with PyInstaller.
    
    If the application is running as a bundled executable, it retrieves resources 
    from the _MEIPASS temporary directory. Otherwise, it returns the relative path.
    
    :param relative_path: The relative path to the resource file.
    :return: The absolute path to the resource.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
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
