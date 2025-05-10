import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton,CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загрузка токена из .env
load_dotenv()
# API_TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN = ''

conn = sqlite3.connect('project_db.db')
cursor = conn.cursor()

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# FSM состояния
class Form(StatesGroup):
    role = State()
    name = State()
    phone = State()
    residence = State()
    participation = State()

role_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Я ищу", callback_data="Я ищу"),
        InlineKeyboardButton(text="Я хочу помочь найти", callback_data="Я хочу помочь найти")
    ]
])

# /start
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Тебе нужна помощь или ты хочешь помочь?", reply_markup=role_kb)
    await state.set_state(Form.role)

@dp.callback_query(lambda c: c.data == "Я ищу")
async def handle_yes(callback: CallbackQuery, state):
    await state.update_data(role='Я ищу')
    await callback.answer()
    await callback.message.answer("Напиши своё имя")
    await state.set_state(Form.name)

@dp.callback_query(lambda c: c.data == "Я хочу помочь найти")
async def handle_yes(callback: CallbackQuery, state):
    await state.update_data(role='Я хочу помочь найти')
    await callback.answer()
    await callback.message.answer("Напиши своё имя")
    await state.set_state(Form.name)


# Обработка имени
async def name_chosen(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Напиши свой телефон")
    await state.set_state(Form.phone)


# Обработка телефона
async def phone_chosen(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
        
    data = await state.get_data()
    if data['role'] == 'Я ищу':
        await message.answer("Напиши свой адрес")
        await state.set_state(Form.residence)
    else:
        await message.answer("Ты уже можешь участвовать? да/нет")
        await state.set_state(Form.participation)

# Обработка адреса
async def residence_chosen(message: Message, state: FSMContext):
    await state.update_data(residence=message.text)
    data = await state.get_data()
    print(  data['name'],
            data['phone'],
            data['residence'])
    await message.answer(f"Твои данные {data}")
    cursor.executemany('''
        INSERT INTO Owners (full_name, phone, residence)
        VALUES (?, ?, ?)
        ''', [
            (data['name'],
            data['phone'],
            data['residence'])
        ])
    conn.commit()
    await state.clear()

# Обработка участия
async def participation_chosen(message: Message, state: FSMContext):
    await state.update_data(participation=message.text)
    data = await state.get_data()
    await message.answer(f"Твои данные {data}")
    cursor.executemany('''
        INSERT INTO Seekers (name, phone, participation)
        VALUES (?, ?, ?)
        ''', [
            (data['name'],
            data['phone'],
            data['participation'])
        ])
    conn.commit()
    await state.clear()


# /cancel
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Окей, всё сбросил. Напиши /start, чтобы начать заново.", reply_markup=ReplyKeyboardRemove())

# Запуск бота
async def main():
    # bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # dp = Dispatcher()

    dp.message.register(cmd_start, F.text == "/start")
    dp.message.register(cancel_handler, F.text == "/cancel")
    # dp.message.register(role_chosen, Form.role)
    dp.message.register(name_chosen, Form.name)
    dp.message.register(phone_chosen, Form.phone)
    dp.message.register(residence_chosen, Form.residence)
    dp.message.register(participation_chosen, Form.participation)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
