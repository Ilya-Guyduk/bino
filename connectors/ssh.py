import paramiko
from typing import Dict, Any, List
from .base_connector import BaseConnector


class SshConnector(BaseConnector):
    """
    SSH-коннектор для подключения к удалённым серверам по SSH.
    """

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


    def get_required_fields(self) -> List[str]:
        """
        Возвращает список обязательных полей для подключения по SSH.
        """
        return ["ip", "port", "login", "password"]

    def connect(self, params: Dict[str, Any]) -> paramiko.SSHClient:
        """
        Подключается к SSH-серверу и возвращает клиент.
        """
        self.validate_params(params)  # Проверяем, что все параметры на месте
        print(params)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=params["ip"],
            port=int(params["port"]),
            username=params["login"],
            password=params["password"],
            timeout=params.get("timeout", 5),
            allow_agent=params.get("allow_agent", False),
            look_for_keys=params.get("look_for_keys", False),
            key_filename=params.get("key_filename", None),
            passphrase=params.get("passphrase", None),
            auth_timeout=params.get("auth_timeout", 10),
            banner_timeout=params.get("banner_timeout", 15),
            compress=params.get("compress", False),
            disabled_algorithms=params.get("disabled_algorithms", None),
            sock=params.get("sock", None),
            gss_auth=params.get("gss_auth", False),
            gss_kex=params.get("gss_kex", False)
        )
        return client

    def test_connection(self, params: Dict[str, Any]) -> bool:
        """
        Проверяет возможность SSH-подключения.
        """
        try:
            client = self.connect(params)
            client.close()
            return True, ""
        except paramiko.AuthenticationException:
            return False, "Ошибка аутентификации. Проверьте логин/пароль."
        except paramiko.SSHException as e:
            return False, e
        except Exception as e:
            return False, e
        return False