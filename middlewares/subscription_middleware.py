from aiogram import BaseMiddleware, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery
from typing import Any
from loader import bot, db
from utils.misc.subscription_checker import check
from aiogram.filters.callback_data import CallbackData

class CheckSubs(CallbackData, prefix="ikb3"):
    check: bool

DEFAULT_RATE_LIMIT = 0.1

class UserCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Any, data: dict):
        user_id = None
        state = data.get("state")  # FSM holatini olish

        # Event turi bo‘yicha tekshirish
        if isinstance(event, Message) and event.text:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        else:
            return await handler(event, data)  # Event noma’lum bo‘lsa, keyingisini uzatadi

        # Obunani tekshirishni boshlash
        builder = InlineKeyboardBuilder()
        channels = await db.select_all_channels()
        unsubscribed_channels = []

        for CHANNEL in channels:
            status = await check(user_id=user_id, channel=CHANNEL[2])
            if not status:
                unsubscribed_channels.append(CHANNEL[2])
                try:
                    channel_info = await bot.get_chat(CHANNEL[2])
                    invite_link = await channel_info.export_invite_link()
                    builder.button(text=f"➕ {channel_info.title}", url=invite_link)
                except Exception as e:
                    print(f"Error fetching channel info: {e}")

        # Tasdiqlash tugmasi
        builder.button(text="✅ Tasdiqlash", callback_data=CheckSubs(check=True))
        builder.adjust(1)

        if unsubscribed_channels:
            # Foydalanuvchi barcha kanallarga obuna bo‘lmagan bo‘lsa
            await bot.send_message(
                chat_id=user_id,
                text="Iltimos, bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling!",
                reply_markup=builder.as_markup(),
            )

            # Holatni saqlash (pending_event)
            if state:
                await state.update_data(pending_event=event)  # Saqlangan eventni saqlaymiz
            print(f"Pending event saqlandi: {event}")
            return  # Foydalanuvchi obuna bo‘lmagan bo‘lsa, jarayonni to'xtatish

        # Agar foydalanuvchi barcha kanallarga obuna bo‘lsa, avtomatik ravishda jarayonni bajarish
        if isinstance(event, CallbackQuery):
            print(f"Received CallbackQuery with data: {event.data}")
            if event.data == "ikb3:check:True":
                print("is working")
                if state:
                    state_data = await state.get_data()
                    pending_event = state_data.get("pending_event")
                    if pending_event:
                        print(f"Pending event: {pending_event}")
                        await state.update_data(pending_event=None)  # Saqlangan eventni o'chirish
                        return await handler(pending_event, data)  # Saqlangan jarayonni bajarish

        # Agar barcha tekshirishlar muvaffaqiyatli bo‘lsa, asosiy handlerni chaqiramiz
        return await handler(event, data)
