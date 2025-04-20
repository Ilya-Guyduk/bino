
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any

#from model.endpoint import Script, Endpoint
from view.theme import StyledButton, StyledFrame, StyledFrameWithLogo, StyledLabel, StyledEntry, StyledCheckbutton
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
        """Открывает окно настроек (options) для текущего объекта."""
        name = self.data_model.name
        options_window = tk.Toplevel()
        options_window.title(f"Options {name}")

        frame = StyledFrameWithLogo(parent=options_window)
        frame.pack(fill="x", padx=0, pady=0)
        frame.columnconfigure(0, weight=1)

        # Получаем опции
        available_options = self._get_option_source()
        options_vars = self.view.render_option_fields(frame.frame, available_options)

        # Добавляем кнопку сохранения
        self.view.render_save_button(frame.frame, options_vars, options_window)

    def _get_option_source(self):
        """Возвращает ключ типа (интерпретатор/endpoint) и его доступные опции."""
        if self._type == "endpoints":
            ch_type = self.data_model.type_
            return self.controller.connectors[ch_type].available_options
        elif self._type == "scripts":
            ch_type = self.data_model.interpreter
            return self.controller.interpreters[ch_type].available_options
        else:
            return {}

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
            data = self.view.get_data()  # Собираем данные
            self.data_model = self.model.from_dict(self.app.storage, data)
            success, message = self.data_model.create()  # Вызываем соответствующий метод сохранения

            if success:
                save_btn.config(text="Saved", font=("Silkscreen", 9), bg="gray80")
                delete_btn = StyledButton(button_container, text="❌ Delete", command=self.data_model.delete)
                delete_btn.pack(fill="x", pady=(2, 0))
                self.listbox.insert(0, data["name"])
                save_btn.after(2000, lambda: save_btn.config(text="Save"))
                messagebox.showwarning("Заебок!", message)
            else:
                messagebox.showwarning("Ошибка", message)

        # Создание кнопок
        save_btn, button_container = self.create_button_frame(container, save)

    def display_and_edit(self, _event) -> None:
        """Отображение и редактирование данных для скрипта или эндпоинта."""

        selected_index = self.listbox.curselection()
        if selected_index:
            name = self.listbox.get(selected_index[0])

            self.data_model = self.model.read(name)
            container, _ = self.create_frame()

            def save_changes():
                """Обработка сохранения изменений."""
                new_name = self.view.name_entry.get()
                old_name = name
                data = self.view.get_data()
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
