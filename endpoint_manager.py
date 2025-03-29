"""docstring"""

import tkinter as tk
import threading
from tkinter import ttk
import tkinter.messagebox as messagebox
import paramiko
import os
import importlib

from storage import save_data
from base_ui import BaseUI
from config import FEATURE_FLAGS

class EndpointManager:
    """docstring"""
    def __init__(self, app):
        self.app = app
        self.ui = BaseUI(app)
        self.connectors = self.load_connectors()

        self.listbox = self.ui.setup_listbox(self.app.endpoints_frame, self.display_endpoint, self.add_endpoint)
        self.load_existing_data()

    def load_connectors(self):
        """Загружает все коннекторы из каталога 'connectors'."""
        connectors = {}
        connectors_dir = os.path.join(os.path.dirname(__file__), 'connectors')

        for file in os.listdir(connectors_dir):
            if file.endswith('.py') and file != '__init__.py':
                module_name = file[:-3]
                module = importlib.import_module(f'connectors.{module_name}')
                # Пытаемся получить класс коннектора по имени файла
                connector_class = getattr(module, module_name.capitalize() + 'Connector', None)
                if connector_class:
                    connectors[module_name] = connector_class()
        return connectors

    def test_connection(self):
        """Проверка соединения с эндпоинтом с потоковым выводом статуса."""
        selected = self.ui.listbox.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите эндпоинт для тестирования.")
            return

        endpoint_name = self.ui.listbox.get(selected[0])
        endpoint_data = self.app.data["endpoints"].get(endpoint_name)
        if not endpoint_data:
            messagebox.showerror("Ошибка", "Не найдено данных для эндпоинта.")
            return

        connection_type = endpoint_data["type"]
        connector = self.connectors.get(connection_type)
        if not connector:
            messagebox.showerror("Ошибка", f"Неизвестный тип соединения: {connection_type}")
            return

        required_fields = connector.get_required_fields()
        missing_fields = [field for field in required_fields if field not in endpoint_data]
        if missing_fields:
            messagebox.showerror("Ошибка", f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")
            return

        self._create_test_connection_window(endpoint_name, connector, endpoint_data)

    def _create_test_connection_window(self, endpoint_name, connector, endpoint_data):
        """Создаёт окно для отображения статуса подключения."""
        result_window = tk.Toplevel()
        result_window.title(f"Test '{endpoint_name}' connection")

        text_widget = tk.Text(result_window, wrap="word", height=10, width=50)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.config(state="disabled")

        close_button = tk.Button(result_window, text="Закрыть", command=result_window.destroy)
        close_button.pack(pady=5)

        status_frame = tk.Frame(result_window)
        status_frame.pack(pady=5)

        status_label = tk.Label(status_frame, text="Connecting...", font=("Silkscreen", 9))
        status_label.pack(side="left")

        status_icon = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
        status_icon.pack(side="left", padx=5)

        def update_output(text):
            """Обновляет вывод в текстовом поле."""
            text_widget.config(state="normal")
            text_widget.insert("end", text + "\n")
            text_widget.see("end")
            text_widget.config(state="disabled")

        def animate_spinner(angle=0):
            """Анимация спиннера в процессе подключения."""
            status_icon.delete("all")
            x0, y0, x1, y1 = 5, 5, 15, 15
            status_icon.create_arc(x0, y0, x1, y1, start=angle, extent=270, outline="black", width=2)
            if status_label["text"] == "Connecting...":
                self.app.root.after(100, animate_spinner, (angle + 30) % 360)

        def check_connection():
            """Проверяет соединение и выводит результаты в окно."""
            try:
                update_output("Попытка подключения...")  # Стартовый вывод
                success, test_result = connector.test_connection(endpoint_data)
                if success:
                    self.app.root.after(0, lambda: status_label.config(text="Connected"))
                    self.app.root.after(0, lambda: status_icon.delete("all"))
                    self.app.root.after(0, lambda: status_icon.create_text(10, 10, text="✔", font=("Arial", 14), fill="green"))
                    self.app.root.after(0, lambda: update_output("Соединение успешно установлено!"))
                else:
                    self.app.root.after(0, lambda: update_output(test_result))
                    self.app.root.after(0, lambda: status_label.config(text="Failed"))
                    self.app.root.after(0, lambda: status_icon.delete("all"))
                    self.app.root.after(0, lambda: status_icon.create_text(10, 10, text="✖", font=("Arial", 14), fill="red"))
            except Exception as e:
                error_message = f"Ошибка: {e}"
                self.app.root.after(0, lambda: update_output(error_message))
                self.app.root.after(0, lambda: status_label.config(text="Failed"))
                self.app.root.after(0, lambda: status_icon.delete("all"))
                self.app.root.after(0, lambda: status_icon.create_text(10, 10, text="✖", font=("Arial", 14), fill="red"))

        animate_spinner()
        threading.Thread(target=check_connection, daemon=True).start()

    def delete_endpoint(self):
        """Удаляет выбранный скрипт."""
        selected = self.ui.listbox.curselection()
        
        if not selected:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите эндпоинт для удаления.")
            return

        # Получаем имя скрипта, который нужно удалить
        endpoint_name = self.ui.listbox.get(selected[0])
        # Удаляем скрипт из данных
        if endpoint_name in self.app.data["endpoints"]:
            del self.app.data["endpoints"][endpoint_name]
            # Удаляем скрипт из списка в UI
            self.ui.listbox.delete(selected[0])
            # Сохраняем обновлённые данные
            save_data(self.app.data)
            # Очищаем поле с кодом и возвращаем в начальный экран
            self.ui.clear_content_frame()
            messagebox.showinfo("Удалено", f"Скрипт '{endpoint_name}' был успешно удалён.")
        else:
            messagebox.showwarning("Ошибка", f"Скрипт '{endpoint_name}' не найден.")

    def load_existing_data(self):
        """docstring"""
        for endpoint in self.app.data["endpoints"]:
            self.ui.listbox.insert(tk.END, endpoint)

    def create_endpoint_fields(self, frame, name="", conn_type="ssh", endpoint_data=None):
        """Добавляет поля формы для создания или редактирования эндпоинта."""
        self.ui.create_label(frame, "Name")
        self.name_entry = self.ui.create_entry(frame, name)

        self.ui.create_label(frame, "Type")
        connection_types = list(self.connectors.keys())
        self.connection_var = tk.StringVar(value=conn_type)
        connection_dropdown = ttk.Combobox(frame, textvariable=self.connection_var, values=connection_types, width=30)
        connection_dropdown.pack(anchor="w", padx=5, pady=(0, 0))

        # Создаём фрейм для выбранного коннектора
        self.connector_frame = tk.Frame(frame, borderwidth=2, bg=frame.cget('bg'))
        self.connector_frame.pack(anchor="w", padx=(0, 0), pady=(0, 10))

        self._update_fields(conn_type, endpoint_data)

        # Функция переключения фреймов при изменении типа соединения
        def update_fields(*args):
            self._update_fields(self.connection_var.get(), endpoint_data)

        self.connection_var.trace_add("write", update_fields)

    def _update_fields(self, conn_type, endpoint_data):
        """Обновляет поля в зависимости от выбранного коннектора."""
        connector = self.connectors.get(conn_type)
        if connector:
            # Очистка текущих полей
            for widget in self.connector_frame.winfo_children():
                widget.destroy()

            # Создание полей для текущего коннектора
            required_fields = connector.get_required_fields()
            endpoint_data = endpoint_data or {}
            for field in required_fields:
                self.ui.create_label(self.connector_frame, field)
                if field.lower() == "password":
                    entry = self.ui.create_entry(self.connector_frame, endpoint_data.get(field.lower(), ""), show="*")
                else:
                    entry = self.ui.create_entry(self.connector_frame, endpoint_data.get(field.lower(), ""))
                
                setattr(self, f"{field.lower()}_entry", entry)


    def add_endpoint(self):
        """Добавляет новый эндпоинт."""
        self.ui.clear_content_frame()
        container, frame = self.ui.create_form_container()
        self.create_endpoint_fields(frame)

        def save_endpoint():
            name = self.name_entry.get()
            connection_type = self.connection_var.get()

            if not name or not connection_type:
                return  # Не сохраняем, если нет имени или типа подключения

            if name and name not in self.app.data["endpoints"]:
                endpoint_data = {
                    "type": connection_type,
                    **{field: getattr(self, f"{field.lower()}_entry").get() for field in self.connectors[connection_type].get_required_fields()}
                }
                self.app.data["endpoints"][name] = endpoint_data

            self.ui.listbox.insert(tk.END, name)
            save_data(self.app.data)
            save_btn.config(text="Saved", font=("Silkscreen", 9), bg="gray80")
            self.ui.create_button(button_container, "Delete", self.delete_endpoint)
            save_btn.after(2000, lambda: save_btn.config(text="Save"))

        button_container = self.ui.buttons_frame(container)
        save_btn = self.ui.create_button(button_container, "Save", save_endpoint)
        self.ui.create_button(button_container, "Cancel", self.ui.clear_content_frame)
        self.ui.create_button(button_container, "Test", self.test_connection)
        self.ui.create_button(button_container, "Options", self.ui.open_options_window)

    def display_endpoint(self, event):
        """Отображает информацию о выбранном эндпоинте."""
        selected = self.ui.listbox.curselection()
        if selected:
            name = self.ui.listbox.get(selected[0])
            endpoint_data = self.app.data["endpoints"][name]

            self.ui.clear_content_frame()
            container, frame = self.ui.create_form_container()

            self.create_endpoint_fields(frame, name=name, conn_type=endpoint_data["type"], endpoint_data=endpoint_data)

            def save_changes():
                new_name = self.name_entry.get()
                old_name = name
                endpoint_data["type"] = self.connection_var.get()

                if not new_name:
                    messagebox.showwarning("Ошибка", "Имя не может быть пустым.")
                    return

                if new_name != old_name:
                    if new_name in self.app.data["endpoints"]:
                        messagebox.showwarning("Ошибка", "Эндпоинт с таким именем уже существует.")
                        return
                        
                    self.app.data["endpoints"][new_name] = self.app.data["endpoints"].pop(old_name)
                    index = self.ui.listbox.get(0, tk.END).index(old_name)
                    self.ui.listbox.delete(index)
                    self.ui.listbox.insert(index, new_name)

                
                connector = self.connectors.get(endpoint_data["type"])
                if connector:
                    for field in connector.get_required_fields():
                        endpoint_data[field] = getattr(self, f"{field.lower()}_entry").get()
                save_data(self.app.data)
                save_btn.config(text="Saved")
                save_btn.after(2000, lambda: save_btn.config(text="Save"))

            button_container = self.ui.buttons_frame(container)
            save_btn = self.ui.create_button(button_container, "Save", save_changes)
            self.ui.create_button(button_container, "Cancel", self.ui.clear_content_frame)
            self.ui.create_button(button_container, "Test", self.test_connection)
            self.ui.create_button(button_container, "Options", lambda: self.ui.open_options_window(name, "endpoints"))
            self.ui.create_button(button_container, "Delete", self.delete_endpoint)
