from loader import dp,db
from aiogram.filters import Command
from filters import IsBotAdmin,IsPrivate
from aiogram import types,F
from keyboards.default.buttons import *

@dp.message(Command('admin'),IsBotAdmin(),IsPrivate())
async def admin(message:types.Message):
    await message.answer("👨‍💻 Admin panel!",reply_markup=admin_buttons())

@dp.message(F.text=='🗣 Reklama yuborish',IsBotAdmin(),IsPrivate())
async def get_add_type(message:types.Message):
    await message.answer("Qanday turdagi xabar yuborasiz?",reply_markup=add_type())

@dp.message(F.text=="📊 Obunachilar soni",IsBotAdmin(),IsPrivate())
async def get_member_count(message:types.Message):
    try:
        count = await db.count_users()
    except Exception as e:
        count = 0
    await message.answer(f"Hozirda botda {count} ta faol obunachi bor!")

@dp.message(F.text=="🔙 Orqaga")
async def admin(message:types.Message):
    await message.answer("👨‍💻 Admin panel!",reply_markup=admin_buttons())