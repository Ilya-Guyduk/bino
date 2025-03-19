"""docstring"""

import tkinter as tk
import threading
from tkinter import ttk
import tkinter.messagebox as messagebox
import paramiko

from storage import save_data
from base_ui import BaseUI

from connectors.ssh import SshConnector
from connectors.PostgreSQL import PostgresConnector

from config import FEATURE_FLAGS

class EndpointManager:
    """docstring"""
    def __init__(self, app):
        self.app = app
        self.ui = BaseUI(app)
        self.connectors = {
            "ssh": SshConnector(),
            "PostgreSQL": PostgresConnector()
        }
        self.options = {
            "Enable Logging": tk.BooleanVar(),
            "Auto-Reconnect": tk.BooleanVar(),
            "Use Compression": tk.BooleanVar()
        }

        self.ui.setup_listbox(self.app.endpoints_frame, self.display_endpoint, self.add_endpoint)
        self.load_existing_data()

    def open_options_window(self, endpoint_name):
        """Открывает окно для выбора опций эндпоинта."""
        if endpoint_name not in self.app.data["endpoints"]:
            return

        options_window = tk.Toplevel(self.app.root)
        options_window.title(f"Options for {endpoint_name}")
        options_window.geometry("300x200")

        endpoint_options = self.app.data["endpoints"].setdefault(endpoint_name, {}).setdefault("options", {})
        options_vars = {opt: tk.BooleanVar(value=endpoint_options.get(opt, False)) for opt in ["Enable Logging", "Auto-Reconnect", "Use Compression"]}

        for option, var in options_vars.items():
            ttk.Checkbutton(options_window, 
                            text=option, 
                            variable=var).pack(anchor="w", padx=10, pady=5)

        def save_options():
            for opt, var in options_vars.items():
                endpoint_options[opt] = var.get()
            save_data(self.app.data)
            options_window.destroy()

        save_btn = ttk.Button(options_window, text="Save", command=save_options)
        save_btn.pack(pady=10)

    def test_connection(self):
        """Проверка соединения с эндпоинтом с потоковым выводом статуса."""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите эндпоинт для тестирования.")
            return

        endpoint_name = self.listbox.get(selected[0])
        endpoint_data = self.app.data["endpoints"].get(endpoint_name)
        if not endpoint_data:
            messagebox.showerror("Ошибка", "Не найдено данных для эндпоинта.")
            return

        hostname = endpoint_data["address"]
        port = int(endpoint_data["port"])
        username = endpoint_data["login"]
        password = endpoint_data["password"]

        # Создаём окно сразу
        result_window = tk.Toplevel()
        result_window.title(f"Test '{endpoint_name}' connection")

        text_widget = tk.Text(result_window, wrap="word", height=10, width=50)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.config(state="disabled")

        close_button = tk.Button(result_window, text="Закрыть", command=result_window.destroy)
        close_button.pack(pady=5)

        # Строка статуса
        status_frame = tk.Frame(result_window)
        status_frame.pack(pady=5)

        status_label = tk.Label(status_frame, text="Connecting...", font=("Silkscreen", 9))
        status_label.pack(side="left")

        status_icon = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
        status_icon.pack(side="left", padx=5)

        def update_output(text):
            """Добавляет текст в окно с результатом."""
            text_widget.config(state="normal")
            text_widget.insert("end", text + "\n")
            text_widget.see("end")
            text_widget.config(state="disabled")

        def animate_spinner(angle=0):
            """Анимация вращающегося значка."""
            status_icon.delete("all")
            x0, y0, x1, y1 = 5, 5, 15, 15
            status_icon.create_arc(x0, y0, x1, y1, 
                                   start=angle, 
                                   extent=270, 
                                   outline="black", 
                                   width=2)
            if status_label["text"] == "Connecting...":
                self.app.root.after(100, animate_spinner, (angle + 30) % 360)

        def check_connection():
            """Функция для проверки соединения."""
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname, port=port, username=username, password=password, timeout=5)
                ssh_client.close()

                self.app.root.after(0, lambda: status_label.config(text="Connected"))
                self.app.root.after(0, lambda: status_icon.delete("all"))
                self.app.root.after(0, lambda: status_icon.create_text(10, 10, text="✔", font=("Arial", 14), fill="green"))
                self.app.root.after(0, lambda: update_output("Соединение успешно установлено!"))
            except Exception as e:
                self.app.root.after(0, lambda: update_output(f"Ошибка: {e}"))
                self.app.root.after(0, lambda: status_label.config(text="Failed"))
                self.app.root.after(0, lambda: status_icon.delete("all"))
                self.app.root.after(0, lambda: status_icon.create_text(10, 10, text="✖", font=("Arial", 14), fill="red"))

        # Запускаем индикатор загрузки
        animate_spinner()
        threading.Thread(target=check_connection, daemon=True).start()

    def delete_endpoint(self):
        """Удаляет выбранный скрипт."""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите эндпоинт для удаления.")
            return

        # Получаем имя скрипта, который нужно удалить
        endpoint_name = self.listbox.get(selected[0])

        # Удаляем скрипт из данных
        if endpoint_name in self.app.data["endpoints"]:
            del self.app.data["endpoints"][endpoint_name]

            # Удаляем скрипт из списка в UI
            self.listbox.delete(selected[0])

            # Сохраняем обновлённые данные
            save_data(self.app.data)

            # Очищаем поле с кодом и возвращаем в начальный экран
            self.clear_content_frame()

            messagebox.showinfo("Удалено", f"Скрипт '{endpoint_name}' был успешно удалён.")
        else:
            messagebox.showwarning("Ошибка", f"Скрипт '{endpoint_name}' не найден.")

    def load_existing_data(self):
        """docstring"""
        for script in self.app.data["endpoints"]:
            self.ui.listbox.insert(tk.END, script)

    def create_endpoint_fields(self, frame, name="", conn_type="ssh", endpoint_data=None):
        """Добавляет поля формы (Name, Type, Connection Details)"""
        tk.Label(frame, text="Name", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        self.name_entry = tk.Entry(frame, width=32, bd=2)
        self.name_entry.insert(0, name)
        self.name_entry.pack(anchor="w", padx=5, pady=(0, 0))

        tk.Label(frame, text="Type", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        connection_types = ["ssh"]
        if FEATURE_FLAGS.get("ENABLE_SQL_SUPPORT", False):
            connection_types.extend(["PostgreSQL", "SQLite"])
        self.connection_var = tk.StringVar(value=conn_type)
        connection_dropdown = ttk.Combobox(frame, textvariable=self.connection_var, values=connection_types, width=30)
        connection_dropdown.pack(anchor="w", padx=5, pady=(0, 0))

        # Фрейм для SSH
        ssh_frame = tk.Frame(frame, borderwidth=2, bg="#C0C0C0")
        ssh_frame.pack(padx=(0, 0), pady=(0, 0))

        ssh_connector = self.connectors["ssh"]
        self.address_entry, self.port_entry, self.login_entry, self.password_entry = ssh_connector.endpoint_fields(ssh_frame)

        # Фрейм для SQL (PostgreSQL)
        sql_frame = tk.Frame(frame, borderwidth=2, bg="#C0C0C0")

        postgres_connector = self.connectors["PostgreSQL"]
        self.sql_host_entry, self.sql_port_entry, self.sql_db_entry, self.sql_user_entry, self.sql_password_entry = postgres_connector.endpoint_fields(sql_frame)

        # Поле для SQLite (путь к файлу базы данных)
        sqlite_frame = tk.Frame(frame, borderwidth=2, bg="#C0C0C0")

        tk.Label(sqlite_frame, text="DB File Path", font=("Courier New", 9, "bold"), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        self.sqlite_file_entry = tk.Entry(sqlite_frame)
        self.sqlite_file_entry.pack(fill=tk.X, padx=5, pady=(2, 5))

        # Функция переключения фреймов при изменении типа соединения
        def update_fields(*args):
            ssh_frame.pack_forget()
            sql_frame.pack_forget()
            sqlite_frame.pack_forget()

            if self.connection_var.get() == "ssh":
                ssh_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            elif self.connection_var.get() == "PostgreSQL":
                sql_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            elif self.connection_var.get() == "SQLite":
                sqlite_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        # Подключаем обработчик изменения типа соединения
        self.connection_var.trace_add("write", update_fields)

        # Заполнение полей, если переданы данные
        if endpoint_data:
            if endpoint_data.get("type") == "ssh":
                self.address_entry.insert(0, endpoint_data.get("address", ""))
                self.port_entry.insert(0, endpoint_data.get("port", "22"))
                self.login_entry.insert(0, endpoint_data.get("login", ""))
                self.password_entry.insert(0, endpoint_data.get("password", ""))
            elif endpoint_data.get("type") == "sql/postgres":
                self.sql_host_entry.insert(0, endpoint_data.get("host", ""))
                self.sql_port_entry.insert(0, endpoint_data.get("port", "5432"))
                self.sql_db_entry.insert(0, endpoint_data.get("database", ""))
                self.sql_user_entry.insert(0, endpoint_data.get("user", ""))
                self.sql_password_entry.insert(0, endpoint_data.get("password", ""))
            elif endpoint_data.get("type") == "sql/sqlite":
                self.sqlite_file_entry.insert(0, endpoint_data.get("db_path", ""))

        # Инициализация правильного фрейма
        update_fields()

    def add_endpoint(self):
        """docstring"""
        self.ui.clear_content_frame()
        container, frame = self.ui.create_form_container()
        # Создаём поля формы для добавления эндпоинта
        self.create_endpoint_fields(frame)

        def save_endpoint():
            name = self.name_entry.get()
            connection_type = self.connection_var.get()

            if not name or not connection_type:
                return  # Не сохраняем, если нет имени или типа подключения

            if name and name not in self.app.data["endpoints"]:
                if connection_type == "ssh":
                    self.app.data["endpoints"][name] = {
                    "type": self.connection_var.get(),
                    "address": self.address_entry.get(),
                    "port": self.port_entry.get(),
                    "login": self.login_entry.get(),
                    "password": self.password_entry.get(),
                    "options": {"Enable Logging": False, "Auto-Reconnect": False, "Use Compression": False}
                }
            self.ui.listbox.insert(tk.END, name)
            save_data(self.app.data)
            save_btn.config(text="Saved", font=("Silkscreen", 9), bg="gray80")
            self.ui.create_button(button_container, "Delete", self.delete_endpoint)
            save_btn.after(2000, lambda: save_btn.config(text="Save"))

        button_container = self.ui.buttons_frame(container)
        save_btn = self.ui.create_button(button_container, "Save", save_endpoint)
        self.ui.create_button(button_container, "Cancel", self.clear_content_frame)
        self.ui.create_button(button_container, "Test", self.test_connection)
        self.ui.create_button(button_container, "Options", lambda: self.open_options_window(name))

    def display_endpoint(self, event):
        """ Отображает информацию о выбранном эндпоинте. """
        selected = self.ui.listbox.curselection()
        if selected:
            name = self.ui.listbox.get(selected[0])
            endpoint_data = self.app.data["endpoints"][name]

            self.ui.clear_content_frame()
            container, frame = self.ui.create_form_container()

            # Создаём поля формы для отображения эндпоинта
            self.create_endpoint_fields(frame, 
                name=name, conn_type=endpoint_data["type"], endpoint_data=endpoint_data)

            def save_changes():

                endpoint_data["type"] = self.connection_var.get()

                if endpoint_data["type"] == "ssh":
                    endpoint_data["address"] = self.address_entry.get()
                    endpoint_data["port"] = self.port_entry.get()
                    endpoint_data["login"] = self.login_entry.get()
                    endpoint_data["password"] = self.password_entry.get()

                save_data(self.app.data)
                save_btn.config(text="Saved")
                save_btn.after(2000, lambda: save_btn.config(text="Save"))

            button_container = self.ui.buttons_frame(container)
            save_btn = self.ui.create_button(button_container, "Save", save_changes)
            self.ui.create_button(button_container, "Cancel", self.ui.clear_content_frame)
            self.ui.create_button(button_container, "Test", self.test_connection)
            self.ui.create_button(button_container, "Options", lambda: self.open_options_window(name))
            self.ui.create_button(button_container, "Delete", self.delete_endpoint)
