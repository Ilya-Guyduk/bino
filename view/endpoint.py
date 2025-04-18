"""docstring"""

import tkinter as tk

from model.endpoint import Endpoint
from view.theme import StyledLabel, StyledEntry, StyledCombobox, StyledFrame

class EndpointUI:
    """docstring"""
    def __init__(self, app, backend):
        self.app = app
        self.backend = backend
        self.name_entry = None
        self.connection_var = None
        self.connector_frame = None
        self.connectors = {0:0}



    def create_fields(self, frame, endpoint: Endpoint):
        """Добавляет поля формы для создания или редактирования эндпоинта."""

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
        def update_fields():
            self._update_fields(endpoint)

        self.connection_var.trace_add("write", update_fields)

    def _update_fields(self, endpoint):
        """Обновляет поля в зависимости от выбранного коннектора."""
        connector = self.backend.connectors.get(endpoint.type_)
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
                    entry.insert(0, getattr(endpoint, field.lower(), ""))
                    entry.pack(anchor="w", padx=5, pady=(0, 0))
                    setattr(self, f"{field.lower()}_entry", entry)

                else:
                    entry = StyledEntry(self.connector_frame)
                    entry.insert(0, getattr(endpoint, field.lower(), ""))
                    entry.pack(anchor="w", padx=5, pady=(0, 0))
                    setattr(self, f"{field.lower()}_entry", entry)
