from db_connector_lib import MySQLConnector

sql_db_data = MySQLConnector(
    host="127.0.0.1",
    user="root",
    password="8523",
    database="student"
)

conn = sql_db_data.connect()

if conn and conn.is_connected():
    print("Connection Verified ")

# Fetch all tables
tables = sql_db_data.execute_query("SHOW TABLES;")
print("Tables:", tables)

# Loop through each table and print its data
for (table_name,) in tables:
    print(f"\nData from table: {table_name}")
    rows = sql_db_data.execute_query(f"SELECT * FROM {table_name};")

    for row in rows:
        print(row)

sql_db_data.close()

