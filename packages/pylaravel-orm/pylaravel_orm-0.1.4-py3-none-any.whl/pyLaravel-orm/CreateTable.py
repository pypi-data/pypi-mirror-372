from database.core import Database

class CreateTable:
    def __init__(self, table_name):
        self.table_name = table_name
        self.columns = []
        self.primary_key = None

    def id(self, name="id"):
        self.columns.append(f"{name} INT AUTO_INCREMENT PRIMARY KEY")
        return self

    def string(self, name, length=255):
        self.columns.append(f"{name} VARCHAR({length})")
        return self

    def integer(self, name):
        self.columns.append(f"{name} INT")
        return self

    def boolean(self, name):
        self.columns.append(f"{name} BOOLEAN")
        return self

    def text(self, name):
        self.columns.append(f"{name} TEXT")
        return self

    def enum(self, name, *values):
        vals = ", ".join(f"'{v}'" for v in values)
        self.columns.append(f"{name} ENUM({vals})")
        return self

    def timestamps(self):
        self.columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        self.columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
        return self

    def build(self):
        cols = ", ".join(self.columns)
        sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({cols})"
        return sql

    def run(self):
        sql = self.build()
        cursor = Database.cursor()
        cursor.execute(sql)
        Database.connect().commit()
        return f"Table {self.table_name} created successfully!"
