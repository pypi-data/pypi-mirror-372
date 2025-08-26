import mysql.connector

class Database:
    host = None
    port = 3306
    name = None
    user = None
    password = None

    _connection = None

    @classmethod
    def connect(cls):
        if cls._connection:  # اگه کانکشن باز بود همونو برگردون
            return cls._connection

        try:
            cls._connection = mysql.connector.connect(
                host=cls.host,
                port=cls.port,
                database=cls.name,
                user=cls.user,
                password=cls.password
            )
        except Exception as e:
            raise ConnectionError(f"Database connection failed: {e}")

        return cls._connection

    @classmethod
    def cursor(cls):
        conn = cls.connect()
        return conn.cursor(dictionary=True)  # خروجی dict

    @classmethod
    def close(cls):
        if cls._connection:
            cls._connection.close()
            cls._connection = None

    @classmethod
    def query(cls, sql: str, params: tuple = ()):
        """SELECT queries"""
        cur = cls.cursor()
        cur.execute(sql, params)
        return cur  # استفاده: cur.fetchall() یا cur.fetchone()

    @classmethod
    def execute(cls, sql: str, params: tuple = ()):
        """INSERT / UPDATE / DELETE"""
        conn = cls.connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        conn.commit()
        return cur  # استفاده: cur.rowcount یا cur.lastrowid

