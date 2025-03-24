import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext, ttk
from storage import save_data
import paramiko
from pygments import highlight
from pygments.lexers import PythonLexer, BashLexer
from pygments.formatters import RawTokenFormatter
from pygments.token import Token
from base_ui import BaseUI
from interpreters.python import PythonInterpreter
from interpreters.bash import BashInterpreter

import threading

class ScriptManager:
    def __init__(self, app):
        self.app = app
        self.ui = BaseUI(app)
        self.interpreters = {
            "python": PythonInterpreter(),
            "bash": BashInterpreter()
        }
        self.ui.setup_listbox(self.app.scripts_frame, self.display_script, self.add_script)
        self.load_existing_data()
    
    def load_existing_data(self):
        for script in self.app.data["scripts"]:
            self.ui.listbox.insert(tk.END, script)

    def delete_script(self):
        """Удаляет выбранный скрипт."""
        selected = self.ui.listbox.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите скрипт для удаления.")
            return

        # Получаем имя скрипта, который нужно удалить
        script_name = self.ui.listbox.get(selected[0])

        # Удаляем скрипт из данных
        if script_name in self.app.data["scripts"]:
            del self.app.data["scripts"][script_name]

            # Удаляем скрипт из списка в UI
            self.ui.listbox.delete(selected[0])

            # Сохраняем обновлённые данные
            save_data(self.app.data)

            # Очищаем поле с кодом и возвращаем в начальный экран
            self.ui.clear_content_frame()

            messagebox.showinfo("Удалено", f"Скрипт '{script_name}' был успешно удалён.")
        else:
            messagebox.showwarning("Ошибка", f"Скрипт '{script_name}' не найден.")

    def run_script(self):
        """Запуск скрипта на удалённом сервере по SSH с потоковым выводом и статусом подключения."""
        name = self.name_entry.get()
        script = self.app.data["scripts"].get(name)
        interpreter_name = script["interpreter"]
        script_code = self.script_text.get("1.0", tk.END).strip()
        options = script["options"]
        endpoint_name = self.endpoint_var.get()

        endpoint_data = self.app.data["endpoints"].get(endpoint_name)
        if not endpoint_data:
            messagebox.showerror("Ошибка", f"Эндпоинт '{endpoint_name}' не найден.")
            return

        hostname = endpoint_data["address"]
        port = int(endpoint_data["port"])
        username = endpoint_data["login"]
        password = endpoint_data["password"]

        # Создаём окно сразу
        result_window = tk.Toplevel()
        result_window.title("Результат выполнения")

        text_widget = tk.Text(result_window, wrap="word", height=20, width=80)
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
            text_widget.insert("end", text)
            text_widget.see("end")
            text_widget.config(state="disabled")

        def animate_spinner(angle=0):
            """Анимация вращающегося значка."""
            status_icon.delete("all")
            x0, y0, x1, y1 = 5, 5, 15, 15
            status_icon.create_arc(x0, y0, x1, y1, start=angle, extent=270, outline="black", width=2)
            if status_label["text"] == "Connecting...":
                self.app.root.after(100, animate_spinner, (angle + 30) % 360)

        def execute_script():
            """Функция для выполнения скрипта и обновления статуса."""
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname, port=port, username=username, password=password)

                # Меняем статус на "Подключено" и ставим галочку
                self.app.root.after(0, lambda: status_label.config(text="Connected"))
                self.app.root.after(0, lambda: status_icon.delete("all"))
                self.app.root.after(0, lambda: status_icon.create_text(10, 10, text="✔", font=("Arial", 14), fill="green"))

                if interpreter_name in self.interpreters:
                    interpreter = self.interpreters[interpreter_name]
                    command = interpreter.format_command(script_code, options)
                else:
                    command = script_code

                stdin, stdout, stderr = ssh_client.exec_command(command)
                for line in iter(stdout.readline, ""):
                    self.app.root.after(0, update_output, line)
                for line in iter(stderr.readline, ""):
                    self.app.root.after(0, update_output, f"[Ошибка] {line}")

                ssh_client.close()

            except Exception as e:
                self.app.root.after(0, update_output, f"Ошибка: {e}")

        # Запускаем индикатор загрузки
        animate_spinner()
        threading.Thread(target=execute_script, daemon=True).start()
    
    def add_syntax_highlighting(self, text_widget, code, language):
        """
        Добавляет подсветку синтаксиса в виджет Text с использованием тегов.
        
        text_widget: виджет Text, в который добавляется подсветка.
        code: код, который будет подсвечен.
        language: язык для подсветки синтаксиса (например, 'python' или 'bash').
        """
        # Выбираем соответствующий лексер для языка
        if language == "python":
            lexer = PythonLexer()
        elif language == "bash":
            lexer = BashLexer()
        else:
            lexer = PythonLexer()  # По умолчанию Python

        # Применяем подсветку к коду с использованием RawTokenFormatter
        highlighted_code = highlight(code, lexer, RawTokenFormatter())

        # Очищаем текущее содержимое виджета
        text_widget.delete(1.0, tk.END)

        # Создаём теги для подсветки
        text_widget.tag_config("keyword", foreground="blue")
        text_widget.tag_config("name", foreground="green")
        text_widget.tag_config("string", foreground="red")
        text_widget.tag_config("operator", foreground="black")
        
        # Разбиваем токены и вставляем их с тегами
        position = 1.0  # Начальная позиция для вставки текста
        for token in lexer.get_tokens(code):
            text = token[1]
            token_type = token[0]

            # Применяем теги в зависимости от типа токена
            if token_type in Token.Keyword:
                tag = "keyword"
            elif token_type in Token.Name:
                tag = "name"
            elif token_type in Token.String:
                tag = "string"
            elif token_type in Token.Operator:
                tag = "operator"
            else:
                tag = None
            
            if tag:
                text_widget.insert(position, text, tag)
            else:
                text_widget.insert(position, text)

            position = text_widget.index(tk.END)  # Переход на следующий индекс

        # Отключаем редактирование (если нужно)
        #text_widget.config(state=tk.DISABLED)

    def create_script_fields(self, frame, name="", interpreter="python", endpoint=""):
        """Добавляет поля формы (Name, Interpreter, Endpoint)"""
        tk.Label(frame, text="Name", font=("Silkscreen", 9), bg="#d5a78d").pack(anchor="w", padx=4, pady=(0, 0))
        self.name_entry = tk.Entry(frame, width=32, bd=1)
        self.name_entry.insert(0, name)
        self.name_entry.pack(anchor="w", padx=5, pady=(0, 0))

        tk.Label(frame, text="Interpreter", font=("Silkscreen", 9), bg="#d5a78d").pack(anchor="w", padx=4, pady=(0, 0))
        self.interpreter_var = tk.StringVar(value=interpreter)
        interpreter_dropdown = ttk.Combobox(frame, textvariable=self.interpreter_var, values=["python", "bash"], width=30)
        interpreter_dropdown.pack(anchor="w", padx=5, pady=(0, 0))

        tk.Label(frame, text="Endpoint", font=("Silkscreen", 9), bg="#d5a78d").pack(anchor="w", padx=4, pady=(0, 0))
        endpoint_names = list(self.app.data["endpoints"].keys())
        self.endpoint_var = tk.StringVar(value=endpoint)
        endpoint_dropdown = ttk.Combobox(frame, textvariable=self.endpoint_var, values=endpoint_names, width=30)
        endpoint_dropdown.pack(anchor="w", padx=5, pady=(0, 8))

    def create_code_field(self, code=""):
        """Создаёт текстовое поле с кодом"""
        tk.Label(self.app.content_frame, text="Code:", font=("Silkscreen", 9),bg="#f2ceae", fg="#000080").pack(anchor="w", padx=7)

        self.script_text = scrolledtext.ScrolledText(self.app.content_frame, height=10, wrap=tk.WORD, font=("Courier", 10))
        self.script_text.insert("1.0", code)
        self.script_text.config(tabs=4)
        self.script_text.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 0))


    def add_script(self):
        """Создание нового скрипта."""
        self.ui.clear_content_frame()
        container, frame = self.ui.create_form_container()
        self.create_script_fields(frame)

        def save_script():
            name = self.name_entry.get()
            interpreter_name = self.interpreter_var.get()
            if name and name not in self.app.data["scripts"]:
                self.app.data["scripts"][name] = {
                    "interpreter": interpreter_name,
                    "endpoint": self.endpoint_var.get(),
                    "code": self.script_text.get("1.0", tk.END),
                    "options": self.interpreters[interpreter_name].available_options
                }
                self.ui.listbox.insert(tk.END, name)
                save_data(self.app.data)
                save_btn.config(text="Saved", font=("Silkscreen", 9), bg="gray80")
                self.ui.create_button(button_container, "Delete", self.delete_script)
                save_btn.after(2000, lambda: save_btn.config(text="Save"))

        button_container = self.ui.buttons_frame(container)
        save_btn = self.ui.create_button(button_container, "Save", save_script)
        self.ui.create_button(button_container, "Cancel", self.ui.clear_content_frame)
        self.ui.create_button(button_container, "Start", self.run_script)
        self.ui.create_button(button_container, "Options", self.open_options_window)
        self.create_code_field()


    def display_script(self, event):
        """Отображение информации о выбранном скрипте."""
        selected = self.ui.listbox.curselection()
        if selected:
            name = self.ui.listbox.get(selected[0])
            script_data = self.app.data["scripts"][name]

            self.ui.clear_content_frame()
            container, frame = self.ui.create_form_container()
            self.create_script_fields(frame, name, script_data["interpreter"], script_data["endpoint"])

            def save_script():
                script_data["interpreter"] = self.interpreter_var.get()
                script_data["endpoint"] = self.endpoint_var.get()
                script_data["code"] = self.script_text.get("1.0", tk.END)
                save_data(self.app.data)
                save_btn.config(text="Saved", font=("Silkscreen", 9), bg="gray80")
                save_btn.after(2000, lambda: save_btn.config(text="Save"))



            button_container = self.ui.buttons_frame(container)
            save_btn = self.ui.create_button(button_container, "Save", save_script)
            self.ui.create_button(button_container, "Cancel", self.ui.clear_content_frame)
            self.ui.create_button(button_container, "Start", self.run_script)
            self.ui.create_button(button_container, "Options", lambda: self.ui.open_options_window(name, "interpreter"))
            self.ui.create_button(button_container, "Delete", self.delete_script)

            self.create_code_field(script_data["code"])
            self.add_syntax_highlighting(self.script_text, script_data["code"], script_data["interpreter"])


