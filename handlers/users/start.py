from loader import bot, dp, db
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram import types, F
from keyboards.reply import main_menu, back_button,send_phone_number
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from utils.subscription_checker import check
from aiogram.fsm.context import FSMContext
from states.states import Comment,Registration
from config import ADMINS

class CheckSubsciptionCallbackData(CallbackData, prefix='ikb3'):
    check: bool

# Referal havola yasovchi funksiya
def generate_referal_link(user_id):
    return f"https://t.me/ZudlikYangilikKonkursBot?start={user_id}"


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    args = message.text.split(' ')[1:]
    try:
        channels = await db.select_all_channels()
        channel_buttons = InlineKeyboardBuilder()
        all_channels_subscribed = True

        for channel in channels:
            is_subscripbed = True
            try:
                # obuna holatini tekshirish
                is_subscripbed = await check(user_id=message.from_user.id,
                                     channel=channel[2])
            except Exception as e:
                print(e)
                is_subscripbed = False
            all_channels_subscribed *= is_subscripbed
            try:
                channel_info = await bot.get_chat(channel[2])
                invite_link = await db.invite_link(channel_info.id)
                print(f"invite_link:{invite_link}")
                if not is_subscripbed:
                    channel_buttons.row(InlineKeyboardButton(text=f"➕ {channel_info.title}", url=invite_link))
            except Exception as e:
                print(e)

        channel_buttons.button(text="✅ Tasdiqlash", callback_data=CheckSubsciptionCallbackData(check=True))
        channel_buttons.adjust(1)

        if not all_channels_subscribed:
            # obuna bo'lmaganlar uchun holatni saqlash
            await state.update_data(pending_event=message)
            await message.answer(
                text="Iltimos bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling:",
                reply_markup=channel_buttons.as_markup(row_width=1),
            )
        else:
            user = await db.select_user(message.from_user.id)
            if user:
                await message.answer("Menyudan bo'lim tanlang:", reply_markup=main_menu())
            else:
                await db.add_user(fullname=message.from_user.first_name,telegram_id=message.from_user.id,phone=None,username=message.from_user.username)
                await message.answer("Telefon raqamingizni yuboring:", reply_markup=send_phone_number())
                await state.set_state(Registration.phone_number)

                referrer_user_id = None
                if args:
                    referrer_user_id = args[0]
                    print(f"Referal user ID: {referrer_user_id}")

                # foydalanuvchi o'zini referal qilib ololmasligi tekshiriladi
                if referrer_user_id == str(message.from_user.id):
                    print("Foydalanuvchi o'zini referal qilib ololmaydi.")
                    return

                # foydalanuvchi allaqachon referal bo'lsa, uni tekshirish
                if referrer_user_id:
                    try:
                        # foydalanuvchi allaqachon referal bo'lganligini tekshirish
                        if not await db.is_referred_by(referrer_user_id, message.from_user.id):
                            # foydalanuvchi boshqa birovning referali emasligini tekshirish
                            referred_exists = await db.is_referred_by_anyone(message.from_user.id)
                            if not referred_exists:
                                # referalga ball qo'shish
                                await db.add_score(referrer_user_id, 10)
                                # referal jadvaliga qo'shish
                                await db.mark_as_referred(referrer_user_id, message.from_user.id)
                                # referal egasiga xabar yuborish
                                await bot.send_message(
                                    chat_id=referrer_user_id,
                                    text=f"🎉 Yangi referal! Do'stingiz <b>{message.from_user.full_name}</b> sizning referal havolangiz orqali ro'yxatdan o'tdi va sizga 10 ball taqdim etildi!"
                                )
                            else:
                                print("Foydalanuvchi boshqa referal sifatida allaqachon ro'yxatdan o'tgan.")
                    except Exception as e:
                        print(f"Referal tizimida xato: {e}")
                else:
                    # agar argument bo'lmasa, referal bo'lishni rad etamiz
                    print("Foydalanuvchi o'zini referal qilib ololmaydi.")
    except Exception as e:
        print(f"Xato: {e}")


@dp.callback_query(CheckSubsciptionCallbackData.filter())
async def check_subscription(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)

    # Davlatdan oldindan saqlangan eventni olish
    state_data = await state.get_data()
    pending_subscription_check = state_data.get("pending_event")

    if pending_subscription_check:
        # Obunani tasdiqlash muvaffaqiyatli bo'lsa
        await state.clear()  # Holatni tozalash
        await call.message.delete()

        # Pending event bo'yicha jarayonni davom ettirish
        if isinstance(pending_subscription_check, types.Message):
            print("Pending event qayta ishlanmoqda...")
            await start(pending_subscription_check, state)  # Asosiy jarayonni qayta chaqirish
    else:
        await call.message.edit_text("Siz barcha kanallarga obuna bo'lgansiz!")  # Tasdiqlovchi javob


@dp.message(F.contact,Registration.phone_number)
async def request_phone_number(message:types.Message,state:FSMContext):
    try:
        if message.contact.user_id == message.from_user.id:
            print(message.contact.user_id)
            print(message.from_user.id)
            phone = message.contact.phone_number
            # Foydalanuvchini ma'lumotlar bazasiga qo'shish
            await db.update_user(phone=phone,telegram_id=message.from_user.id)
            await message.answer("<b>Quyidagi menyudan kerakli bo'limni tanlang:</b>", reply_markup=main_menu())
            await state.clear()
        else:
            await message.answer("Iltimos o'zingizni raqamingizni yuboring!")

    except Exception as e:
        print(f"Xato: {e}")





@dp.message(F.text=="🎁 Konkursda qatnashish")
async def send_contest_invitation(message:types.Message):
    text = """
<b>Zudlik Yangilik telegram kanali konkursi</b>

<i>G'oliblar har hafta yakshanba kuni telegram va intagram kanallarimizda jonli efirda aniqlanadi!
G'oliblikni qo'lga kiritish uchun ko'proq do'stlaringizni taklif qiling va ko'proq imkoniyatlarga ega bo'ling</i>

{}
    """.format(generate_referal_link(message.from_user.id))
    first_message = await message.answer(text=text)
    second_message = """⬆️ Yuqorida sizning linkingiz qo'shilgan taklifnoma!

Uni do'stlaringizga, jo'nating hamda g'oliblikni qo'lga kiriting! Omad🔥"""
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
    await message.answer(f"<b>📊 Sizning ma'lumotlaringiz:</b>\n\n<b>Sizning ID:</b> <code>{message.from_user.id}</code>\n<b>Siz to'plagan ball:</b> {score}\n<b>Siz taklif qilgan do'stlar:</b> {invited_friends_count}")

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
        await message.answer("Menyudan bo'lim tanlang:",reply_markup=main_menu())
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