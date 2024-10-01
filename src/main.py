import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import yaml
import os
import requests
import sqlite3
from datetime import datetime 

file_path = '.config/fin_bot_config.yaml'

if not os.path.exists(file_path):
    print(os.getcwd())
    print(f'Файл не найден: {file_path}')
    exit(1)

with open(file_path, 'rt') as config_file:
    config = yaml.safe_load(config_file)

tkn = str(config['token'])
bot = Bot(token=tkn)
storage = MemoryStorage()

class CheckStockStates(StatesGroup):
    StockID = State()

class User:
    def __init__(self, telegram_id):
        self.telegram_id = telegram_id

    def checkUserRecord(self):
        with sqlite3.connect('./dbase.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)''')
            cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (self.telegram_id,))
            return cursor.fetchone()

    def createUserRecord(self):
        with sqlite3.connect('./dbase.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)''')
            cursor.execute('INSERT INTO users (telegram_id) VALUES (?)', (self.telegram_id,))
            conn.commit()

def check_stock_existance(stock_id):
    url = f'https://iss.moex.com/iss/securities/{stock_id}.json'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        exist = data.get('boards', {}).get('data', [])
        return bool(exist)
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return False


def get_stock_price(stock_id):
    #https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/sber.json?iss.only=securities&securities.columns=PREVPRICE
    url = f'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{stock_id}.json?iss.only=securities&securities.columns=PREVPRICE,CURRENCYID'
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        data = response.json()
        data = data.get('securities').get('data')
        stock_price = data[0][0]
        stock_currency = data[0][1]
        if stock_currency == 'SUR':
            stock_currency = 'RUB'
        return stock_price, stock_currency
dp = Dispatcher(storage=storage)
dp['bot'] = bot

# Функция для записи в таблицу с ценами акций
def record_stock_price(stock_id, stock_price, stock_currency):
    timestamp = datetime.utcnow()  # Получение текущего времени в формате UTC
    with sqlite3.connect('./dbase.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS stock_prices (
            stock_id TEXT,
            price REAL,
            currency TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        cursor.execute('INSERT INTO stock_prices (stock_id, price, currency, timestamp) VALUES (?, ?, ?, ?)', 
                       (stock_id, stock_price, stock_currency, timestamp))
        conn.commit()


@dp.message(Command(commands=['start']))
async def start_command(message: types.Message):
    user = User(message.from_user.id)
    if user.checkUserRecord() is None:
        user.createUserRecord()
        await message.reply("Привет! Регистрация прошла успешно")
    else:
        await message.reply("Привет! Вы уже зарегистрированы")

@dp.message(Command('checkStock'))
async def check_stock_start(message: types.Message, state: FSMContext):
    await message.reply('Введите идентификатор ценной бумаги')
    await state.set_state(CheckStockStates.StockID.state)  # Установка состояния

@dp.message(StateFilter(CheckStockStates.StockID))
async def check_stock_id(message: types.Message, state: FSMContext):
    stock_id = message.text.upper()
    try:
        stock_existance = check_stock_existance(stock_id)
        if stock_existance:
            await message.reply('Ценная бумага существует')
            stock_price, stock_currency = get_stock_price(stock_id)
            if stock_price is not None and stock_currency is not None:
                await message.reply(f'Стоимость {stock_price} {stock_currency}')
                # Записываем данные о цене и валюте в базу данных
                record_stock_price(stock_id, stock_price, stock_currency)

            else:
                await message.reply('Не удалось получить цену акции.')
        else:
            await message.reply('Ценная бумага не существует')
    except Exception as e:
        await message.reply('Произошла ошибка при обработке запроса.')
        print(f'Ошибка: {e}')
    finally:
        await state.set_state(None)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
