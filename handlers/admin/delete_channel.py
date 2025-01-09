from loader import bot,dp,db
from aiogram import types,F
from filters import *
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.default.buttons import admin_menu
from aiogram.filters.callback_data import CallbackData
class CheckDeleteChannel(CallbackData,prefix='ikb34'):
    channel_id:str

@dp.message(F.text=="❌ Kanal o'chirish",IsBotAdmin(),IsPrivate())
async def delete_channel(message:types.Message,state:FSMContext):
    channels = await db.select_all_channels()
    btn = InlineKeyboardBuilder()
    for channel in channels:
        try:
            # kanal ma'lumotlarini olish
            channel_info = await bot.get_chat(chat_id=channel[2])
            # kanal nomi
            title = channel_info.title
            # tugma qo'shish
            btn.button(text=title, callback_data=CheckDeleteChannel(channel_id=str(channel[2])))
            btn.adjust(1)
        except Exception as e:
            print(e)
    await message.answer("<b>O'chirmoqchi bo'lgan kanalingizni tanlang:</b>", reply_markup=btn.as_markup())

@dp.callback_query(CheckDeleteChannel.filter())
async def get(call:types.CallbackQuery,callback_data:CheckDeleteChannel,state:FSMContext):
    # kanal ID'sini callback ma'lumotlaridan olish
    channel_id = callback_data.channel_id
    try:
        # kanalni ma'lumotlar bazasidan o'chirish
        await db.delete_channel(channel_id=channel_id)
    except Exception as e:
        print(e)
    await call.answer("Kanal o'chirildi!",show_alert=True)
    await call.message.answer("👨‍💻 Admin panel!", reply_markup=admin_menu())
    await call.message.delete()