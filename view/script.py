"""
This module provides the ScriptUI class, which is responsible for creating
the user interface for managing and editing scripts, including features
like syntax highlighting and form fields for script attributes.
"""

import tkinter as tk
from typing import Any, Optional, Type
from tkinter import scrolledtext
from pygments.token import Token
from pygments.lexers import get_lexer_by_name
from pygments import lex


from model.script import Script
from view.main import MainUI
from view.theme import StyledLabel, StyledEntry, StyledCombobox


class ScriptUI(MainUI):
    """
    This class handles the user interface for editing and managing scripts.
    It allows users to interact with script attributes like name, interpreter,
    endpoint, and code, while providing syntax highlighting for the code field.
    """
    def __init__(self, app: Any):
        self.app = app
        self.model = None
        self.script_text: Optional[scrolledtext.ScrolledText] = None
        self.name_entry: Optional[StyledEntry] = None
        self.interpreter_entry: Optional[tk.StringVar] = None
        self.endpoint_var: Optional[tk.StringVar] = None


    def _add_syntax_highlighting(self, code: str, language: str) -> None:
        if not self.script_text:
            return

        text_widget = self.script_text
        text_widget.config(state="normal")
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", code)

        lexer = get_lexer_by_name(language, stripall=True)

        # Удалим предыдущие теги
        for tag in text_widget.tag_names():
            text_widget.tag_delete(tag)

        # Определяем стили
        styles = {
            Token.Keyword: {"foreground": "blue"},
            Token.Name: {"foreground": "darkgreen"},
            Token.String: {"foreground": "darkred"},
            Token.Comment: {"foreground": "gray"},
            Token.Number: {"foreground": "purple"},
            Token.Operator: {"foreground": "black"},
        }

        for token_type, style in styles.items():
            text_widget.tag_configure(str(token_type), **style)

        # Начальная позиция в тексте
        line = 1
        column = 0

        for token_type, token_text in lex(code, lexer):
            lines = token_text.split("\n")

            for i, part in enumerate(lines):
                start_index = f"{line}.{column}"
                end_col = column + len(part)
                end_index = f"{line}.{end_col}"

                if part.strip():  # не подсвечиваем пустые символы
                    tag_name = str(token_type)
                    text_widget.tag_add(tag_name, start_index, end_index)

                column = end_col

                if i < len(lines) - 1:
                    line += 1
                    column = 0

        text_widget.config(state="normal")


    def _create_labeled_widget(
        self,
        parent: tk.Widget,
        label_text: str,
        widget_class: Type[tk.Widget],
        **widget_kwargs: Any
    ) -> tk.Widget:

        label = StyledLabel(parent, text=label_text)
        label.pack(anchor="w", padx=4, pady=(0, 0))
        widget = widget_class(parent, **widget_kwargs)
        widget.pack(anchor="w", padx=5, pady=(0, 0))
        return widget


    def create_fields(
        self,
        frame: tk.Widget,
        script: Script
    ) -> None:

        """Добавляет поля формы (Name, Interpreter, Endpoint)"""
        self.model = script
        self.name_entry = self._create_labeled_widget(frame, "Name", StyledEntry)
        self.name_entry.insert(0, script.name)

        self.interpreter_entry = tk.StringVar(value=script.interpreter)
        self._create_labeled_widget(frame,
                                    "Interpreter",
                                    StyledCombobox,
                                    textvariable=self.interpreter_entry,
                                    value=["python", "bash"])

        self.endpoint_var = tk.StringVar(value=script.endpoint)
        self._create_labeled_widget(frame,
                                    "Endpoint",
                                    StyledCombobox,
                                    textvariable=self.endpoint_var,
                                    value=list(self.app.data["endpoints"].keys()))

        self._create_code_field(self.app.content_frame, script.code)
        self._add_syntax_highlighting(script.code, script.interpreter)


    def _create_code_field(self, parent: tk.Widget, code: str = "") -> None:
        """Создаёт текстовое поле с кодом"""
        label = StyledLabel(parent, text="Code:")
        label.pack(anchor="w", padx=4, pady=(0, 0))

        self.script_text = scrolledtext.ScrolledText(parent,
                                                     height=10,
                                                     wrap=tk.WORD,
                                                     font=("Courier", 10))
        self.script_text.insert("1.0", code)
        self.script_text.config(tabs=4)

        self.script_text.bind("<Control-a>", lambda event: self._select_all())
        self.script_text.bind("<Control-c>", lambda e: (self.script_text.event_generate("<<Copy>>"),
                                                        self._show_copy_overlay()))
        self.script_text.bind("<Control-v>", lambda e: self.script_text.event_generate("<<Paste>>"))
        self.script_text.bind("<Control-x>", lambda e: self.script_text.event_generate("<<Cut>>"))
        self.script_text.bind("<Control-z>", lambda e: self.script_text.edit_undo())
        self.script_text.bind("<Control-y>", lambda e: self.script_text.edit_redo())

        self.script_text.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 0))

    def _select_all(self) -> str:
        """Выделяет весь текст в поле"""
        if self.script_text:
            self.script_text.tag_add("sel", "1.0", "end-1c")
            return "break"
        return ""

    def _show_copy_overlay(self) -> None:
        """Показывает полупрозрачный оверлей 'Copy' внизу окна"""
        if not hasattr(self.app, "root"):
            return

        overlay = StyledLabel(self.app.root, text="Copy", bg="#000000", fg="white")
        overlay.place(relx=0.5, rely=1.0, anchor="s", y=-10)

        # Начальная прозрачность (эмулируем через цвет)
        alpha_steps = 10
        fade_duration = 500  # мс

        def fade(step=0):
            if step >= alpha_steps:
                overlay.destroy()
                return
            intensity = int(255 * (1 - step / alpha_steps))
            hex_color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
            overlay.config(bg=hex_color)
            self.app.root.after(fade_duration // alpha_steps, lambda: fade(step + 1))

        fade()

    def get_data(self) -> dict:
        """
        Собирает и возвращает данные, введённые пользователем в форму.
        """
        name = self.name_entry.get() if self.name_entry else ""
        interpreter = self.interpreter_entry.get() if self.interpreter_entry else ""
        endpoint = self.endpoint_var.get() if self.endpoint_var else ""
        code = self.script_text.get("1.0", tk.END).strip() if self.script_text else ""

        return {
            "name": name,
            "interpreter": interpreter,
            "endpoint": endpoint,
            "code": code
        }
