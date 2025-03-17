import paramiko
import tkinter as tk

class SshConnector:
    def __init__(self, interpreter_args=""):
        """
        :param interpreter_args: Аргументы для подключения (по умолчанию "")
        """
        self.interpreter_args = interpreter_args

    def test_ssh_connection(self,  endpoint):
        """Проверяет соединение с SSH-эндпоинтом."""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(endpoint["address"], port=int(endpoint["port"]), username=endpoint["login"], password=endpoint["password"], timeout=5)
            client.close()
            return True
        except Exception:
            return False

    def endpoint_fields(self, container):
        tk.Label(container, text="IP", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=0, pady=(0, 0))
        address_entry = tk.Entry(container, width=32, bd=2)
        address_entry.pack(anchor="w", padx=0, pady=(0, 0))

        tk.Label(container, text="Port", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=0, pady=(0, 0))
        port_entry = tk.Entry(container, width=32, bd=2)
        port_entry.pack(anchor="w", padx=0, pady=(0, 0))

        tk.Label(container, text="Login", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=0, pady=(0, 0))
        login_entry = tk.Entry(container, width=32, bd=2)
        login_entry.pack(anchor="w", padx=0, pady=(0, 0))

        tk.Label(container, text="Password", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=0, pady=(0, 0))
        password_entry = tk.Entry(container, show="*", width=32, bd=2)
        password_entry.pack(anchor="w", padx=0, pady=(0, 3))

        return address_entry, port_entry, login_entry, password_entry
