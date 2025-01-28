from loader import bot, dp, db
from filters import IsBotAdmin, IsPrivate
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from states.states import AddChannel
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from keyboards.reply import back_button, admin_menu
from aiogram.filters.callback_data import CallbackData


class CheckAddChannel(CallbackData, prefix="ikb4"):
    channel_id: str

@dp.message(F.text == "📢 Kanal qo'shish", IsBotAdmin(), IsPrivate())
async def add_channel(message: types.Message, state: FSMContext):
    await message.answer("Kanal ID sini yuboring!", reply_markup=back_button())
    await state.set_state(AddChannel.channel_id)

@dp.message(F.text, AddChannel.channel_id)
async def channel_id(message: types.Message, state: FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("👨‍💻 Admin panel!", reply_markup=admin_menu())
        await state.clear()
    else:
        try:
            # kanal ma'lumotlarini olish
            channel = await bot.get_chat(chat_id=message.text)
            # ID kanalning ID si ekanligini tekshirish
            if channel.type == "channel":
                # kanal nomi
                title = channel.title

                try:
                    # kanal obunachilari soni
                    subscribers = await bot.get_chat_member_count(chat_id=message.text)
                    subscribers = str(subscribers)
                except Exception as e:
                    print(e)
                    subscribers = "0"

                # holat mashinasiga ma'lumotlarni saqlash
                await state.update_data(
                    channel_id=message.text,
                    channel_name=title,
                    channel_subscribers=subscribers,
                )

                await message.answer("Kanal taklif havolasini yuboring!", reply_markup=back_button())
                await state.set_state(AddChannel.invite_link)
            else:
                await message.answer("Bu kanal emas. Kanal ID sini yuboring!", reply_markup=back_button())
        except Exception as e:
            print(e)
            await message.answer("Iltimos botni kanalga admins qiling!", reply_markup=back_button())

@dp.message(F.text, AddChannel.invite_link)
async def invite_link(message: types.Message, state: FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("👨‍💻 Admin panel!", reply_markup=admin_menu())
        await state.clear()
    else:
        try:
            # holat mashinasiga havolani saqlash
            data = await state.get_data()
            await state.update_data(invite_link=message.text)

            # tugma qo'shish
            btn = InlineKeyboardBuilder()
            btn.add(InlineKeyboardButton(text=data['channel_name'], url=message.text))
            btn.button(
                text="✅ Tasdiqlash",
                callback_data=CheckAddChannel(channel_id=data['channel_id']),
            )
            btn.adjust(1, 1)

            await message.answer("Kanalni tasdiqlaysizmi?", reply_markup=btn.as_markup())
            await state.set_state(AddChannel.check)
        except Exception as e:
            print(e)
            await message.answer("Yuborilgan havola noto'g'ri. Qaytadan yuboring!", reply_markup=back_button())


# kanalni tasdiqlash va qo'shish
@dp.callback_query(CheckAddChannel.filter(), AddChannel.check)
async def confirm_channel(call: types.CallbackQuery, callback_data: CheckAddChannel, state: FSMContext):
    await call.answer("Kanal qo'shildi!", show_alert=True)

    # holatdan ma'lumotlarni olish
    data = await state.get_data()
    channel_id = callback_data.channel_id
    channel_name = data.get("channel_name")
    channel_subscribers = data.get("channel_subscribers")
    invite_link = data.get("invite_link")

    # kanalni ma'lumotlar bazasiga qo'shish
    await db.add_channel(
        channel_id=channel_id,
        channel_name=channel_name,
        channel_members_count=channel_subscribers,
        invite_link=invite_link
    )

    # admins paneliga qaytish
    await call.message.answer("👨‍💻 Admin panel!", reply_markup=admin_menu())
    await call.message.delete()
    await state.clear()