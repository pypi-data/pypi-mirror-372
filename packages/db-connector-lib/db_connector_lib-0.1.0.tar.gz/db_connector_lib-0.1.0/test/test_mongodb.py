# ---------- Test MongoDB ----------
from db_connector_lib import MongoDBConnector

mongo_conn = MongoDBConnector(
    uri="mongodb://ecommNoSQLDb_fishseeraw:5215cac7ed1cb8ed63cbaed2661d5d4f0fb7b3c8@epqzxf.h.filess.io:27018/ecommNoSQLDb_fishseeraw", 
    database="ecommNoSQLDb_fishseeraw"
)

db = mongo_conn.connect()
if db:
    print("MongoDB connected!")

    # Fetch some data (example: from collection 'users')
    collection = db["users"]
    docs = collection.find().limit(5)   # fetch first 5 documents
    print(" MongoDB Data (first 5 docs):")
    for doc in docs:
        print(doc)

mongo_conn.close()

