from loader import dp,bot,db
from aiogram import types,F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from filters import *

class ChannelInfo(CallbackData,prefix='ikb8'):
    channel_id:str

@dp.message(F.text=="📢 Kanallar",IsBotAdmin(),IsPrivate())
async def channels(message:types.Message):
    channels = await db.select_all_channels()
    btn = InlineKeyboardBuilder()
    for channel in channels:
        try:
            kanal = await bot.get_chat(chat_id=channel[2]) # Kanal ma'lumotlarini olish
            title = kanal.title #kanal nomini olish
            btn.button(text=f"{title}",callback_data=ChannelInfo(channel_id=str(channel[2])))  # Tugma qo'shish
            btn.adjust(1)
        except Exception as e:
            print(e)
    await message.answer("<b>Kanallar ro'yhati:</b>",reply_markup=btn.as_markup())

@dp.callback_query(ChannelInfo.filter(), IsBotAdmin())
async def channel_info(call:types.CallbackQuery,callback_data=ChannelInfo):
    channel_id = callback_data.channel_id # Kanal ID'sini callback ma'lumotlaridan olish
    try:
        kanal = await bot.get_chat(chat_id=channel_id) #kanal ma'lumotlarini olish
        title = kanal.title #kanal nomini olish
        members_count = await bot.get_chat_member_count(chat_id=channel_id) #obunachilar sonini olish
        await call.answer(cache_time=60)
        await call.message.answer(f"📢 Kanal nomi: <b>{title}</b>\n👥 Obunachilar soni : <b>{members_count} ta</b>")
    except Exception as e:
        print(e)