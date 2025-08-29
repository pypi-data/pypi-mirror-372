from .db import db

# ---------------------------
# Model Manager
# ---------------------------

class Model:
    table_name = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def create(cls, **kwargs):
        table = db.get_table(cls.table_name)
        new_id = (max([row["id"] for row in table], default=0) + 1)
        kwargs["id"] = new_id
        table.append(kwargs)
        db.save()
        return cls(**kwargs)

    @classmethod
    def all(cls):
        return [cls(**row) for row in db.get_table(cls.table_name)]

    @classmethod
    def get(cls, **kwargs):
        for row in db.get_table(cls.table_name):
            if all(row.get(k) == v for k, v in kwargs.items()):
                return cls(**row)
        return None

    def save(self):
        table = db.get_table(self.table_name)
        for row in table:
            if row["id"] == self.id:
                for k, v in self.__dict__.items():
                    row[k] = v
        db.save()

    def delete(self):
        table = db.get_table(self.table_name)
        db.data[self.table_name] = [row for row in table if row["id"] != self.id]
        db.save()
