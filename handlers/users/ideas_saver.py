from loader import dp
from aiogram import types
from hashlib import md5
from data.config import ANONYMOUS, SUPER_USERS
from data.long_messages import *
from time import asctime, localtime, time
from utils.db_core import DbCore
from os import listdir, remove

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
        all_ideas = DbCore().get_ideas()
        output_message = "ID / USERNAME / FIRSTNAME / DATE\n"

        if all_ideas:
            for idea in all_ideas:
                output_message += " / ".join(idea) + "\n"
            await message.answer(output_message)
        else:
            await message.answer(content["ideas_empty"])


@dp.message_handler(commands=["export"])
async def export_into(message: types.Message):
    if message.from_user.username in SUPER_USERS:
        all_data = DbCore().get_ideas()
        if all_data:
            filename = "export%d.txt" % int(time())
            with open(filename, "w") as export_file:
                for data in all_data:
                    if data[1] != "N/A":
                        data = list(data)
                        data[1] = "@" + data[1]

                    export_file.write(" / ".join(data)+"\n")

            await message.answer(f"БД успешно экспортирована в {filename}")
        else:
            await message.answer(content["db_empty"])


@dp.message_handler(commands=["clear"])
async def clear_database(message: types.Message):
    if message.from_user.username in SUPER_USERS:
        DbCore().clear()
        await message.answer(content["db_cleaned"])


@dp.message_handler(commands=["remove"])
async def remove_exports(message: types.Message):
    if message.from_user.username in SUPER_USERS:
        for file in listdir():
            if file.startswith("export") and file.endswith(".txt"):
                remove(file)

        await message.answer(content["export_cleaned"])


@dp.message_handler(content_types=["text"])
async def get_message(message: types.Message):
    if message.chat.type == "private":
        # check message on length and bad symbols
        if (len(message.text) < 10) or ("#" in message.text or "--" in message.text) or (message.text.count(" ") < 5):
            await message.answer(content["bad_message"])
            return

        user = message.from_user

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

            user_countinfo = DbCore().get_user_count(user_id)

            if user_countinfo:
                if user_countinfo[2] < int(time.time()):
                    if user_countinfo[1] == 5:
                        await message.answer(content["limit_reached"])
                        return
                    elif user_countinfo[1]+1 == 5:
                        # отправить сообщение и установить кол-во 5 и время
                        timeleft = int(time.time()) + 3600*12
                        DbCore().restrict_for_time([timeleft, user_countinfo[0]])
                    else:
                        # просто увеличить кол-во
                        user_countinfo[1] += 1
                        DbCore().increment_user_count(user_countinfo)
                else:
                    await message.answer(content["limit_reached"])
                    return
            else:
                add_user_to_count(user_id)

        text      = message.text
        date      = asctime( localtime(time()) )

        DbCore().insert_user((user_id, username, firstname, text, date))

        # if ANONYMOUS -> another message
        if ANONYMOUS:
            await message.answer(content["anonymous_to_user_on"])
        else:
            await message.answer(content["anonymous_to_user_off"])

        print(consoleContent["got_message"])