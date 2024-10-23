from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# текст для кнопки назад
COMEBACK_BTN = "⬅️ Back"
# Словарь для многоуровневого меню
menu_structure = {
    "main_menu": ["Банк-Крипто", "Крипто-Банк", "Списки активов"],
    "Банк-Крипто": ["Купить за RUB", "Список продавцов"],
    "Крипто-Банк": ["Продать за RUB", "Список покупателей"],
    "Списки активов": ["Инструменты RUB", "Криптовалюты", "Криптобиржи" ]
}

# Генерация клавиатуры бота по заданному уровню меню
def generate_menu(level: str):
    buttons = menu_structure.get(level, [])
    
    # Проверяем, если кнопки "Назад" нет в списке, добавляем её в конец
    if COMEBACK_BTN not in buttons and level != "main_menu":
        buttons.append(COMEBACK_BTN)
    keyboard_buttons = [KeyboardButton(text=button_text) for button_text in buttons]
    return ReplyKeyboardMarkup(keyboard=[keyboard_buttons], resize_keyboard=True)

# Список конечных пунктов меню
def get_terminal_points(menu_structure, current_level):
    terminal_points = []
    
    # Получаем элементы текущего уровня
    for item in menu_structure.get(current_level, []):
        # Если элемент есть в ключах menu_structure, это подменю, нужно рекурсивно проверить его
        if item in menu_structure:
            terminal_points.extend(get_terminal_points(menu_structure, item))
        else:
            # Если элемента нет в ключах menu_structure, это конечный пункт
            terminal_points.append(item)    
    return terminal_points

# поиск родителя по конечному значению 
def find_parent_key(menu, value):
    for parent_key, sub_menu in menu.items():
        if value in sub_menu:
            return parent_key
    return None

# Проверка возможности преобразования списка строковых значений в целочисленные
def all_integers(lst):
    print(f'list: {lst}')
    for item in lst:
        try:
            int(item)
        except ValueError:
            return False
    return True

def sorted_list(data,reverse=True):
    return sorted(data, key=lambda x: float(x.split(":")[1].split(",")[0]),reverse=reverse)
