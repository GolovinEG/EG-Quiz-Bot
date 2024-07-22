import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_globals import *
from bot_new_quiz import new_quiz
from bot_quiz_flow import get_question, get_score

logging.basicConfig(level = logging.INFO)
with open("Pasta.txt") as file: API_TOKEN = file.readline()[:-1]
bot = Bot(API_TOKEN)

async def create_table():
    async with aiosqlite.connect(Globals.DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, score INTEGER, question_index INTEGER, question_list TEXT)''')
        await db.commit()

async def main():
    await create_table()
    await Globals.dp.start_polling(bot)     

@Globals.dp.message(Command("start"))
async def start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text = "Start the quiz"))
    #await message.edit_text("Start")
    score = await get_score(message.from_user.id)
    await message.answer(f"Welcome to the quiz! Your score on the last quiz was {score}.", reply_markup = builder.as_markup(resize_keyboard = True))

@Globals.dp.message(F.text == "Start the quiz")
@Globals.dp.message(Command("quiz"))
async def quiz(message: types.Message):
    #await message.edit_text("Start the quiz")
    await message.answer("Time to start the quiz!")
    await new_quiz(message)
    await get_question(message, message.from_user.id)

if __name__ == "__main__": asyncio.run(main())