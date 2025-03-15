import json

SAVE_FILE = "data.json"

def load_data():
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"scripts": {}, "endpoints": []}

def save_data(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)