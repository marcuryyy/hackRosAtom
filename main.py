import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters.command import Command

logging.basicConfig(level=logging.INFO)
bot = Bot(token="7169830227:AAFVpoHPO3ZVSJ7eLRyI0DIaidYs7r7e-Ms")
router = Router()
dp = Dispatcher()
GREETINGS_MESSAGE = "Привет! Я могу помочь тебе определить дефектых сварных швов!"

class Processor:
    @staticmethod
    def processPhoto():
        # TODO process photo with AI
        pass

    @staticmethod
    def processVideo():
        # TODO process video with AI
        pass


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Отлично")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
    await message.answer(GREETINGS_MESSAGE, reply_markup=keyboard)

@dp.message(F.text.lower() == "отлично")
async def chooseInputType(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Фото"),
         types.KeyboardButton(text="Видео")]
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb)
    await message.answer("Выберите тип ввода данных: фото или видео?", reply_markup=keyboard)

@dp.message()
async def userInput(message: types.Message):
    if message.photo:
        print(message.photo)
    elif message.video:
        await message.answer("video")
    else:
        await message.answer("smthelse")
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
