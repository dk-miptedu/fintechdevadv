import requests
import os
import sqlite3
import time
import threading

# импорт пользовательских функций и инициализация окружения
from ConfigInit import dblink, bchange_api_url, bchange_api, bchange_sl_api

api_url= '/'.join ([bchange_api_url,bchange_api])
print(f'api_url: {api_url}')
class BestChange():
    def __init__(self):
        self.db_name = dblink
        self.api_url = api_url

    def update_changers(self):
        """Получение данных из API и обновление базы данных."""
        print(f'update_changers: {self.api_url}/changers/')
        response = requests.get(f'{self.api_url}/changers/', headers={'accept': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            changers = data.get('changers', [])
            
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                for changer in changers:
                    cursor.execute('''
                        INSERT OR REPLACE INTO changers (id, name, reserve, age, listed,
                        positive_reviews, negative_reviews, neutral_reviews, verify, country, active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        changer['active']
                    ))
                conn.commit()
            print("Таблица участников обмена успешно обновлена.")
        else:
            print(f"Ошибка при запросе: {response.status_code}")

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
            print("Таблица валют успешно обновлена.")
        else:
            print(f"Ошибка при запросе: {response.status_code}")            

    def run_periodically(self, interval):
        """Запуск обновления каждые interval секунд."""
        while True:
            self.update_changers()
            self.update_currencies()
            time.sleep(interval)

    def start_periodic_update(self, interval=600):
        """Запуск обновления в отдельном потоке."""
        thread = threading.Thread(target=self.run_periodically, args=(interval,))
        thread.start()


