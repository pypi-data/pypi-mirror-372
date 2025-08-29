# JSON2ORM

A lightweight **JSON-based ORM** for Python 🚀  
No SQL, no external DB engine — just plain JSON files acting like a database.

Perfect for **small projects, testing, prototyping** or educational purposes.

---

## ✨ Features
- Define models like in Django ORM or Prisma
- Auto-increment IDs for each model
- Basic CRUD support (`create`, `all`, `get`, `save`, `delete`)
- Simple JSON file storage, no setup required
- Human-readable database (`.json` file)

---

## 📦 Installation
```bash
pip install json2orm
```

---

## ⚡ Quick Start Example

```python
from json2orm import Database, Model

# Setup database (JSON file)
db = Database("mydb.json")

# Define models
class User(Model):
    table_name = "users"

class Post(Model):
    table_name = "posts"


# Create users
u1 = User.create(name="Ali", email="ali@test.com")
u2 = User.create(name="Sara", email="sara@test.com")
print([u.name for u in User.all()])  # ➝ ['Ali', 'Sara']

# Get user
ali = User.get(name="Ali")
print(ali.email)  # ➝ ali@test.com

# Update user
ali.email = "ali_updated@test.com"
ali.save()
print(User.get(id=1).email)  # ➝ ali_updated@test.com

# Delete user
u2.delete()
print([u.name for u in User.all()])  # ➝ ['Ali']

# Create posts
p1 = Post.create(title="First Post", content="Hello World", user_id=ali.id)
p2 = Post.create(title="Second Post", content="Next Post", user_id=ali.id)

print([p.title for p in Post.all()])  # ➝ ['First Post', 'Second Post']
```

---

## 🔮 Roadmap / Future Features
JSONORM is in its early stages. Planned features include:

- [ ] **Field definitions in models** (like Django `models.CharField`, `IntegerField`, etc.)
- [ ] **Schema validation** (prevent invalid fields)
- [ ] **Query filters** (e.g., `User.filter(age__gt=18)`)
- [ ] **Export database** (to CSV, SQLite, MongoDB, etc.)
- [ ] **Simple GUI** for browsing and editing JSON-based data
- [ ] **CLI tool** to manage database & migrations
- [ ] **Relationships** (OneToMany / ManyToMany)

---

## 🧪 Running Tests
You can run the provided example tests:

```bash
python examples/test_example.py
```

Expected output is included as comments in the file.

---

## 📜 License
This project is licensed under the **MIT License**.  
Feel free to use, modify and distribute.

---

## ❤️ Contributing
PRs are welcome! Ideas, bug reports, and feature requests are highly appreciated.
