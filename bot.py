import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, KeyboardButton,CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загрузка токена из .env
load_dotenv()
# API_TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN = '7228651021:AAF2mFoe0bC0BL5bngUtqvwggkOL2iPNeGM'

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


class FindForm(StatesGroup):
    dog = State()
    breed = State()
    photo = State()

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


@dp.callback_query(lambda c: c.data in ["Я хочу помочь найти", "Я ищу"])
async def handle_yes(callback: CallbackQuery, state):
    print(callback)
    await state.update_data(role=callback)
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

@dp.message(F.text == "/find")
async def find_command_handler(message: Message, state):
    await message.answer("Что ты хочешь найти?")
    await state.set_state(FindForm.dog)

# Обработка имени собаки
async def dog_chosen(message: Message, state: FSMContext):
    await state.update_data(dog=message.text)
    # data = await state.get_data()
    await message.answer(f"Отлично! Теперь породу")
    await state.set_state(FindForm.breed)


# Обработка породы собаки
async def breed_chose(message: Message, state: FSMContext):
    await state.update_data(breed=message.text)
    await message.answer("Теперь отправьте фото собаки:")
    await state.set_state(FindForm.photo)

async def photo_chose(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    photo_data = await bot.download_file(file.file_path)
    photo_bytes = photo_data.read()
    data = await state.get_data()
    name = data["dog"]
    breed = data["breed"]
    cursor.execute("INSERT INTO Dogs (name, breed, photo) VALUES (?, ?, ?)", (name, breed, photo_bytes))
    conn.commit()
    await message.answer(f"Собака {name} добавлена!")
    await state.clear()


# выводим всех собак после команды /list 
@dp.message(F.text == "/list")
async def list_dogs(message: Message):
    cursor.execute("SELECT name, breed FROM Dogs")
    rows = cursor.fetchall()

    if not rows:
        await message.answer("В базе пока нет ни одной собаки.")
        return

    for name, breed in rows:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Фото", callback_data=f"photo:{name}")]
        ])
        await message.answer(f"{name} - {breed}", reply_markup=keyboard)


# Обработка кнопок для отправки фотографии у каждой собаки
@dp.callback_query(F.data.startswith("photo:"))
async def send_dog_photo(callback: CallbackQuery):
    dog_name = callback.data.split(":")[1]

    cursor.execute("SELECT breed, photo FROM Dogs WHERE name = ?", (dog_name,))
    row = cursor.fetchone()

    if row:
        breed, photo_blob = row
        with open("temp.jpg", "wb") as f:
            f.write(photo_blob)

        photo = FSInputFile("temp.jpg")
        await callback.message.answer_photo(photo, caption=f"{dog_name}\n Порода: {breed}")
        os.remove("temp.jpg")
    else:
        await callback.message.answer(" не найдено.")

    await callback.answer()


# /cancel
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Окей, всё сбросил. Напиши /start, чтобы начать заново.", reply_markup=ReplyKeyboardRemove())

# Запуск бота
async def main():
    dp.message.register(cmd_start, F.text == "/start")
    dp.message.register(cancel_handler, F.text == "/cancel")
    dp.message.register(name_chosen, Form.name)
    dp.message.register(phone_chosen, Form.phone)
    dp.message.register(residence_chosen, Form.residence)
    dp.message.register(participation_chosen, Form.participation)
    dp.message.register(dog_chosen, FindForm.dog)
    dp.message.register(breed_chose, FindForm.breed)
    dp.message.register(photo_chose, FindForm.photo)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
