from loader import bot,dp,db
from aiogram import types,F,html
from aiogram.fsm.context import FSMContext
from keyboards.reply import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states.states import *
from filters import *
from utils.link_checker import check_url
from keyboards.reply import admin_menu

@dp.message(F.text=='📹 Video',IsBotAdmin(),IsPrivate())
async def get_format_text(message:types.Message,state:FSMContext):
    await message.answer(html.bold("Post videosini yuboring!"),reply_markup=back_button())
    await state.set_state(VideoAdvertising.video)

@dp.message(F.text=='◀️ Orqaga',VideoAdvertising.video,IsBotAdmin())
async def back(message:types.Message,state:FSMContext):
    await message.answer("👨‍💻 Admin panel!", reply_markup=admin_menu())
    await state.clear()

@dp.message(VideoAdvertising.video,IsBotAdmin())
async def get_text(message:types.Message,state:FSMContext):
    if message.content_type=='video':
        await message.answer_video(video=message.video.file_id,caption=message.caption)
        await state.update_data({
            'video':message.video.file_id,
            'caption':message.caption
        })
        text = "Havolani quyidagi formatda yuborish:\n" \
               "[tugma matni+havola]\n" \
               "Misol:\n" \
               "[Kanal+https://t.me/World_Facts_Channel]\n" \
               "Bir qatorga bir nechta tugmalar qo'shish uchun yangi qatorga yangi havolalarni yozing.\n" \
               "[Birinchi matn+Birinchi havola]\n" \
               "[Ikkinchi matn+Ikkinchi havola]"
        await message.answer(text,reply_markup=get_before_url())
        await state.set_state(VideoAdvertising.url)
    else:
        await message.answer(html.bold("Post videosini yuboring!"))
        await state.set_state(VideoAdvertising.video)

@dp.message(F.text=='⏺ Bekor qilish',VideoAdvertising.url,IsBotAdmin())
async def back(message:types.Message,state:FSMContext):
    await message.answer("👨‍💻 Admin panel!", reply_markup=admin_menu())
    await state.clear()

@dp.message(F.text=='⏺ Bekor qilish',VideoAdvertising.check,IsBotAdmin())
async def back(message:types.Message,state:FSMContext):
    await message.answer("👨‍💻 Admin panel!", reply_markup=admin_menu())
    await state.clear()

@dp.message(F.text=='🆗 Kerakmas',VideoAdvertising.url,IsBotAdmin())
async def back(message:types.Message,state:FSMContext):
    data = await state.get_data()
    await message.answer_video(video=data['video'], caption=data['caption'])
    await message.answer("Agar tayyor bo'lsa '📤 Yuborish' tugmasini bosing!", reply_markup=send_button())
    await state.set_state(VideoAdvertising.check)

@dp.message(VideoAdvertising.url,IsBotAdmin())
async def get_url(message:types.Message,state:FSMContext):
    if message.content_type=='text':
        urls = check_url(text=message.text)
        urls = urls if urls else None
        await state.update_data({
            'buttons':urls
        })
        data = await state.get_data()
        links = urls.splitlines()
        btn = InlineKeyboardBuilder()
        for link in links:
            manzil = link[link.rfind('+') + 1:]
            manzil = manzil.strip()
            text = link[:link.rfind('+')]
            text = text.strip()
            btn.button(text=text, url=manzil)
        btn.adjust(1)
        await message.answer_video(video=data['video'], caption=data['caption'], reply_markup=btn.as_markup())
        await message.answer("Agar tayyor bo'lsa '📤 Yuborish' tugmasini bosing!", reply_markup=send_button())
        await state.set_state(VideoAdvertising.check)
    else:
        text ="Havolani quyidagi formatda yuborish:\n"\
             "[tugma matni+havola]\n"\
              "Misol:\n"\
              "[Tarjimon+https://t.me/Behzod_Asliddinov]\n"\
             "Bir qatorga bir nechta tugmalar qo'shish uchun yangi qatorga yangi havolalarni yozing.\n"\
              "Format:\n"\
              "[Birinchi matn+birinchi havola]\n"\
              "[Ikkinchi matn+ikkinchi havola]"

        await message.answer(text, reply_markup=get_before_url())
        await state.set_state(VideoAdvertising.url)

@dp.message(F.text=='📤 Yuborish',IsBotAdmin(),VideoAdvertising.check)
async def send_add(message:types.Message,state:FSMContext):
    data = await state.get_data()
    users = await db.select_all_users()
    if data.get('buttons', None):
        links = data['buttons'].splitlines()
        btn = InlineKeyboardBuilder()
        for link in links:
            manzil = link[link.rfind('+') + 1:]
            manzil = manzil.strip()
            text = link[:link.rfind('+')]
            text = text.strip()
            btn.button(text=text, url=manzil)
        btn.adjust(1)
        counter = 0
        for user in users:
            try:
                await bot.send_video(video=data['video'], caption=data['caption'], chat_id=user[2],
                                       reply_markup=btn.as_markup(row_width=1))
                counter += 1
            except Exception as e:
                print(e)
        await message.answer(f"{counter} kishiga xabar yuborildi!", reply_markup=admin_menu())
    else:
        counter = 0
        for user in users:
            try:
                await bot.send_video(video=data['video'], caption=data['caption'], chat_id=user[2])
                counter += 1
            except Exception as e:
                print(e)
        await message.answer(f"{counter} kishiga xabar yuborildi!", reply_markup=admin_menu())
    await state.clear()