from loader import bot,dp,db
from aiogram import types,F
from filters import *
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.default.buttons import admin_buttons
from aiogram.filters.callback_data import CallbackData
class CheckDeleteChannel(CallbackData,prefix='ikb4'):
    channel_id:str

@dp.message(F.text=="❌ Kanal o'chirish",IsBotAdmin(),IsPrivate())
async def delete_channel(message:types.Message,state:FSMContext):
    channels = await db.select_all_channels()
    btn = InlineKeyboardBuilder()
    for channel in channels:
        try:
            kanal = await bot.get_chat(chat_id=channel[2])
            title = kanal.title
            btn.button(text=f"{title} | ❌", callback_data=CheckDeleteChannel(channel_id=str(channel[2])))
            btn.adjust(1)
        except Exception as e:
            print(e)
    await message.answer("O'chirmoqchi bo'lgan kanaliz ustiga bosing!", reply_markup=btn.as_markup())

@dp.callback_query(CheckDeleteChannel.filter(),IsBotAdmin())
async def get(call:types.CallbackQuery,callback_data:CheckDeleteChannel,state:FSMContext):
    channel_id = callback_data.channel_id
    try:
        await db.delete_channel(channel_id=channel_id)
    except Exception as e:
        print(e)
    await call.answer("Kanal o'chirildi!",show_alert=True)
    await call.message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())
    await call.message.delete()