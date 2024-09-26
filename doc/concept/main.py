from aiogram import Bot, Dispatcher #, executor, types
import yaml, os

file_path = '.config/fin_bot_config.yaml'
if not os.path.exists(file_path):
    print (os.getcwd())
    print(f'file not found')
with open(file_path,'rt') as config_file:
    config = yaml.safe_load(config_file)
token = config['token']
print(token)
#bot = Bot(token='')

#dp = Dispatcher(bot)