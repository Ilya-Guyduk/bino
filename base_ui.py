import tkinter as tk

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

    def create_buttons(self, container, buttons_data):
        """
        Создаёт кнопки на основе переданного списка.
        
        :param container: Родительский виджет для кнопок
        :param buttons_data: Список кортежей (Название, Функция)
        """
        buttons_frame = tk.Frame(container)
        buttons_frame.grid(row=0, column=1, sticky="ne")

        def on_enter(e):
            e.widget.config(bg="gray80")

        def on_leave(e):
            e.widget.config(bg="SystemButtonFace")

        buttons = []
        for text, command in buttons_data:
            btn = tk.Button(buttons_frame, text=text, font=("Silkscreen", 9), command=command)
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            buttons.append(btn)

        return buttons
        """Создаёт кнопки на основе переданного списка buttons_info."""
        buttons_frame = tk.Frame(container)
        buttons_frame.grid(row=0, column=1, sticky="ne")

        def on_enter(e):
            e.widget.config(bg="gray80")

        def on_leave(e):
            e.widget.config(bg="SystemButtonFace")

        buttons = []
        for text, command in buttons_info:
            btn = tk.Button(buttons_frame, text=text, font=("Silkscreen", 9), command=command)
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            buttons.append(btn)

        return buttons