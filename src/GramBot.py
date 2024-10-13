from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ForceReply
from aiogram.filters.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from aiogram import F

import os
import requests
import sqlite3
from datetime import datetime 
from math import ceil
import logging

# импорт пользовательских функций и инициализация окружения
from ConfigInit import tkn
from MenuStructure import *

# импорт Классов
#from CreateDB importAPI_TOKEN = "ВАШ_ТОКЕН"*
from User import *
from BestChange import *

bot = Bot(token=tkn)
storage = MemoryStorage()        
dp = Dispatcher(storage=storage)
dp['bot'] = bot
router = Router()

best_change = BestChange()

# Определяем состояния для FSM (Finite State Machine)
class ExchangeStates(StatesGroup):
    waiting_for_confirmation = State()
    waiting_for_currency_count = State()
    waiting_for_currency_code = State()    


# Обработчик команды /start, отображает главное меню
@router.message(Command(commands=['start','s','.ы']))
async def start_handler(message: types.Message, state: FSMContext):
    print('async def start_command')
    msg_log = "registration new user"
    msg_welcome = "Привет! Регистрация прошла успешно\nДля старта набери: '/s' или '/start'"
    user = User(message.from_user.id)
    if user.checkUserRecord() is None:
        user.createUserRecord()
    else:
        msg_welcome = "Привет!"
        msg_log = "success user login"
    user.log_event(msg_log)
    await message.reply(msg_welcome)
    await message.answer("Главное меню:", reply_markup=generate_menu("main_menu"))

# Обработка выбора уровней меню
@router.message(lambda message: message.text in menu_structure or message.text == COMEBACK_BTN)
async def menu_handler(message: types.Message):
    if message.text == COMEBACK_BTN:
        await message.answer("Выберите направление обмена или посмотрите списки направлений", reply_markup=generate_menu("main_menu"))
    else:
        await message.answer(f"Вы перешли в {message.text}. Выберите действие:", reply_markup=generate_menu(message.text))

# Обработка ввода кода валюты
@router.message(ExchangeStates.waiting_for_currency_code)
async def process_currency_code(message: types.Message, state: FSMContext):
    currency_code = message.text
    await state.update_data(currency_code=currency_code)  # Сохраняем код валюты

    # Получаем количество обменников
    changers_count = len(best_change.get_online_banks_currencies())
    #print(f'changers_count:{changers_count}')

    # Сохраняем количество обменников в состояние
    await state.update_data(exchanger_count=changers_count)

    # Спрашиваем пользователя, готов ли он подождать
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да")],
            [KeyboardButton(text="Нет")]
        ], resize_keyboard=True)
    await message.answer(f"Число обменников: {changers_count}. Вы готовы подождать?", reply_markup=keyboard)
    await state.set_state(ExchangeStates.waiting_for_confirmation)


# Обработка подтверждения
@router.message(ExchangeStates.waiting_for_confirmation)
async def process_confirmation(message: types.Message, state: FSMContext):
    confirmation = message.text.lower()
    user_data = await state.get_data()
    text = user_data['selected_menu']
    #logging.debug(f'menu_structure: {menu_structure}')
    if confirmation in ["да","yes","y"]:
        logging.debug(f'user_data: {user_data}')      
        currency_code = user_data['currency_code']
        exchanger_count = user_data['exchanger_count']
        logging.debug(f'text: {text}')  
        path = (lambda text: 'in' if text == 'Купить за RUB' else 'out' if text == 'Продать за RUB' else '')
        await message.answer(f'Запрашиваем курсы обмена для валюты: {currency_code} в {exchanger_count} обменниках. Работаем...', reply_markup=generate_menu(find_parent_key(menu_structure,text)))       
        if all_integers([currency_code]):
            pair_best = best_change.get_best_rates_fiat(currency_code,path(text))        
            if pair_best:
                pair_best_list = "\n".join(sorted_list(pair_best))
                await message.answer(f"Курсы обмена:\n {pair_best_list}")
            else:
                await message.answer("Нет направлений обмена валюты")
        else:
            await message.answer(f"Ошибка цифрового кода криптовалюты: {message.text}")
        # Возвращаемся к исходному состоянию, если нужно продолжать взаимодействие
        await state.clear()
    elif confirmation in ["нет","no","n"]:
        await message.answer("Операция отменена.", reply_markup=generate_menu(find_parent_key(menu_structure,text)))
        await state.clear()  # Очищаем состояние, завершая диалог
    else:
        await message.answer("Пожалуйста, введите 'Да' или 'Нет'.")
    

# Обработка действий в конечных пунктах меню
@router.message(lambda message: message.text in get_terminal_points(menu_structure, "main_menu"))
async def action_handler(message: types.Message, state: FSMContext):
    selected_menu = message.text   
    logging.debug(f'message.text: {message.text}')
    if selected_menu == "Купить за RUB":
        # Сохраняем текст выбранного пункта меню
        await state.update_data(selected_menu=selected_menu)
        # Переходим в состояние ожидания кода валюты
        await message.answer("Введите цифровой код Криптовалюты (140)")
        await state.set_state(ExchangeStates.waiting_for_currency_code)
    elif selected_menu == "Список продавцов":
        changers = best_change.get_changers_url_list()
        if changers:
            changers_list = "\n".join(changers)
            await message.answer(f"{selected_menu}:\n{changers_list}", parse_mode="Markdown")
        else:
            await message.answer("Нет доступных продавцов.")        
        
    elif selected_menu == "Продать за RUB":
        # Сохраняем текст выбранного пункта меню
        await state.update_data(selected_menu=selected_menu)
        # Переходим в состояние ожидания кода валюты
        await message.answer("Введите цифровой код Криптовалюты (139)")
        await state.set_state(ExchangeStates.waiting_for_currency_code)
    elif selected_menu == "Список покупателей":
        changers = best_change.get_changers_url_list()
        if changers:
            changers_list = "\n".join(changers)
            await message.answer(f"{selected_menu}:\n{changers_list}", parse_mode="Markdown")
        else:
            await message.answer("Нет доступных покупателей.")        
    elif selected_menu == "Криптовалюты":
        currencies=best_change.get_crypto_currencies()
        if currencies:
            currencies_list = "\n".join(currencies)
            await message.answer(f"Список криптовалют:\n{currencies_list}")
        else:
            await message.answer("Нет доступных криптовалют с кодом RUB.")
    elif selected_menu == "Валюты в Банках":
        currencies=best_change.get_online_banks_currencies()
        if currencies:
            currencies_list = "\n".join(currencies)
            await message.answer(f"Список валют с кодом RUB:\n{currencies_list}")
        else:
            await message.answer("Нет доступных валют с кодом RUB.")
    elif selected_menu == "Криптобиржи":
        currencies=best_change.get_crypto_currencies_exchange()
        if currencies:
            currencies_list = "\n".join(currencies)
            await message.answer(f"Список криптобирж:\n{currencies_list}")
        else:
            await message.answer("Нет доступных вкриптобирж с кодом RUB.")
    else:
        await message.answer("Неизвестное действие.")

@router.message(Command(commands=['help','h']))
async def help_command(message: types.Message):
    help_text = (
        "Привет! Я помогу Вам получить актальную информацию по вариантам обмена фиатных и цифровых валют.\n\n"
        "Покупка криптовалюты за фиатные деньги осуществляется через различные финансовые организации. Обратите внимание, что из-за большого количества операторов обмена курсы могут значительно отличаться.\n"
        "Вот что я могу делать:\n\n"
        "**Купить за RUB** – Узнайте лучшие курсы для покупки криптовалют за рубли.\n"
        "**Продать за RUB** – Получите актуальные курсы для продажи криптовалют за рубли.\n"
        "**Список обменников:** – Список поддерживаемых участников обмена.\n\n"
        "**Валюты в Банках** – Список поддерживаемых инструментов для ввод/вывода криптовалюты за рубли.\n"
        "**Криптовалюты:** – Список поддерживаемых криптовалют.\n\n"
        "**Криптобиржи:** – Список поддерживаемых для использования балансов криптобирж.\n\n"
        "Используйте кнопки в меню для навигации по этим функциям или введите команды вручную.\n"
        "Покупка и продажа криптовалют производится через проверенные обменники, но их количество и условия могут повлиять на итоговые курсы.\n\n"
        "Команды:\n"
        "/start, /s - начать работу с ботом\n"
        "/help - показать это сообщение"
    )
    await message.answer(help_text, parse_mode="Markdown")

    "Валюты в Банках", "Криптовалюты", "Криптобиржи" 
