import aiosqlite
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types, F
import json

from bot_globals import *

async def get_question_index(user_id: int):
    async with aiosqlite.connect(Globals.DB_NAME) as db:
        async with db.execute('''SELECT question_index FROM quiz_state WHERE user_id = (?)''', (user_id, )) as cursor:
            results = await cursor.fetchone()
            return 0 if results is None else results[0]  

def generate_answers_keyboard(answer_list: list, correct_answer: str):
    builder = InlineKeyboardBuilder()
    for answer in answer_list:
        data = "correct" if answer == correct_answer else "wrong"
        builder.add(types.InlineKeyboardButton(text = answer,
            callback_data = data + " " + answer))
    builder.adjust(1)
    return builder.as_markup()

async def get_score(user_id: int):
    async with aiosqlite.connect(Globals.DB_NAME) as db:
        async with db.execute('''SELECT score FROM quiz_state WHERE user_id = (?)''', (user_id, )) as cursor:
            result = await cursor.fetchone()
            return result[0]

async def update_quiz_state(user_id: int, question_index: int, increase_score: bool = False):
    async with aiosqlite.connect(Globals.DB_NAME) as db:
        if increase_score:
            score = await get_score(user_id)
            await db.execute('''UPDATE quiz_state SET question_index = (?), score = (?) WHERE user_id = (?)''', (question_index, score + 1, user_id))
        else: await db.execute('''UPDATE quiz_state SET question_index = (?) WHERE user_id = (?)''', (question_index, user_id))
        await db.commit()

async def refresh(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.bot.edit_message_text(
        chat_id = user_id,
        message_id = callback.message.message_id,
        text = callback.data.split(maxsplit = 1)[1])
    #await callback.bot.edit_message_reply_markup(
    #    chat_id = user_id,
    #    message_id = callback.message.message_id,
    #    reply_markup = None)
    if len(Globals.question_list) == 0:
        async with aiosqlite.connect(Globals.DB_NAME) as db:
            async with db.execute('''SELECT question_list FROM quiz_state WHERE user_id = (?)''', (user_id, )) as cursor:
                result = await cursor.fetchone()
                Globals.question_list = json.loads(result[0])
    question_index = await get_question_index(user_id)
    return Globals.question_list[question_index]

async def next_question(callback: types.CallbackQuery, increase_score: bool = False):
    user_id = callback.from_user.id
    question_index = await get_question_index(user_id) + 1
    await update_quiz_state(user_id, question_index, increase_score)
    if question_index < len(Globals.question_list): await get_question(callback.message, user_id)
    else:
        score = await get_score(user_id)
        await callback.message.answer(f"That was the last question. Quiz finished! You got {score}/10 questions correct. {'Perfect!' if score == 10 else ''}")

async def get_question(message: types.Message, user_id: int):
    question_index = await get_question_index(user_id)
    current_question = Globals.question_list[question_index]
    question_text = current_question["question_text"]
    answer_list = current_question["answer_list"]
    correct_answer = current_question["correct_answer"]
    keyboard = generate_answers_keyboard(answer_list, correct_answer)
    await message.answer(question_text, reply_markup = keyboard)

@Globals.dp.callback_query(F.data.split(maxsplit = 1)[0] == "correct")
async def correct(callback: types.CallbackQuery):
    await refresh(callback)
    await callback.message.answer("Correct!")
    await next_question(callback, True)

@Globals.dp.callback_query(F.data.split(maxsplit = 1)[0] == "wrong")
async def correct(callback: types.CallbackQuery):
    current_question = await refresh(callback)
    await callback.message.answer(f"Wrong. The correct answer is '{current_question["correct_answer"]}'")
    await next_question(callback)