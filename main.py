import os
import re
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiohttp import web

# ==== 1. НАСТРОЙКИ ====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен из переменных окружения
if not BOT_TOKEN:
    BOT_TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН"  # если хочешь вручную

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ==== 2. ПАМЯТЬ ДЛЯ ПРЕДУПРЕЖДЕНИЙ ====
warnings = {}

# ==== 3. СПИСОК ЗАПРЕЩЁННЫХ СЛОВ ====
BAD_WORDS = {"дурак", "идиот", "лох", "тупой", "блять", "сука", "хуй", "пидор"}

# ==== 4. КОМАНДЫ ====
@dp.message_handler(commands=["start", "help"])
async def start_cmd(message: types.Message):
    await message.reply(
        "👮 Привет! Я модератор чата.\n\n"
        "🧩 Команды:\n"
        "/warn — выдать предупреждение\n"
        "/kick — кикнуть пользователя\n"
        "/ban — забанить\n"
        "/unban — разбанить\n"
        "Я также фильтрую мат и спам."
    )


# ==== 5. ВЫДАЧА ПРЕДУПРЕЖДЕНИЙ ====
@dp.message_handler(commands=["warn"])
async def warn_user(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ Ответь на сообщение пользователя, чтобы выдать предупреждение.")
    user_id = message.reply_to_message.from_user.id
    warnings[user_id] = warnings.get(user_id, 0) + 1
    count = warnings[user_id]

    await message.reply(f"⚠️ Предупреждение {count}/3 пользователю @{message.reply_to_message.from_user.username or user_id}")

    if count >= 3:
        await message.chat.kick(user_id)
        await message.reply("🚫 Пользователь заблокирован за 3 предупреждения!")
        warnings[user_id] = 0


# ==== 6. АВТОМАТИЧЕСКИЙ ФИЛЬТР ====
@dp.message_handler(lambda m: any(bad in m.text.lower() for bad in BAD_WORDS))
async def bad_word_filter(message: types.Message):
    await message.delete()
    await message.reply(f"🧹 @{message.from_user.username or message.from_user.id}, без мата в чате!")
    user_id = message.from_user.id
    warnings[user_id] = warnings.get(user_id, 0) + 1
    if warnings[user_id] >= 3:
        await message.chat.kick(user_id)
        await message.reply(f"🚫 @{message.from_user.username or user_id} заблокирован за 3 предупреждения.")
        warnings[user_id] = 0


# ==== 7. АНТИСПАМ (удаляет слишком частые сообщения) ====
user_last_msg = {}

@dp.message_handler()
async def anti_spam(message: types.Message):
    uid = message.from_user.id
    now = message.date.timestamp()
    last = user_last_msg.get(uid, 0)
    user_last_msg[uid] = now

    if now - last < 1.5:  # меньше 1.5 сек между сообщениями
        await message.delete()
        await message.reply("🤐 Не спамь, брат!")
        return

# ==== 8. ВЕБ-СЕРВЕР ДЛЯ RENDER ====
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.add_routes([web.get("/", handle)])

# ==== 9. ЗАПУСК ====
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(executor.start_polling(dp, skip_updates=True))
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
