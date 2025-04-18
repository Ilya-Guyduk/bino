import pytest
from model.endpoint import Endpoint


class DummyStorage:
    def __init__(self):
        self.endpoints = {}
        self.saved = False

    def save(self):
        self.saved = True


def test_create_endpoint_success():
    storage = DummyStorage()
    endpoint = Endpoint(name="ep1", type_="ssh", storage=storage, host="127.0.0.1")

    success, message = endpoint.create()
    
    assert success is True
    assert "создан" in message
    assert "ep1" in storage.endpoints
    assert storage.saved is True


def test_create_endpoint_already_exists():
    storage = DummyStorage()
    storage.endpoints["ep1"] = {}
    
    endpoint = Endpoint(name="ep1", type_="ssh", storage=storage)

    success, message = endpoint.create()
    
    assert success is False
    assert "уже существует" in message


def test_read_endpoint_found():
    storage = DummyStorage()
    storage.endpoints["ep1"] = {
        "name": "ep1",
        "type": "ssh",
        "host": "localhost"
    }

    endpoint = Endpoint(storage=storage).read("ep1")

    assert isinstance(endpoint, Endpoint)
    assert endpoint.name == "ep1"
    assert endpoint.host == "localhost"


def test_read_endpoint_not_found():
    storage = DummyStorage()
    endpoint = Endpoint(storage=storage).read("not_exist")
    assert endpoint is None


def test_update_endpoint_success():
    storage = DummyStorage()
    storage.endpoints["old"] = {"name": "old", "type": "ssh"}

    ep = Endpoint(storage=storage)
    success, message = ep.update("old", "new", {"name": "new", "type": "ssh"})

    assert success is True
    assert "обновлён" in message
    assert "new" in storage.endpoints
    assert "old" not in storage.endpoints


def test_update_endpoint_conflict():
    storage = DummyStorage()
    storage.endpoints["ep1"] = {"name": "ep1", "type": "ssh"}
    storage.endpoints["ep2"] = {"name": "ep2", "type": "ssh"}

    ep = Endpoint(storage=storage)
    success, message = ep.update("ep1", "ep2", {"name": "ep2", "type": "ssh"})

    assert success is False
    assert "Имя уже занято" in message


def test_update_endpoint_not_found():
    storage = DummyStorage()
    ep = Endpoint(storage=storage)
    success, message = ep.update("ghost", "new", {})
    assert success is False
    assert "не найден" in message


def test_delete_endpoint_success():
    storage = DummyStorage()
    storage.endpoints["ep1"] = {"name": "ep1", "type": "ssh"}

    ep = Endpoint(name="ep1", storage=storage)
    success, message = ep.delete()

    assert success is True
    assert "удалён" in message
    assert "ep1" not in storage.endpoints


def test_delete_endpoint_not_found():
    storage = DummyStorage()
    ep = Endpoint(name="ghost", storage=storage)
    success, message = ep.delete()

    assert success is False
    assert "не найден" in message


def test_dynamic_attributes():
    endpoint = Endpoint(name="dyn", type_="sqlite", path="/db.sqlite", storage=None)

    assert endpoint.path == "/db.sqlite"
    endpoint.port = 8080
    assert endpoint.port == 8080
    assert endpoint.to_dict()["port"] == 8080

def test_getattr_non_existent_attribute():
    """
    Проверяем, что если запрашиваем несуществующий атрибут, возвращается None.
    """
    storage = DummyStorage()
    endpoint = Endpoint(name="ep1", type_="ssh", storage=storage, host="127.0.0.1")

    # Запрашиваем несуществующий атрибут
    assert endpoint.non_existent_attribute is None


def test_getattr_fixed_attribute():
    """
    Проверяем, что фиксированные атрибуты доступны напрямую,
    и __getattr__ не мешает их работе.
    """
    storage = DummyStorage()
    endpoint = Endpoint(name="ep1", type_="ssh", storage=storage, host="127.0.0.1")

    assert endpoint.name == "ep1"
    assert endpoint.type_ == "ssh"
    assert endpoint.storage is storage

def test_getattr_dynamic_attribute():
    endpoint = Endpoint(name="ep1", type_="ssh", host="127.0.0.1")
    assert endpoint.host == "127.0.0.1"

def test_getattr_nonexistent_attribute_returns_none():
    endpoint = Endpoint(name="ep1", type_="ssh")
    assert endpoint.nonexistent is None



def test_empty_model():
    """
    Проверяем метод empty_model.
    """
    endpoint = Endpoint.empty_model()
    assert isinstance(endpoint, Endpoint)
    assert endpoint.name == ""
    assert endpoint.type_ == ""
    assert endpoint.storage == None
    assert endpoint._attributes == {}
