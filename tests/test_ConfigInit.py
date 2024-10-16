import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))



class TestConfigInit(unittest.TestCase):

    @patch('os.path.isfile', side_effect=lambda path: path == '.config/fin_bot_config.yaml')  
    @patch('os.path.exists', side_effect=lambda path: path not in ['app_data', 'db_users', '.config/fin_bot_config.yaml'])
    @patch('builtins.open', new_callable=mock_open, read_data='''db_parh: app_data
db_name: dbase.db
db_users_path: db_users
db_user_db_name_pre: user_
api_url: https://www.bestchange.app/v2
api_token:
  main: 658dba1d7fbcc27f562b660568a6ab4d
  slave:
    - c052723ae9659345ec2750dadd880100
token_tg: 7361445538:AAFu24WyPLujFGbmFHWMBxjyXRWU_l2K6Gg
    ''')
    @patch('os.makedirs')  # Мокируем создание директорий
    def test_config_loading_and_directory_creation(self, mock_makedirs, mock_open, mock_exists, mock_isfile):
        # Импортируем код из ConfigInit
        import ConfigInit

        # Проверяем, что файл конфигурации был правильно открыт
        mock_open.assert_called_once_with('.config/fin_bot_config.yaml', 'rt')

        # Проверяем, что были созданы необходимые директории
        mock_makedirs.assert_any_call('app_data')
        mock_makedirs.assert_any_call('db_users')

        # Проверяем правильность загруженных данных
        self.assertEqual(ConfigInit.db_parh, 'app_data')
        self.assertEqual(ConfigInit.db_name, 'dbase.db')
        self.assertEqual(ConfigInit.db_users_path, 'db_users')
        self.assertEqual(ConfigInit.bchange_api_url, 'https://www.bestchange.app/v2')
        self.assertEqual(ConfigInit.bchange_api, '658dba1d7fbcc27f562b660568a6ab4d')
        self.assertEqual(ConfigInit.tkn, '7361445538:AAFu24WyPLujFGbmFHWMBxjyXRWU_l2K6Gg')

if __name__ == '__main__':
    unittest.main()
