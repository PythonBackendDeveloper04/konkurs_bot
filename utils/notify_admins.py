from data.config import ADMINS
from loader import bot
async def start():
    for i in ADMINS:
        try:
            await bot.send_message(chat_id=i,text="Bot faollashdi!")
        except:
            pass
async def shutdown():
    for i in ADMINS:
        try:
            await bot.send_message(chat_id=i,text="Bot to'xtadi!")
        except:
            pass