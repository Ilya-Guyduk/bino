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
import threading

class ScriptManager(BaseUI):
    def __init__(self, app):
        self.app = app
        self.listbox = tk.Listbox(self.app.scripts_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.display_script)

        # Кнопка Add
        self.add_button = tk.Button(self.app.scripts_frame, text="Add",font=("Silkscreen", 9), command=self.add_script)
        self.add_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.load_existing_data()
    
    
    def load_existing_data(self):
        for script in self.app.data["scripts"]:
            self.listbox.insert(tk.END, script)


    def run_script(self):
        """Запуск скрипта на удалённом сервере по SSH с выводом результата в отдельном окне."""
        interpreter = self.interpreter_var.get()  # Интерпретатор (bash или python)
        script_code = self.script_text.get("1.0", tk.END).strip()  # Код скрипта
        endpoint_name = self.endpoint_var.get()  # Эндпоинт
        
        # Найти данные о выбранном эндпоинте
        endpoint_data = next((ep for ep in self.app.data["endpoints"] if ep["name"] == endpoint_name), None)
        
        if not endpoint_data:
            messagebox.showerror("Ошибка", f"Эндпоинт '{endpoint_name}' не найден.")
            return
        
        # Устанавливаем параметры для подключения по SSH
        hostname = endpoint_data["address"]
        port = int(endpoint_data["port"])
        username = endpoint_data["login"]
        password = endpoint_data["password"]

        def execute_script():
            """Функция для выполнения скрипта и обновления окна вывода."""
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Игнорировать неизвестные ключи
                ssh_client.connect(hostname, port=port, username=username, password=password)

                command = f"python -c '{script_code}'" if interpreter == "python" else f"bash -c '{script_code}'"
                stdin, stdout, stderr = ssh_client.exec_command(command)

                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()
                ssh_client.close()
                
                result_text = "Вывод скрипта:\n" + (output if output else "(Нет вывода)") + "\n"
                if error:
                    result_text += "\nОшибка:\n" + error
                
            except Exception as e:
                result_text = f"Ошибка подключения или выполнения команды:\n{e}"

            # Обновляем текст в окне результатов
            tk._default_root.after(0, lambda: self.show_result_window(result_text))

        # Запуск выполнения в отдельном потоке
        threading.Thread(target=execute_script, daemon=True).start()

    def show_result_window(self, text):
        """Открывает окно с результатом выполнения."""
        result_window = tk.Toplevel()
        result_window.title("Результат выполнения")

        text_widget = tk.Text(result_window, wrap="word", height=20, width=80)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")  # Запретить редактирование

        close_button = tk.Button(result_window, text="Закрыть", command=result_window.destroy)
        close_button.pack(pady=5)

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
        tk.Label(frame, text="Name:", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        self.name_entry = tk.Entry(frame, width=32, bd=2)
        self.name_entry.insert(0, name)
        self.name_entry.pack(anchor="w", padx=5, pady=(0, 0))

        tk.Label(frame, text="Interpreter:", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        self.interpreter_var = tk.StringVar(value=interpreter)
        interpreter_dropdown = ttk.Combobox(frame, textvariable=self.interpreter_var, values=["python", "bash"], width=30)
        interpreter_dropdown.pack(anchor="w", padx=5, pady=(0, 0))

        tk.Label(frame, text="Endpoint:", font=("Silkscreen", 9), bg="#C0C0C0").pack(anchor="w", padx=4, pady=(0, 0))
        endpoint_names = [endpoint["name"] for endpoint in self.app.data["endpoints"]]
        self.endpoint_var = tk.StringVar(value=endpoint)
        endpoint_dropdown = ttk.Combobox(frame, textvariable=self.endpoint_var, values=endpoint_names, width=30)
        endpoint_dropdown.pack(anchor="w", padx=5, pady=(0, 8))

    def create_buttons(self, container, save_command):
        """Создаёт кнопки (Сохранить, Отмена, Запустить)"""
        buttons_frame = tk.Frame(container)
        buttons_frame.grid(row=0, column=1, sticky="ne")

        def on_enter(e):
            e.widget.config(bg="gray80")

        def on_leave(e):
            e.widget.config(bg="SystemButtonFace")

        btn_save = tk.Button(buttons_frame, text="Save",font=("Silkscreen", 9), command=save_command)
        btn_save.pack(fill="x", pady=2)
        btn_save.bind("<Enter>", on_enter)
        btn_save.bind("<Leave>", on_leave)

        btn_cancel = tk.Button(buttons_frame, text="Cancel",font=("Silkscreen", 9), command=self.clear_content_frame)
        btn_cancel.pack(fill="x", pady=2)
        btn_cancel.bind("<Enter>", on_enter)
        btn_cancel.bind("<Leave>", on_leave)

        btn_run = tk.Button(buttons_frame, text="Start",font=("Silkscreen", 9), command=self.run_script)
        btn_run.pack(fill="x", pady=2)
        btn_run.bind("<Enter>", on_enter)
        btn_run.bind("<Leave>", on_leave)

        return btn_save

    def create_code_field(self, code=""):
        """Создаёт текстовое поле с кодом"""
        tk.Label(self.app.content_frame, text="Code:", font=("Silkscreen", 9), fg="#000080").pack(anchor="w", padx=7)

        self.script_text = scrolledtext.ScrolledText(self.app.content_frame, height=10, wrap=tk.WORD, font=("Courier", 10))
        self.script_text.insert("1.0", code)
        self.script_text.config(tabs=4)
        self.script_text.pack(fill=tk.BOTH, expand=True, padx=7, pady=(0, 7))


    def add_script(self):
        """Создание нового скрипта."""
        self.clear_content_frame()
        container, frame = self.create_form_container()
        self.create_script_fields(frame)

        def save_script():
            name = self.name_entry.get()
            if name and name not in self.app.data["scripts"]:
                self.app.data["scripts"][name] = {
                    "interpreter": self.interpreter_var.get(),
                    "endpoint": self.endpoint_var.get(),
                    "code": self.script_text.get("1.0", tk.END)
                }
                self.listbox.insert(tk.END, name)
                save_data(self.app.data)
                btn_save.config(text="Saved", font=("Silkscreen", 9), bg="gray80")
                btn_save.after(2000, lambda: btn_save.config(text="Save"))

        btn_save = self.create_buttons(container, save_script)
        self.create_code_field()


    def display_script(self, event):
        """Отображение информации о выбранном скрипте."""
        selected = self.listbox.curselection()
        if selected:
            name = self.listbox.get(selected[0])
            script_data = self.app.data["scripts"][name]

            self.clear_content_frame()
            container, frame = self.create_form_container()
            self.create_script_fields(frame, name, script_data["interpreter"], script_data["endpoint"])

            def save_script():
                script_data["interpreter"] = self.interpreter_var.get()
                script_data["endpoint"] = self.endpoint_var.get()
                script_data["code"] = self.script_text.get("1.0", tk.END)
                save_data(self.app.data)
                btn_save.config(text="Saved", font=("Silkscreen", 9), bg="gray80")
                btn_save.after(2000, lambda: btn_save.config(text="Save"))

            btn_save = self.create_buttons(container, save_script)
            self.create_code_field(script_data["code"])
            self.add_syntax_highlighting(self.script_text, script_data["code"], script_data["interpreter"])


