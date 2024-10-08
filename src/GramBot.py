from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import os
import requests
import sqlite3
from datetime import datetime 

# импорт пользовательских функций и инициализация окружения
from ConfigInit import tkn

# импорт Классов
from User import *
from CheckStockStates import *

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
