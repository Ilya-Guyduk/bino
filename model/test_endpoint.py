"""unit-tests for endpoint model"""
import pytest
from model.endpoint import Endpoint


class DummyStorage:
    """
    Dummy storage class to simulate endpoint storage behavior.
    """
    def __init__(self):
        self.endpoints = {}
        self.saved = False

    def save(self):
        """
        Simulate saving the storage.
        """
        self.saved = True


def test_create_endpoint_success():
    """
    Test case for successful creation of an endpoint.
    """
    storage = DummyStorage()
    endpoint = Endpoint(name="ep1", type_="ssh", storage=storage, host="127.0.0.1")

    success, message = endpoint.create()

    assert success is True
    assert "создан" in message
    assert "ep1" in storage.endpoints
    assert storage.saved is True


def test_create_endpoint_already_exists():
    """
    Test case when trying to create an endpoint that already exists.
    """
    storage = DummyStorage()
    storage.endpoints["ep1"] = {}

    endpoint = Endpoint(name="ep1", type_="ssh", storage=storage)

    success, message = endpoint.create()

    assert success is False
    assert "уже существует" in message


def test_read_endpoint_found():
    """
    Test case for reading an endpoint that exists in storage.
    """
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
    """
    Test case when reading a non-existent endpoint.
    """
    storage = DummyStorage()
    endpoint = Endpoint(storage=storage).read("not_exist")
    assert endpoint is None


def test_update_endpoint_success():
    """
    Test case for successfully updating an endpoint.
    """
    storage = DummyStorage()
    storage.endpoints["old"] = {"name": "old", "type": "ssh"}

    ep = Endpoint(storage=storage)
    success, message = ep.update("old", "new", {"name": "new", "type": "ssh"})

    assert success is True
    assert "обновлён" in message
    assert "new" in storage.endpoints
    assert "old" not in storage.endpoints


def test_update_endpoint_conflict():
    """
    Test case when trying to update an endpoint with a name that already exists.
    """
    storage = DummyStorage()
    storage.endpoints["ep1"] = {"name": "ep1", "type": "ssh"}
    storage.endpoints["ep2"] = {"name": "ep2", "type": "ssh"}

    ep = Endpoint(storage=storage)
    success, message = ep.update("ep1", "ep2", {"name": "ep2", "type": "ssh"})

    assert success is False
    assert "Имя уже занято" in message


def test_update_endpoint_not_found():
    """
    Test case when trying to update an endpoint that does not exist.
    """
    storage = DummyStorage()
    ep = Endpoint(storage=storage)
    success, message = ep.update("ghost", "new", {})
    assert success is False
    assert "не найден" in message


def test_delete_endpoint_success():
    """
    Test case for successfully deleting an endpoint.
    """
    storage = DummyStorage()
    storage.endpoints["ep1"] = {"name": "ep1", "type": "ssh"}

    ep = Endpoint(name="ep1", storage=storage)
    success, message = ep.delete()

    assert success is True
    assert "удалён" in message
    assert "ep1" not in storage.endpoints


def test_delete_endpoint_not_found():
    """
    Test case when trying to delete an endpoint that does not exist.
    """
    storage = DummyStorage()
    ep = Endpoint(name="ghost", storage=storage)
    success, message = ep.delete()

    assert success is False
    assert "не найден" in message


def test_dynamic_attributes():
    """
    Test dynamic attributes assignment and retrieval.
    """
    endpoint = Endpoint(name="dyn", type_="sqlite", path="/db.sqlite", storage=None)

    assert endpoint.path == "/db.sqlite"
    endpoint.port = 8080
    assert endpoint.port == 8080
    assert endpoint.to_dict()["port"] == 8080


def test_getattr_non_existent_attribute():
    """
    Test if requesting a non-existent attribute returns None.
    """
    storage = DummyStorage()
    endpoint = Endpoint(name="ep1", type_="ssh", storage=storage, host="127.0.0.1")

    assert endpoint.non_existent_attribute is None


def test_getattr_fixed_attribute():
    """
    Test if fixed attributes are accessed correctly, and __getattr__ does not interfere.
    """
    storage = DummyStorage()
    endpoint = Endpoint(name="ep1", type_="ssh", storage=storage, host="127.0.0.1")

    assert endpoint.name == "ep1"
    assert endpoint.type_ == "ssh"
    assert endpoint.storage is storage


def test_getattr_dynamic_attribute():
    """
    Test if dynamic attributes are accessible directly.
    """
    endpoint = Endpoint(name="ep1", type_="ssh", host="127.0.0.1")
    assert endpoint.host == "127.0.0.1"


def test_getattr_nonexistent_attribute_returns_none():
    """
    Test if a non-existent dynamic attribute returns None.
    """
    endpoint = Endpoint(name="ep1", type_="ssh")
    assert endpoint.nonexistent is None


def test_empty_model():
    """
    Test the empty_model method.
    """
    endpoint = Endpoint.empty_model()
    assert isinstance(endpoint, Endpoint)
    assert endpoint.name == ""
    assert endpoint.type_ == ""
    assert endpoint.storage is None
    assert not endpoint._attributes  # Use implicit booleaness to check for an empty dictionary.
