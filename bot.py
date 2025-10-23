import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

BAD_WORDS = ["спам", "порно", "xxx", "http", "https", "мат2", "сука"]
warns = {}

async def is_admin(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in [types.ChatMemberStatus.ADMINISTRATOR, types.ChatMemberStatus.OWNER]

@dp.message_handler()
async def filter_bad_words(message: types.Message):
    text = message.text.lower() if message.text else ""
    if any(word in text for word in BAD_WORDS):
        await message.delete()
        user_id = message.from_user.id
        warns[user_id] = warns.get(user_id, 0) + 1
        count = warns[user_id]
        if count < 3:
            await message.answer(f"⚠️ {message.from_user.first_name}, предупреждение {count}/3.")
        else:
            await message.answer(f"🔇 {message.from_user.first_name} получил мут на 1 час.")
            await bot.restrict_chat_member(
                message.chat.id,
                user_id,
                permissions=types.ChatPermissions(can_send_messages=False),
                until_date=int(asyncio.get_event_loop().time()) + 3600
            )
            warns[user_id] = 0

@dp.message_handler(commands=["warn"])
async def cmd_warn(message: types.Message):
    if not await is_admin(message):
        return await message.reply("🚫 Только для админов.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, чтобы выдать предупреждение.")
    user = message.reply_to_message.from_user
    warns[user.id] = warns.get(user.id, 0) + 1
    count = warns[user.id]
    await message.reply(f"⚠️ {user.first_name} получил предупреждение {count}/3.")
    if count >= 3:
        await message.reply(f"🔇 {user.first_name} замьючен на 1 час.")
        await bot.restrict_chat_member(
            message.chat.id,
            user.id,
            permissions=types.ChatPermissions(can_send_messages=False),
            until_date=int(asyncio.get_event_loop().time()) + 3600
        )
        warns[user.id] = 0

# web-сервер часть (для Render-WebService)
async def handle(request):
    return web.Response(text="Bot is running")

app = web.Application()
app.add_routes([web.get("/", handle)])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(executor.start_polling(dp, skip_updates=True))
    web.run_app(app, host="0.0.0.0", port=10000)

    loop.create_task(executor.start_polling(dp, skip_updates=True))

    # Запускаем веб-сервер для Render
    web.run_app(app, host="0.0.0.0", port=10000)
