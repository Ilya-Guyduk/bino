from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type


class BaseConnector(ABC):
    """
    Абстрактный класс для всех коннекторов.
    Определяет интерфейс взаимодействия с удалёнными сервисами.
    """

    def __init__(self) -> None:
        """
        Инициализирует базовый коннектор.
        """
        self.available_options: Dict[str, Dict[str, Any]] = self.default_options()
        self.required_fields: List[str] = self.get_required_fields()

    @abstractmethod
    def default_options(self) -> Dict[str, Dict[str, Any]]:
        """
        Возвращает настройки по умолчанию для коннектора.
        """
        pass

    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """
        Возвращает список обязательных полей для подключения.
        """
        pass

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Проверяет, что переданы все необходимые параметры.

        :param params: Словарь с параметрами подключения.
        :return: True, если все параметры на месте, иначе False.
        :raises ValueError: Если какого-то параметра нет.
        """
        missing_fields = [field for field in self.required_fields if field not in params or not params[field]]
        if missing_fields:
            raise ValueError(f"Отсутствуют обязательные параметры: {', '.join(missing_fields)}")
        return True

    @abstractmethod
    def connect(self, params: Dict[str, Any]) -> Any:
        """
        Устанавливает соединение и возвращает объект соединения.

        :param params: Параметры подключения.
        :return: Объект соединения.
        """
        pass

    @abstractmethod
    def test_connection(self, params: Dict[str, Any]) -> bool:
        """
        Проверяет возможность подключения.

        :param params: Параметры подключения.
        :return: `True`, если подключение успешно, иначе `False`.
        """
        pass
