import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch

from controller.controller import FormHandler


@pytest.fixture
def dummy_app():
    """Создает поддельное приложение с нужными полями."""
    app = MagicMock()
    app.root = MagicMock()
    app.storage = MagicMock()
    app.scripts_frame = tk.Frame()
    app.endpoints_frame = tk.Frame()
    app.content_frame = tk.Frame()
    app.data = {
        "scripts": ["script1", "script2"],
        "endpoints": ["endpoint1"]
    }
    return app


@patch("controller.controller.ScriptUI")
@patch("controller.controller.ScriptBackend")
@patch("controller.controller.Script")
def test_form_handler_init_scripts(mock_model, mock_backend, mock_ui, dummy_app):
    handler = FormHandler(app=dummy_app, obj_type="scripts")

    assert handler._type == "scripts"
    assert handler.controller == mock_backend.return_value
    assert handler.view == mock_ui.return_value
    assert isinstance(handler.listbox, tk.Listbox)
    assert handler.listbox.size() == 2  # Загружены script1 и script2


@patch("controller.controller.EndpointUI")
@patch("controller.controller.EndpointBackend")
@patch("controller.controller.Endpoint")
def test_form_handler_init_endpoints(mock_model, mock_backend, mock_ui, dummy_app):
    handler = FormHandler(app=dummy_app, obj_type="endpoints")

    assert handler._type == "endpoints"
    assert handler.controller == mock_backend.return_value
    assert handler.view == mock_ui.return_value
    assert isinstance(handler.listbox, tk.Listbox)
    assert handler.listbox.size() == 1  # Загружен endpoint1


def test_clear_content_frame_removes_widgets(dummy_app):
    dummy_widget = tk.Label(dummy_app.content_frame, text="Test")
    dummy_widget.pack()
    assert len(dummy_app.content_frame.winfo_children()) == 1

    handler = FormHandler(app=dummy_app, obj_type="scripts")
    handler.clear_content_frame()
    assert len(dummy_app.content_frame.winfo_children()) == 0


@patch("controller.controller.ScriptUI")
@patch("controller.controller.ScriptBackend")
@patch("controller.controller.Script")
def test_display_and_edit_populates_form(mock_model, mock_backend, mock_ui, dummy_app):
    handler = FormHandler(app=dummy_app, obj_type="scripts")
    
    dummy_model = MagicMock()
    dummy_model.read.return_value = dummy_model
    handler.model = dummy_model
    handler.view.create_fields = MagicMock()

    handler.listbox.insert(0, "script1")
    handler.listbox.select_set(0)

    handler.display_and_edit(None)

    handler.view.create_fields.assert_called()  # Проверим, что поля формы созданы
    assert handler.data_model == dummy_model


@patch("controller.controller.ScriptUI")
@patch("controller.controller.ScriptBackend")
@patch("controller.controller.Script")
def test_create_form_and_save(mock_model, mock_backend, mock_ui, dummy_app):
    handler = FormHandler(app=dummy_app, obj_type="scripts")

    mock_instance = MagicMock()
    mock_instance.create.return_value = (True, "Создано")
    handler.model.empty_model.return_value = mock_instance
    handler.model.from_dict.return_value = mock_instance
    handler.collect_data = MagicMock(return_value={
        "name": "new_script", "interpreter": "python3", "endpoint": "", "code": ""
    })

    # Чтобы достать функцию save изнутри create_form_and_save,
    # мы мокнем create_button_frame и сразу вызовем save из неё
    with patch.object(handler, "create_button_frame", wraps=handler.create_button_frame) as mock_button_frame:
        handler.create_form_and_save()
        # Извлекаем сохранённую функцию и вызываем её
        args, kwargs = mock_button_frame.call_args
        save_func = args[1]
        save_func()

    assert handler.data_model == mock_instance

