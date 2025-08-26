# PyLaravel ORM

A simple Laravel-like ORM and query builder for MySQL in Python.  
This package provides a convenient way to interact with your MySQL database, inspired by the database components of the Laravel PHP framework.

---

## ✨ Features

- Fluent Query Builder for `SELECT`, `INSERT`, `UPDATE`, `DELETE`.
- Simple Schema Builder for creating and modifying tables.
- Easy-to-configure database connection.
- Support for raw SQL queries.
- Access to cursor attributes (`lastrowid`, `rowcount`, etc.).

---

## 📦 Installation

You can install the package from PyPI:

```bash
pip install pylaravel-orm
```

Or, for local development:

```bash
pip install -e .
```

---

## 🚀 Usage

### 1. Database Configuration

First, configure your database connection details.

```python
from database import Database

Database.host = '127.0.0.1'
Database.port = 3306
Database.name = 'your_database_name'
Database.user = 'your_username'
Database.password = 'your_password'
```

---

### 2. Creating Tables (Schema)

You can easily define and create tables using the `CreateTable` class.

```python
from database import CreateTable

# Create a 'users' table
schema = CreateTable('users')
schema.id()
schema.string('name', length=100)
schema.string('email').unique()   # unique field
schema.text('bio').nullable()     # nullable field
schema.timestamps()               # created_at & updated_at
schema.run()

print("Table 'users' created successfully!")
```

---

### 3. Query Builder

#### 🔹 Inserting Data

```python
from database import Table

users = Table('users')

# Insert a single record
users.insert({
    'name': 'John Doe',
    'email': 'john.doe@example.com',
    'bio': 'A software developer.'
}).run()

# Insert multiple records (looping)
for i in range(5):
    users.insert({
        'name': f'User {i}',
        'email': f'user{i}@example.com'
    }).run()
```

---

#### 🔹 Selecting Data

```python
from database import Table

users = Table('users')

# Get all users
all_users = users.select().run()
print("All users:", all_users)

# Get a user by ID
user = users.select().where("id = 1").run()
print("User with ID 1:", user)

# Select specific columns
emails = users.select('id, name, email').run()
for row in emails:
    print(row['name'], row['email'])
```

---

#### 🔹 Updating Data

```python
from database import Table

users = Table('users')

# Update a user's bio
users.update({'bio': 'An amazing software developer.'}).where("id = 1").run()
```

---

#### 🔹 Deleting Data

```python
from database import Table

users = Table('users')

# Delete a user by ID
users.delete().where("id = 5").run()
```

---

### 4. Raw Queries

You can also run raw SQL queries directly using the `Database.query()` or `Database.execute()` methods.

```python
from database import Database

# SELECT query
cur = Database.query("SELECT * FROM users WHERE email=%s", ("john.doe@example.com",))
print(cur.fetchone())

# INSERT query with lastrowid
cur = Database.execute(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    ("Ali", "ali@example.com")
)
print("Inserted ID:", cur.lastrowid)

# UPDATE query with rowcount
cur = Database.execute("UPDATE users SET bio=%s WHERE id=%s", ("Updated bio", 1))
print("Rows updated:", cur.rowcount)
```

---

### 5. Closing the Connection

Always close the connection when your application shuts down:

```python
from database import Database

Database.close()
```



---

## 📝 License
MIT