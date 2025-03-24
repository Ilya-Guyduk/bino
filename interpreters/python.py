import subprocess

class PythonInterpreter:
    def __init__(self, interpreter_args="-c"):
        """
        :param interpreter_args: Аргументы для интерпретатора (по умолчанию "-c")
        """
        self.available_options = {
            "-c": None,                          # Выполнение строки Python-кода
            "-m": None,                          # Запуск модуля как скрипта
            "--help": False,                     # Показывает справку по использованию Python
            "--version": False,                  # Показывает версию Python
            "-V": False,                         # Псевдоним для --version
            "-i": False,                         # Запускает интерактивную оболочку после выполнения скрипта
            "-u": False,                         # Включает небуферизованный режим вывода
            "-O": False,                         # Запускает в оптимизированном режиме (без assert, .pyo файлы)
            "-B": False,                         # Не создает .pyc файлы
            "-s": False,                         # Не загружать файл site.py
            "-S": False,                         # Не инициализировать стандартную библиотеку
            "--no-user-site": False,             # Не использовать директорию user-site
            "--user-site": False,                # Использует директорию user-site для модулей
            "--no-warn-script-location": False,  # Отключает предупреждения о местоположении исполнимых файлов
            "-v": False,                         # Включает подробный вывод, трассировку импорта
            "-X": None,                          # Устанавливает параметры интерпретатора (например, -X dev)
            "--check-hash-based-pycs": False,    # Отключает создание .pyc файлов на основе хеша
            "--enable-shared": False,            # Компилирует Python как разделяемую библиотеку
            "--with-pymalloc": False,            # Включает использование PyMalloc для памяти
            "--without-ensurepip": False,        # Отключает встроенный модуль ensurepip
            "--with-threads": False,             # Включает поддержку многопоточности
            "--without-gcc": False,              # Отключает поддержку компиляции C
            "--no-site": False,                  # Отключает загрузку модулей из site.py
            "--pythonpath": None,                # Устанавливает PYTHONPATH
            "--help-verbose": False,             # Подробная справка
            "--no-warn-implicit-python3": False  # Отключает предупреждения о неявном использовании Python 3
        }

        
        if interpreter_args:
            for key in interpreter_args:
                if key in self.available_options:
                    self.available_options[key] = interpreter_args[key]

    def format_command(self, script_code):
        """Форматирует команду для выполнения в bash."""
        return f"python3 {self.interpreter_args} \"{script_code}\""

    def execute(script_code):
        """Выполняет Python код."""
        command = self.format_command(script_code)
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
            return result.stdout, None  # Возвращаем вывод и ошибку (если она есть)
        except subprocess.CalledProcessError as e:
            return None, e.stderr
