from loader import bot,dp,db
from aiogram.filters import CommandStart,Command
from aiogram.filters.callback_data import CallbackData
from aiogram import types,F
from keyboards.default.buttons import main_menu,back_button
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardButton
from utils.misc.subscription_checker import check
from aiogram.fsm.context import FSMContext
from states.states import Comment
from data.config import ADMINS

class CheckSubs(CallbackData,prefix='ikb3'):
    check:bool

#referal havola yasovchi funksiya
def get_referal_link(user_id):
    return f"https://t.me/KonkursChampBot?start={user_id}"

@dp.message(CommandStart())
async def start(message:types.Message):
    try:
        # foydalanuvchini ma'lumotlar bazasiga qo'shish
        await db.add_user(fullname=message.from_user.full_name, telegram_id=message.from_user.id)
    except Exception as e:
        print(f"Xato: {e}")

    # start bilan kelgan argumentni olish
    args = message.text.split(' ')[1:]
    ref_user_id = None
    if args:
        ref_user_id = args[0]
        print(f"Referal user ID: {ref_user_id}")

    # foydalanuvchi o'zini referal qilib ololmasligi tekshiriladi
    if ref_user_id == str(message.from_user.id):
        print("Foydalanuvchi o'zini referal qilib ololmaydi.")
        return

    # foydalanuvchi avval botdan foydalanmaganligini tekshirish
    if not ref_user_id:
        user_start_time = await db.get_user_start_time(message.from_user.id)
        if user_start_time is None:
            await message.answer(
                "Siz faqat botning o'zidan start bosgan bo'lsangiz, referal orqali start bossa ball qo'shilmaydi.")
            return

    # foydalanuvchi allaqachon referal bo'lsa, uni tekshirish
    if ref_user_id:
        try:
            # foydalanuvchi allaqachon referal bo'lganligini tekshirish
            if not await db.is_referred_by(ref_user_id, message.from_user.id):
                # foydalanuvchi boshqa birovning referali emasligini tekshirish
                referred_exists = await db.is_referred_by_anyone(message.from_user.id)
                if not referred_exists:
                    # referalga ball qo'shish
                    await db.add_score(ref_user_id, 10)
                    # referal jadvaliga qo'shish
                    await db.mark_as_referred(ref_user_id, message.from_user.id)
                    # referal egasiga xabar yuborish
                    await bot.send_message(
                        chat_id=ref_user_id,
                        text=f"🎉 Yangi referal! Do'stingiz <b>{message.from_user.full_name}</b> sizning referal havolangiz orqali ro'yxatdan o'tdi va sizga 10 ball taqdim etildi!"
                    )
                else:
                    print("Foydalanuvchi boshqa referal sifatida allaqachon ro'yxatdan o'tgan.")
        except Exception as e:
            print(f"Referal tizimida xato: {e}")
    else:
        # agar argument bo'lmasa, referal bo'lishni rad etamiz
        print("Foydalanuvchi o'zini referal qilib ololmaydi.")

    # kanal obuna tekshiruvi uchun tugmalar
    btn = InlineKeyboardBuilder()
    channels = await db.select_all_channels()
    final_status = True
    for channel in channels:
        try:
            status = await check(user_id=message.from_user.id, channel=channel[2])
        except Exception as e:
            print(e)
            status = False
            if not status:
                final_status *= status
                try:
                    channel_info = await bot.get_chat(channel[2])
                    invite_link = await channel_info.export_invite_link()
                    btn.row(InlineKeyboardButton(text=f"➕ {channel_info.title}", url=invite_link))
                except Exception as e:
                    print(e)

    # tasdiqlash tugmasini qo'shish
    btn.button(text="✅ Tasdiqlash", callback_data=CheckSubs(check=True))
    btn.adjust(1)
    if final_status:
        await message.answer("<b>Quyidagi menyudan kerakli bo'limni tanlang:</b>", reply_markup=main_menu())
    else:
        await message.answer(text="Iltimos bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling:",
                             reply_markup=btn.as_markup(row_width=1))

# tasdiqlash tugmasini qayta ishlash
@dp.callback_query(CheckSubs.filter())
async def test(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    user_id = call.from_user.id
    channels = await db.select_all_channels()
    buttons = []
    all_subscribed = True
    for channel in channels:
        try:
            chat = await bot.get_chat(channel[2])
            res = await bot.get_chat_member(chat_id=channel[2], user_id=user_id)
            if res.status not in ['member', 'administrator', 'creator']:
                buttons.append(InlineKeyboardButton(text=f"➕ {chat.title}", url=await chat.export_invite_link()))
                all_subscribed = False
        except Exception as e:
            print(e)

    # kanal tugmalarini joylash
    builder = InlineKeyboardBuilder()
    builder.add(*buttons)
    builder.button(text="✅ Tasdiqlash", callback_data=CheckSubs(check=True))
    builder.adjust(1)

    if not all_subscribed:
        await bot.send_message(
            chat_id=user_id,
            text="Iltimos bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=builder.as_markup()
        )

    try:
        await call.message.delete()
    except Exception as e:
        print(e)

@dp.message(F.text=="Konkursda qatnashish 🔴")
async def participate_in_contest(message:types.Message):
    text = """
            <b>Yilning so'ngi eng katta konkursi ⚡️</b>

1. Apple iPhone 14 Pro (128 GB)
2. Noutbuk (Dell/HP)
3. Noutbuk (Lenovo/Asus)
4. Samsung Galaxy A14 5G
5. Xiaomi Redmi 12C
6. Xiaomi Mi Band 8
7. Televizor pristavkasi
8. LED stol lampasi
9. PowerBank
10. Elektr choynak
🎁 G'oliblar 4-dekabr 23:59da aniqlanadi.
<b>Hammaga Omad!</b>

{}
    """.format(get_referal_link(message.from_user.id))
    first_message = await message.answer(text=text)
    second_message = """⬆️ Yuqorida sizning linkingiz qo'shilgan taklifnoma!

Uni do'stlaringizga, yaqinlaringizga va barcha guruhlarga jo'nating hamda o'z sovg'angizni qo'lga kiriting! Omad🔥"""
    await message.answer(second_message, reply_to_message_id=first_message.message_id)

@dp.message(F.text=="🎁 Sovg'alar")
async def show_gifts(message:types.Message):
    text = """
    <b>Yilning so'ngi eng katta konkursi ⚡️</b>

1. Apple iPhone 14 Pro (128 GB)
2. Noutbuk (Dell/HP)
3. Noutbuk (Lenovo/Asus)
4. Samsung Galaxy A14 5G
5. Xiaomi Redmi 12C
6. Xiaomi Mi Band 8
7. Televizor pristavkasi
8. LED stol lampasi
9. PowerBank
10. Elektr choynak
🎁 G'oliblar 4-dekabr 23:59da aniqlanadi.
<b>Hammaga Omad!</b>
    """
    await message.answer(text=text)

@dp.message(F.text=="👤 Profil")
async def show_profile(message:types.Message):
    score = await db.get_score(message.from_user.id)
    invited_friends_count = await db.friends_count(message.from_user.id)
    await message.answer(f"<b>📊 Sizning ma'lumotlaringiz:</b>\n\n<b>Sizning ID:</b> {message.from_user.id}\n<b>Siz to'plagan ball:</b> {score}\n<b>Siz taklif qilgan do'stlar:</b> {invited_friends_count}")

@dp.message(F.text=="📊 Reyting")
async def show_leaderboard(message: types.Message):
    top_users = await db.top_users_by_score(limit=10)
    data = ""
    index = 1
    for user in top_users:
        data += f"<b>{index}.</b> {user['fullname']} - {user['score']}\n"
        index += 1
    await message.answer(f"<b>Top 10 talik:</b>\n\n{data}")

@dp.message(F.text == "📞 Admin")
async def contact_admin(message: types.Message,state:FSMContext):
    await message.answer("✉️ Agar sizda ushbu bot bo'yicha savollar yoki qo'shimcha ma'lumot olish istagi bo'lsa, murojaat qiling!\n\n<i>Bizga savol yo'llang, biz sizning savollaringiz va qiziqishlaringizga tezkor javob berishga tayyormiz! 🎯</i>",reply_markup=back_button())
    await state.set_state(Comment.message)

@dp.message(F.text,Comment.message)
async def send_message_to_admin(message: types.Message,state:FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("Home",reply_markup=main_menu())
        await state.clear()
    else:
        first_name = message.from_user.first_name
        username = message.from_user.username
        text = f"<b>{first_name}:</b>\n\n{message.text}"
        for admin in ADMINS:
            profile = InlineKeyboardBuilder()
            profile.button(text="Profilga o'tish",url=f"https://t.me/{username}")
            profile.adjust(1)
            await bot.send_message(chat_id=admin,text=text,reply_markup=profile.as_markup())
        await state.set_state()
        await message.answer("✅ Adminlarga jo'natildi!",reply_markup=main_menu())