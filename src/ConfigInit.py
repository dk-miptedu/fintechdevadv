import yaml
import os

file_path = '.config/__fin_bot_config.yaml'

if not os.path.exists(file_path):
    print(os.getcwd())
    print(f'Файл не найден: {file_path}')
    exit(1)

with open(file_path, 'rt') as config_file:
    config = yaml.safe_load(config_file)

#print(config)

db_parh = str(config['db_parh'])
db_name = str(config['db_name'])

dblink = os.path.join(db_parh, db_name)

# Проверяем наличие поддиректории, если её нет, создаем
if not os.path.exists(db_parh):
    try:
        os.makedirs(db_parh)
    except OSError as e:
        print(f"Ошибка при создании директории: {e}")
        exit(1)

bchange_api = str(config['token_api']['main'])
bchange_sl_api = str(config['token_api']['slave'])

tkn = str(config['token_tg'])