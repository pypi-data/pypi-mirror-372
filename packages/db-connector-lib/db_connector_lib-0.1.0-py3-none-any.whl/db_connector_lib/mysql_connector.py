import mysql.connector

class MySQLConnector:
    def __init__(self, host="localhost", user="root", password="", database=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor()
        print("MySQL Connected!")

    def execute_query(self, query):
        if not self.cursor:
            raise Exception("Not connected to DB")
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()
        print("MySQL Connection Closed!")
