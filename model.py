
class Script:
    def __init__(self, data):
        self.name
        self.interpreter = data["interpreter"]
        self.code = data["code"]
        self.endpoint = data["endpoint"]
        self.options = data["options"]


class Endpoint:
    def __init__(self, data):
        self.name
        self.type = data["type"]