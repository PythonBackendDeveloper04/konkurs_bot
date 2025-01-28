from aiogram import Bot,Dispatcher
from aiogram.client.bot import DefaultBotProperties
from config import BOT_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
from utils.database.postgresql import Database
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp=Dispatcher(storage=MemoryStorage())
db = Database()