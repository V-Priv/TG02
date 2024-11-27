import os
import random
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from googletrans import Translator
from gtts import gTTS
import config

# Убедитесь, что папка 'img' существует
if not os.path.exists('img'):
    os.makedirs('img')

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

translator = Translator()


@dp.message(Command('translate'))
async def send_welcome(message: Message):
    await message.reply("Привет! Отправьте мне текст, и я переведу его на английский язык.")


@dp.message(lambda message: message.photo)
async def handle_photos(message: Message):
    photo = message.photo[-1]  # Берем фото в наибольшем разрешении
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path
    file_name = f"img/{photo.file_id}.jpg"

    # Скачиваем файл
    await bot.download_file(file_path, file_name)
    await message.reply("Фото сохранено!")


@dp.message(lambda message: message.text and not message.text.startswith('/'))
async def translate_message(message: Message):
    try:
        translated = translator.translate(message.text, dest='en')
        await message.reply(translated.text)
    except Exception as e:
        await message.reply(f"Ошибка при переводе: {e}")


@dp.message(Command('voice'))
async def send_voice_message(message: Message):
    try:
        # Извлекаем текст после команды '/voice'
        text = message.text.split(maxsplit=1)
        if len(text) > 1:
            text = text[1]
        else:
            text = "Привет, это голосовое сообщение!"

        tts = gTTS(text=text, lang='ru')
        file_path = f"voice_{random.randint(1, 1000)}.mp3"
        tts.save(file_path)

        voice = FSInputFile(file_path)
        await message.reply_voice(voice)

        os.remove(file_path)  # Удаляем временный файл
    except Exception as e:
        await message.reply(f"Ошибка при отправке голосового сообщения: {e}")

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Приветики, {message.from_user.full_name}!")

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды: \n/start \n/help \n/translate \n/voice")


async def main():
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())