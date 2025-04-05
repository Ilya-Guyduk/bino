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
from theme import StyledButton, StyledLabel, StyledEntry, StyledCheckbutton, StyledCombobox, StyledFrame
from backend import EndpointBackend, FormHandler

class EndpointManager(FormHandler):
    """docstring"""
    def __init__(self, app):
        self.app = app
        self.ui = BaseUI(app)
        self.backend = EndpointBackend(app)
        self.connectors = self.backend.load_connectors()
        self.listbox = self.ui.setup_listbox(self.app.endpoints_frame, self.display_endpoint, self.add_endpoint)
        self.backend.load_existing_data(self.ui)
        super().__init__(self.ui, self.backend)

    def test_connection(self):
        """Проверка соединения с эндпоинтом с потоковым выводом статуса."""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите эндпоинт для тестирования.")
            return

        endpoint_name = self.listbox.get(selected[0])
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

        close_button = StyledButton(result_window, text="Закрыть", command=result_window.destroy)
        close_button.pack(pady=5)

        status_frame = StyledFrame(result_window)
        status_frame.pack(pady=5)

        status_label = StyledLabel(status_frame, text="Connecting...")
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


    def create_endpoint_fields(self, frame, name="", type="ssh", **endpoint_data):
        """Добавляет поля формы для создания или редактирования эндпоинта."""

        name_label = StyledLabel(frame, text="Name")
        name_label.pack(anchor="w", padx=4, pady=(0, 0))

        self.name_entry = StyledEntry(frame)
        self.name_entry.insert(0, name)
        self.name_entry.pack(anchor="w", padx=5, pady=(0, 0))

        name_label = StyledLabel(frame, text="Type")
        name_label.pack(anchor="w", padx=4, pady=(0, 0))
        connection_types = list(self.connectors.keys())
        self.connection_var = tk.StringVar(value=type)
        connection_dropdown = StyledCombobox(frame, textvariable=self.connection_var, values=connection_types)
        connection_dropdown.pack(anchor="w", padx=5, pady=(0, 0))

        # Создаём фрейм для выбранного коннектора
        self.connector_frame = StyledFrame(frame)
        self.connector_frame.pack(anchor="w", padx=(0, 0), pady=(0, 10))

        self._update_fields(type, endpoint_data)

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
                name_label = StyledLabel(self.connector_frame, text=field)
                name_label.pack(anchor="w", padx=4, pady=(0, 0))
                if field.lower() == "password":
                    entry = StyledEntry(self.connector_frame, show="*")
                    entry.insert(0, endpoint_data.get(field.lower(), ""))
                    entry.pack(anchor="w", padx=5, pady=(0, 0))

                else:
                    entry = StyledEntry(self.connector_frame)
                    entry.insert(0, endpoint_data.get(field.lower(), ""))
                    entry.pack(anchor="w", padx=5, pady=(0, 0))
                
                setattr(self, f"{field.lower()}_entry", entry)


    def add_endpoint(self):
        """Добавляет новый эндпоинт."""
        self.create_form_and_save("endpoints", self.create_endpoint_fields, self.backend.save_endpoint)

    def display_endpoint(self, event):
        """Отображение информации о выбранном эндпоинте."""
        self.display_and_edit(
            "endpoints", 
            self.create_endpoint_fields, 
            self.backend.save_endpoint, 
            self.backend.delete_endpoint, 
            self.ui.open_options_window,
            self.update_endpoint_fields
        )

    def update_endpoint_fields(self, endpoint_data, key):
        """Обновление специфичных для эндпоинтов полей."""
        if key == "type":
            endpoint_data[key] = self.connection_var.get()
        elif key != "type":
            # Обновляем поля, связанные с конкретным типом соединения
            connector = self.connectors.get(endpoint_data["type"])
            if connector:
                endpoint_data[key] = getattr(self, f"{key.lower()}_entry").get()