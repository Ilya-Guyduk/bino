import os
import sys
import importlib
import tkinter as tk
from tkinter import messagebox


class EndpointBackend:
    """Класс для работы с эндпоинтами и коннекторами."""
    def __init__(self, app):
        self.app = app
        self.storage = self.app.storage
        self.connectors = self.load_connectors()

    def load_connectors(self):
        """Загружает все коннекторы из каталога 'connectors'."""

        if getattr(sys, 'frozen', False):
            # Если запущено из .exe
            base_path = sys._MEIPASS
            con_path = "connectors"
        else:
            # Если обычный запуск из .py
            base_path = os.path.dirname(__file__)
            con_path = "../connectors"
        connectors = {}
        connectors_dir = os.path.join(base_path, con_path)

        for file in os.listdir(connectors_dir):
            if file.endswith('.py') and file != '__init__.py':
                module_name = file[:-3]
                module = importlib.import_module(f'connectors.{module_name}')
                connector_class = getattr(module, module_name.capitalize() + 'Connector', None)
                if connector_class:
                    connectors[module_name] = connector_class()
        return connectors

    def test_connection(self):
        """Проверка соединения с эндпоинтом с потоковым выводом статуса."""

        #selected = self.app.endpoints_manager.listbox.curselection()
        #if not selected:
        #    messagebox.showwarning("Ошибка", "Выберите эндпоинт для тестирования.")
        #    return

        name = self.app.endpoints_manager.view.name_entry.get()
        endpoint = self.app.endpoints_manager.model.read(name)

        if not endpoint:
            messagebox.showerror("Ошибка", "Не найдено данных для эндпоинта.")
            return

        connector = self.connectors.get(endpoint.type_)
        if not connector:
            messagebox.showerror("Ошибка", f"Неизвестный тип соединения: {endpoint.type_}")
            return

        required_fields = connector.get_required_fields()
        missing_fields = [field for field in required_fields if field not in endpoint._attributes]
        if missing_fields:
            messagebox.showerror("Ошибка", f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")
            return

        self.app.endpoints_manager.view.create_test_connection_window(connector, endpoint)
