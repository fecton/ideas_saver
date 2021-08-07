#!/usr/env/python3
#-*- encoding: UTF-8 -*-

__version__ = "0.1"

import sqlite3
import time
import os

from aiogram import Bot, Dispatcher, executor, types
from hashlib import md5




# here is your token
TOKEN = ""
# save user's information?
ANONYMOUS = False
# database name
DB_NAME = "db_ideas.sqlite3"
# enter username without '@'
SUPER_USERS = []

content = {
  "Astart" : "Привет! Я тут играю роль секретаря и записываю все ваши идеи себе в блокнотик. Напииши мне любое сообщение и я передам его своему хозяину.",
  "start"  : "Привет! Я тут играю роль секретаря и записываю все ваши идеи себе в блокнотик. Напииши мне любое сообщение и я передам его своему хозяину.\nКоличество отправленных сообщений в день ограничено - 5 сообщений",
  "help"   : "Вот краткая справка по всему:\n⭕️ /start - показать стартовое сообщение\n⭕️ /help - показать эту справку\n⭕️ /show - показать все сообщения\n⭕️ /export - экспортировать сообщения в txt-файл\n⭕️ /clear - очистить БД\n⭕️ /remove - удалить все экспортированные файлы из текущей директории\n⭕️ *Просто сообщение* - закинуть в БД"
}

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
if not os.path.exists(DB_NAME):
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
    db.execute("""
    CREATE TABLE `count`(
        user_id  VARCHAR(255) NOT NULL,
        count    INTEGER NOT NULL,
        timeleft INTEGER NOT NULL
    )
    """)
    db.commit()
    db.close()
    print("[+] Database has created successfully! <3")


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if ANONYMOUS:
        await message.answer(content["Astart"])
    else:
        await message.answer(content["start"])


@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    if message.from_user.username in SUPER_USERS:
        await message.answer(content["help"])


@dp.message_handler(commands=["show"])
async def show_all_ideas(message: types.Message):
    if message.from_user.username in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)

        all_ideas = db.execute("SELECT * FROM `ideas`").fetchall()

        db.close()

        output_message = "ID / USERNAME / FIRSTNAME / DATE\n"

        if all_ideas:
            for idea in all_ideas:
                output_message += " / ".join(idea) + "\n"
            await message.answer(output_message)
        else:
            await message.answer("Упс! Ещё нету предложений!")


@dp.message_handler(commands=["export"])
async def export_into(message: types.Message):
    if message.from_user.username in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)
        all_data = db.execute("SELECT * FROM `ideas`").fetchall()
        db.close()
        if all_data:
            filename = "export%d.txt" % int(time.time())
            with open(filename, "w") as export_file:
                for data in all_data:
                    if data[1] != "N/A":
                        data = list(data)
                        data[1] = "@" + data[1]

                    export_file.write(" / ".join(data)+"\n")

            await message.answer(f"[+] БД успешно экспортирована в {filename}")
        else:
            await message.answer("[-] БД пуста! Экспорт не выполнен!")


@dp.message_handler(commands=["clear"])
async def clear_database(message: types.Message):
    if message.from_user.username in SUPER_USERS:
        db = sqlite3.connect(DB_NAME)
        db.execute("DELETE FROM `ideas`")
        db.commit()
        db.close()
        await message.answer("[+] БД успешно очищена!")


@dp.message_handler(commands=["remove"])
async def remove_exports(message: types.Message):
    if message.from_user.username in SUPER_USERS:
        deleted_files = 0
        for file in os.listdir():
            if file.startswith("export") and file.endswith(".txt"):
                os.remove(file)
                deleted_files += 1

        if not deleted_files:
            await message.answer("[-] Нету файлов экспорта для удаления!")
        else:
            await message.answer("[+] Все файлы экспорта очищены успешно!")


@dp.message_handler(content_types=["text"])
async def get_message(message: types.Message):
    if message.chat.type == "private":
        # check message on length and bad symbols
        if len(message.text) < 10:
            await message.answer("Ваше сообщение слишком короткое!")
            return
        elif "#" in message.text or "--" in message.text:
            await message.answer("В вашем сообщении недопустимые символы! (#, --)")
            return
        elif message.text.count(" ") < 5:
            await message.answer("Что-то не так в вашем сообщении :(")
            return

        user = message.from_user
        db = sqlite3.connect(DB_NAME)
        # do not save info about user if ANONYMOUS
        if ANONYMOUS:
            # no info
            user_id, username, firstname   = "N/A", "N/A", "N/A"
        else:
            # info
            user_id   = user.id
            username  = user.username
            firstname = user.first_name
                        # if aldready inserted

            user_countinfo = list(db.execute(f"SELECT * FROM `count` WHERE user_id={user_id}").fetchone())

            if user_countinfo:
                if user_countinfo[2] < int(time.time()):
                    if user_countinfo[1] == 5:
                        await message.answer("Вы достигли лимита отправки сообщений в день!")
                        db.close()
                        return
                    elif user_countinfo[1]+1 == 5:
                        # отправить сообщение и установить кол-во 5 и время
                        timeleft = int(time.time()) + 3600*12
                        db.execute(f"UPDATE `count` SET count=5, timeleft={timeleft} WHERE user_id={user_countinfo[0]}")
                    else:
                        # просто увеличить кол-во
                        user_countinfo[1] += 1
                        db.execute(f"UPDATE `count` SET count={user_countinfo[1]} WHERE user_id={user_countinfo[0]}")
                else:
                    await message.answer("Вы достигли лимита отправки сообщений в день!")
                    db.close()
                    return
            else:
                db.execute("INSERT INTO `count` (user_id, count, timeleft) VALUES (?,?,?)",(user_id, 1, 0))

        text      = message.text
        date      = time.asctime( time.localtime(time.time()) )

        db.execute("""
        INSERT INTO `ideas` (user_id, username, firstname, text, date)
        VALUES (?,?,?,?,?)
        """, (user_id, username, firstname, text, date))

        db.commit()
        db.close()
        # if ANONYMOUS -> another message
        if ANONYMOUS:
            await message.answer("Мой хозяин позаботился о вашей конфидициальности — я сохраню только ваш текст и дату отправки!\n\n💛 Спасибо вам за вашу активность!")
        else:
            await message.answer("💛 Спасибо вам за вашу активность!")

        print("[+] Мы получили сообщение! =)")

# start bot execution
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
