import asyncio
import logging
import shutil

import aiogram
import cv2
from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from typing import Any, Awaitable, Callable, Dict, List, Union
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
import ultralytics
import os
from aiogram.types import FSInputFile
from aiogram.types import (
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    TelegramObject,
)
from cv2 import Mat

logging.basicConfig(level=logging.INFO)

API_TOKEN = "7169830227:AAFVpoHPO3ZVSJ7eLRyI0DIaidYs7r7e-Ms"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

DEFAULT_DELAY = 0.6

INPUT_MEDIA_MAP = {
    "photo": InputMediaPhoto,
    "video": InputMediaVideo,
    "document": InputMediaDocument,
    "audio": InputMediaAudio,
}

GREETINGS_MESSAGE = "Привет! Я могу помочь тебе определить дефекты сварных швов!"

defect_book: dict[str, str] = {"adj": "Прилегающие дефекты(adj): брызги, прожоги от дуги.",
                               "int": "Дефекты целостности(int): кратер, шлак, свищ, пора, прожог, включения.",
                               "geo": "Дефекты геометрии(geo): подрез, непровар, наплыв, чешуйчатость, западание, неравномерность.",
                               "pro": "Дефекты постобработки(pro): заусенец, торец, задир, забоина.",
                               "non": "Дефекты невыполнения(non): незаполнение раковины, несплавление."}


class MediaGroupMiddleware(BaseMiddleware):
    ALBUM_DATA: dict[str, list[Message]] = {}

    def __init__(self, delay: Union[int, float] = DEFAULT_DELAY):
        self.delay = delay

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        try:
            self.ALBUM_DATA[event.media_group_id].append(event)
            return  # Don't propagate the event
        except KeyError:
            self.ALBUM_DATA[event.media_group_id] = [event]
            await asyncio.sleep(self.delay)
            data["album"] = self.ALBUM_DATA.pop(event.media_group_id)

        return await handler(event, data)


class Processor:
    @staticmethod
    async def process_photo(message: types.Message, photo: types.PhotoSize):
        result_message: str = "На данной фотографии были замечены следующие дефекты: "
        unique_defects: set[str] = set()
        file_id: str = photo.file_id
        file: aiogram.types.File = await bot.get_file(file_id)
        file_path: str = file.file_path
        await bot.download_file(file_path, f"downloaded_photo.jpg")
        results: list = model(f"downloaded_photo.jpg")
        img: Mat = cv2.imread(f"downloaded_photo.jpg")
        for result in results:
            if not result.boxes:
                result_message = "Дефектов не обнаружено! :)"
            else:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()

                    class_id: str = box.cls[0].item()
                    class_name: str = model.names[int(class_id)]
                    unique_defects.add(class_name)

                    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                    cv2.putText(img, class_name, (int(x1), int(y1)), cv2.FONT_HERSHEY_PLAIN,
                                3, (0, 255, 0), 3)

        cv2.imwrite("processed_photo.jpg", img)
        os.remove("downloaded_photo.jpg")

        for defect in unique_defects:
            result_message += f"\n\n{defect_book[defect]}"

        return result_message


processor = Processor()
model = ultralytics.YOLO("best.pt")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Отлично")]])
    await message.answer(GREETINGS_MESSAGE, reply_markup=keyboard)


@dp.message(F.text.lower() == "отлично")
async def choose_input_type(message: types.Message):
    await message.answer("Отправьте фото")


@dp.message(F.media_group_id)
async def handle_albums(message: Message, album: List[Message]):
    """This handler will receive a complete album of any type."""
    for element in album:
        res_msg = await processor.process_photo(element, element.photo[-1])
        await message.answer_photo(photo=FSInputFile('processed_photo.jpg'), caption=res_msg)


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    res_msg = await processor.process_photo(message, message.photo[-1])
    await message.answer_photo(photo=FSInputFile('processed_photo.jpg', filename='Швы'), caption=res_msg)


@dp.message()
async def handle_other(message: types.Message):
    await message.answer("Пожалуйста, отправьте фото")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    dp.message.middleware(MediaGroupMiddleware())
    asyncio.run(main())
