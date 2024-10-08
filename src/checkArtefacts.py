import hashlib
# импорт пользовательских функций и инициализация окружения
from ConfigInit import *

print(f'config:\n{config}')

print(f'dblink:{dblink}')
print(f'bchange_api:{bchange_api}')
print(f'bchange_sl_api:{bchange_sl_api}')

print(f'tkn:{tkn}')

def print_json(data, indent=0):
    for key, value in data.items():
        print('  ' * indent + str(key) + ':', end=' ')
        if isinstance(value, dict):
            print()  # Новый уровень вложенности
            print_json(value, indent + 1)
        else:
            print(value)
# Вызов функции
print_json(config)

# импорт Классов


def hash_user_id(user_id):
        """Хеширование идентификатора пользователя."""
        print(f'user_id: {user_id}')
        return hashlib.sha256(user_id.encode()).hexdigest()

print(hash_user_id(str(7361445538)))
