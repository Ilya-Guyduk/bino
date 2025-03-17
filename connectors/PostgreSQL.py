import psycopg2
import tkinter as tk

class PostgresConnector:
    def __init__(self, interpreter_args=""):
        """
        :param interpreter_args: Аргументы для подключения (по умолчанию "")
        """
        self.interpreter_args = interpreter_args

    def test_sql_connection(self, endpoint):
        """Проверяет соединение с PostgreSQL-эндпоинтом."""
        try:
            conn = psycopg2.connect(
                host=endpoint["address"],
                port=int(endpoint["port"]),
                dbname=endpoint["database"],
                user=endpoint["login"],
                password=endpoint["password"]
            )
            conn.close()
            return True
        except Exception:
            return False

    def endpoint_fields(self, container):
        tk.Label(container, text="Host:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sql_host_entry = tk.Entry(container)
        sql_host_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(container, text="Port:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sql_port_entry = tk.Entry(container)
        sql_port_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(container, text="Database:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sql_db_entry = tk.Entry(container)
        sql_db_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(container, text="User", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sql_user_entry = tk.Entry(container)
        sql_user_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(container, text="Password", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sql_password_entry = tk.Entry(container, show="*")
        sql_password_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        return sql_host_entry, sql_port_entry, sql_db_entry, sql_user_entry, sql_password_entry
