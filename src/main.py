import asyncio

# импорт пользовательских функций и инициализация окружения
from LogInit import *
from TgFunctions import *

# импорт workflow чат бота
from GramBot import *


# Запуск бота @crypt_helper_basic_bot
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
