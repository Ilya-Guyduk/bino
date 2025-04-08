import os
import importlib
import paramiko
import threading
import tkinter as tk
from tkinter import messagebox
from storage import save_data
from interpreters.python import PythonInterpreter
from interpreters.bash import BashInterpreter
from theme import StyledButton, StyledLabel, StyledEntry, StyledCheckbutton, StyledCombobox, StyledFrame


class FormHandler:
    def __init__(self, ui, backend):
        self.ui = ui
        self.backend = backend

    def create_frame(self, create_fields_func, **item_data):
        self.backend.clear_content_frame()
        container, frame = self.ui.create_form_container()
        create_fields_func(frame, **item_data)
        return container, frame

    def create_button_frame(self, data_type, container, save_func, delete_func=None):

        button_container = StyledFrame(container)
        button_container.grid(row=0, column=1, sticky="ne")

        save_btn = StyledButton(button_container, text="💾 Save", command=save_func)
        save_btn.pack(fill="x", pady=(2, 0))
        cancel_btn = StyledButton(button_container, text="⬅️ Cancel", command=self.backend.clear_content_frame)
        cancel_btn.pack(fill="x", pady=(2, 0))

        if data_type == "scripts":
            run_btn = StyledButton(button_container, text="🚀 Start", command=self.run_script)
            run_btn.pack(fill="x", pady=(2, 0))
        elif data_type == "endpoints":
            test_btn = StyledButton(button_container, text="🚀 Test", command=self.test_connection)
            test_btn.pack(fill="x", pady=(2, 0))

        opt_btn = StyledButton(button_container, text="⚙️ Options", command=lambda: self.ui.open_options_window(data_type))
        opt_btn.pack(fill="x", pady=(2, 0))

        if delete_func:
            del_btn = StyledButton(button_container, text="❌ Delete", command=lambda: delete_func(self.ui))
            del_btn.pack(fill="x", pady=(2, 0))

        return save_btn, button_container


    def create_form_and_save(self, data_type, create_fields_func, save_func):
        """Создает форму и обрабатывает сохранение данных для скрипта или эндпоинта."""

        container, frame = self.create_frame(create_fields_func)

        def save():
            """Обработка сохранения данных."""
            data = self.collect_data(data_type)  # Собираем данные
            success, message = save_func(self.ui,"",data)  # Вызываем соответствующий метод сохранения

            if success:
                save_btn.config(text="Saved", font=("Silkscreen", 9), bg="gray80")
                StyledButton(button_container, text="❌ Delete", command=lambda: self.backend.delete(data_type, self.ui))
                save_btn.after(2000, lambda: save_btn.config(text="Save"))
                messagebox.showwarning("Заебок!", message)
            else:
                messagebox.showwarning("Ошибка", message)

        # Создание кнопок
        save_btn, button_container = self.create_button_frame(data_type, container, save)

        self.create_code_field() if data_type == "scripts" else None

    def collect_data(self, data_type):
        """Собирает данные в зависимости от типа (скрипт или эндпоинт)."""
        if data_type == "scripts":
            return {
                "name": self.name_entry.get(),
                "interpreter": self.interpreter_entry.get(),
                "endpoint": self.endpoint_var.get(),
                "code": self.script_text.get("1.0", tk.END)
            }
        elif data_type == "endpoints":
            connection_type = self.connection_var.get()
            return {
                "name": self.name_entry.get(),
                "type": connection_type,
                **{field: getattr(self, f"{field.lower()}_entry").get() for field in self.connectors[connection_type].get_required_fields()}
            }
    
    def display_and_edit(self, data_type, create_fields_func, save_func, delete_func, open_options_func, additional_fields_func=None):
        """Отображение и редактирование данных для скрипта или эндпоинта."""

        selected = self.ui.listbox.curselection()
        if selected:
            name = self.ui.listbox.get(selected[0])
            item_data = self.app.data[data_type][name]

            container, frame = self.create_frame(create_fields_func, **item_data)
            if data_type == "scripts":
                self.create_code_field(item_data.get("code", ""))
                self.add_syntax_highlighting(self.script_text, item_data.get("code", ""), item_data.get("interpreter", ""))

            def save_changes():
                """Обработка сохранения изменений."""
                new_name = self.name_entry.get()
                old_name = name

                data = self.collect_data(data_type)
                success, message = save_func(self.ui, name, data)
                # Собираем данные для сохранения
                if success:
                    save_btn.config(text="Saved", bg="gray80")
                    save_btn.after(2000, lambda: save_btn.config(text="Save"))
                    messagebox.showwarning("Заебок!", message)
                else:
                    messagebox.showwarning("Ошибка", message)

            # Создание кнопок
            save_btn, button_container = self.create_button_frame(data_type, container, save_changes, delete_func)
            





class EndpointBackend:
    """Класс для работы с эндпоинтами и коннекторами."""
    
    def __init__(self, app):
        self.app = app

        self.connectors = self.load_connectors()

    def load_existing_data(self, ui):
        """docstring"""
        for endpoint in self.app.data["endpoints"]:
            ui.listbox.insert(tk.END, endpoint)

    def clear_content_frame(self):
        """Очистка основного контентного фрейма."""
        for widget in self.app.content_frame.winfo_children():
            widget.destroy()

    def load_connectors(self):
        """Загружает все коннекторы из каталога 'connectors'."""
        connectors = {}
        connectors_dir = os.path.join(os.path.dirname(__file__), 'connectors')

        for file in os.listdir(connectors_dir):
            if file.endswith('.py') and file != '__init__.py':
                module_name = file[:-3]
                module = importlib.import_module(f'connectors.{module_name}')
                connector_class = getattr(module, module_name.capitalize() + 'Connector', None)
                if connector_class:
                    connectors[module_name] = connector_class()
        return connectors

    def test_connection(self, endpoint_name, endpoint_data):
        """Проверяет соединение с эндпоинтом."""
        connection_type = endpoint_data["type"]
        connector = self.connectors.get(connection_type)
        if not connector:
            return False, f"Неизвестный тип соединения: {connection_type}"

        required_fields = connector.get_required_fields()
        missing_fields = [field for field in required_fields if field not in endpoint_data]
        if missing_fields:
            return False, f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
        
        try:
            success, test_result = connector.test_connection(endpoint_data)
            return success, test_result
        except Exception as e:
            return False, f"Ошибка: {e}"

    def save_object(self, ui, old_name, endpoint_data):
        """Сохраняет новый или отредактированный эндпоинт."""

        new_name = endpoint_data.get("name")
        if not new_name:
            return False, "Имя не может быть пустым."

        endpoints = self.app.data["endpoints"]
        list_items = ui.listbox.get(0, tk.END)

        # Обновление существующего
        if old_name:
            if old_name != new_name:
                if new_name in endpoints:
                    return False, f"Эндпоинт с именем '{new_name}' уже существует."
                if old_name in endpoints:
                    del endpoints[old_name]
                endpoints[new_name] = endpoint_data

                if old_name in list_items:
                    index = list_items.index(old_name)
                    ui.listbox.delete(index)
                    ui.listbox.insert(index, new_name)
            else:
                endpoints[new_name] = endpoint_data
            save_data(self.app.data)
            return True, f"Эндпоинт '{new_name}' успешно сохранён."

        # Добавление нового
        if new_name not in endpoints:
            endpoints[new_name] = endpoint_data
            ui.listbox.insert(tk.END, new_name)
            save_data(self.app.data)
            return True, f"Эндпоинт '{new_name}' успешно добавлен."

        return False, f"Эндпоинт с именем '{new_name}' уже существует."



    def delete_endpoint(self, ui):
        """Удаляет эндпоинт."""
        selected = ui.listbox.curselection()
        if not selected:
            return False, "Пожалуйста, выберите эндпоинт для удаления."

        endpoint_name = ui.listbox.get(selected[0])

        if endpoint_name in self.app.data["endpoints"]:
            del self.app.data["endpoints"][endpoint_name]
            ui.listbox.delete(selected[0])
            save_data(self.app.data)
            return True, f"Эндпоинт '{endpoint_name}' был успешно удалён."
        else:
            return False, f"Эндпоинт '{endpoint_name}' не найден."

class ScriptBackend:
    def __init__(self, app):
        self.app = app
        self.interpreters = {
            "python": PythonInterpreter(),
            "bash": BashInterpreter()
        }

    def load_existing_data(self, ui):
        """Загружает уже существующие скрипты в UI."""
        for script in self.app.data["scripts"]:
            ui.listbox.insert(tk.END, script)

    def clear_content_frame(self):
        """Очистка основного контентного фрейма."""
        for widget in self.app.content_frame.winfo_children():
            widget.destroy()

    def delete_script(self, ui):
        """Удаляет выбранный скрипт."""
        selected = ui.listbox.curselection()
        if not selected:
            return False, "Пожалуйста, выберите скрипт для удаления."

        script_name = ui.listbox.get(selected[0])

        if script_name in self.app.data["scripts"]:
            del self.app.data["scripts"][script_name]
            ui.listbox.delete(selected[0])
            save_data(self.app.data)
            return True, f"Скрипт '{script_name}' был успешно удалён."
        else:
            return False, f"Скрипт '{script_name}' не найден."

    def run_script(self, ui, script_data, endpoint_data):
        """Запускает скрипт на удалённом сервере по SSH с потоковым выводом и статусом подключения."""
        hostname = endpoint_data["ip"]
        port = int(endpoint_data["port"])
        username = endpoint_data["login"]
        password = endpoint_data["password"]
        interpreter_name = script_data["interpreter"]
        script_code = script_data["code"]
        options = script_data["options"]

        def update_output(text):
            """Добавляет текст в окно с результатом."""
            ui.text_widget.config(state="normal")
            ui.text_widget.insert("end", text)
            ui.text_widget.see("end")
            ui.text_widget.config(state="disabled")

        def animate_spinner(angle=0):
            """Анимация вращающегося значка."""
            ui.status_icon.delete("all")
            x0, y0, x1, y1 = 5, 5, 15, 15
            ui.status_icon.create_arc(x0, y0, x1, y1, start=angle, extent=270, outline="black", width=2)
            if ui.status_label["text"] == "Connecting...":
                self.app.root.after(100, animate_spinner, (angle + 30) % 360)

        def execute_script():
            """Функция для выполнения скрипта и обновления статуса."""
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname, port=port, username=username, password=password)

                # Статус подключения
                self.app.root.after(0, lambda: ui.status_label.config(text="Connected"))
                self.app.root.after(0, lambda: ui.status_icon.delete("all"))
                self.app.root.after(0, lambda: ui.status_icon.create_text(10, 10, text="✔", font=("Arial", 14), fill="green"))

                if interpreter_name in self.interpreters:
                    interpreter = self.interpreters[interpreter_name]
                    command = interpreter.format_command(script_code, options)
                else:
                    command = script_code

                stdin, stdout, stderr = ssh_client.exec_command(command)
                for line in iter(stdout.readline, ""):
                    self.app.root.after(0, update_output, line)
                for line in iter(stderr.readline, ""):
                    self.app.root.after(0, update_output, f"[Ошибка] {line}")

                ssh_client.close()

            except Exception as e:
                self.app.root.after(0, update_output, f"Ошибка: {e}")

        # Запуск индикатора загрузки
        animate_spinner()
        threading.Thread(target=execute_script, daemon=True).start()

    def save_object(self, ui, name, script_data):
        """Создание нового скрипта."""
        name = script_data.get("name")
        interpreter_name = script_data.get("interpreter")
        endpoint_name = script_data.get("endpoint")

        if name and name not in self.app.data["scripts"]:
            self.app.data["scripts"][name] = {
                "name": name,
                "interpreter": interpreter_name,
                "endpoint": endpoint_name,
                "code": script_data["code"],
                "options": self.interpreters[interpreter_name].available_options
            }
            ui.listbox.insert(tk.END, name)
            save_data(self.app.data)
            return True, f"Скрипт '{name}' успешно сохранён."
        return False, f"Скрипт с именем '{name}' уже существует."

    def update_script(self, ui, old_name, new_name, script_data):
        """Обновляет существующий скрипт."""
        if new_name != old_name:
            if new_name in self.app.data["scripts"]:
                return False, f"Скрипт с таким именем уже существует."
            self.app.data["scripts"][new_name] = self.app.data["scripts"].pop(old_name)
            ui.listbox.delete(ui.listbox.get(0, tk.END).index(old_name))
            ui.listbox.insert(ui.listbox.get(0, tk.END).index(old_name), new_name)

        self.app.data["scripts"][new_name] = {
            "interpreter": script_data["interpreter"],
            "endpoint": script_data["endpoint"],
            "code": script_data["code"],
            "options": self.interpreters[script_data["interpreter"]].available_options
        }
        save_data(self.app.data)
        return True, f"Скрипт '{new_name}' успешно обновлён."
