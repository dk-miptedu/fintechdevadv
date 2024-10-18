import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

import unittest
from unittest.mock import patch, MagicMock
import threading
import time
from api_handler.BestChange import BestChange


TEST_DBNAME = "dbname.db" 
API_URL = 'https://www.bestchange.app/v2'

class TestBestChange(unittest.TestCase):

    @patch('sqlite3.connect')
    def test_get_changers_url_list(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        test_name_db = [
            (1, 'Changer1', 100, 10, 'https://changer1.com'),
            (2, 'Changer2', 200, 5, 'https://changer2.com'),
            (3, 'Changer3', 202, 4, 'https://changer3.com'),
            (4, 'Changer4', 203, 3, 'https://changer4.com'),
            (5, 'Changer5', 204, 2, 'https://changer5.com'),
        ]
        
        mock_cursor.fetchall.return_value = test_name_db

        obj = BestChange()
        obj.db_name =  TEST_DBNAME

        result = obj.get_changers_url_list()
        mock_cursor.execute.assert_called_once_with(
            'SELECT id, name, positive_reviews, negative_reviews, url_en FROM changers WHERE active=1 ORDER BY reserve DESC limit 50'
        )

        # Проверка, что возвращается корректный результат
        # result (f"{changers_id}: [{viewname}]({url_en}), pos-neg: {positive_reviews}-{negative_reviews}")
        expected_result = [
            "1: [Changer1](https://changer1.com), pos-neg: 100-10",
            "2: [Changer2](https://changer2.com), pos-neg: 200-5",
            "3: [Changer3](https://changer3.com), pos-neg: 202-4",
            "4: [Changer4](https://changer4.com), pos-neg: 203-3",
            "5: [Changer5](https://changer5.com), pos-neg: 204-2"
        ]
        self.assertEqual(result, expected_result)
        self.assertEqual(len(result), len(test_name_db))

    @patch('sqlite3.connect')
    def test_get_crypto_currencies_exchange(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        test_crypto_dataset = [
            (1, 'BTC'),
            (2, 'ETH'),
            (3, 'LTC'),
        ]

        mock_cursor.fetchall.return_value = test_crypto_dataset
        obj = BestChange()
        obj.db_name = TEST_DBNAME

        result = obj.get_crypto_currencies_exchange()

        mock_cursor.execute.assert_called_once_with(
            'SELECT id, viewname FROM currencies WHERE group_id = 2'
        )

        expected_result = [
            "1: BTC",
            "2: ETH",
            "3: LTC"
        ]
        self.assertEqual(result, expected_result)
        self.assertEqual(len(result), len(test_crypto_dataset))

    @patch('sqlite3.connect')  
    def  test_get_crypto_currencies(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        test_crypto_dataset = [
            (1, 'BTC'),
            (2, 'ETH'),
            (3, 'LTC'),
        ]

        mock_cursor.fetchall.return_value = test_crypto_dataset
        obj = BestChange()
        obj.db_name = TEST_DBNAME

        result = obj.get_crypto_currencies()

        mock_cursor.execute.assert_called_once_with(
            'SELECT id, viewname FROM currencies WHERE group_id = 0'
        )

        # Проверка, что возвращается корректный результат
        expected_result = [
            "1: BTC",
            "2: ETH",
            "3: LTC"
        ]
        self.assertEqual(result, expected_result)
        self.assertEqual(len(result), len(test_crypto_dataset))

    @patch('sqlite3.connect')
    def test_get_online_banks_currencies(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        test_name_db = [
            (1, 'Tinkoff Bank'),
            (2, 'Sberbank'),
            (3, 'Alfa Bank'),
        ]
        
        mock_cursor.fetchall.return_value = test_name_db

        obj = BestChange()
        obj.db_name =  TEST_DBNAME

        result = obj.get_online_banks_currencies()

        mock_cursor.execute.assert_called_once_with(
            'SELECT id, viewname FROM currencies WHERE group_id = 3 AND code LIKE "%RUB"'
        )

        # Проверка, что возвращается корректный результат
        # result (f"{changers_id}: [{viewname}]({url_en}), pos-neg: {positive_reviews}-{negative_reviews}")
        expected_result = [
            "1: Tinkoff Bank",
            "2: Sberbank",
            "3: Alfa Bank"
        ]
        self.assertEqual(result, expected_result)
        self.assertEqual(len(result), len(test_name_db))
    
    # get_best_rates_fiat
    @patch('api_handler.BestChange.BestChange.get_online_banks_currencies')
    @patch('requests.get')
    def test_get_best_rates_fiat_path_out(self, mock_get, mock_get_online_banks_currencies):

        mock_get_online_banks_currencies.return_value = [
            "1: Tinkoff Bank",
            "2: Sberbank",
            "3: Alfa Bank",
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {
                'presences': [
                    {'pair': 'BTC-1', 'best': '50000', 'count': 5},
                    {'pair': 'BTC-1', 'best': '49500', 'count': 3}
                ]
            },
            {
                'presences': [
                    {'pair': 'BTC-2', 'best': '49000', 'count': 4}
                ]
            },
            {
                'presences': [
                    {'pair': 'BTC-3', 'best': '48000', 'count': 2},
                    {'pair': 'BTC-3', 'best': '47000', 'count': 1}
                ]
            }
        ]
        mock_get.return_value = mock_response

        obj = BestChange()
        obj.api_url = API_URL

        result = obj.get_best_rates_fiat("BTC", "out")

        mock_get_online_banks_currencies.assert_called_once()

        fiat_list = mock_get_online_banks_currencies.return_value
        self.assertEqual(mock_get.call_count, len(fiat_list))

        expected_calls = [
            (f'{API_URL}/presences/BTC-1/', {'accept': 'application/json'}),
            (f'{API_URL}/presences/BTC-2/', {'accept': 'application/json'}),
            (f'{API_URL}/presences/BTC-3/', {'accept': 'application/json'}),
        ]
        for i, call in enumerate(expected_calls):
            mock_get.assert_any_call(call[0], headers=call[1])

        expected_result = [
            'BTC-1: 50000, количество обменников: 5',
            'BTC-1: 49500, количество обменников: 3',
            'BTC-2: 49000, количество обменников: 4',
            'BTC-3: 48000, количество обменников: 2',
            'BTC-3: 47000, количество обменников: 1'
        ]
        self.assertEqual(result, expected_result)

    @patch('api_handler.BestChange.BestChange.get_online_banks_currencies')
    @patch('requests.get')
    def test_get_best_rates_fiat_path_in(self, mock_get, mock_get_online_banks_currencies):
        mock_get_online_banks_currencies.return_value = [
            "1: Tinkoff Bank",
            "2: Sberbank",
            "3: Alfa Bank",
        ]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {
                'presences': [
                    {'pair': '1-BTC', 'best': '0.00050000', 'count': 5},
                    {'pair': '1-BTC', 'best': '0.00049500', 'count': 3}
                ]
            },
            {
                'presences': [
                    {'pair': '2-BTC', 'best': '0.00049000', 'count': 4}
                ]
            },
            {
                'presences': [
                    {'pair': '3-BTC', 'best': '0.00048000', 'count': 2},
                    {'pair': '3-BTC', 'best': '0.00047000', 'count': 1}
                ]
            }
        ]
        mock_get.return_value = mock_response

        obj = BestChange()
        obj.api_url = API_URL

        # Вызов функции get_best_rates_fiat - path=out
        result = obj.get_best_rates_fiat("BTC", "in")

        # Проверка, что get_online_banks_currencies был вызван
        mock_get_online_banks_currencies.assert_called_once()

        # Проверка, что requests.get был вызван столько раз, сколько элементов в fiat
        fiat_list = mock_get_online_banks_currencies.return_value
        self.assertEqual(mock_get.call_count, len(fiat_list))

        # Проверка правильности вызова requests.get для каждого элемента
        expected_calls = [
            (f'{API_URL}/presences/1-BTC/', {'accept': 'application/json'}),
            (f'{API_URL}/presences/2-BTC/', {'accept': 'application/json'}),
            (f'{API_URL}/presences/3-BTC/', {'accept': 'application/json'}),
        ]
        for i, call in enumerate(expected_calls):
            mock_get.assert_any_call(call[0], headers=call[1])

        # Проверка возвращаемого результата
        expected_result = [
            '1-BTC: 0.00050000, количество обменников: 5',
            '1-BTC: 0.00049500, количество обменников: 3',
            '2-BTC: 0.00049000, количество обменников: 4',
            '3-BTC: 0.00048000, количество обменников: 2',
            '3-BTC: 0.00047000, количество обменников: 1'
        ]
        self.assertEqual(result, expected_result)
    # get_changer_url
    def test_get_changer_url_first_result(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (["https://changer1.com"])
        changer_id = 1
        result = BestChange.get_changer_url(changer_id, mock_conn)
        #print(result)
        mock_cursor.execute.assert_called_once_with("SELECT url_en FROM changers WHERE id = ?", (changer_id,))
        self.assertEqual(result, "https://changer1.com")

    def test_get_changer_url_none(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        changer_id = 1
        result = BestChange.get_changer_url(changer_id, mock_conn)
        mock_cursor.execute.assert_called_once_with("SELECT url_en FROM changers WHERE id = ?", (changer_id,))

        self.assertIsNone(result)        
    
    #update_changers
    @patch('requests.get')
    @patch('sqlite3.connect')
    def test_update_changers_successful_response(self, mock_connect, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        sample_data = {
            'changers': [
                {
                    'id': 1,
                    'name': 'Changer1',
                    'reserve': 1000,
                    'age': 2,
                    'listed': True,
                    'reviews': {'positive': 10, 'closed': 2, 'neutral': 1},
                    'verify': True,
                    'country': 'Country1',
                    'active': True,
                    'urls': {'en': 'http://example.com/en', 'ru': 'http://example.com/ru'}
                },
            ]
        }
        mock_response.json.return_value = sample_data
        mock_get.return_value = mock_response

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        obj = BestChange()  
        obj.api_url = 'http://api.example.com'
        obj.db_name = ':memory:' 

        obj.update_changers()

        mock_get.assert_called_with('http://api.example.com/changers/', headers={'accept': 'application/json'})

        expected_sql = '''
            INSERT OR REPLACE INTO changers (id, name, reserve, age, listed,
            positive_reviews, negative_reviews, neutral_reviews, verify, country, active, url_en)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        expected_sql = ' '.join(expected_sql.split())  
        actual_sql = mock_cursor.execute.call_args[0][0]
        actual_sql = ' '.join(actual_sql.split())  

        self.assertEqual(expected_sql, actual_sql)

        expected_params = (
            1,
            'Changer1',
            1000,
            2,
            True,
            10,
            2,
            1,
            1,
            'Country1',
            1,
            'http://example.com/en'
        )
        actual_params = mock_cursor.execute.call_args[0][1]
        self.assertEqual(expected_params, actual_params)

        mock_conn.commit.assert_called_once()

    @patch('requests.get')
    def test_update_changers_non_200_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        obj = BestChange()
        obj.api_url = 'http://api.example.com'
        obj.db_name = ':memory:'
        obj.update_changers()
        mock_get.assert_called_with('http://api.example.com/changers/', headers={'accept': 'application/json'})

    @patch('requests.get')
    @patch('sqlite3.connect')
    def test_update_currencies_successful_response(self, mock_connect, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        sample_data = {
            'currencies': [
                {
                    'id': 1,
                    'name': 'Currency1',
                    'urlname': 'currency1',
                    'viewname': 'Currency One',
                    'code': 'CUR1',
                    'crypto': True,
                    'cash': False,
                    'ps': False,
                    'group': 10
                },
                {
                    'id': 2,
                    'name': 'Currency2',
                    'urlname': 'currency2',
                    'viewname': 'Currency Two',
                    'code': 'CUR2',
                    'crypto': False,
                    'cash': True,
                    'ps': False,
                    'group': 20
                }
            ]
        }
        mock_response.json.return_value = sample_data
        mock_get.return_value = mock_response

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        obj = BestChange() 
        obj.api_url = 'https://www.bestchange.app/v2'
        obj.db_name = ':memory:'

        obj.update_currencies()

        mock_get.assert_called_with(f'{obj.api_url}/currencies/', headers={'accept': 'application/json'})

        expected_sql = '''
            INSERT OR REPLACE INTO currencies (id, name, urlname, viewname, code, crypto, cash, ps, group_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        expected_sql_clean = ' '.join(expected_sql.split())

        expected_calls = [
            ((expected_sql_clean, (
                1,
                'Currency1',
                'currency1',
                'Currency One',
                'CUR1',
                True,
                False,
                False,
                10
            )),),
            ((expected_sql_clean, (
                2,
                'Currency2',
                'currency2',
                'Currency Two',
                'CUR2',
                False,
                True,
                False,
                20
            )),)
        ]

        actual_calls = []
        for call in mock_cursor.execute.call_args_list:
            sql = call[0][0]
            sql_clean = ' '.join(sql.split())  
            params = call[0][1]
            actual_calls.append(((sql_clean, params),))

        self.assertEqual(expected_calls, actual_calls)

        mock_conn.commit.assert_called_once()

    @patch('requests.get')
    def test_update_currencies_non_200_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        obj = BestChange()
        obj.api_url = 'https://www.bestchange.app/v2'
        obj.db_name = ':memory:'

        obj.update_currencies()

        mock_get.assert_called_with(f'{obj.api_url}/currencies/', headers={'accept': 'application/json'})

        with patch('sqlite3.connect') as mock_connect:
            mock_connect.assert_not_called()

    @patch('time.sleep', return_value=None)  # Мокируем time.sleep, чтобы избежать задержек
    def test_start_and_stop_updates(self, mock_sleep):
        # Создаем экземпляр класса
        obj = BestChange()
        obj.running = False
        obj.changers_interval = 0.1  # Устанавливаем небольшой интервал для тестирования
        obj.currencies_interval = 0.1

        # Мокируем методы update_changers и update_currencies
        obj.update_changers = MagicMock()
        obj.update_currencies = MagicMock()

        # Запускаем обновления
        obj.start_updates()

        # Даем потокам время для выполнения (используем небольшую задержку)
        time.sleep(0.3)

        # Останавливаем обновления
        obj.stop_updates()

        # Проверяем, что переменная running установлена в False
        self.assertFalse(obj.running)

        # Проверяем, что методы update_changers и update_currencies были вызваны несколько раз
        self.assertGreaterEqual(obj.update_changers.call_count, 2)
        self.assertGreaterEqual(obj.update_currencies.call_count, 2)

        # Проверяем, что потоки были корректно остановлены
        self.assertFalse(obj.changers_thread.is_alive())
        self.assertFalse(obj.currencies_thread.is_alive())

    @patch('time.sleep', return_value=None)
    def test_periodic_update_changers(self, mock_sleep):
        # Создаем экземпляр класса
        obj = BestChange()
        obj.running = True
        obj.changers_interval = 0.1

        # Мокируем метод update_changers
        obj.update_changers = MagicMock()

        # Используем событие для остановки цикла после нескольких итераций
        def side_effect(*args, **kwargs):
            obj.running = False  # Останавливаем цикл после первого вызова sleep

        mock_sleep.side_effect = side_effect

        # Запускаем метод в отдельном потоке для тестирования
        thread = threading.Thread(target=obj.periodic_update_changers)
        thread.start()
        thread.join()

        # Проверяем, что update_changers был вызван один раз
        obj.update_changers.assert_called_once()

    @patch('time.sleep', return_value=None)
    def test_periodic_update_currencies(self, mock_sleep):
        # Создаем экземпляр класса
        obj = BestChange()
        obj.running = True
        obj.currencies_interval = 0.1

        # Мокируем метод update_currencies
        obj.update_currencies = MagicMock()

        # Используем событие для остановки цикла после нескольких итераций
        def side_effect(*args, **kwargs):
            obj.running = False  # Останавливаем цикл после первого вызова sleep

        mock_sleep.side_effect = side_effect

        # Запускаем метод в отдельном потоке для тестирования
        thread = threading.Thread(target=obj.periodic_update_currencies)
        thread.start()
        thread.join()

        # Проверяем, что update_currencies был вызван один раз
        obj.update_currencies.assert_called_once()

    def test_start_updates_already_running(self):
        # Создаем экземпляр класса
        obj = BestChange()
        obj.running = True  # Уже запущен

        # Мокируем методы
        obj.periodic_update_changers = MagicMock()
        obj.periodic_update_currencies = MagicMock()

        # Вызываем start_updates
        obj.start_updates()

        # Проверяем, что новые потоки не были запущены
        self.assertIsNone(obj.changers_thread)
        self.assertIsNone(obj.currencies_thread)

    def test_stop_updates_not_running(self):
        # Создаем экземпляр класса
        obj = BestChange()
        obj.running = False  # Уже остановлен

        # Мокируем потоки
        obj.changers_thread = None
        obj.currencies_thread = None

        # Вызываем stop_updates
        obj.stop_updates()

        # Проверяем, что ничего не произошло
        self.assertFalse(obj.running)
        self.assertIsNone(obj.changers_thread)
        self.assertIsNone(obj.currencies_thread)




if __name__ == '__main__':
    unittest.main(verbosity=2)
