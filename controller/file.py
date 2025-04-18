import json
import os

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
