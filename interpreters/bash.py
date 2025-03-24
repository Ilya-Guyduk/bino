import subprocess

class BashInterpreter:
    def __init__(self, interpreter_args=None):
        """
        :param interpreter_args: Словарь с аргументами интерпретатора
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

    def format_command(self, script_code, options):
        """Форматирует команду для выполнения в bash."""
        options = " ".join([key for key, value in options.items() if value])
        return f"bash {options} -c \"{script_code}\""

    def execute(self, script_code, options):
        """Выполняет команду в Bash."""
        command = self.format_command(script_code, options)
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return result.stdout, None  # Возвращаем вывод и ошибку (если она есть)
        except subprocess.CalledProcessError as e:
            return None, e.stderr