from loader import dp
from filters import IsBotAdmin,IsPrivate
from aiogram import types,F
from aiogram.fsm.context import FSMContext
from keyboards.default.buttons import admin_menu

@dp.message(F.text=='⏺ Bekor qilish',IsBotAdmin(),IsPrivate())
async def back(message:types.Message,state:FSMContext):
    await message.answer("👨‍💻 Admin panel!", reply_markup=admin_menu())
    await state.clear()

@dp.message(F.text=='◀️ Orqaga',IsBotAdmin(),IsPrivate())
async def back(message:types.Message,state:FSMContext):
    await message.answer("👨‍💻 Admin panel!", reply_markup=admin_menu())
    await state.clear()