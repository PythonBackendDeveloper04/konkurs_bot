from loader import bot,dp,db
from aiogram.filters import Command
from filters import IsBotAdmin,IsPrivate
from aiogram import types,F
from keyboards.default.buttons import admin_menu,add_type
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from utils.misc.subscription_checker import check
class UserInfo(CallbackData,prefix='ikb35'):
    user_id:str

@dp.message(Command('admin'),IsBotAdmin(),IsPrivate())
async def admin(message:types.Message):
    await message.answer("👨‍💻 Admin panel!",reply_markup=admin_menu())

@dp.message(F.text=="Top 10 users",IsBotAdmin(),IsPrivate())
async def users(message:types.Message):
    top_users = await db.top_users_by_score(limit=10)
    btn = InlineKeyboardBuilder()
    for user in top_users:
        fullname = user['fullname']
        user_id = user['telegram_id']
        btn.button(text=fullname,callback_data=UserInfo(user_id=str(user_id)))
        btn.adjust(1)
    await message.answer(f"<b>Top 10 talik:</b>",reply_markup=btn.as_markup())

@dp.callback_query(UserInfo.filter())
async def user_info(call: types.CallbackQuery, callback_data: UserInfo):
    user_id = callback_data.user_id
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
        result_message = f"<b>ID:</b> {user_id}\n\n"
        if subscribed_channels:
            result_message += "<b>Obuna bo'lgan kanallar:</b>\n" + subscribed_channels + "\n"
        if unsubscribed_channels:
            result_message += "<b>Obuna bo'lmagan kanallar:</b>\n" + unsubscribed_channels

        await call.answer(cache_time=60)
        await call.message.answer(result_message)

    except Exception as e:
        print(f"Xatolik: {e}")
        await call.message.answer("Xatolik yuz berdi.")

@dp.message(F.text=="Top 10 users",IsBotAdmin(),IsPrivate())
async def search(message:types.Message):
    await message.answer()

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