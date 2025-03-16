import tkinter as tk
from interpreters.python import PythonInterpreter
from interpreters.bash import BashInterpreter

class BaseUI:
    def __init__(self, app):
        self.app = app
        

    def create_form_container(self):
        """Создаёт контейнер и рамку формы"""
        container = tk.Frame(self.app.content_frame)
        container.pack(fill="x", padx=7, pady=(0, 5))
        container.columnconfigure(0, weight=1)

        frame = tk.Frame(container, relief="groove", borderwidth=2, bg="#C0C0C0")
        frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        logo_label = tk.Label(frame, text=self.app.BINO_LOGO, font=("Courier", 10, "bold"), bg="#C0C0C0", anchor="e")
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