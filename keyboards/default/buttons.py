from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton

def admin_menu():
    btn = ReplyKeyboardBuilder()
    btn.button(text="🗣 Reklama yuborish")
    btn.button(text="📊 Obunachilar soni")
    btn.button(text="📢 Kanal qo'shish")
    btn.button(text="❌ Kanal o'chirish")
    btn.button(text="📢 Kanallar")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True,input_placeholder="Kerakli bo'limni tanlang...",
                         one_time_keyboard=True)
def add_type():
    btn = ReplyKeyboardBuilder()
    btn.button(text="✏️ Matn")
    btn.button(text="📸 Rasm")
    btn.button(text="📹 Video")
    btn.button(text="🔙 Orqaga")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)

def back_button():
    btn = ReplyKeyboardBuilder()
    btn.button(text="◀️ Orqaga")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)

def get_before_url():
    btn = ReplyKeyboardBuilder()
    btn.button(text="⏺ Bekor qilish")
    btn.button(text="🆗 Kerakmas")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)

def send_button():
    btn = ReplyKeyboardBuilder()
    btn.button(text="⏺ Bekor qilish")
    btn.button(text="📤 Yuborish")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)

def main_menu():
    btn = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Konkursda qatnashish 🔴")],  # 1 ta tugma alohida qatorda
            [KeyboardButton(text="🎁 Sovg'alar"), KeyboardButton(text="👤 Profil")],  # 2 ta tugma bitta qatorda
            [KeyboardButton(text="📊 Reyting"), KeyboardButton(text="📞 Admin")]  # 2 ta tugma bitta qatorda
        ],
        resize_keyboard=True
    )
    return btn