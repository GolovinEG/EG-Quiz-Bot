from random import randrange
import aiosqlite
from aiogram import types
import json

from bot_globals import Globals

def shuffle_list(unshuffled_list: list) -> list:
    shuffled_list = list()
    while len(unshuffled_list) > 0: shuffled_list.append(unshuffled_list.pop(randrange(len(unshuffled_list))))
    return shuffled_list

async def shuffle_question_list():
    for item in Globals.question_list: item["answer_list"] = shuffle_list(item["answer_list"])
    Globals.question_list = shuffle_list(Globals.question_list)

async def insert_question_index(user_id: int, question_index: int):
    await shuffle_question_list()
    async with aiosqlite.connect(Globals.DB_NAME) as db:
        await db.execute('''INSERT OR REPLACE INTO quiz_state (user_id, score, question_index, question_list) VALUES (?, ?, ?, ?)''', (user_id, 0, question_index, json.dumps(Globals.question_list)))
        await db.commit()

async def new_quiz(message: types.Message):
    user_id = message.from_user.id
    question_index = 0
    with open("question_list.json", "r") as file: json_str = file.readline()
    Globals.question_list = json.loads(json_str)
    Globals.question_list = shuffle_list(Globals.question_list)
    await insert_question_index(user_id, question_index)