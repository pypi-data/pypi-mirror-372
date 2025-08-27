import sqlite3

class DB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, **columns):
        columns_str = ', '.join([f'{column_name} {column_type}' for column_name, column_type in columns.items()])
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})')
        self.conn.commit()

    def check_duplicate(self, table_name, column_name, value):
        self.cursor.execute(f'SELECT * FROM {table_name} WHERE {column_name} = ?', (value,))
        if self.cursor.fetchone():
            return True
        return False

    def insert(self, table_name, **data):
        columns = ', '.join(data.keys())
        values = ', '.join(['?'] * len(data))
        self.cursor.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({values})', list(data.values()))
        self.conn.commit()
    
    def update(self, table_name, condition, **data):
        sets = ', '.join([f'{column_name} = ?' for column_name in data.keys()])
        values = list(data.values())
        query = f'UPDATE {table_name} SET {sets} WHERE {condition}'
        self.cursor.execute(query, values)
        self.conn.commit()

    def delete(self, table_name, condition):
        self.cursor.execute(f'DELETE FROM {table_name} WHERE {condition}')
        self.conn.commit()

    def select(self, table_name, columns='*'):
        self.cursor.execute(f'SELECT {columns} FROM {table_name}')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
