import sqlite3
from typing import Dict, Any, List, Tuple
from .base_connector import BaseConnector


class SqliteConnector(BaseConnector):
    """
    Коннектор для подключения к базе данных SQLite.
    """

    def default_options(self) -> Dict[str, Dict[str, Any]]:
        """
        Возвращает настройки по умолчанию для SQLite-коннектора.
        """
        return {
            "timeout": {
                "type": float,
                "description": "Таймаут соединения с базой (в секундах)",
                "value": 5.0
            },
            "detect_types": {
                "type": int,
                "description": "Режим определения типов (обычно 0 или sqlite3.PARSE_DECLTYPES)",
                "value": 0
            },
            "isolation_level": {
                "type": str,
                "description": "Уровень изоляции транзакций (например, 'DEFERRED', 'IMMEDIATE', 'EXCLUSIVE')",
                "value": None
            },
            "check_same_thread": {
                "type": bool,
                "description": "Разрешить использование соединения в разных потоках",
                "value": True
            }
        }

    def get_required_fields(self) -> List[str]:
        """
        Возвращает список обязательных полей для подключения к SQLite.
        """
        return ["path"]

    def connect(self, params: Dict[str, Any]) -> sqlite3.Connection:
        """
        Подключается к SQLite-базе данных и возвращает соединение.
        """
        self.validate_params(params)

        connection = sqlite3.connect(
            database=params["path"],
            timeout=params.get("timeout", 5.0),
            detect_types=params.get("detect_types", 0),
            isolation_level=params.get("isolation_level", None),
            check_same_thread=params.get("check_same_thread", True)
        )
        return connection

    def test_connection(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Проверяет возможность подключения к SQLite базе данных.
        """
        try:
            conn = self.connect(params)
            conn.execute("SELECT 1")  # Простая проверка
            conn.close()
            return True, ""
        except sqlite3.OperationalError as e:
            return False, f"Ошибка подключения к базе: {e}"
        except Exception as e:
            return False, str(e)
