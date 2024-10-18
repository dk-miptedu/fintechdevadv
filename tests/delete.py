import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

import unittest
from unittest.mock import patch, MagicMock
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
        print(f'{API_URL}')

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
        print(f'result: {result}, expected_result: {expected_result}')
        self.assertEqual(result, expected_result)



if __name__ == "__main__":
    unittest.main(verbosity=2)        