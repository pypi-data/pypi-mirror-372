from database.core import Database

class Table:
    def __init__(self, table):
        self.table = table
        self._query = ""
        self._where = ""
        self._limit = ""
        self._order = ""
        self._join = ""
        self._group = ""
        self._values = None

    # -------------------
    # SELECT
    # -------------------
    def select(self, fields="*"):
        self._query = f"SELECT {fields} FROM {self.table}"
        return self

    # -------------------
    # INSERT
    # -------------------
    def insert(self, data: dict):
        keys = ", ".join(data.keys())
        values = ", ".join(["%s"] * len(data))
        self._query = f"INSERT INTO {self.table} ({keys}) VALUES ({values})"
        self._values = tuple(data.values())
        return self

    # -------------------
    # UPDATE
    # -------------------
    def update(self, data: dict):
        sets = ", ".join([f"{k}=%s" for k in data.keys()])
        self._query = f"UPDATE {self.table} SET {sets}"
        self._values = tuple(data.values())
        return self

    # -------------------
    # DELETE
    # -------------------
    def delete(self):
        self._query = f"DELETE FROM {self.table}"
        return self

    # -------------------
    # WHERE
    # -------------------
    def where(self, condition):
        self._where = f" WHERE {condition}"
        return self

    # -------------------
    # LIMIT
    # -------------------
    def limit(self, n):
        self._limit = f" LIMIT {n}"
        return self

    # -------------------
    # ORDER BY
    # -------------------
    def orderBy(self, field, direction="ASC"):
        self._order = f" ORDER BY {field} {direction}"
        return self

    # -------------------
    # JOIN
    # -------------------
    def join(self, other_table, on, join_type="INNER"):
        self._join += f" {join_type} JOIN {other_table} ON {on}"
        return self

    # -------------------
    # GROUP BY
    # -------------------
    def groupBy(self, field):
        self._group = f" GROUP BY {field}"
        return self

    # -------------------
    # اجرای کوئری
    # -------------------
    def run(self):
        sql = self._query + self._join + self._where + self._group + self._order + self._limit
        cur = Database.cursor()
        try:
            if self._values:
                cur.execute(sql, self._values)
            else:
                cur.execute(sql)

            if self._query.strip().upper().startswith("SELECT"):
                return cur.fetchall()
            else:
                Database._connection.commit()
                return cur.rowcount
        except Exception as e:
            raise RuntimeError(f"Query failed: {e}")
        pass
