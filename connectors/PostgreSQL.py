import psycopg2
from psycopg2 import OperationalError
from typing import Dict, Any, List
from .base_connector import BaseConnector

class PostgresqlConnector(BaseConnector):
    """
    Реализация коннектора для PostgreSQL.
    """

    def __init__(self) -> None:
        super().__init__()

    def default_options(self) -> Dict[str, Any]:
        """
        Возвращает настройки по умолчанию для PostgreSQL коннектора.
        """
        return {
            "host": "localhost",
            "port": 5432,
            "database": "postgres",
            "user": "postgres",
            "password": "",
        }

    def get_required_fields(self) -> List[str]:
        """
        Возвращает обязательные поля для подключения к PostgreSQL.
        """
        return ["host","port", "database", "user", "password"]

    def connect(self, params: Dict[str, Any]) -> Any:
        """
        Устанавливает соединение с базой данных PostgreSQL.
        
        :param params: Параметры подключения.
        :return: Объект соединения psycopg2.
        """
        try:
            connection = psycopg2.connect(
                host=params["host"],
                port=params["port"],
                database=params["database"],
                user=params["user"],
                password=params["password"],
            )
            return connection
        except OperationalError as e:
            raise ValueError(f"Ошибка при подключении к PostgreSQL: {e}")

    def test_connection(self, params: Dict[str, Any]) -> bool:
        """
        Проверяет возможность подключения к PostgreSQL.

        :param params: Параметры подключения.
        :return: `True`, если подключение успешно, иначе `False`.
        """
        try:
            connection = self.connect(params)
            connection.close()  # Закрываем соединение после теста
            return True, ""
        except ValueError as e:
            return False, str(e)
