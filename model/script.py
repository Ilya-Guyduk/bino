"""Module containing classes for Script and Endpoint configurations.

This module provides data models for scripts and flexible endpoints
used in the application. Script stores interpreter and execution data,
while Endpoint can be dynamically configured depending on its type.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


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
        if self.name in self.storage.scripts:
            return False, "Скрипт уже существует"
        self.storage.scripts[self.name] = self.to_dict()
        self.storage.save()
        return True, f"Скрипт '{self.name}' создан."

    def read(self, name) -> Optional["Script"]:
        """
        Retrieve a script from storage by name.
        """
        data = self.storage.scripts.get(name)
        return self.from_dict(self.storage, data) if data else None

    def update(self, old_name: str, new_name: str, script_data: Dict[str, Any]):
        """
        Update existing script in storage.
        """
        if old_name not in self.storage.scripts:
            return False, "Скрипт не найден"
        if old_name != new_name and new_name in self.storage.scripts:
            return False, "Имя уже занято"
        self.storage.scripts.pop(old_name)
        self.storage.scripts[new_name] = script_data
        self.storage.save()
        return True, f"Скрипт '{new_name}' обновлён."

    def delete(self):
        """
        Delete script from storage.
        """
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
