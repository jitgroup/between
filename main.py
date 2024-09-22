import asyncio
import logging
import database as db

from aiogram import Dispatcher, Bot, types, enums, html, F
from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, 
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties


logging.basicConfig(level=logging.INFO)



class RegisterState(StatesGroup):
    full_name = State()
    phone_number = State()

class CreateAnnouncement(StatesGroup):
    title = State()
    description = State()


BOT_TOKEN = '7224050581:AAHrb6hnOAZ5OlUudb0dsmz-uin6DxtHNZU'
bot = Bot(
    token = BOT_TOKEN, 
    default = DefaultBotProperties(
        parse_mode = enums.ParseMode.HTML
    )
)


dp = Dispatcher(storage = MemoryStorage())
storage = dp.storage


@dp.message(CommandStart())
async def command_start(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)

    if user:
        if user[1] == 'user':
            await message.answer(
                text = f"Salom {message.from_user.first_name} 👋",
                reply_markup=types.ReplyKeyboardRemove()
            )
        elif user[1] == 'business':
            await message.answer(
                text = f"Salom {message.from_user.first_name}!\n\n" + (
                    html.italic("Kerakli bo'limni  tanlang 👇")
                ),
                reply_markup = types.ReplyKeyboardMarkup(
                    resize_keyboard = True,
                    one_time_keyboard = True,
                    keyboard = [
                        [
                            KeyboardButton(text = "🚀 E'lon qo'shish", callback_data = "create_annoucment")
                        ]
                    ]
                )
            )
    else:
        await state.set_state(RegisterState.full_name)
        await message.answer(
            text = "Ism-familyangizni kiriting!",
            reply_markup = types.ReplyKeyboardRemove()
        )


@dp.message(F.content_type == 'text', StateFilter(RegisterState.full_name))
async def full_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(RegisterState.phone_number)
    
    await message.answer("Telefon raqamingizni yuboring!",
        reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            keyboard=[
                [
                    KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)
                ]
            ]
        ))


@dp.message(F.content_type == 'contact', StateFilter(RegisterState.phone_number))
async def contact_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    full_name = data['full_name']
    phone_number = message.contact.phone_number

    await db.create_user(message.from_user.id, phone_number, full_name)

    await message.answer("Siz muvaffaqiyatli ro'yhatdan o'tdingiz!",
        reply_markup=types.ReplyKeyboardRemove())
    
    await state.clear()


@dp.message(F.text == '🚀 E\'lon qo\'shish')
async def create_annoucment_handler(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)

    if user[1] == 'business':
        await state.set_state(CreateAnnouncement.title)
        await message.answer(text="E'lon qo'shish uchun nom kiriting!", reply_markup=types.ReplyKeyboardRemove())


@dp.message(F.content_type == 'text', StateFilter(CreateAnnouncement.title))
async def announcement_title_handler(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(CreateAnnouncement.description)
    
    await message.answer("E'lon haqida to'liq ma'umot yozing!")


@dp.message(F.content_type == 'text', StateFilter(CreateAnnouncement.description))
async def announcement_description_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data['title']
    description = message.text
    
    await db.create_announcement(from_user_id=message.from_user.id, title=title, description=description)
    await message.answer("E'lon muvaffaqiyatli yaratildi!")
    await state.clear()

    users = await db.get_users_list()
    for user in users:
        await bot.send_message(user[0], f"""E'LON               
<b>{title}</b>

<i>{description}</i>""", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Javob yozish", callback_data='answer')
            ]
        ]
    ))



# ------------------------------------------


async def main():
    await db.create_table()
    await dp.start_polling(bot)

asyncio.run(main())