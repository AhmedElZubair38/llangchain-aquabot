import sqlite3
from crewai import Tool

class DatabaseTool(Tool):
    def __init__(self, db_name='database.db'):
        self.db_name = db_name
        self.conn = None
        
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
            
    def create_table(self, table_name, columns):
        """Create a new table in the database"""
        if not self.conn:
            self.connect()
            
        columns_with_types = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})"
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            return False
            
    def insert_data(self, table_name, data):
        """Insert data into a table"""
        if not self.conn:
            self.connect()
            
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, tuple(data.values()))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")
            return False
            
    def get_data(self, table_name, limit=10):
        """Retrieve data from a table"""
        if not self.conn:
            self.connect()
            
        query = f"SELECT * FROM {table_name} LIMIT ?"
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving data: {e}")
            return None
            
    def mock_api(self, endpoint):
        """Mock API endpoint that returns sample data"""
        if endpoint == '/users':
            return {
                'status': 'success',
                'data': [
                    {'id': 1, 'name': 'John Doe'},
                    {'id': 2, 'name': 'Jane Smith'}
                ]
            }
        elif endpoint == '/products':
            return {
                'status': 'success',
                'data': [
                    {'id': 101, 'name': 'Product A'},
                    {'id': 102, 'name': 'Product B'}
                ]
            }
        else:
            return {
                'status': 'error',
                'message': 'Endpoint not found'
            }

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
