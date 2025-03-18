"""
This module provides an SSH connection utility with a GUI component for entering SSH credentials.

It includes:
- A `SshConnector` class for testing SSH connections using `paramiko`.
- A method for creating Tkinter-based input fields for SSH connection parameters.
"""
import tkinter as tk
import paramiko

class SshConnector:
    """
    This class provides methods to test SSH connections and create input fields 
    for SSH connection details in a Tkinter GUI.
    """

    def __init__(self, interpreter_args=""):
        """
        Initializes the SSH connector with optional interpreter arguments.

        :param interpreter_args: Arguments for the SSH connection (default is an empty string).
        """
        self.interpreter_args = interpreter_args

    def test_ssh_connection(self, endpoint):
        """
        Tests the SSH connection to the specified endpoint.

        :param endpoint: A dictionary containing connection details like address, port, 
                         login, and password.
        :return: True if the connection is successful, False otherwise.
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Разбиваем длинную строку на две для улучшения читаемости
            client.connect(
                endpoint["address"], port=int(endpoint["port"]),
                username=endpoint["login"], password=endpoint["password"], timeout=5
            )
            client.close()
            return True
        except paramiko.AuthenticationException:
            # Ловим конкретное исключение для аутентификации
            return False
        except paramiko.SSHException as e:
            print(f"SSH error: {e}")
            return False
        except Exception as e:
            print(f"General error: {e}")
            return False

    def endpoint_fields(self, container):
        """
        Creates and packs the fields (IP, Port, Login, Password) for the SSH connection
        details in the provided Tkinter container.

        :param container: The Tkinter container where the fields will be packed.
        :return: The entry widgets for address, port, login, and password.
        """
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
