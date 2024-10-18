import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

import unittest
import sqlite3
from unittest.mock import patch
from user_handler.User import User

class TestUser(unittest.TestCase):

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.user_id = 'test_user'
        self.user = User(self.user_id)
        self.hashed_id = self.user.hash_user_id(self.user_id)

    def tearDown(self):
        """Очистка после каждого теста"""
        db_path = os.path.join(self.user.db_users_path, f"user_{self.hashed_id}.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        if os.path.exists(self.user.db_name):
            conn = sqlite3.connect(self.user.db_name)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE user_id = ?', (self.hashed_id,))
            conn.commit()
            conn.close()

    def test_hash_user_id(self):
        """Тест хеширования идентификатора пользователя"""
        expected_hash = self.user.hash_user_id(self.user_id)
        actual_hash = self.hashed_id
        self.assertEqual(expected_hash, actual_hash)

    def test_create_user_db(self):
        """Тест создания базы данных пользователя"""
        self.user.create_user_db(self.hashed_id)
        db_path = os.path.join(self.user.db_users_path, f"user_{self.hashed_id}.db")
        self.assertTrue(os.path.exists(db_path))

    def test_createUserRecord(self):
        """Тест добавления пользователя в базу данных"""
        self.user.createUserRecord()
        with sqlite3.connect(self.user.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (self.hashed_id,))
            result = cursor.fetchone()
            self.assertIsNotNone(result)

    def test_checkUserRecord(self):
        """Тест проверки, что пользователь зарегистрирован"""
        self.user.createUserRecord()
        result = self.user.checkUserRecord()
        self.assertIsNotNone(result)

    def test_log_event(self):
        """Тест логирования событий"""
        event = "test event"
        self.user.log_event(event)
        db_path = os.path.join(self.user.db_users_path, f"user_{self.hashed_id}.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_logs WHERE event = ?', (event,))
            result = cursor.fetchone()
            self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main(verbosity=2)
