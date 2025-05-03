import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загрузка токена из .env
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

# FSM состояния
class Form(StatesGroup):
    role = State()
    name = State()
    phone = State()
    residence = State()
    participation = State()

# Клавиатура выбора пола
role_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Я ищу")],
        [KeyboardButton(text="Я хочу помочь найти")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# /start
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Тебе нужна помощь или ты хочешь помочь?", reply_markup=role_kb)
    await state.set_state(Form.role)

# Обработка роли
async def role_chosen(message: Message, state: FSMContext):
    if message.text not in ["Я ищу", "Я хочу помочь найти"]:
        return await message.answer("Пожалуйста, выбери вариант с клавиатуры.")
    await state.update_data(role=message.text)
    await message.answer("Напиши своё имя", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.name)
    # if message.text == "👦 Мальчик":
    #     await state.set_state(Form.name)
    # else:
    #     await state.set_state(Form.second_name)

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
    await message.answer(f"Твои данные {data}")
    await state.clear()

# Обработка участия
async def participation_chosen(message: Message, state: FSMContext):
    await state.update_data(participation=message.text)
    data = await state.get_data()
    await message.answer(f"Твои данные {data}")
    await state.clear()


# /cancel
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Окей, всё сбросил. Напиши /start, чтобы начать заново.", reply_markup=ReplyKeyboardRemove())

# Запуск бота
async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.register(cmd_start, F.text == "/start")
    dp.message.register(cancel_handler, F.text == "/cancel")
    dp.message.register(role_chosen, Form.role)
    dp.message.register(name_chosen, Form.name)
    dp.message.register(phone_chosen, Form.phone)
    dp.message.register(residence_chosen, Form.residence)
    dp.message.register(participation_chosen, Form.participation)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
