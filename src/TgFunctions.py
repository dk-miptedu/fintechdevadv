# user functions
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
