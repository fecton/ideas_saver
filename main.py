#!/usr/env/python3
#-*- encoding: UTF-8 -*-

__version__ = "0.1"

import sqlite3
import time

from aiogram import Bot, Dispatcher, executor, types
from os import path
from hashlib import md5

# here is your token
TOKEN = ""
# save user's information?
ANONYMOUS = True
DB_NAME = "db_ideas.sqlite3"

# if token wasn't entered
if not TOKEN:
    print("[-] Введите токен!")
    exit()

if ANONYMOUS:
    print("[?] Бот не будет сохранять информацию о пользователях!")

print('[?] Имя БД: "%s"' % DB_NAME)

# creates the bot
bot = Bot(TOKEN)
# gets bot's decorator
dp = Dispatcher(bot)

# if it's first start -> create the database and tables
if not path.exists(DB_NAME):
    db = sqlite3.connect(DB_NAME)
    db.execute("""
    CREATE TABLE `ideas`(
        user_id   VARCHAR(255) NOT NULL,
        username  VARCHAR(32)  NOT NULL,
        firstname VARCHAR(255) NOT NULL,
        text      TEXT         NOT NULL,
        date      VARCHAR(128) NOT NULL
    )
    """)
    db.commit()
    db.close()
    print("[+] Database has created successfully! <3")


@dp.message_handler(commands=["show"])
async def show_all_ideas(message : types.Message):
    db = sqlite3.connect(DB_NAME)

    all_ideas = db.execute("SELECT * FROM `ideas`").fetchall()

    db.close()

    output_message = "ID*USERNAME*FIRSTNAME*DATE\n"

    if all_ideas:
        for idea in all_ideas:
            output_message += "*".join(idea) + "\n"
        await message.answer(output_message)
    else:
        await message.answer("Упс! Ещё нету предложений!")


@dp.message_handler(content_types=["text"])
async def get_message(message: types.Message):
    if message.chat.type == "private":
        if len(message.text) < 10:
            await message.answer("Ваше сообщение слишком короткое!")
            return
        elif "#" in message.text or "--" in message.text:
            await message.answer("В вашем сообщении недопустимые символы! (#, --)")
            return

        # hash user's id if global HASH
        if ANONYMOUS:
            user_id, username, firstname   = "N/A", "N/A", "N/A"
        else:
            user_id   = message.from_user.id
            username  = message.from_user.username
            firstname = message.from_user.first_name

        text      = message.text
        date      = time.asctime( time.localtime(time.time()) )

        db = sqlite3.connect(DB_NAME)

        db.execute("""
        INSERT INTO `ideas` (user_id, username, firstname, text, date)
        VALUES (?,?,?,?,?)
        """, (user_id, username, firstname, text, date))

        db.commit()
        db.close()
        if ANONYMOUS:
            await message.answer("Мой хозяин позаботился о вашей конфидициальности — я сохраню только ваш текст и дату отправки!\n\n💛 Спасибо вам за вашу активность!")
        else:
            await message.answer("💛 Спасибо вам за вашу активность!")

        print("[+] Мы получили сообщение! =)")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
