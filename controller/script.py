"""docstring"""
import tkinter as tk
import threading
from tkinter import messagebox
import paramiko

#from model.script import Script
from model.endpoint import Endpoint
from view.theme import StyledToplevel, StyledButton, StyledFrame, StyledLabel
from interpreters.python import PythonInterpreter
from interpreters.bash import BashInterpreter

class ScriptBackend:
    """docstring"""
    def __init__(self, app):
        self.app = app
        self.storage = self.app.storage  # ссылка на file_storage
        self.interpreters = {
            "python": PythonInterpreter(),
            "bash": BashInterpreter()
        }

    def run_script(self):
        """
        Запускает скрипт на удалённом сервере 
        по SSH с потоковым выводом и статусом подключения.
        """
        name = self.app.scripts_manager.view.name_entry.get()
        script = self.app.scripts_manager.model.read(name)

        endpoint_name = script.endpoint
        endpoint_data = self.storage.endpoints.get(endpoint_name)
        if not endpoint_data:
            messagebox.showwarning("Ошибка", "Эндпоинт не существует")
            return

        endpoint = Endpoint.from_dict(self.storage, endpoint_data)

        hostname = endpoint.ip
        port = int(endpoint.port)
        username = endpoint.login
        password = endpoint.password
        interpreter_name = script.interpreter
        script_code = script.code
        options = script.options

        # Создаём окно сразу
        result_window = StyledToplevel()
        result_window.title("Результат выполнения")

        text_widget = tk.Text(result_window, wrap="word", height=20, width=80)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.config(state="disabled")

        close_button = StyledButton(result_window, text="Закрыть", command=result_window.destroy)
        close_button.pack(pady=5)

        # Строка статуса
        status_frame = StyledFrame(result_window)
        status_frame.pack(pady=5)

        status_label = StyledLabel(status_frame, text="Connecting...", font=("Silkscreen", 9))
        status_label.pack(side="left")

        status_icon = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
        status_icon.pack(side="left", padx=5)

        def update_output(text):
            """Добавляет текст в окно с результатом."""
            text_widget.config(state="normal")
            text_widget.insert("end", text)
            text_widget.see("end")
            text_widget.config(state="disabled")

        def animate_spinner(angle=0):
            """Анимация вращающегося значка."""
            status_icon.delete("all")
            x0, y0, x1, y1 = 5, 5, 15, 15
            status_icon.create_arc(x0, y0, x1, y1, start=angle,
                                   extent=270, outline="black", width=2)
            if status_label["text"] == "Connecting...":
                self.app.root.after(100, animate_spinner, (angle + 30) % 360)

        def execute_script():
            """Функция для выполнения скрипта и обновления статуса."""
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname, port=port, username=username, password=password)

                # Статус подключения
                self.app.root.after(0, lambda: status_label.config(text="Connected"))
                self.app.root.after(0, lambda: status_icon.delete("all"))
                self.app.root.after(0, lambda: status_icon.create_text(10,
                                                                       10, text="✔",
                                                                       font=("Arial", 14),
                                                                       fill="green"))

                if interpreter_name in self.interpreters:
                    interpreter = self.interpreters[interpreter_name]
                    command = interpreter.format_command(script_code, options)
                else:
                    command = script_code

                _, stdout, stderr = ssh_client.exec_command(command)
                for line in iter(stdout.readline, ""):
                    self.app.root.after(0, update_output, line)
                for line in iter(stderr.readline, ""):
                    self.app.root.after(0, update_output, f"[Ошибка] {line}")

                ssh_client.close()

            except Exception as e:
                self.app.root.after(0, update_output, f"Ошибка: {e}")

        # Запуск индикатора загрузки
        animate_spinner()
        threading.Thread(target=execute_script, daemon=True).start()
