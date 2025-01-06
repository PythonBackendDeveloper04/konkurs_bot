from aiogram.filters import BaseFilter
from aiogram import types
class IsPrivate(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        """
        Ushbu metod xabar yuborilgan chat turi "private" (shaxsiy chat) ekanligini tekshiradi.
        Agar chat turi "private" bo'lsa, True qaytaradi.
        """
        return message.chat.type in (
            'private'
        )