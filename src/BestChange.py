from aiogram.types import Message
import aiohttp
import asyncio
import requests
import os
import sqlite3
import time
import threading
import logging

# импорт пользовательских функций и инициализация окружения
from ConfigInit import dblink, bchange_api_url, bchange_api, bchange_sl_api

api_url= '/'.join ([bchange_api_url,bchange_api])
print(f'api_url: {api_url}')
class BestChange():
    def __init__(self):
        self.db_name = dblink
        self.api_url = api_url
        self.changers_interval = 3600  # обновление changers в секундах
        self.currencies_interval = 72000  # Интервал обновления currencies в секундах
        self.changers_thread = None
        self.currencies_thread = None
        self.running = False  # Флаг для управления запуском/остановкой
        logging.debug(f'__init__ params: {self}') 

    
    def get_changers_url_list(self, top=100):
        query = 'SELECT id, name, positive_reviews, negative_reviews, url_en FROM changers WHERE active=1 ORDER BY reserve DESC limit 50'
        result = []
        # Открытие соединения с базой данных
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            # Форматируем результатget_best_rates_fiat
            for row in rows:
                changers_id, viewname, positive_reviews, negative_reviews, url_en = row
                result.append(f"{changers_id}: [{viewname}]({url_en}), pos-neg: {positive_reviews}-{negative_reviews}")
        logging.debug(f'get_changers_url_list results - count rows: {len(result)}')                
        return result
    
    def get_crypto_currencies_exchange(self):
        query = 'SELECT id, viewname FROM currencies WHERE group_id = 2'
        result = []
        # Открытие соединения с базой данных
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            # Форматируем результатget_best_rates_fiat
            for row in rows:
                currency_id, viewname = row
                result.append(f"{currency_id}: {viewname}")
        logging.debug(f'get_crypto_currencies_exchange results - count rows: {len(result)}')                
        return result

    def  get_crypto_currencies(self):
        query = 'SELECT id, viewname FROM currencies WHERE group_id = 0'
        result = []
        # Открытие соединения с базой данных
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            # Форматируем результат
            for row in rows:
                currency_id, viewname = row
                result.append(f"{currency_id}: {viewname}")
        logging.debug(f'get_crypto_currencies results - count rows: {len(result)}')                
        return result

    def get_online_banks_currencies(self):
        query = 'SELECT id, viewname FROM currencies WHERE group_id = 3 AND code LIKE "%RUB"'
        result = []
        # Открытие соединения с базой данных
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            # Форматируем результат
            for row in rows:
                currency_id, viewname = row
                result.append(f"{currency_id}: {viewname}")
        logging.debug(f'get_online_banks_currencies results - count rows: {len(result)}')
        return result

    def get_best_rates_fiat(self, curr_code, path_curr="out", message: Message = None):
        """Получить лучшие курсы обмена для криптовалюты"""
        logging.debug(f'get_best_rates_fiat params-  curr_code: {curr_code}, path_curr: {path_curr}')
        result = []
        fiat_code = []
        fiat = self.get_online_banks_currencies()
        if path_curr == "in":
            fiat_code = ([[item.split(':')[0],curr_code] for item in fiat])
        elif path_curr =="out":
            fiat_code = ([[curr_code,item.split(':')[0]]for item in fiat])
        else:
            return []
        for i in fiat_code:
            response = requests.get(f'{self.api_url}/presences/{i[0]}-{i[1]}/', headers={'accept': 'application/json'})
            if response.status_code == 200:
                data = response.json()
                presences = data.get('presences', [])
                for presence in presences:
                    result.append(f'{presence["pair"]}: {presence["best"]}, количество обменников: {presence["count"]}')
        logging.debug(f'get_best_rates_fiat count rows: {len(result)}')                    
        return result    

    def get_best_rates(self, pair):
        """Получить лучшие курсы обмена для валютной пары"""
        result = []
        response = requests.get(f'{self.api_url}/presences/{pair[0]}-{pair[1]}/', headers={'accept': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            presences = data.get('presences', [])
            for presence in presences:
                result.append(f'{presence["pair"]}: {presence["best"]}, количество обменников: {presence["count"]}')
        logging.debug(f'get_best_rates results - count rows: {len(result)}')                
        return result      

    def get_changer_url(changer_id, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT url_en FROM changers WHERE id = ?", (changer_id,))
        result = cursor.fetchone()
        return result[0] if result else None    

    def get_best_rates_top(self, pair):
        """Получить курсы обменных пунков для валютной пары с отклонением в rates% от get_best_rates"""
        query = 'SELECT positive_reviews FROM changers WHERE id = ?'
        best_rates = []
        results = []
        response = requests.get(f'{self.api_url}/presences/{pair[0]}-{pair[1]}/', headers={'accept': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            presences = data.get('presences', [])
            for presence in presences:
                best_rates.append(float(presence["best"]))
        if len(best_rates)>0:
            lower_rates = max(best_rates)*0.95

        # /v2/{apiKey}/rates/{fromCurrencyId}-{toCurrencyId}
            response = requests.get(f'{self.api_url}/rates/{pair[0]}-{pair[1]}/', headers={'accept': 'application/json'})
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {}).get('-'.join(pair),[])
                conn = sqlite3.connect(self.db_name)
                for rate in rates:
                    if lower_rates >= float(rate["rate"]):
                        changer_id = rate["changer"]
                
                        # Получаем URL обменника из таблицы changers в базе данных
                        changer_url = get_changer_url(changer_id, conn)
                        
                        # Добавляем данные в результат, включая URL
                        results.append([changer_id, rate["rate"], rate["reserve"], changer_url])
        conn.close()
        logging.debug(f'get_best_rates_top results - count rows: {len(result)}')           
        return results
    
    def update_changers(self):
        """Получение данных из API и обновление базы данных."""
        print(f'update_changers: {self.api_url}/changers/')
        response = requests.get(f'{self.api_url}/changers/', headers={'accept': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            changers = data.get('changers', [])
            #print(changers)
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                for changer in changers:
                    cursor.execute('''
                                   INSERT OR REPLACE INTO changers (id, name, reserve, age, listed,
                        positive_reviews, negative_reviews, neutral_reviews, verify, country, active, url_en)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                        changer['id'],
                        changer['name'],
                        changer['reserve'],
                        changer['age'],
                        changer['listed'],
                        changer['reviews']['positive'],
                        changer['reviews']['closed'],
                        changer['reviews']['neutral'],
                        changer['verify'],
                        changer['country'],
                        changer['active'],
                        changer['urls'].get('en') or changer['urls'].get('ru', None)  
                    ))
                conn.commit()
            logging.info("Таблица участников обмена успешно обновлена.")
        else:
            logging.info(f"Ошибка при запросе: {response.status_code}")


    def update_currencies(self):
        """Получение данных о валютах из API и обновление базы данных."""
        print(f'update_changers: {self.api_url}/currencies/')
        response = requests.get(f'{self.api_url}/currencies/', headers={'accept': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            currencies = data.get('currencies', [])
            
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                for currency in currencies:
                    cursor.execute('''
                        INSERT OR REPLACE INTO currencies (id, name, urlname, viewname, code, crypto, cash, ps, group_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        currency['id'],
                        currency['name'],
                        currency['urlname'],
                        currency['viewname'],
                        currency['code'],
                        currency['crypto'],
                        currency['cash'],
                        currency['ps'],
                        currency['group']
                    ))
                conn.commit()
            logging.info("Таблица валют успешно обновлена.")
        else:
             logging.info(f"Ошибка при запросе: {response.status_code}")            

    def periodic_update_changers(self):
        """Периодический вызов функции update_changers."""
        while self.running:
            self.update_changers()
            time.sleep(self.changers_interval)

    def periodic_update_currencies(self):
        """Периодический вызов функции update_currencies."""
        while self.running:
            self.update_currencies()
            time.sleep(self.currencies_interval)

    def start_updates(self):
        """Запуск периодических обновлений в отдельных потоках."""
        if not self.running:
            self.running = True
            print("Запущены обновления общих данных bestChange.")
            self.changers_thread = threading.Thread(target=self.periodic_update_changers)
            self.currencies_thread = threading.Thread(target=self.periodic_update_currencies)
            self.changers_thread.start()
            self.currencies_thread.start()

    def stop_updates(self):
        """Остановка периодических обновлений."""
        if self.running:
            print("Остановлены обновления общих данных bestChange.")
            self.running = False
            if self.changers_thread is not None:
                self.changers_thread.join()  # Дожидаемся завершения потока
            if self.currencies_thread is not None:
                self.currencies_thread.join()  # Дожидаемся завершения потока