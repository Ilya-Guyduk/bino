import subprocess
from typing import Dict, Any, List

class BashInterpreter:
    def __init__(self, interpreter_args=None):
        """
        :param interpreter_args: Словарь с аргументами интерпретатора
        """
        self.available_options: Dict[str, Dict[str, Any]] = self.default_options()

    def default_options(self) -> Dict[str, Dict[str, Any]]:
        """
        Возвращает настройки по умолчанию для SSH-коннектора.
        """

        return {
            "timeout": {
                "type": int,
                "description": "Таймаут подключения (в секундах)",
                "value": 5
            },
            "allow_agent": {
                "type": bool,
                "description": "Разрешить использование SSH-агента",
                "value": False
            },
            "look_for_keys": {
                "type": bool,
                "description": "Искать ключи для аутентификации в стандартных местах",
                "value": False
            },
            "key_filename": {
                "type": str,
                "description": "Путь к файлу приватного ключа",
                "value": None
            },
            "passphrase": {
                "type": str,
                "description": "Парольная фраза для ключа",
                "value": None
            },
            "auth_timeout": {
                "type": int,
                "description": "Таймаут аутентификации (в секундах)",
                "value": 10
            },
            "banner_timeout": {
                "type": int,
                "description": "Таймаут ожидания баннера SSH (в секундах)",
                "value": 15
            },
            "compress": {
                "type": bool,
                "description": "Использование сжатия",
                "value": False
            },
            "disabled_algorithms": {
                "type": list,
                "description": "Список отключённых алгоритмов для SSH",
                "value": None
            },
            "sock": {
                "type": object,
                "description": "Предустановленное сокет-соединение",
                "value": None
            },
            "gss_auth": {
                "type": bool,
                "description": "Использование GSS-API аутентификации",
                "value": False
            },
            "gss_kex": {
                "type": bool,
                "description": "Использование GSS-API для обмена ключами",
                "value": False
            }
        }


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