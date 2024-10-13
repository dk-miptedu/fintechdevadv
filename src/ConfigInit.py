import yaml
import os

file_path = '.config/__fin_bot_config.yaml'
if not os.path.isfile(file_path):
    # Убираем "__" из имени файла
    file_path = file_path.replace('__', '', 1)

if not os.path.exists(file_path):
    print(os.getcwd())
    print(f'Файл не найден: {file_path}')
    exit(1)

with open(file_path, 'rt') as config_file:
    config = yaml.safe_load(config_file)

#print(config)

db_parh = str(config['db_parh'])
db_name = str(config['db_name'])
db_users_path = str(config['db_users_path'])
db_user_db_name_pre = str(config['db_user_db_name_pre'])

print(f'db_users_path: {db_users_path}')
dblink = os.path.join(db_parh, db_name)

# Проверяем наличие поддиректории, если её нет, создаем
if not os.path.exists(db_parh):
    try:
        os.makedirs(db_parh)
    except OSError as e:
        print(f"Ошибка при создании директории: {e}")
        exit(1)

if not os.path.exists(db_users_path):
    print(f'путь не существует: {db_users_path}')
    try:
        os.makedirs(db_users_path)
    except OSError as e:
        print(f"Ошибка при создании поддиректории: {e}")
        exit(1)


        
bchange_api_url = str(config['api_url'])
bchange_api = str(config['api_token']['main'])
bchange_sl_api = str(config['api_token']['slave'])

tkn = str(config['token_tg'])

# logging_level = str(config['logging_level'])