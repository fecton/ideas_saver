from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.config import TOKEN, DB_NAME
from utils.db_core import DbCore
from data.long_messages import consoleContent
from os.path import exists

if not TOKEN:
    print(consoleContent["bad_token"])
    exit()

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

print('[?] Имя БД: "%s"' % DB_NAME)

if not exists(DB_NAME):
	DbCore().create_table()
	print(consoleContent["database_created"])
