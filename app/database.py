# from langchain_community.utilities import SQLDatabase

# db = SQLDatabase.from_uri("sqlite:///Chinook.db")
# print(db.dialect)
# print(db.get_usable_table_names())
# db.run("SELECT * FROM Artist LIMIT 10;")


# import psycopg2
# from psycopg2 import OperationalError

# # Database connection details
# DB_HOST = "127.0.0.1"  # Replace with your Windows host IP
# DB_NAME = "postgres"
# DB_USER = "postgres"
# DB_PASSWORD = "ahmed"
# DB_PORT = "5432"

# try:
#     # Attempt to connect to the database
#     print("Connecting to the database...")
#     connection = psycopg2.connect(
#         host=DB_HOST,
#         database=DB_NAME,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         port=DB_PORT
#     )
#     print("Connected successfully!")

#     # Create a cursor
#     cursor = connection.cursor()

#     # Execute a query
#     query = "SELECT * FROM inquiries;"
#     print("Executing query...")
#     cursor.execute(query)

#     # Fetch and display results
#     print("Fetching results...")
#     results = cursor.fetchall()

#     if results:
#         print("Query results:")
#         for row in results:
#             print(row)
#     else:
#         print("No results found.")

# except OperationalError as e:
#     print(f"Operational error occurred: {e}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")
# finally:
#     # Close the cursor and connection
#     if 'cursor' in locals():
#         cursor.close()
#         print("Cursor closed.")
#     if 'connection' in locals():
#         connection.close()
#         print("Connection closed.")






from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import pandas as pd

# Database credentials & details
uid = 'postgress'
pwd = 'ahmed'
server = "172.27.240.1"
database = "testing"

# Create the database engine
engine = create_engine(f'postgresql://{uid}:{pwd}@{server}:5432/{database}')

# SQL Query
sql = "SELECT 1;"

df = pd.read_sql_query(sql, engine)
df.head()
