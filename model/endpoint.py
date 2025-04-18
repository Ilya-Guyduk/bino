"""Module containing classes for Script and Endpoint configurations.

This module provides data models for scripts and flexible endpoints
used in the application. Script stores interpreter and execution data,
while Endpoint can be dynamically configured depending on its type.
"""

from typing import Optional, Dict, Any


class Endpoint:
    """
    Represents a flexible endpoint. Only 'name' and 'type' are fixed; other fields are dynamic.
    """

    def __init__(self, name: str = "", type_: str = "ssh", storage = None, **kwargs: Any) -> None:
        """
        Initialize an Endpoint instance.

        Args:
            name (str): Name of the endpoint.
            type (str): Type of the endpoint (e.g., ssh, sqlite).
            **kwargs (Any): Additional attributes depending on endpoint type.
        """
        self.name = name
        self.type_ = type_
        self._attributes: Dict[str, Any] = kwargs
        self.storage = storage

    def __getattr__(self, item: str) -> Any:
        """
        Allow access to dynamic attributes if they are not found in the fixed attributes.

        Args:
            item (str): Attribute name.

        Returns:
            Any: Attribute value or None if not found.
        """
        # Accessing dynamic attributes only if they are not fixed
        if item not in {"name", "type_", "_attributes"}:
            return self._attributes.get(item, None)
        # Fallback if attribute is fixed
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Allow setting of fixed or dynamic attributes.

        Args:
            key (str): Attribute name.
            value (Any): Attribute value.
        """
        # Fixed attributes (name, type) are handled by the parent
        if key in {"name", "type_", "storage", "_attributes"}:
            super().__setattr__(key, value)
        else:
            self._attributes[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Endpoint instance to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        return {
            "name": self.name,
            "type": self.type_,
            **self._attributes
        }

    @classmethod
    def from_dict(cls, storage, data: Dict[str, Any]) -> "Endpoint":
        """
        Create an Endpoint instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with endpoint data.

        Returns:
            Endpoint: A new Endpoint instance.
        """
        name = data.get("name", "")
        type_ = data.get("type", "")
        other = {k: v for k, v in data.items() if k not in {"name", "type"}}
        return cls(name=name, type_=type_, storage=storage, **other)

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation.

        Returns:
            str: Debug representation.
        """
        return f"<Endpoint name={self.name} type={self.type_}>"

    def __str__(self) -> str:
        """
        Return a readable string representation of the endpoint.

        Returns:
            str: Readable representation.
        """
        base = f"Endpoint:\n  Name : {self.name}\n  Type : {self.type_}"
        dynamic = "\n".join(
            f"  {k.capitalize():<8}: {('***' if k == 'password' else v) if v is not None else '-'}"
            for k, v in self._attributes.items()
        )
        return f"{base}\n{dynamic}" if dynamic else base
    
    def create(self):
        if self.name in self.storage.endpoints:
            return False, "Скрипт уже существует"
        self.storage.endpoints[self.name] = self.to_dict()
        self.storage.save()
        return True, f"Скрипт '{self.name}' создан."
    
    def read(self, name) -> "Endpoint":
        data = self.storage.endpoints.get(name)
        return self.from_dict(self.storage, data) if data else None
    
    def update(self, old_name, new_name, data):
        """Обновляет существующий скрипт."""
        if old_name not in self.storage.endpoints:
            return False, "Скрипт не найден"
        if old_name != new_name and new_name in self.storage.endpoints:
            return False, "Имя уже занято"
        self.storage.endpoints.pop(old_name)
        self.storage.endpoints[new_name] = data
        self.storage.save()
        return True, f"Скрипт '{new_name}' обновлён."

    def delete(self):
        if self.name in self.storage.endpoints:
            del self.storage.endpoints[self.name]
            self.storage.save()
            return True, f"Скрипт '{self.name}' удалён."
        return False, "Скрипт не найден."
    
    @classmethod
    def empty_model(cls) -> "Endpoint":
        return cls(name="", type_="", storage=None, **{})