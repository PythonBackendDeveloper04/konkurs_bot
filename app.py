from loader import bot,dp,db
import handlers,middlewares
from utils.notify_admins import start,shutdown
from aiogram.types.bot_command_scope_all_private_chats import BotCommandScopeAllPrivateChats
from utils.set_botcommands import commands
from middlewares.subscription_middleware import UserCheckMiddleware
import logging
import sys
import asyncio
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands(commands=commands,scope=BotCommandScopeAllPrivateChats(type='all_private_chats'))
        dp.message.middleware(UserCheckMiddleware())
        dp.startup.register(start)
        dp.shutdown.register(shutdown)
        try:
            await db.connection()
            await db.users_table()
            await db.referrals_table()
            await db.channels_table()
        except Exception as e:
            print(e)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())