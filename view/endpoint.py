"""docstring"""

import tkinter as tk

from model.endpoint import Endpoint
from view.main import MainUI
from view.theme import StyledLabel, StyledEntry, StyledCombobox, StyledFrame, StyledButton
import threading

class EndpointUI(MainUI):
    """docstring"""
    def __init__(self, app, backend):
        self.app = app
        self.backend = backend
        self.model = None
        self.name_entry = None
        self.connection_var = None
        self.connector_frame = None
        self.options = None
        self.connectors = backend.connectors

    def create_fields(self, frame, endpoint: Endpoint):
        """Добавляет поля формы для создания или редактирования эндпоинта."""
        self.model = endpoint
        name_label = StyledLabel(frame, text="Name")
        name_label.pack(anchor="w", padx=4, pady=(0, 0))
        self.name_entry = StyledEntry(frame)
        self.name_entry.insert(0, endpoint.name)
        self.name_entry.pack(anchor="w", padx=5, pady=(0, 0))

        name_label = StyledLabel(frame, text="Type")
        name_label.pack(anchor="w", padx=4, pady=(0, 0))
        connection_types = list(self.connectors.keys())
        self.connection_var = tk.StringVar(value=endpoint.type_)
        connection_dropdown = StyledCombobox(frame,
                                             textvariable=self.connection_var,
                                             values=connection_types)
        connection_dropdown.pack(anchor="w", padx=5, pady=(0, 0))

        # Создаём фрейм для выбранного коннектора
        self.connector_frame = StyledFrame(frame)
        self.connector_frame.pack(anchor="w", padx=(0, 0), pady=(0, 10))

        self._update_fields(endpoint)

        # Функция переключения фреймов при изменении типа соединения
        def update_fields(*args):
            self._update_fields(endpoint)

        self.connection_var.trace_add("write", update_fields)

    def _update_fields(self, endpoint):
        """Обновляет поля в зависимости от выбранного коннектора."""
        connection_type = self.connection_var.get()
        connector = self.backend.connectors.get(connection_type)
        if connector:
            # Очистка текущих полей
            for widget in self.connector_frame.winfo_children():
                widget.destroy()

            # Создание полей для текущего коннектора
            required_fields = connector.get_required_fields()
            for field in required_fields:
                name_label = StyledLabel(self.connector_frame, text=field)
                name_label.pack(anchor="w", padx=4, pady=(0, 0))
                if field.lower() == "password":
                    entry = StyledEntry(self.connector_frame, show="*")
                    value = getattr(endpoint, field.lower(), "")
                    entry.insert(0, str(value) if value is not None else "")
                    entry.pack(anchor="w", padx=5, pady=(0, 0))
                    setattr(self, f"{field.lower()}_entry", entry)

                else:
                    entry = StyledEntry(self.connector_frame)
                    value = getattr(endpoint, field.lower(), "")
                    entry.insert(0, str(value) if value is not None else "")
                    entry.pack(anchor="w", padx=5, pady=(0, 0))
                    setattr(self, f"{field.lower()}_entry", entry)

    def get_data(self) -> dict:
        """
        Собирает и возвращает данные из формы эндпоинта.
        """
        data = {
            "name": self.name_entry.get() if self.name_entry else "",
            "type": self.connection_var.get() if self.connection_var else ""
        }

        # Получаем поля, специфичные для текущего коннектора
        connection_type = self.connection_var.get()
        connector = self.connectors.get(connection_type)
        if connector:
            for field in connector.get_required_fields():
                entry_widget = getattr(self, f"{field.lower()}_entry", None)
                if entry_widget:
                    data[field.lower()] = entry_widget.get()

        return data

    def create_test_connection_window(self, connector, endpoint):
        """Создаёт окно для отображения статуса подключения."""
        result_window = tk.Toplevel()
        result_window.title(f"Test '{endpoint.name}' connection")

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
                data = self.app.endpoints_manager.view.get_data()
                success, test_result = connector.test_connection(data)
                if success:
                    self.app.root.after(0, lambda: status_label.config(text="Connected"))
                    self.app.root.after(0, lambda: status_icon.delete("all"))
                    self.app.root.after(0, lambda: status_icon.create_text(10, 10, text="✔", font=("Arial", 14), fill="green"))
                    self.app.root.after(0, lambda: update_output("Соединение успешно установлено!"))
                else:
                    self.app.root.after(0, lambda: update_output(str(test_result)))
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