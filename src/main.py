import asyncio

# импорт пользовательских функций и инициализация окружения
from LogInit import *
from TgFunctions import *

# импорт workflow чат бота
from GramBot import *

# импорт Классов
from CreateDB import *


# Запуск бота @crypt_helper_basic_bot
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    CreateDB()
    bestChange_db = BestChange()
    bestChange_db.start_periodic_update(60) # Запуск обновления каждые N секунд
    asyncio.run(main())
