import tkinter as tk
from tkinter import ttk
from storage import save_data
import paramiko
import requests
import threading
import tkinter.messagebox as messagebox
from base_ui import BaseUI

from connectors.ssh import SshConnector
from connectors.PostgreSQL import PostgresConnector

from config import FEATURE_FLAGS

class EndpointManager(BaseUI):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.connectors = {
            "ssh": SshConnector(),
            "PostgreSQL": PostgresConnector()
        }
        self.options = {
            "Enable Logging": tk.BooleanVar(),
            "Auto-Reconnect": tk.BooleanVar(),
            "Use Compression": tk.BooleanVar()
        }

        self.setup_listbox(self.app.endpoints_frame, self.display_endpoint, self.add_endpoint)
        self.load_existing_data()

    def open_options_window(self, endpoint_name):
        """Открывает окно для выбора опций эндпоинта."""
        options_window = tk.Toplevel(self.app.root)
        options_window.title(f"Options for {endpoint_name}")
        options_window.geometry("300x200")

        for option, var in self.options.items():
            ttk.Checkbutton(options_window, text=option, variable=var).pack(anchor="w", padx=10, pady=5)
        
        def save_options():
            selected_options = {opt: var.get() for opt, var in self.options.items()}
            self.app.data.setdefault("options", {})[endpoint_name] = selected_options
            save_data(self.app.data)
            options_window.destroy()
        
        save_btn = ttk.Button(options_window, text="Save", command=save_options)
        save_btn.pack(pady=10)

    def test_connection(self):
        """Проверка соединения с эндпоинтом в отдельном потоке."""
        selected = self.listbox.curselection()
        if not selected:
            return

        def check():

            result = False
            if "ssh" in self.listbox.get(selected[1]):
                try:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(selected, timeout=5)
                    client.close()
                    result = True
                except Exception:
                    result = False

            # Вывод результата в отдельном окне
            tk._default_root.after(0, lambda: messagebox.showinfo("Тест соединения", 
                            f"Соединение {'успешно' if result else 'не удалось'}"))

        # Запускаем проверку в отдельном потоке
        threading.Thread(target=check, daemon=True).start()

    def delete_endpoint(self):
        """Удаляет выбранный эндпоинт."""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Не выбран эндпоинт для удаления!")
            return

        # Получаем имя выбранного эндпоинта
        name = self.listbox.get(selected[0])

        # Запрашиваем подтверждение удаления
        confirmation = messagebox.askyesno("Подтверждение удаления", f"Вы уверены, что хотите удалить эндпоинт '{name}'?")

        if confirmation:
            # Удаляем эндпоинт из данных
            self.app.data["endpoints"] = [ep for ep in self.app.data["endpoints"] if ep["name"] != name]
            
            # Обновляем список в интерфейсе
            self.listbox.delete(selected[0])

            # Сохраняем обновлённые данные
            save_data(self.app.data)

            self.clear_content_frame()
            # Показываем уведомление об успешном удалении
            messagebox.showinfo("Удаление", f"Эндпоинт '{name}' успешно удалён.")
  
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
        tk.Label(frame, text="Name", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        name_entry = tk.Entry(frame, width=32, bd=2)
        name_entry.insert(0, name)
        name_entry.pack(anchor="w", padx=5, pady=(0, 0))

        tk.Label(frame, text="Type", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        connection_types = ["ssh"]
        if FEATURE_FLAGS.get("ENABLE_SQL_SUPPORT", False):
            connection_types.extend(["PostgreSQL", "SQLite"])
        connection_var = tk.StringVar(value=conn_type)
        connection_dropdown = ttk.Combobox(frame, textvariable=connection_var, values=connection_types, width=30)
        connection_dropdown.pack(anchor="w", padx=5, pady=(0, 0))

        # Фрейм для SSH
        ssh_frame = tk.Frame(frame, borderwidth=2, bg="#C0C0C0")
        ssh_frame.pack(padx=(0, 0), pady=(0, 0))

        ssh_connector = self.connectors["ssh"]
        address_entry, port_entry, login_entry, password_entry = ssh_connector.endpoint_fields(ssh_frame)

        # Фрейм для SQL (PostgreSQL)
        sql_frame = tk.Frame(frame, borderwidth=2, bg="#C0C0C0")

        postgres_connector = self.connectors["PostgreSQL"]
        sql_host_entry, sql_port_entry, sql_db_entry, sql_user_entry, sql_password_entry = postgres_connector.endpoint_fields(sql_frame)

        # Поле для SQLite (путь к файлу базы данных)
        sqlite_frame = tk.Frame(frame, borderwidth=2, bg="#C0C0C0")

        tk.Label(sqlite_frame, text="DB File Path", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        sqlite_file_entry = tk.Entry(sqlite_frame)
        sqlite_file_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        # Функция переключения фреймов при изменении типа соединения
        def update_fields(*args):
            ssh_frame.pack_forget()
            sql_frame.pack_forget()
            sqlite_frame.pack_forget()

            if connection_var.get() == "ssh":
                ssh_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            elif connection_var.get() == "PostgreSQL":
                sql_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            elif connection_var.get() == "SQLite":
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
            save_btn.config(text="Saved")
            save_btn.after(2000, lambda: save_btn.config(text="Save"))

        button_container = self.buttons_frame(container)
        save_btn = self.create_button(button_container, "Save", save_endpoint)
        cancel_btn = self.create_button(button_container, "Cancel", self.clear_content_frame)
        test_btn = self.create_button(button_container, "Test", self.test_connection)
        opt_btn = self.create_button(button_container, "Options", lambda: self.open_options_window(name))
    
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
        opt_btn = self.create_button(button_container, "Options", lambda: self.open_options_window(name))
        delete_btn = self.create_button(button_container, "Delete", self.delete_endpoint)



