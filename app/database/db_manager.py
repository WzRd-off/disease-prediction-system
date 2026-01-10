import sqlite3
import os

class DatabaseManager():
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self._ensure_db_folder_exists()
    

    def connect(self):
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                self.connection.execute("PRAGMA foreign_keys = ON;")
            except sqlite3.Error as e:
                print(f"CRITICAL ERROR: Помилка підключення до БД: {e}")

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_script(self, script_path: str):
        self.connect()
        if not os.path.exists(script_path):
            return False
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            self.connection.executescript(sql_script)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            return False

    def execute_query(self, query: str, params: tuple = (), fetch_one=False, fetch_all=False):
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.connection.commit()
                return cursor.lastrowid
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f'Error: {e}')
            return None

    def _ensure_db_folder_exists(self):
        folder = os.path.dirname(self.db_path)
        if folder and not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except OSError as e:
                print(f"ERROR: Не Вдалося створити папку {folder}: {e}")