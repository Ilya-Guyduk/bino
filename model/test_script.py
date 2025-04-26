import pytest
from model.script import Script

class MockStorage:
    """
    Mock storage class to simulate saving and retrieving scripts.
    """
    def __init__(self):
        self.scripts = {}
        self.saved = False

    def save(self):
        """
        Simulate saving data to storage.
        """
        self.saved = True

@pytest.fixture
def mock_storage():
    """
    Fixture for MockStorage to simulate storage operations during tests.
    """
    return MockStorage()

def test_to_dict_returns_correct_structure(mock_storage):
    """
    Test that the to_dict method returns the correct structure.
    """
    storage_instance = mock_storage
    script = Script(
        name="test_script",
        interpreter="bash",
        code="echo Hello",
        endpoint="test",
        options={"timeout": 10},
        storage=storage_instance
    )
    result = script.to_dict()
    assert result == {
        "name": "test_script",
        "interpreter": "bash",
        "code": "echo Hello",
        "endpoint": "test",
        "options": {"timeout": 10}
    }

def test_create_success(mock_storage):
    """
    Test that a new script is successfully created and stored.
    """
    storage_instance = mock_storage
    script = Script(name="new_script", storage=storage_instance)
    success, msg = script.create()
    assert success is True
    assert "создан" in msg
    assert "new_script" in storage_instance.scripts
    assert storage_instance.saved is True

def test_create_duplicate(mock_storage):
    """
    Test that creating a script with a duplicate name fails.
    """
    mock_storage.scripts["new_script"] = {}
    script = Script(name="new_script", storage=mock_storage)
    success, msg = script.create()
    assert success is False
    assert "уже существует" in msg

def test_read_existing_script(mock_storage):
    """
    Test reading an existing script from storage.
    """
    data = {
        "name": "hello",
        "interpreter": "python",
        "code": "print('hi')",
        "endpoint": "api/test",
        "options": {"debug": True}
    }
    mock_storage.scripts["hello"] = data
    dummy = Script(storage=mock_storage)
    result = dummy.read("hello")
    assert isinstance(result, Script)
    assert result.name == "hello"
    assert result.code == "print('hi')"
    assert result.options["debug"] is True

def test_read_missing_script_returns_none(mock_storage):
    """
    Test reading a non-existent script returns None.
    """
    dummy = Script(storage=mock_storage)
    assert dummy.read("missing") is None

def test_update_existing_script(mock_storage):
    """
    Test updating an existing script in storage.
    """
    mock_storage.scripts["old"] = {"name": "old"}
    script = Script(name="old", storage=mock_storage)
    success, msg = script.update("old", "new", {"name": "new"})
    assert success is True
    assert "обновлён" in msg
    assert "old" not in mock_storage.scripts
    assert "new" in mock_storage.scripts
    assert mock_storage.saved is True

def test_update_name_conflict(mock_storage):
    """
    Test updating a script to a name that already exists in storage.
    """
    mock_storage.scripts["old"] = {}
    mock_storage.scripts["new"] = {}
    script = Script(name="old", storage=mock_storage)
    success, msg = script.update("old", "new", {})
    assert success is False
    assert "Имя уже занято" in msg

def test_update_nonexistent_script(mock_storage):
    """
    Test attempting to update a script that does not exist.
    """
    script = Script(name="notfound", storage=mock_storage)
    success, msg = script.update("notfound", "anything", {})
    assert success is False
    assert "не найден" in msg

def test_delete_existing_script(mock_storage):
    """
    Test deleting an existing script from storage.
    """
    mock_storage.scripts["deleteme"] = {}
    script = Script(name="deleteme", storage=mock_storage)
    success, msg = script.delete()
    assert success is True
    assert "удалён" in msg
    assert "deleteme" not in mock_storage.scripts
    assert mock_storage.saved is True

def test_delete_missing_script(mock_storage):
    """
    Test attempting to delete a script that does not exist.
    """
    script = Script(name="ghost", storage=mock_storage)
    success, msg = script.delete()
    assert success is False
    assert "не найден" in msg

def test_empty_model_returns_default_instance():
    """
    Test the empty model method to ensure it returns a default instance of Script.
    """
    empty = Script.empty_model()
    assert isinstance(empty, Script)
    assert empty.name == ""
    assert empty.interpreter == "python"

def test_from_dict_creates_valid_script():
    """
    Test that the from_dict method creates a valid Script object from a dictionary.
    """
    data = {
        "name": "test",
        "interpreter": "bash",
        "code": "ls",
        "endpoint": "sys",
        "options": {"a": 1}
    }
    script = Script.from_dict(data_storage=None, data=data)
    assert script.name == "test"
    assert script.interpreter == "bash"
    assert script.options["a"] == 1
