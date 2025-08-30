# amdata/db.py
import sqlite3

class DB:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, **columns):
        columns_list = [f"{col_name} {col_type}" for col_name, col_type in columns.items()]
        columns_str = ", ".join(columns_list)
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})')
        self.conn.commit()
        print(f"تم إنشاء الجدول '{table_name}' بنجاح.")

    def insert(self, table_name, **data):
        columns = ", ".join(data.keys())
        values_placeholders = ", ".join(['?'] * len(data))
        self.cursor.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({values_placeholders})', list(data.values()))
        self.conn.commit()
        print(f"تمت إضافة سجل جديد إلى الجدول '{table_name}'.")

    def select_all(self, table_name):
        self.cursor.execute(f'SELECT * FROM {table_name}')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
