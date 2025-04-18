import os
import sys
import importlib

from model.endpoint import Endpoint

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

    def empty_model(self) -> Endpoint:
        """docstring"""
        return Endpoint()

    def read(self, name) -> Endpoint:
        """Чтение данных конкретного эндпоинта."""
        data = self.storage.endpoints.get(name)
        return Endpoint.from_dict(data) if data else None

    def delete(self, name):
        if name in self.storage.endpoints:
            del self.storage.endpoints[name]
            self.storage.save()
            return True, f"Эндпоинт '{name}' удалён."
        return False, "Эндпоинт не найден."