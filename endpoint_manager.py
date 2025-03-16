import tkinter as tk
from tkinter import ttk
from storage import save_data
import paramiko
import requests
import threading
import tkinter.messagebox as messagebox
from base_ui import BaseUI


class EndpointManager(BaseUI):
    def __init__(self, app):
        self.app = app
        self.listbox = tk.Listbox(self.app.endpoints_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.display_endpoint)
        
        self.add_button = tk.Button(self.app.endpoints_frame, text="Add", font=("Silkscreen", 9), command=self.add_endpoint)
        self.add_button.pack(fill=tk.X)
        
        self.load_existing_data()

    def test_connection(self, endpoint):
        """Проверка соединения с эндпоинтом в отдельном потоке."""
        def check():
            result = False
            if endpoint.startswith("http"):
                try:
                    response = requests.get(endpoint, timeout=5)
                    result = response.status_code == 200
                except requests.RequestException:
                    result = False
            elif "ssh" in endpoint:
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(endpoint, timeout=5)
                    client.close()
                    result = True
                except Exception:
                    result = False

            # Вывод результата в отдельном окне
            tk._default_root.after(0, lambda: messagebox.showinfo("Тест соединения", 
                            f"Соединение {'успешно' if result else 'не удалось'}"))

        # Запускаем проверку в отдельном потоке
        threading.Thread(target=check, daemon=True).start()

    def load_existing_data(self):
        """ Загружает эндпоинты в listbox, приводя старые строки к новому формату. """
        updated_endpoints = []

        for endpoint in self.app.data["endpoints"]:
            if isinstance(endpoint, str):
                # Старый формат (просто строка) -> преобразуем в словарь
                endpoint = {"name": endpoint, "type": "unknown"}
            
            updated_endpoints.append(endpoint)
            self.listbox.insert(tk.END, endpoint["name"])  # Используем name

        # Обновляем self.app.data["endpoints"] новым форматом
        self.app.data["endpoints"] = updated_endpoints
    
    def create_endpoint_fields(self, frame, name="", conn_type="ssh", endpoint_data=None):
        """Добавляет поля формы (Name, Type, Connection Details)"""
        tk.Label(frame, text="Name:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        name_entry = tk.Entry(frame, width=32, bd=2)
        name_entry.insert(0, name)
        name_entry.pack(anchor="w", padx=5, pady=(0, 0))

        tk.Label(frame, text="Type:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        connection_var = tk.StringVar(value=conn_type)
        connection_dropdown = ttk.Combobox(frame, textvariable=connection_var, values=["ssh", "sql/postgres", "sql/sqlite"], width=30)
        connection_dropdown.pack(anchor="w", padx=5, pady=(0, 0))

        # Фрейм для SSH
        ssh_frame = tk.Frame(frame, bg="#C0C0C0")

        tk.Label(ssh_frame, text="IP:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        address_entry = tk.Entry(ssh_frame)
        address_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(ssh_frame, text="Port:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        port_entry = tk.Entry(ssh_frame)
        port_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(ssh_frame, text="Login:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        login_entry = tk.Entry(ssh_frame)
        login_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(ssh_frame, text="Password:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        password_entry = tk.Entry(ssh_frame, show="*")
        password_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        # Фрейм для SQL (PostgreSQL и SQLite)
        sql_frame = tk.Frame(frame, bg="#C0C0C0")

        tk.Label(sql_frame, text="Host:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sql_host_entry = tk.Entry(sql_frame)
        sql_host_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(sql_frame, text="Port:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sql_port_entry = tk.Entry(sql_frame)
        sql_port_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(sql_frame, text="Database:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sql_db_entry = tk.Entry(sql_frame)
        sql_db_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(sql_frame, text="User:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sql_user_entry = tk.Entry(sql_frame)
        sql_user_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        tk.Label(sql_frame, text="Password:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sql_password_entry = tk.Entry(sql_frame, show="*")
        sql_password_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        # Поле для SQLite (путь к файлу базы данных)
        sqlite_frame = tk.Frame(frame, bg="#C0C0C0")

        tk.Label(sqlite_frame, text="DB File Path:", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sqlite_file_entry = tk.Entry(sqlite_frame)
        sqlite_file_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        # Функция переключения фреймов при изменении типа соединения
        def update_fields(*args):
            ssh_frame.pack_forget()
            sql_frame.pack_forget()
            sqlite_frame.pack_forget()

            if connection_var.get() == "ssh":
                ssh_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            elif connection_var.get() == "sql/postgres":
                sql_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            elif connection_var.get() == "sql/sqlite":
                sqlite_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        # Подключаем обработчик изменения типа соединения
        connection_var.trace_add("write", update_fields)

        # Заполнение полей, если переданы данные
        if endpoint_data:
            if endpoint_data.get("type") == "ssh":
                address_entry.insert(0, endpoint_data.get("address", ""))
                port_entry.insert(0, endpoint_data.get("port", "22"))
                login_entry.insert(0, endpoint_data.get("login", ""))
                password_entry.insert(0, endpoint_data.get("password", ""))
            elif endpoint_data.get("type") == "sql/postgres":
                sql_host_entry.insert(0, endpoint_data.get("host", ""))
                sql_port_entry.insert(0, endpoint_data.get("port", "5432"))
                sql_db_entry.insert(0, endpoint_data.get("database", ""))
                sql_user_entry.insert(0, endpoint_data.get("user", ""))
                sql_password_entry.insert(0, endpoint_data.get("password", ""))
            elif endpoint_data.get("type") == "sql/sqlite":
                sqlite_file_entry.insert(0, endpoint_data.get("db_path", ""))

        # Инициализация правильного фрейма
        update_fields()

        return name_entry, connection_var, ssh_frame, sql_frame, sqlite_frame, address_entry, port_entry, login_entry, password_entry, sql_host_entry, sql_port_entry, sql_db_entry, sql_user_entry, sql_password_entry, sqlite_file_entry


    def add_endpoint(self):
        self.clear_content_frame()
        container, frame = self.create_form_container()

        # Создаём поля формы для добавления эндпоинта
        name_entry, connection_var, ssh_frame, sql_frame, sqlite_frame, address_entry, port_entry, login_entry, password_entry, sql_host_entry, sql_port_entry, sql_db_entry, sql_user_entry, sql_password_entry, sqlite_file_entry = self.create_endpoint_fields(frame)

        def save_endpoint():
            name = name_entry.get()
            connection_type = connection_var.get()

            if not name or not connection_type:
                return  # Не сохраняем, если нет имени или типа подключения

            new_endpoint = {"name": name, "type": connection_type}

            if connection_type == "ssh":
                new_endpoint.update({
                    "address": address_entry.get(),
                    "port": port_entry.get(),
                    "login": login_entry.get(),
                    "password": password_entry.get()
                })

            self.app.data["endpoints"].append(new_endpoint)
            self.listbox.insert(tk.END, name)
            save_data(self.app.data)
            save_btn.config(text="Сохранено!")
            save_btn.after(2000, lambda: save_btn.config(text="Сохранить"))

        button_container = self.buttons_frame(container)
        save_btn = self.create_button(button_container, "Save", save_changes)
        cancel_btn = self.create_button(button_container, "Cancel", self.clear_content_frame)
        test_btn = self.create_button(button_container, "Test", self.test_connection)
    
    def display_endpoint(self, event):
        """ Отображает информацию о выбранном эндпоинте. """
        selected = self.listbox.curselection()
        if not selected:
            return

        name = self.listbox.get(selected[0])

        # Ищем эндпоинт по имени
        endpoint_data = next((ep for ep in self.app.data["endpoints"] if ep["name"] == name), None)
        if not endpoint_data:
            return

        self.clear_content_frame()
        container, frame = self.create_form_container()

        # Создаём поля формы для отображения эндпоинта
        name_entry, connection_var, ssh_frame, sql_frame, sqlite_frame, address_entry, port_entry, login_entry, password_entry, sql_host_entry, sql_port_entry, sql_db_entry, sql_user_entry, sql_password_entry, sqlite_file_entry = self.create_endpoint_fields(frame, name=endpoint_data["name"], conn_type=endpoint_data["type"], endpoint_data=endpoint_data)

        def save_changes():
            endpoint_data["name"] = name_entry.get()
            endpoint_data["type"] = connection_var.get()

            if endpoint_data["type"] == "ssh":
                endpoint_data["address"] = address_entry.get()
                endpoint_data["port"] = port_entry.get()
                endpoint_data["login"] = login_entry.get()
                endpoint_data["password"] = password_entry.get()

            save_data(self.app.data)
            save_btn.config(text="Saved")
            save_btn.after(2000, lambda: save_btn.config(text="Save"))

        button_container = self.buttons_frame(container)
        save_btn = self.create_button(button_container, "Save", save_changes)
        cancel_btn = self.create_button(button_container, "Cancel", self.clear_content_frame)
        test_btn = self.create_button(button_container, "Test", self.test_connection)



