from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile
from loader import bot,dp,db
from aiogram.filters import Command
from filters import IsBotAdmin,IsPrivate
from aiogram import types,F
from keyboards.default.buttons import admin_menu,add_type
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from utils.misc.subscription_checker import check
from states.states import SearchUser
class UserInfo(CallbackData,prefix='ikb35'):
    user_id:str

@dp.message(Command('admin'),IsBotAdmin(),IsPrivate())
async def admin(message:types.Message):
    await message.answer("👨‍💻 Admin panel!",reply_markup=admin_menu())


@dp.message(Command('get_excel'),IsBotAdmin(),IsPrivate())
async def export_users_to_excel(message: types.Message):
    table_name = "Users"
    file_name = f"{table_name}.xlsx"

    # Ma'lumotlarni eksport qilish
    await db.export_to_excel(table_name, file_name)

    # Faylni foydalanuvchiga yuborish
    try:
        document = open(file_name,'rb')
        file = types.input_file.BufferedInputFile(file=document.read(),filename=file_name)
        # Faylni to'g'ri yo'l bilan yuklaymiz
        await message.answer_document(file, caption=f"{table_name} jadvali ma'lumotlari.")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")
@dp.message(Command('get_logs'),IsBotAdmin(),IsPrivate())
async def log(message: types.Message):
    document = open('bot_logs.log','rb')
    file = types.input_file.BufferedInputFile(file=document.read(),filename="bot_logs.log")
    await message.answer_document(document=file)

# @dp.message(F.text=="Top 10 users",IsBotAdmin(),IsPrivate())
# async def users(message:types.Message):
#     top_users = await db.top_users_by_score(limit=10)
#     btn = InlineKeyboardBuilder()
#     for user in top_users:
#         fullname = user['fullname']
#         user_id = user['telegram_id']
#         btn.button(text=fullname,callback_data=UserInfo(user_id=str(user_id)))
#         btn.adjust(1)
#     await message.answer(f"<b>Top 10 talik:</b>",reply_markup=btn.as_markup())

# @dp.message(UserInfo.filter())
# async def user_info(call: types.CallbackQuery, callback_data: UserInfo):
#     user_id = callback_data.user_id
#     channels = await db.select_all_channels()  # Barcha kanallarni bazadan olish
#     final_status = True
#     subscribed_channels = ""  # Obuna bo'lgan kanallar ro'yxati
#     unsubscribed_channels = ""  # Obuna bo'lmagan kanallar ro'yxati
#
#     try:
#         for channel in channels:
#             channel_id = channel[2]
#             channel_info = await bot.get_chat(channel_id)
#             title = channel_info.title
#
#             # Foydalanuvchi obuna holatini tekshirish
#             status = await check(user_id=user_id, channel=channel_id)
#             if status:
#                 subscribed_channels += f"✅ {title}\n"  # Obuna bo'lganlar
#             else:
#                 final_status = False
#                 unsubscribed_channels += f"❌ {title}\n"  # Obuna bo'lmaganlar
#
#         # Foydalanuvchiga natijani yuborish
#         result_message = f"<b>ID:</b> {user_id}\n\n"
#         if subscribed_channels:
#             result_message += "<b>Obuna bo'lgan kanallar:</b>\n" + subscribed_channels + "\n"
#         if unsubscribed_channels:
#             result_message += "<b>Obuna bo'lmagan kanallar:</b>\n" + unsubscribed_channels
#
#         await call.answer(cache_time=60)
#         await call.message.answer(result_message)
#
#     except Exception as e:
#         print(f"Xatolik: {e}")
#         await call.message.answer("Xatolik yuz berdi.")

@dp.message(F.text=="🆔 ID orqali qidirish")
async def user_info(message:types.Message,state:FSMContext):
    await message.answer("Foydalanuvchi ID sini kiriting:")
    await state.set_state(SearchUser.id)

@dp.message(F.text,SearchUser.id)
async def search(message:types.Message,state:FSMContext):
    user_id = message.text
    user = await db.select_user(user_id)

    time = user[7]  # Ro‘yxatdan o‘tgan vaqti

    # Ro'yhatdan o'tgan vaqtni formatlash
    time = datetime.strftime(time, "%Y-%m-%d %H:%M")

    channels = await db.select_all_channels()  # Barcha kanallarni bazadan olish
    final_status = True
    subscribed_channels = ""  # Obuna bo'lgan kanallar ro'yxati
    unsubscribed_channels = ""  # Obuna bo'lmagan kanallar ro'yxati

    try:
        for channel in channels:
            channel_id = channel[2]
            channel_info = await bot.get_chat(channel_id)
            title = channel_info.title

            # Foydalanuvchi obuna holatini tekshirish
            status = await check(user_id=user_id, channel=channel_id)
            if status:
                subscribed_channels += f"✅ {title}\n"  # Obuna bo'lganlar
            else:
                final_status = False
                unsubscribed_channels += f"❌ {title}\n"  # Obuna bo'lmaganlar

        # Foydalanuvchiga natijani yuborish
        result_message = f"<b>ID:</b> {user_id}\n<b>Ismi: </b>{user[1]}\n<b>Telefon: </b>+{user[3]}\n<b>Username: </b>@{user[4]}\n<b>Ro'yhatgan o'tgan vaqti: </b>{time}"
        if subscribed_channels:
            result_message += "<b>Obuna bo'lgan kanallar:</b>\n" + subscribed_channels + "\n"
        if unsubscribed_channels:
            result_message += "<b>Obuna bo'lmagan kanallar:</b>\n" + unsubscribed_channels

        await message.answer(result_message)
        await state.clear()
    except Exception as e:
        print(f"Xatolik: {e}")
        await message.answer("Xatolik yuz berdi.")
        await state.clear()

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

@dp.message(F.text=="◀️ Orqaga")
async def admin(message:types.Message):
    await message.answer("👨‍💻 Admin panel!",reply_markup=admin_menu())

@dp.message(F.text=="🔙 Orqaga")
async def admin(message:types.Message):
    await message.answer("👨‍💻 Admin panel!",reply_markup=admin_menu())