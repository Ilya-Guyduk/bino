import os
import sys
import importlib

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
