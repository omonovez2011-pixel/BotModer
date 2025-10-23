import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiohttp import web

# ==== 1. Настройки ====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен бота из переменных окружения
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# ==== 2. Команды бота ====
@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.reply("Дарова, Лее брат! 🔥 Бот работает бесплатно, создатель - yuzvenko")


@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(f"Ты сказал: {message.text}")


# ==== 3. Веб-сервер для Render ====
async def handle(request):
    return web.Response(text="Bot is running!")


app = web.Application()
app.add_routes([web.get("/", handle)])


# ==== 4. Запуск ====
if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # Запускаем бота в фоне
    loop.create_task(executor.start_polling(dp, skip_updates=True))

    # Запускаем веб-сервер для Render
    web.run_app(app, host="0.0.0.0", port=10000)
