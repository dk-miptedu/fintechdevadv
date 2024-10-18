import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

import unittest
import sqlite3
from create_db.CreateDB import CreateDB

class TestCreateDB(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up a temporary database for testing."""
        cls.test_db_name = 'test_db.sqlite'
        cls.original_dblink = os.path.join('test_db.sqlite')
        cls.db = CreateDB()
        cls.db.db_name = cls.test_db_name
        cls.db.create_db()
    
    @classmethod
    def tearDownClass(cls):
        """Remove the temporary database after tests."""
        if os.path.exists(cls.test_db_name):
            os.remove(cls.test_db_name)

    def test_users_table_creation(self):
        """Test if the users table is created correctly."""
        with sqlite3.connect(self.test_db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            result = cursor.fetchone()
            self.assertIsNotNone(result, "Users table was not created.")

    def test_changers_table_creation(self):
        """Test if the changers table is created correctly."""
        with sqlite3.connect(self.test_db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='changers';")
            result = cursor.fetchone()
            self.assertIsNotNone(result, "Changers table was not created.")
    
    def test_currencies_table_creation(self):
        """Test if the currencies table is created correctly."""
        with sqlite3.connect(self.test_db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currencies';")
            result = cursor.fetchone()
            self.assertIsNotNone(result, "Currencies table was not created.")

if __name__ == '__main__':
    unittest.main(verbosity=2)
