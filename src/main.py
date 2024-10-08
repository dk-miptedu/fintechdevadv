import asyncio
import logging
from decouple import config # pip install python-decouple
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

# импорт пользовательских функций
from TgFunctions import *

# импорт Классов
from User import *
from CheckStockStates import *


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
logger = logging.getLogger(__name__)

file_path = '.config/fin_bot_config.yaml'

if not os.path.exists(file_path):
    print(os.getcwd())
    print(f'Файл не найден: {file_path}')
    exit(1)

with open(file_path, 'rt') as config_file:
    config = yaml.safe_load(config_file)

print(config)
bchange_api = str(config['main'])
bchange_sl_api = str(config['slave'])

tkn = str(config['token_tg'])
bot = Bot(token=tkn)
storage = MemoryStorage()        
dp = Dispatcher(storage=storage)
dp['bot'] = bot


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
