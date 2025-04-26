"""
This module defines custom styled widgets for the user interface, 
including buttons, labels, frames, and other UI elements with 
consistent styling. The goal is to provide a set of reusable components 
that can be easily applied across the application.
"""

import tkinter as tk
from tkinter import ttk
from config import VERSION

BINO_LOGO = (
    " _   _         \n"
    "| |_| |___ ___ \n"
    "| . |_|   | . |\n"
    "|___|_|_|_|___|\n"
    f"/////{VERSION}////"
)

class StyledToplevel(tk.Toplevel):
    """
    A custom Toplevel window with default styling and behavior.
    
    Inherits from `tk.Toplevel` and allows customizations such as font and background.
    
    :param parent: The parent widget, typically a Tk window or another Toplevel window.
    """
    def __init__(self, parent: tk.Widget = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

class StyledButton(tk.Button):
    """
    A custom Button widget with a hover effect and default font and background color.
    
    Inherits from `tk.Button` and applies a default font, background, and hover effect.
    
    :param parent: The parent widget, typically a Frame or Tk window.
    :param args: Additional arguments for Button initialization.
    :param kwargs: Additional keyword arguments for Button initialization (e.g., text, command).
    """
    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        kwargs.setdefault("font", ("Silkscreen", 9))
        kwargs.setdefault("bg", "#ffffff")
        super().__init__(parent, *args, **kwargs)

        # Hover effect
        self.bind("<Enter>", lambda e: self.config(bg="#d5a78d"))
        self.bind("<Leave>", lambda e: self.config(bg="#ffffff"))

class StyledLabel(tk.Label):
    """
    A custom Label widget with default font and background.
    
    Inherits from `tk.Label` and sets a default font and background color.
    
    :param parent: The parent widget, typically a Frame or Tk window.
    :param args: Additional arguments for Label initialization.
    :param kwargs: Additional keyword arguments for Label initialization (e.g., text).
    """
    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        kwargs.setdefault("font", ("Silkscreen", 9))
        kwargs.setdefault("bg", parent.cget("bg"))
        super().__init__(parent, *args, **kwargs)

class StyledEntry(tk.Entry):
    """
    A custom Entry widget with default width and border style.
    
    Inherits from `tk.Entry` and provides a default width and border width.
    
    :param parent: The parent widget, typically a Frame or Tk window.
    :param args: Additional arguments for Entry initialization.
    :param kwargs: Additional keyword arguments for Entry initialization.
    """
    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        kwargs.setdefault("width", 32)
        kwargs.setdefault("bd", 1)
        super().__init__(parent, *args, **kwargs)

class StyledCheckbutton(tk.Checkbutton):
    """
    A custom Checkbutton widget with default font and background.
    
    Inherits from `tk.Checkbutton` and sets a default font and background color.
    
    :param parent: The parent widget, typically a Frame or Tk window.
    :param args: Additional arguments for Checkbutton initialization.
    :param kwargs: Additional keyword arguments for Checkbutton initialization.
    """
    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        kwargs.setdefault("font", ("Silkscreen", 9))
        kwargs.setdefault("bg", parent.cget("bg"))
        super().__init__(parent, *args, **kwargs)

class StyledCombobox(ttk.Combobox):
    """
    A custom Combobox widget with a default width.
    
    Inherits from `ttk.Combobox` and provides a default width.
    
    :param parent: The parent widget, typically a Frame or Tk window.
    :param args: Additional arguments for Combobox initialization.
    :param kwargs: Additional keyword arguments for Combobox initialization.
    """
    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        kwargs.setdefault("width", 30)
        super().__init__(parent, *args, **kwargs)

class StyledFrame(tk.Frame):
    """
    A custom Frame widget with a default background color matching the parent's background.
    
    Inherits from `tk.Frame` and sets a default background color.
    
    :param parent: The parent widget, typically a Tk window or another Frame.
    :param args: Additional arguments for Frame initialization.
    :param kwargs: Additional keyword arguments for Frame initialization.
    """
    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        kwargs.setdefault("bg", parent.cget("bg"))
        super().__init__(parent, *args, **kwargs)

class StyledFrameWithLogo(tk.Frame):
    """
    A custom Frame widget that includes a logo in the top-right corner.
    
    Inherits from `tk.Frame` and displays a logo in the top-right corner with a grooved border.
    
    :param parent: The parent widget, typically a Tk window or another Frame.
    :param bino_logo: A string containing the logo text to display (defaults to a predefined logo).
    :param args: Additional arguments for Frame initialization.
    :param kwargs: Additional keyword arguments for Frame initialization.
    """
    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.bino_logo = BINO_LOGO
        self.bg_color = kwargs.get("bg", parent.cget("bg"))

        # Create a container with background color
        self.container = tk.Frame(self, bg=self.bg_color)
        self.container.pack(fill="x", padx=(0, 0), pady=(0, 0))
        self.container.columnconfigure(0, weight=1)

        # Create a frame with a "groove" effect
        self.frame = tk.Frame(self.container, relief="groove", borderwidth=2, bg="#d5a78d")
        self.frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        # Create a label for the logo, placed in the top-right corner
        self.logo_label = tk.Label(self.frame,
                                   text=self.bino_logo,
                                   font=("Courier", 10, "bold"),
                                   bg=self.frame.cget('bg'),
                                   anchor="e")
        self.logo_label.pack(side=tk.RIGHT, anchor="ne", padx=5)
