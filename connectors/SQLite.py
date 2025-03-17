import sqlite3
import tkinter as tk

class SQLiteConnector:
    def __init__(self, interpreter_args=""):
        """
        :param interpreter_args: Аргументы для подключения (по умолчанию "")
        """
        self.interpreter_args = interpreter_args

    def test_sql_connection(self, endpoint):
        """Проверяет соединение с SQLite-эндпоинтом."""
        try:
            conn = sqlite3.connect(endpoint["db_file"])
            conn.close()
            return True
        except Exception:
            return False

    def endpoint_fields(self, container):
        tk.Label(container, text="DB File Path", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sqlite_file_entry = tk.Entry(container)
        sqlite_file_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        return sqlite_file_entry