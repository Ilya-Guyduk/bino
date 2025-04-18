import pytest
from model.script import Script

class MockStorage:
    def __init__(self):
        self.scripts = {}
        self.saved = False

    def save(self):
        self.saved = True

@pytest.fixture
def storage():
    return MockStorage()

def test_to_dict_returns_correct_structure(storage):
    script = Script(
        name="test_script",
        interpreter="bash",
        code="echo Hello",
        endpoint="test",
        options={"timeout": 10},
        storage=storage
    )
    result = script.to_dict()
    assert result == {
        "name": "test_script",
        "interpreter": "bash",
        "code": "echo Hello",
        "endpoint": "test",
        "options": {"timeout": 10}
    }

def test_create_success(storage):
    script = Script(name="new_script", storage=storage)
    success, msg = script.create()
    assert success is True
    assert "создан" in msg
    assert "new_script" in storage.scripts
    assert storage.saved is True

def test_create_duplicate(storage):
    storage.scripts["new_script"] = {}
    script = Script(name="new_script", storage=storage)
    success, msg = script.create()
    assert success is False
    assert "уже существует" in msg

def test_read_existing_script(storage):
    data = {
        "name": "hello",
        "interpreter": "python",
        "code": "print('hi')",
        "endpoint": "api/test",
        "options": {"debug": True}
    }
    storage.scripts["hello"] = data
    dummy = Script(storage=storage)
    result = dummy.read("hello")
    assert isinstance(result, Script)
    assert result.name == "hello"
    assert result.code == "print('hi')"
    assert result.options["debug"] is True

def test_read_missing_script_returns_none(storage):
    dummy = Script(storage=storage)
    assert dummy.read("missing") is None

def test_update_existing_script(storage):
    storage.scripts["old"] = {"name": "old"}
    script = Script(name="old", storage=storage)
    success, msg = script.update("old", "new", {"name": "new"})
    assert success is True
    assert "обновлён" in msg
    assert "old" not in storage.scripts
    assert "new" in storage.scripts
    assert storage.saved is True

def test_update_name_conflict(storage):
    storage.scripts["old"] = {}
    storage.scripts["new"] = {}
    script = Script(name="old", storage=storage)
    success, msg = script.update("old", "new", {})
    assert success is False
    assert "Имя уже занято" in msg

def test_update_nonexistent_script(storage):
    script = Script(name="notfound", storage=storage)
    success, msg = script.update("notfound", "anything", {})
    assert success is False
    assert "не найден" in msg

def test_delete_existing_script(storage):
    storage.scripts["deleteme"] = {}
    script = Script(name="deleteme", storage=storage)
    success, msg = script.delete()
    assert success is True
    assert "удалён" in msg
    assert "deleteme" not in storage.scripts
    assert storage.saved is True

def test_delete_missing_script(storage):
    script = Script(name="ghost", storage=storage)
    success, msg = script.delete()
    assert success is False
    assert "не найден" in msg

def test_empty_model_returns_default_instance():
    empty = Script.empty_model()
    assert isinstance(empty, Script)
    assert empty.name == ""
    assert empty.interpreter == "python"

def test_from_dict_creates_valid_script():
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