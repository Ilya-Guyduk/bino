"""Module containing classes for Script and Endpoint configurations.

This module provides data models for scripts and flexible endpoints
used in the application. Script stores interpreter and execution data,
while Endpoint can be dynamically configured depending on its type.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Script:
    """
    Represents a script configuration with interpreter, code, endpoint and options.
    """

    name: str = ""
    interpreter: str = "python"
    code: str = ""
    endpoint: str = ""
    options: Dict[str, Any] = field(default_factory=dict)
    storage: Any = field(default=None, repr=False, compare=False)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Script instance to dictionary (excluding storage).
        """
        return {
            "name": self.name,
            "interpreter": self.interpreter,
            "code": self.code,
            "endpoint": self.endpoint,
            "options": self.options
        }

    def create(self):
        """
        Create a new script in the storage.
        """
        logger.debug("Script.create() -> call")
        logger.info("Script.create() -> '%s'", self)

        ret_code = True
        message = ""

        if str(self.name) == "":
            ret_code, message = False, "Не указано имя"
        if str(self.interpreter) == "":
            ret_code, message = False, "Не указан интерпретатор"
        if str(self.endpoint) == "":
            ret_code, message = False, "Не указан ендпоинт"
        if self.name in self.storage.scripts:
            ret_code, message = False, "Скрипт уже существует"

        if ret_code:
            self.storage.scripts[self.name] = self.to_dict()
            self.storage.save()
            ret_code, message = True, f"Скрипт '{self.name}' создан."

        logger.info("Script.create() -> Tuple[%s, %s]", ret_code, message)
        return ret_code, message

    def read(self, name) -> Optional["Script"]:
        """
        Retrieve a script from storage by name.
        """
        logger.debug("Script.read(name=%s) -> call", name)

        data = self.storage.scripts.get(name)
        if data:
            result = self.from_dict(self.storage, data)
        else:
            result = None
        logger.info("Script.read(name=%s) -> '%s'", name, result)
        return result

    def update(self, old_name: str, new_name: str, script_data: Dict[str, Any]):
        """
        Update existing script in storage.
        """
        logger.debug("Script.update(old_name=%s, new_name=%s, script_data=%s) -> call", old_name, new_name, script_data)

        ret_code = True
        message = ""

        if not new_name:
            ret_code, message = False, "Не указано имя"
        if not script_data["interpreter"]:
            ret_code, message = False, "Не указан интерпретатор"
        if old_name not in self.storage.scripts:
            ret_code, message = False, "Скрипт не найден"
        if old_name != new_name and new_name in self.storage.scripts:
            ret_code, message = False, "Имя уже занято"

        if ret_code:
            self.storage.scripts.pop(old_name)
            self.storage.scripts[new_name] = script_data
            self.storage.save()
            ret_code, message = True, f"Скрипт '{new_name}' обновлён."

        logger.info("Script.update() -> Tuple[%s, %s]", ret_code, message)
        return ret_code, message

    def delete(self):
        """
        Delete script from storage.
        """
        logger.debug("Script.delete() -> call")
        logger.info("Script.delete() -> '%s'", self)

        if self.name in self.storage.scripts:
            del self.storage.scripts[self.name]
            self.storage.save()
            return True, f"Скрипт '{self.name}' удалён."
        return False, "Скрипт не найден."

    @classmethod
    def empty_model(cls) -> "Script":
        """
        Return an empty Script model.
        """
        logger.debug("Script.empty_model() -> call")
        return cls()

    @classmethod
    def from_dict(cls, storage: Any, data: Dict[str, Any]) -> "Script":
        """
        Create Script instance from dictionary.
        """
        return cls(
            storage=storage,
            name=data.get("name", ""),
            interpreter=data.get("interpreter", "python"),
            code=data.get("code", ""),
            endpoint=data.get("endpoint", ""),
            options=data.get("options", {})
        )

    def __str__(self) -> str:
        return (
            f"Script:\n"
            f"  Name        : {self.name}\n"
            f"  Interpreter : {self.interpreter}\n"
            f"  Endpoint    : {self.endpoint}\n"
            f"  Code        : {self.code.strip()[:50]}{'...' if len(self.code.strip()) > 50 else ''}\n"
            f"  Options     : {self.options}"
        )
