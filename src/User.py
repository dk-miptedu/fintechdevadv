# class User
import sqlite3
import hashlib
import os
# импорт пользовательских функций и инициализация окружения
from ConfigInit import dblink
class User():
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.db_name = os.path.join(dblink)
        self.create_db()
    
    def hash_user_id(self, user_id):
        """Хеширование идентификатора пользователя."""
        print(f'user_id: {user_id}')
        return hashlib.sha256(user_id.encode()).hexdigest()
    
    def create_db(self):
        """Создание базы данных и таблиц."""
        print(self.db_name)
        print('*'*20)
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
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
                    active BOOLEAN
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    registration_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def createUserRecord(self):
        """Добавление нового пользователя в базу данных."""
        hashed_id = self.hash_user_id(self.user_id)
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (user_id) VALUES (?)', (hashed_id,))
                conn.commit()
                print(f'Пользователь {self.user_id} успешно добавлен.')
            except sqlite3.IntegrityError:
                print(f'Пользователь {self.user_id} уже зарегистрирован.')
   


    def checkUserRecord(self):
        """Проверка пользователя - внесен ли в базу данных"""
        hashed_id = self.hash_user_id(self.user_id)
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (hashed_id,))
            return cursor.fetchone()

    #def createUserRecord(self):
    #    with sqlite3.connect(self.db_name) as conn:
    #        cursor = conn.cursor()
    #        cursor.execute('INSERT INTO users (telegram_id) VALUES (?)', (self.telegram_id,))
    #        conn.commit()*/
