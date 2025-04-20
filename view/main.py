import tkinter as tk
from view.theme import StyledButton, StyledFrame, StyledFrameWithLogo, StyledLabel, StyledEntry, StyledCheckbutton

class MainUI:
    def __init__(self):
        self.model = None


    def render_option_fields(self, container, available_options):
        """Создает UI элементы для опций и возвращает связанные переменные."""
        options_vars = {}
        for option, details in available_options.items():
            opt_type = details["type"]
            opt_desc = details["description"]
            opt_value = self.model.options.get(option, details.get("value"))

            var = None
            if opt_type == bool:
                var = tk.BooleanVar(value=opt_value)
                chk = StyledCheckbutton(container, text=f"{option} - {opt_desc}", variable=var)
                chk.pack(anchor="w", padx=5, pady=2)

            elif opt_type in (int, str):
                var = tk.IntVar(value=opt_value) if opt_type == int else tk.StringVar(value=opt_value)
                label = StyledLabel(container, text=f"{option} - {opt_desc}")
                label.pack(anchor="w", padx=5, pady=0)
                entry = StyledEntry(container, textvariable=var)
                entry.pack(anchor="w", padx=5, pady=2)

            if var is not None:
                options_vars[option] = var

        return options_vars

    def render_save_button(self, container, options_vars, window):
        """Добавляет кнопку сохранения опций."""
        button_container = StyledFrame(container)
        button_container.pack(anchor="e", padx=10, pady=10)

        def save_options():
            if not self.model.options:
                self.model.options = {}
            for opt, var in options_vars.items():
                self.model.options[opt] = var.get()
                data = self.model.to_dict()
            self.model.update(self.model.name, self.model.name, data)
            window.destroy()

        save_btn = StyledButton(button_container, text="Save", command=save_options)
        save_btn.grid(row=0, column=0, pady=10)
