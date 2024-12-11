from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

class ChooseLanguageCallback(CallbackData,prefix='ikb01'):
    language : str
class TextFormatCallBack(CallbackData,prefix='text_format'):
    format:str
def format_btn(format):
    btn = InlineKeyboardBuilder()
    next = "HTML" if format=='html' else "TEXT"   # Formatga qarab "HTML" yoki "TEXT" ni tanlaydi
    btn.button(text=f"Markup format: {next}" ,callback_data=TextFormatCallBack(format=format))  # Tugma qo'shadi
    return btn.as_markup()

button = InlineKeyboardBuilder()
button.button(text="🇺🇿 O'zbek tili",callback_data=ChooseLanguageCallback(language='uz'))
button.button(text="🇬🇧 English",callback_data=ChooseLanguageCallback(language='en'))
button.adjust(1)