# class Create DataBase & Common Tables
import sqlite3
import os
# импорт пользовательских функций и инициализация окружения
from ConfigInit import dblink

class CreateDB():
    def __init__(self):
        self.db_name = os.path.join(dblink)
        self.create_db()
    
    def create_db(self):
        """Создание базы данных и таблиц."""
        #print(self.db_name)
        #print('*'*20)
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    registration_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS changers (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    reserve INTEGER,
                    age INTEGER,
                    listed INTEGER,
                    positive_reviews INTEGER,
                    negative_reviews INTEGER,
                    neutral_reviews INTEGER,
                    verify BOOLEAN,
                    country INTEGER,
                    active BOOLEAN,
                    url_en TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS currencies (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    urlname TEXT,
                    viewname TEXT,
                    code TEXT,
                    crypto BOOLEAN,
                    cash BOOLEAN,
                    ps INTEGER,
                    group_id INTEGER
                )
            ''')            
            conn.commit()
            