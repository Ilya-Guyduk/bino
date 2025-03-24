import subprocess

class PythonInterpreter:
    def __init__(self, interpreter_args="-c"):
        """
        :param interpreter_args: Аргументы для интерпретатора (по умолчанию "-c")
        """
        self.available_options = {
            "--debug": False,
            "--debugger": False,
            "--dump-po-strings": False,
            "--dump-strings": False,
            "--help": False,
            "--init-file": False,
            "--login": False,
            "--noediting": False,
            "--noprofile": False,
            "--norc": False,
            "--posix": False,
            "--pretty-print": False,
            "--rcfile": False,
            "--restricted": False,
            "--verbose": False,
            "--version": False
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
