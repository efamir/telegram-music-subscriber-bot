from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data_base import sqlite_dp
from aiogram.utils.exceptions import ChatNotFound

import os

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot)


def start_logging():
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')


@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.reply("Hi. Use /help command to view the list of available commands.")


@dp.message_handler(Text(startswith="/set_channel "))
async def set_chanel_cmd(message: types.Message):
    channel_id = message.text[13:]
    if len(message.text) == 23:
        channel_id = "-100" + channel_id
    try:
        if message.from_user.id in \
                [item.user.id for item in await (await bot.get_chat(channel_id)).get_administrators()]:
            if await sqlite_dp.sql_add(message.from_user.id, channel_id, True):
                await message.answer("Channel is added successfully.")
            else:
                await message.answer("You've already added the channel.")
        else:
            await message.answer("You are not channel admin or you are bot. If it's not true, type /set_bot command "
                                 "in channel again.")
    except Exception as ex:
        await message.answer(f"Something went wrong")
        print(ex)


@dp.message_handler(Text(startswith="/sub "))
async def set_chanel_sub_cmd(message: types.Message):
    channel_id = message.text[5:]
    if len(message.text) == 15:
        channel_id = "-100" + channel_id
    try:
        print(channel_id)
        await bot.get_chat(channel_id)
        if await sqlite_dp.sql_add(message.from_user.id, channel_id, False):
            await message.answer("You've subscribed successfully.")
        else:
            await message.answer("You've already subscribed to the channel.")
    except ChatNotFound:
        await message.answer("There is no channel by this id.")


@dp.channel_post_handler(content_types=["audio"])
async def mus_handler(message: types.Message):
    file_id = message.audio.file_id
    channel_subs = await sqlite_dp.read_channels_subs(message.chat.id)
    for user_id in channel_subs[0]:
        if sqlite_dp.check_if_admin(user_id):
            b1 = InlineKeyboardButton(text="+", callback_data=f"add {message.chat.id}")  # add_{file_id}
            b2 = InlineKeyboardButton(text="-", callback_data="del")
            await bot.send_audio(user_id, file_id, reply_markup=InlineKeyboardMarkup(row_width=2).add(b1).insert(b2))
        else:
            await bot.send_audio(user_id, file_id)


@dp.callback_query_handler(text="del")
async def del_audio_suggest(callback: types.CallbackQuery):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)


@dp.callback_query_handler(Text(startswith="add "))
async def del_audio_suggest(callback: types.CallbackQuery):
    print(callback.data)
    await bot.send_audio(callback.data.replace("add ", ""), callback.message.audio.file_id)
    await bot.delete_message(callback.from_user.id, callback.message.message_id)


@dp.message_handler(Text(startswith="/unsub "))
async def set_chanel_sub_cmd(message: types.Message):
    channel_id = message.text[7:]
    if len(message.text) == 17:
        channel_id = "-100" + channel_id
    try:
        await bot.get_chat(channel_id)
        await sqlite_dp.unsub(channel_id, message.from_user.id)
        await message.answer("You have been unsubscribed successfully")
    except ChatNotFound:
        await message.answer("There is no channel by this id")


@dp.message_handler(commands=["help"])
async def help_com(message: types.Message):
    await message.answer("List of commands:\n/sub <channel id> - subscribe to the channel.\n"
                         "/unsub <channel id> - unsubscribe\n"
                         "/set_channel <channel id> - choose your channel.")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("I don't understand XD. Use /help command to view the list of available commands")


if __name__ == '__main__':
    start_logging()
    sqlite_dp.sql_start()
    executor.start_polling(dp, skip_updates=True)
