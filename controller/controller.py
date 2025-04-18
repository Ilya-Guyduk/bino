
import tkinter as tk
from tkinter import messagebox

#from model.endpoint import Script, Endpoint
from view.theme import StyledButton, StyledFrame, StyledFrameWithLogo, StyledLabel
from model.script import Script
from model.endpoint import Endpoint
from view.script import ScriptUI
from view.endpoint import EndpointUI
from controller.script import ScriptBackend
from controller.endpoint import EndpointBackend



class FormHandler:
    """docstring"""
    def __init__(self, app, obj_type):
        self.app = app
        self._type = obj_type

        self.data_model = None

        self.controller = self._set_controller()
        self.view = self._set_view()
        self.model = self._set_model()

        self.listbox = self._setup_listbox()
        self.load_existing_data()
        print(f"<Create {self._type} handler>")

    def _set_view(self):
        """docstring"""
        if self._type == "scripts":
            return ScriptUI(self.app)
        if self._type == "endpoints":
            return EndpointUI(self.app, self.controller)
        else:
            print("неизвестный тип ui")

    def _set_model(self):
        """docstring"""
        if self._type == "scripts":
            return Script(storage=self.app.storage)
        if self._type == "endpoints":
            return Endpoint(storage=self.app.storage)
        else:
            print("неизвестный тип obj_type")

    def _set_controller(self):
        if self._type == "scripts":
            return ScriptBackend(self.app)
        if self._type == "endpoints":
            return EndpointBackend(self.app)
        else:
            print("неизвестный тип obj_type")

    def _setup_listbox(self):
        """Создает листбокс и кнопку"""
        if self._type == "scripts":
            container = self.app.scripts_frame
        elif self._type == "endpoints":
            container = self.app.endpoints_frame
        else:
            print("неизвестный тип obj_type")
            return
        self.listbox = tk.Listbox(container, selectbackground="#f37600", selectforeground="black")
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.display_and_edit)
        self.add_button = StyledButton(container, text="➕ Add", command=self.create_form_and_save)
        self.add_button.pack(fill=tk.X)
        return self.listbox

    def clear_content_frame(self):
        """Очистка основного контентного фрейма."""
        for widget in self.app.content_frame.winfo_children():
            widget.destroy()

    def load_existing_data(self):
        """Загружает уже существующие скрипты в UI."""
        for obj in self.app.data[self._type]:
            self.listbox.insert(tk.END, obj)

    def open_options_window(self):
        """Открывает окно для выбора опций эндпоинта или скрипта."""
        name = self.data_model.name

        options_window = tk.Toplevel()
        options_window.title(f"Options {name}")
        frame = StyledFrameWithLogo(parent=options_window)
        frame.pack(fill="x", padx=(0, 0), pady=(0, 0))
        frame.columnconfigure(0, weight=1)

        #container, frame = self.create_frame(parent=options_window)
        #frame.grid(padx=4, pady=4)


        # Определяем, какой тип данных мы обрабатываем (эндпоинт или скрипт)
        if self._type == "endpoints":
            ch_type = self.data_model.type_
            point_data = self.controller.connectors
        elif self._type == "scripts":
            ch_type = self.data_model.interpreter
            point_data = self.controller.interpreters
        else:
            return

        options_vars = {}

        # Перебираем все опции для выбранного типа (ендпоинт или интерпретатор)
        for i, (option, details) in enumerate(point_data[ch_type].available_options.items()):
            opt_type = details["type"]
            opt_desc = details["description"]
            opt_value = self.data_model.options

            # В зависимости от типа опции создаём виджет для неё
            if opt_type == bool:
                var = tk.BooleanVar(value=opt_value)
                chk = tk.Checkbutton(frame, text=f"{option} - {opt_desc}", variable=var, bg=frame.cget("bg"))
                chk = self.create_checkbutton(frame, text=f"{option} - {opt_desc}", variable=var)
            elif opt_type == int:
                var = tk.IntVar(value=opt_value)
                label = StyledLabel(frame, text=f"{option} - {opt_desc}")
                label.pack(anchor="w")
                entry = self.create_entry(frame, name="", textvariable=var)  # Привязываем переменную к Entry
                entry.pack(anchor="w")
            elif opt_type == str:
                var = tk.StringVar(value=opt_value)
                label = StyledLabel(frame, text=f"{option} - {opt_desc}")
                label.pack(anchor="w")
                entry = self.create_entry(frame, name="", textvariable=var)  # Привязываем переменную к Entry
                entry.pack(anchor="w")
            else:
                continue  # Если тип не поддерживается, пропускаем его

            # Сохраняем переменную в словарь для дальнейшего использования
            options_vars[option] = var

        def save_options():
            # Сохраняем изменения
            if "options" not in self.data_model:
                self.data_model.options = {}
            for opt, var in options_vars.items():
                parent_data["options"][opt] = var.get()
            save_data(self.app.data)
            options_window.destroy()

        button_container = self.buttons_frame(frame.container)
        button_container.grid(padx=(0, 4))
        save_btn = StyledButton(button_container, text="Save", command=save_options)
        save_btn.grid(row=len(options_vars), column=0, pady=10)  # Сохраняем кнопку в grid

    def create_frame(self, parent=None, model=None):
        """docstring"""
        if parent is None:
            parent = self.app.content_frame
        if model is None:
            model = self.data_model

        self.clear_content_frame()
        frame = StyledFrameWithLogo(parent=parent)
        frame.pack(fill="x", padx=(0, 0), pady=(0, 0))
        frame.columnconfigure(0, weight=1)
        self.view.create_fields(frame.frame, model)
        return frame.container, frame.frame

    def create_button_frame(self, container, save_func, delete_func=None):
        """docstring"""
        button_container = StyledFrame(container)
        button_container.grid(row=0, column=1, sticky="ne")

        save_btn = StyledButton(button_container,
                                text="💾 Save",
                                command=save_func)
        save_btn.pack(fill="x", pady=(2, 0))
        self.app.root.bind("<Control-s>", lambda event: save_func())

        cancel_btn = StyledButton(button_container,
                                  text="⬅️ Cancel",
                                  command=self.clear_content_frame)
        cancel_btn.pack(fill="x", pady=(2, 0))
        self.app.root.bind("<Control-q>", lambda event: self.clear_content_frame())

        if self._type == "scripts":
            run_btn = StyledButton(button_container,
                                   text="🚀 Start",
                                   command=self.controller.run_script)
            run_btn.pack(fill="x", pady=(2, 0))
        elif self._type == "endpoints":
            test_btn = StyledButton(button_container,
                                    text="🚀 Test",
                                    command=self.controller.test_connection)
            test_btn.pack(fill="x", pady=(2, 0))

        opt_btn = StyledButton(button_container,
                               text="⚙️ Options",
                               command=self.open_options_window)
        opt_btn.pack(fill="x", pady=(2, 0))

        if delete_func:
            del_btn = StyledButton(button_container, text="❌ Delete", command=delete_func)
            del_btn.pack(fill="x", pady=(2, 0))

        return save_btn, button_container

    def create_form_and_save(self):
        """Создает форму и обрабатывает сохранение данных для скрипта или эндпоинта."""

        model = self.model.empty_model()
        container, _ = self.create_frame(model=model)

        def save():
            """Обработка сохранения данных."""
            data = self.collect_data(self._type)  # Собираем данные
            self.data_model = self.model.from_dict(self.app.storage, data)
            success, message = self.data_model.create()  # Вызываем соответствующий метод сохранения

            if success:
                save_btn.config(text="Saved", font=("Silkscreen", 9), bg="gray80")
                StyledButton(button_container, text="❌ Delete", command=self.data_model.delete)
                self.listbox.insert(0, data["name"])
                save_btn.after(2000, lambda: save_btn.config(text="Save"))
                messagebox.showwarning("Заебок!", message)
            else:
                messagebox.showwarning("Ошибка", message)

        # Создание кнопок
        save_btn, button_container = self.create_button_frame(container, save)


    def collect_data(self, data_type):
        """Собирает данные в зависимости от типа (скрипт или эндпоинт)."""
        if data_type == "scripts":
            return {
                "name": self.view.name_entry.get(),
                "interpreter": self.view.interpreter_entry.get(),
                "endpoint": self.view.endpoint_var.get(),
                "code": self.view.script_text.get("1.0", tk.END)
            }
        elif data_type == "endpoints":
            connection_type = self.view.connection_var.get()
            return {
                "name": self.view.name_entry.get(),
                "type": connection_type,
                **{field: getattr(self, f"{field.lower()}_entry").get() for field in self.view.connectors[connection_type].get_required_fields()}
            }

    def display_and_edit(self, _event):
        """Отображение и редактирование данных для скрипта или эндпоинта."""

        selected = self.listbox.curselection()
        if selected:
            name = self.listbox.get(selected[0])

            self.data_model = self.model.read(name)
            print(self.data_model)
            container, _ = self.create_frame()

            def save_changes():
                """Обработка сохранения изменений."""
                new_name = self.view.name_entry.get()
                old_name = name
                data = self.collect_data(self._type)
                success, message = self.data_model.update(old_name, new_name, data)
                # Собираем данные для сохранения
                if success:
                    list_items = self.listbox.get(0, tk.END)
                    index = list_items.index(old_name)
                    self.listbox.delete(index)
                    self.listbox.insert(index, new_name)

                    save_btn.config(text="Saved", bg="gray80")
                    save_btn.after(2000, lambda: save_btn.config(text="💾 Save"))
                    messagebox.showwarning("Заебок!", message)
                else:
                    messagebox.showwarning("Ошибка", message)

            def delete():
                success, message = self.data_model.delete()
                if success:
                    list_items = self.listbox.get(0, tk.END)
                    index = list_items.index(name)
                    self.listbox.delete(index)
                    messagebox.showwarning("Заебок!", message)
                    self.clear_content_frame()
                else:
                    messagebox.showwarning("Ошибка", message)

            # Создание кнопок
            save_btn, _ = self.create_button_frame(container, save_changes, delete)
