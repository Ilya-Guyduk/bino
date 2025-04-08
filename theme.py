import tkinter as tk
from tkinter import ttk

class StyledButton(tk.Button):
    def __init__(self, parent, *args, **kwargs):
        kwargs.setdefault("font", ("Silkscreen", 9))
        kwargs.setdefault("bg", "#ffffff")
        super().__init__(parent, *args, **kwargs)

        self.bind("<Enter>", lambda e: self.config(bg="#d5a78d"))
        self.bind("<Leave>", lambda e: self.config(bg="#ffffff"))

class StyledLabel(tk.Label):
    def __init__(self, parent, *args, **kwargs):
        kwargs.setdefault("font", ("Silkscreen", 9))
        kwargs.setdefault("bg", parent.cget("bg"))
        super().__init__(parent, *args, **kwargs)

class StyledEntry(tk.Entry):
    def __init__(self, parent, *args, **kwargs):
        kwargs.setdefault("width", 32)
        kwargs.setdefault("bd", 1)
        super().__init__(parent, *args, **kwargs)

class StyledCheckbutton(tk.Checkbutton):
    def __init__(self, parent, *args, **kwargs):
        kwargs.setdefault("font", ("Silkscreen", 9))
        kwargs.setdefault("bg", parent.cget("bg"))
        super().__init__(parent, *args, **kwargs)

class StyledCombobox(ttk.Combobox):
    def __init__(self, parent, *args, **kwargs):
        kwargs.setdefault("width", 30)
        super().__init__(parent, *args, **kwargs)

class StyledFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        kwargs.setdefault("bg", parent.cget("bg"))
        super().__init__(parent, *args, **kwargs)
