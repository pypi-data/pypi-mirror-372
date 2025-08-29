from pymongo import MongoClient

class MongoDBConnector:
    def __init__(self, uri="mongodb://localhost:27017/", database=None):
        self.uri = uri
        self.database_name = database
        self.client = None
        self.db = None

    def connect(self):
        self.client = MongoClient(self.uri)
        self.db = self.client[self.database_name]
        print("MongoDB Connected!")

    def insert_one(self, collection, data):
        return self.db[collection].insert_one(data)

    def find(self, collection, query={}):
        return list(self.db[collection].find(query))

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB Connection Closed!")
