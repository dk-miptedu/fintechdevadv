# class User
import sqlite3
import hashlib
import os
# импорт пользовательских функций и инициализация окружения
from ConfigInit import dblink, db_users_path, db_user_db_name_pre
class User():
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.db_name = os.path.join(dblink)
        self.db_users_path = db_users_path
        self.db_user_db_name_pre = db_user_db_name_pre
    
    def hash_user_id(self, user_id):
        """Хеширование идентификатора пользователя."""
        return hashlib.sha256(user_id.encode()).hexdigest()
    
    def create_user_db(self, hashed_id):
        """Создание базы данных для нового пользователя и таблицы user_logs."""
        db_name = os.path.join(self.db_users_path, f"{self.db_user_db_name_pre}{hashed_id}.db")
        #print(f'попытка создать базу данных для пользователя: {db_name}')
        if not os.path.exists(db_name):
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        event TEXT
                    )
                ''')
                conn.commit()
            print(f'Создана база данных для пользователя: {db_name}')

    def log_event(self, event):
        """Добавление записи в таблицу user_logs."""
        hashed_id = self.hash_user_id(self.user_id)
        self.create_user_db(hashed_id)
        db_name = os.path.join(self.db_users_path, f"user_{hashed_id}.db")
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO user_logs (event) VALUES (?)', (event,))
            conn.commit()
        print(f'Добавлено событие: "{event}" для пользователя с хешом {hashed_id}.')

    
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
