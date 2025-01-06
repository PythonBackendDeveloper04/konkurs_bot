from aiogram import BaseMiddleware, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Update
from loader import bot, db
from utils.misc.subscription_checker import check
from aiogram.filters.callback_data import CallbackData

class CheckSubs(CallbackData, prefix='ikb3'):
    check: bool

class CheckSubsCall(CallbackData, prefix='ikb25'):
    test: str

DEFAULT_RATE_LIMIT = 1

class UserCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data):
        if event.text:
            user_id = event.from_user.id
        elif event.callback_query:
            user_id = event.callback_query.from_user.id

        builder = InlineKeyboardBuilder()
        channels = await db.select_all_channels()
        unsubscribed_channels = []

        for CHANNEL in channels:
            status = await check(user_id=user_id, channel=CHANNEL[2])
            print(status)
            if not status:
                unsubscribed_channels.append(CHANNEL[2])
                try:
                    channel_info = await bot.get_chat(CHANNEL[2])
                    invite_link = await channel_info.export_invite_link()
                    builder.button(text=f"➕ {channel_info.title}", url=invite_link)
                except Exception as e:
                    print(e)

        text = "✅ Tasdiqlash"
        builder.button(text=text, callback_data=CheckSubs(check=True))
        builder.adjust(1)

        if unsubscribed_channels:
            await bot.send_message(chat_id=user_id,
                                   text="Iltimos bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling!",
                                   reply_markup=builder.as_markup())
        else:
            if isinstance(event, types.CallbackQuery) and event.data == CheckSubs(check=True).pack():
                await bot.send_message(chat_id=user_id, text="✅ Barcha kanallarga muvaffaqiyatli obuna bo'lgansiz!")
            return await handler(event, data)