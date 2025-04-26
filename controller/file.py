import json
import os

from view.theme import StyledToplevel, StyledLabel, StyledButton, StyledEntry

class FileStorage:
    def __init__(self, file_path="data.json"):
        self.file_path = file_path
        self.data = self.load()

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"scripts": {}, "endpoints": {}}

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    @property
    def scripts(self):
        return self.data["scripts"]

    @property
    def endpoints(self):
        return self.data["endpoints"]


class StorageHandler:
    def __init__(self, config):
        self.config = config

    def setting_window(self):
        result_window = StyledToplevel()
        result_window.title("Настройки Storage")
        result_window.configure(bg="#f2ceae")

        entries = {}

        # Получаем все ключи и значения из секции [Storage]
        if not self.config.has_section('Storage'):
            self.config.add_section('Storage')

        for i, (key, value) in enumerate(self.config.items('Storage')):
            label = StyledLabel(result_window, text=key, font=("Silkscreen", 9), bg="#f2ceae")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            entry = StyledEntry(result_window, width=40)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            entries[key] = entry

        def save_settings():
            for key, entry in entries.items():
                self.config.set('Storage', key, entry.get())

            # Сохраняем настройки обратно в файл
            with open("settings.ini", "w") as configfile:
                self.config.write(configfile)

            result_window.destroy()  # Закрыть окно после сохранения

        save_button = StyledButton(result_window, text="Save", command=save_settings, bg="#fdbf1c", font=("Silkscreen", 9))
        save_button.grid(row=len(entries), column=0, columnspan=2, pady=15)

