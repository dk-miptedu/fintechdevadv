import yaml
import os

file_path = '.config/fin_bot_config.yaml'

if not os.path.exists(file_path):
    print(os.getcwd())
    print(f'Файл не найден: {file_path}')
    exit(1)

with open(file_path, 'rt') as config_file:
    config = yaml.safe_load(config_file)

#print(config)
dblink = str(config['db_link'])
bchange_api = str(config['token_api']['main'])
bchange_sl_api = str(config['token_api']['slave'])

tkn = str(config['token_tg'])