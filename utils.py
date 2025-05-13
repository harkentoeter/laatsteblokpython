import json
from pathlib import Path

STORAGE_FILE = "storage.json"

def load_data():
    if Path(STORAGE_FILE).exists():
        with open(STORAGE_FILE, "r") as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(STORAGE_FILE, "w") as file:
        json.dump(data, file, indent=4)

