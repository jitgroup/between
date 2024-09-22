import asyncio
import logging
import database as db
from aiogram import Dispatcher, Bot, types, enums, html, F
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

logging.basicConfig(level=logging.INFO)


class RegisterState(StatesGroup):
    user_type = State()
    full_name = State()
    phone_number = State()
    company_name = State()
    company_logo = State()


class CreateAnnouncement(StatesGroup):
    title = State()
    description = State()


class AnswerAnnouncement(StatesGroup):
    answer = State()


BOT_TOKEN = '7224050581:AAHrb6hnOAZ5OlUudb0dsmz-uin6DxtHNZU'
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=enums.ParseMode.HTML),
)

dp = Dispatcher(storage=MemoryStorage())
storage = dp.storage


@dp.message(CommandStart())
async def command_start(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if user:
        if user[1] == 'user':
            await message.answer(
                text=f"Salom, <b>{user[2]}</b> 👋",
                reply_markup=types.ReplyKeyboardRemove(),
            )
        elif user[1] == 'business':
            await message.answer(
                text=f"Salom, <b>{user[2]}</b>!\n\n"
                + html.italic("Kerakli bo'limni tanlang 👇"),
                reply_markup=types.ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    keyboard=[
                        [
                            KeyboardButton(
                                text="🚀 E'lon qo'shish",
                                callback_data="create_annoucement",
                            )
                        ]
                    ],
                ),
            )
    else:
        await message.answer(
            text="<b>Kerakli bo'limni tanlang 👇</b>",
            reply_markup=ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True,
                keyboard=[
                    [
                        KeyboardButton(text="Oddiy foydalanuvchi"),
                        KeyboardButton(text="Biznes (Kompaniya)")
                    ]
                ]
            )
        )
        await state.set_state(RegisterState.user_type)
        

@dp.message(F.text == "Oddiy foydalanuvchi", StateFilter(RegisterState.user_type))
async def user_type_handler(message: types.Message, state: FSMContext):
    await state.set_state(RegisterState.full_name)
    await state.update_data(user_type='user')
    await message.answer(
        text="<i>Ism-familyangizni kiriting!</i>",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@dp.message(F.text == "Biznes (Kompaniya)", StateFilter(RegisterState.user_type))
async def user_type_handler(message: types.Message, state: FSMContext):
    await state.set_state(RegisterState.full_name)
    await state.update_data(user_type='business')
    await message.answer(
        text="<i>Ism-familyangizni kiriting!</i>",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@dp.message(F.content_type == 'text', StateFilter(RegisterState.full_name))
async def full_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(RegisterState.phone_number)
    await message.answer(
        "<i>Telefon raqamingizni yuboring!</i>",
        reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            keyboard=[
                [
                    KeyboardButton(
                        text="📱 Telefon raqamni yuborish",
                        request_contact=True,
                    )
                ]
            ],
        ),
    )


@dp.message(F.content_type == 'contact', StateFilter(RegisterState.phone_number))
async def contact_handler(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    data = await state.get_data()
    full_name = data['full_name']
    phone_number = message.contact.phone_number
    user_type = data['user_type']

    if user_type == 'user':
        await db.create_user(
            user_id=message.from_user.id, 
            phone_number=phone_number, 
            full_name=full_name,
            user_type='user'
        )
        await message.answer(
            "<b>Siz muvaffaqiyatli ro'yhatdan o'tdingiz!</b>",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.clear()
    else:
        await state.set_state(RegisterState.company_name)
        await message.answer("<i>Kompaniya nomini kiriting</i>")


@dp.message(F.content_type == 'text', StateFilter(RegisterState.company_name))
async def company_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(company_name=message.text)

    await state.set_state(RegisterState.company_logo)
    await message.answer("<i>Kompaniya logotipini yuboring</i>")


@dp.message(F.content_type == 'photo', StateFilter(RegisterState.company_logo))
async def company_photo_handler(message: types.Message, state: FSMContext):
    await state.update_data(company_photo=message.photo[-1].file_id)
    data = await state.get_data()
    full_name = data['full_name']
    phone_number = data['phone_number']
    company_name = data['company_name']
    company_logo = data['company_photo']

    await db.create_user(
        user_id=message.from_user.id, 
        phone_number=phone_number, 
        full_name=full_name,
        company_name=company_name,
        company_photo=company_logo,
        user_type='business'
    )
    
    await message.answer("<b>Siz muvaffaqiyatli ro'yxatdan o'tdingiz!</b>")


@dp.message(F.text == '🚀 E\'lon qo\'shish')
async def create_annoucement_handler(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if user[1] == 'business':
        await state.set_state(CreateAnnouncement.title)
        await message.answer(
            text="<i>E'lon qo'shish uchun nom kiriting!</i>",
            reply_markup=types.ReplyKeyboardRemove(),
        )


@dp.message(F.content_type == 'text', StateFilter(CreateAnnouncement.title))
async def announcement_title_handler(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(CreateAnnouncement.description)
    await message.answer("<i>E'lon haqida to'liq ma'lumot yozing!</i>")


@dp.message(F.content_type == 'text', StateFilter(CreateAnnouncement.description))
async def announcement_description_handler(
    message: types.Message, state: FSMContext
):
    data = await state.get_data()
    title = data['title']
    description = message.text
    business_user = await db.get_user(message.from_user.id)
    announcement = await db.create_announcement(
        from_user_id=message.from_user.id, title=title, description=description
    )
    announcement_msg = await message.answer_photo(
        photo=business_user[-1],
        caption=f"""⚠️ <b>E'LON</b> ⚠️

<b>Kompaniya: {business_user[-2]}</b>
<b>E'lon: {title}</b>
<b>Telefon raqam: {business_user[3]}</b>

<i>E'lon haqida: {description}</i>"""
    )
    await message.answer(
        "<b>E'lon muvaffaqiyatli yaratildi!</b>",
        reply_to_message_id=announcement_msg.message_id,
    )
    await state.clear()
    users = await db.get_users_list()
    for user in users:
        await bot.send_photo(
            chat_id=user[0],
            photo=business_user[-1],
            caption=f"""⚠️ <b>E'LON</b> ⚠️

<b>Kompaniya: {business_user[-2]}</b>
<b>E'lon: {title}</b>
<b>Telefon raqam: {business_user[3]}</b>

<i>E'lon haqida: {description}</i>
            """,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✍️ Javob yozish",
                            callback_data=f'announcement_{announcement_msg.message_id}_{announcement[0]}',
                        )
                    ]
                ]
            ),
        )


@dp.callback_query(F.data.startswith('announcement_'))
async def answer_announcement_handler(
    call: types.CallbackQuery, state: FSMContext
):
    announcement_id = call.data.split("_")[-1]
    announcement_msg_id = call.data.split("_")[1]
    announcement = await db.get_announcement(announcement_id)
    await state.set_state(AnswerAnnouncement.answer)
    await state.update_data(
        announcement=announcement,
        message_id=call.message.message_id,
        business_account_message_id=announcement_msg_id,
    )
    await call.message.edit_reply_markup()
    await call.message.answer(
        f"<i>Javob yozing!</i>\n\n<i>Siz ushbu e'longa javob yozyapsiz</i>",
        reply_to_message_id=call.message.message_id,
    )


@dp.message(F.content_type == 'text', StateFilter(AnswerAnnouncement.answer))
async def answer_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data['message_id']
    announcement = data['announcement']
    business_account_message_id = data['business_account_message_id']
    user = await db.get_user(message.from_user.id)
    answer = await db.create_answer(
        user_id=message.from_user.id, announcement_id=announcement[0]
    )
    try:
        await bot.send_message(
            chat_id=announcement[1],
            text=f"""<b>E'LON JAVOBI 👇</b>

{message.text}""",
            reply_to_message_id=business_account_message_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{user[2]}",
                            url=f'https://t.me/{message.from_user.username}',
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Qabul qilish ✅",
                            callback_data=f'accept_answer_{answer[0]}',
                        )
                    ]
                ]
            )
        )
    except:
        await bot.send_message(
            chat_id=announcement[1],
            text=f"""<b>E'LON JAVOBI 👇</b>

{message.text}""",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{user[2]}",
                            url=f'https://t.me/{message.from_user.username}',
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Qabul qilish ✅",
                            callback_data=f'accept_answer_{answer[0]}',
                        )
                    ]
                ]
            )
        )
    await bot.edit_message_reply_markup(
        message_id=message_id,
        chat_id=message.chat.id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✍️ Javob yozish",
                        callback_data=f'announcement_{business_account_message_id}_{announcement[0]}',
                    )
                ]
            ]
        ),
    )
    await message.answer("<b>Javob yuborildi ✅</b>")
    await state.clear()


@dp.callback_query(F.data.startswith('accept_answer_'))
async def accept_answer_handler(call: types.CallbackQuery, state: FSMContext):
    answer_id = call.data.split("_")[-1]
    answer = await db.get_answer(answer_id)
    announcement = await db.get_announcement(answer[2])
    await bot.send_message(
        chat_id=answer[1],
        text=f"Siz qabul qildingiz ✅\n\nE'lon: <b>{announcement[3]}</b>",
    )
    reply_markup = call.message.reply_markup
    await call.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            reply_markup.inline_keyboard[0]
        ]
    ))
    await call.message.answer("<i>Xabar foydalanuvchiga yuborildi ✅</i>", reply_to_message_id=call.message.message_id)


# ------------------------------------------

async def main():
    await db.create_table()
    await dp.start_polling(bot)


asyncio.run(main())
