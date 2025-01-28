from aiogram.filters import Filter
from aiogram import types
from config import ADMINS
class IsBotAdmin(Filter):
    async def __call__(self, message: types.Message) -> bool:
        """
        Ushbu metod xabar yuborgan foydalanuvchining IDsi adminlar ro'yxatida bor yoki yo'qligini tekshiradi
        Agar foydalanuvchi IDsi ADMINS ro'yxatida bo'lsa, True qaytaradi.
        """
        return str(message.from_user.id) in ADMINS