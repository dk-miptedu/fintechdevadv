# class User
import sqlite3
class User:
    def __init__(self, telegram_id):
        self.telegram_id = telegram_id

    def checkUserRecord(self):
        with sqlite3.connect('./dbase.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)''')
            cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (self.telegram_id,))
            return cursor.fetchone()

    def createUserRecord(self):
        with sqlite3.connect('./dbase.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)''')
            cursor.execute('INSERT INTO users (telegram_id) VALUES (?)', (self.telegram_id,))
            conn.commit()
