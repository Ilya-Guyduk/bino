"""Module containing classes for Script and Endpoint configurations.

This module provides data models for scripts and flexible endpoints
used in the application. Script stores interpreter and execution data,
while Endpoint can be dynamically configured depending on its type.
"""

from typing import Optional, Dict, Any


class Script:
    """
    Represents a script configuration with interpreter, code, endpoint and options.
    """

    def __init__(
        self,
        name: str = "",
        interpreter: str = "python",
        code: str = "",
        endpoint: str = "",
        options: Optional[Dict[str, Any]] = None,
        storage = None
    ) -> None:
        """
        Initialize a Script instance.

        Args:
            name (str): Name of the script.
            interpreter (str): Interpreter to run the script.
            code (str): Script source code.
            endpoint (str): Name of the endpoint the script is associated with.
            options (Optional[Dict[str, Any]]): Execution options or flags.
        """
        self.name: str = name
        self.interpreter: str = interpreter
        self.code: str = code
        self.endpoint: str = endpoint
        self.options: Dict[str, Any] = options if options is not None else {}
        self.storage = storage


    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Script instance to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the script.
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

        Returns:
            Tuple[bool, str]: Success status and message.
        """
        if self.name in self.storage.scripts:
            return False, "Скрипт уже существует"
        self.storage.scripts[self.name] = self.to_dict()
        self.storage.save()
        return True, f"Скрипт '{self.name}' создан."

    def read(self, name) -> "Script":
        """
        Retrieve a script from storage by its name.

        Args:
            name (str): Name of the script.

        Returns:
            Script or None: The script instance or None if not found.
        """
        data = self.storage.scripts.get(name)
        return self.from_dict(self.storage, data) if data else None

    def update(self, old_name, new_name, script_data):
        """
        Update an existing script in the storage.

        Args:
            old_name (str): Current name of the script.
            new_name (str): New name for the script.
            script_data (dict): Updated script data.

        Returns:
            Tuple[bool, str]: Success status and message.
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
        Delete the script from the storage.

        Returns:
            Tuple[bool, str]: Success status and message.
        """
        if self.name in self.storage.scripts:
            del self.storage.scripts[self.name]
            self.storage.save()
            return True, f"Скрипт '{self.name}' удалён."
        return False, "Скрипт не найден."

    @classmethod
    def empty_model(cls) -> "Script":
        """
        Create and return an empty Script model instance.

        Returns:
            Script: An instance of Script with default values.
        """
        return cls()

    @classmethod
    def from_dict(cls, data_storage, data: Dict[str, Any]) -> "Script":
        """
        Create a Script instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing script data.

        Returns:
            Script: A new Script instance.
        """
        return cls(
            storage=data_storage,
            name=data.get("name", ""),
            interpreter=data.get("interpreter", "python"),
            code=data.get("code", ""),
            endpoint=data.get("endpoint", ""),
            options=data.get("options", {})
        )

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation.

        Returns:
            str: Debug representation.
        """
        return f"<Script name={self.name} interpreter={self.interpreter}>"

    def __str__(self) -> str:
        """
        Return a readable string representation of the script.

        Returns:
            str: Readable representation.
        """
        return (
            f"Script:\n"
            f"  Name        : {self.name}\n"
            f"  Interpreter : {self.interpreter}\n"
            f"  Endpoint    : {self.endpoint}\n"
            f"  Code        : {self.code.strip()[:50]}{'...' if len(self.code.strip()) > 50 else ''}\n"
            f"  Options     : {self.options}"
        )
