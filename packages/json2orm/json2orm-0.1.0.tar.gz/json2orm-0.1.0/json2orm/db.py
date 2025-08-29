import json
import os

# ---------------------------
# Database Manager
# ---------------------------

class Database:
    def __init__(self, path="db.json"):
        self.path = path
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump({}, f)
        self._load()

    def _load(self):
        with open(self.path, "r") as f:
            self.data = json.load(f)

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def get_table(self, name):
        if name not in self.data:
            self.data[name] = []
        return self.data[name]


db = Database()
