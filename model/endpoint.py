from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class Endpoint:
    """
    Represents a flexible endpoint. Only 'name' and 'type_' are fixed; other fields are dynamic.
    """

    name: str = ""
    type_: str = "ssh"
    storage: Any = field(default=None, repr=False, compare=False)
    options: Dict[str, Any] = field(default_factory=dict)
    _attributes: Dict[str, Any] = field(default_factory=dict, repr=False)

    def __getattr__(self, item: str) -> Any:
        """
        Allow access to dynamic attributes.
        """
        if item not in {"name", "type_", "storage", "options", "_attributes"}:
            return self._attributes.get(item, None)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Allow setting dynamic attributes as if they were real fields.
        """
        if key in {"name", "type_","options", "storage", "_attributes"}:
            super().__setattr__(key, value)
        else:
            self._attributes[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Endpoint instance to dictionary.
        """
        return {
            "name": self.name,
            "type": self.type_,
            "options": self.options,
            **self._attributes
        }

    @classmethod
    def from_dict(cls, storage, data: Dict[str, Any]) -> "Endpoint":
        """
        Create Endpoint from dictionary.
        """
        name = data.get("name", "")
        type_ = data.get("type", "")
        options = data.get("options", {})
        other = {k: v for k, v in data.items() if k not in {"name", "type"}}
        return cls(name=name, type_=type_, storage=storage, options=options, _attributes=other)

    def __str__(self) -> str:
        base = f"Endpoint:\n  Name : {self.name}\n  Type : {self.type_}\n  Options : {self.options}"
        dynamic = "\n".join(
            f"  {k.capitalize():<8}: {('***' if k == 'password' else v) if v is not None else '-'}"
            for k, v in self._attributes.items()
        )
        return f"{base}\n{dynamic}" if dynamic else base

    def __repr__(self) -> str:
        return f"<Endpoint name={self.name} type={self.type_}>"

    def create(self) -> Tuple[bool, str]:
        logger.debug("Endpoint.create() -> call")
        logger.info("Endpoint.create() -> '%s'", self)

        ret_code = True
        message = ""

        if str(self.name) == "":
            ret_code, message = False, "Не указано имя"
        if str(self.type_) == "":
            ret_code, message = False, "Не указан тип"
        if self.name in self.storage.endpoints:
            ret_code, message = False, "Ендпоинт уже существует"

        if ret_code:
            self.storage.endpoints[self.name] = self.to_dict()
            self.storage.save()
            ret_code, message = True, f"Ендпоинт '{self.name}' создан"

        logger.info("Endpoint.create() -> Tuple[%s, %s]", ret_code, message)
        return ret_code, message

    def read(self, name: str) -> "Endpoint":
        logger.debug("Endpoint.read(name=%s) -> call", name)
        data = self.storage.endpoints.get(name)
        if data:
            result = self.from_dict(self.storage, data)
        else:
            result = None
        logger.info("Endpoint.read(name=%s) -> '%s'", name, result)
        return result

    def update(self, old_name: str, new_name: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        logger.debug("Endpoint.update(old_name=%s, new_name=%s, data=%s) -> call", old_name, new_name, data)

        ret_code = True
        message = ""

        if not new_name:
            ret_code, message = False, "Не указано имя"
        if not data["type"]:
            ret_code, message = False, "Не указан тип"
        if old_name not in self.storage.endpoints:
            ret_code, message = False, "Ендпоинт не найден"
        if old_name != new_name and new_name in self.storage.endpoints:
            ret_code, message = False, "Имя уже занято"

        if ret_code:
            self.storage.endpoints.pop(old_name)
            self.storage.endpoints[new_name] = data
            self.storage.save()
            ret_code, message = True, f"Ендпоинт '{new_name}' обновлён."

        logger.info("Endpoint.update() -> Tuple[%s, %s]", ret_code, message)
        return ret_code, message

    def delete(self) -> Tuple[bool, str]:
        logger.debug("Endpoint.delete() -> call")
        logger.info("Endpoint.delete() -> '%s'", self)

        if self.name in self.storage.endpoints:
            del self.storage.endpoints[self.name]
            self.storage.save()

            logger.info("Endpoint.delete() -> Tuple[%s, %s]", True, f"Ендпоинт '{self.name}' удалён.")
            return True, f"Ендпоинт '{self.name}' удалён."

        logger.warning("Endpoint.delete() -> Tuple[%s, %s]", False, "Ендпоинт не найден.")
        return False, "Ендпоинт не найден."

    @classmethod
    def empty_model(cls) -> "Endpoint":
        logger.debug("Endpoint.empty_model() -> call")
        result = cls(name="", type_="ssh", storage=None, options={}, _attributes={})
        logger.info("Endpoint.empty_model() -> '%s'", result)
        return result
