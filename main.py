import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
import ultralytics
import os
from aiogram.types import FSInputFile

logging.basicConfig(level=logging.INFO)

API_TOKEN = "7169830227:AAFVpoHPO3ZVSJ7eLRyI0DIaidYs7r7e-Ms"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

GREETINGS_MESSAGE = "Привет! Я могу помочь тебе определить дефекты сварных швов!"


class Processor:
    @staticmethod
    async def process_photo(message: types.Message, photo: types.PhotoSize):
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, "downloaded_photo.jpg")
        results = model("downloaded_photo.jpg", save=True, conf=0.4)


processor = Processor()
model = ultralytics.YOLO("best.pt")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Отлично")]])
    await message.answer(GREETINGS_MESSAGE, reply_markup=keyboard)


@dp.message(F.text.lower() == "отлично")
async def choose_input_type(message: types.Message):
    await message.answer("Отправьте фото")


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await processor.process_photo(message, message.photo[-1])
    await message.answer_photo(photo=FSInputFile('runs/detect/predict/downloaded_photo.jpg', filename='Швы'))
    os.remove("downloaded_photo.jpg")



@dp.message()
async def handle_other(message: types.Message):
    await message.answer("Пожалуйста, отправьте фото")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
