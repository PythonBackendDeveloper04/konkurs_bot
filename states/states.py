from aiogram.filters.state import State,StatesGroup

class TextAdvertising(StatesGroup):
    text = State()
    url = State()
    check = State()
class ImageAdvertising(StatesGroup):
    image = State()
    url = State()
    check = State()
class VideoAdvertising(StatesGroup):
    video = State()
    url = State()
    check = State()

class AddChannel(StatesGroup):
    channel_id = State()
    invite_link = State()
    check = State()

class Comment(StatesGroup):
    message = State()