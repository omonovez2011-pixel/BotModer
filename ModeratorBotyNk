import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.enums import ChatMemberStatus

API_TOKEN = "8394599436:AAFbNU2AUz1epCUN76QSVd8GljaSc--Jfi4"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Список плохих слов
BAD_WORDS = ["пидр", "мат2", "сука", "спам", "порно", "xxx", "http", "https"]

# Счётчики предупреждений
warns = {}

# --- Проверка, админ ли пользователь ---
async def is_admin(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


# --- Приветствие новых участников ---
@dp.message(F.new_chat_members)
async def greet_new_member(message: types.Message):
    for member in message.new_chat_members:
        await message.reply(f"👋 Добро пожаловать, {member.full_name}!")


# --- Фильтр плохих слов и ссылок ---
@dp.message(F.text)
async def filter_bad_words(message: types.Message):
    text = message.text.lower()
    if any(word in text for word in BAD_WORDS):
        await message.delete()

        user_id = message.from_user.id
        warns[user_id] = warns.get(user_id, 0) + 1
        count = warns[user_id]

        if count < 3:
            await message.answer(f"⚠️ {message.from_user.first_name}, предупреждение {count}/3.")
        else:
            await message.answer(f"🔇 {message.from_user.first_name} получил мут за 3 предупреждения.")
            await bot.restrict_chat_member(
                message.chat.id, user_id,
                permissions=types.ChatPermissions(can_send_messages=False),
                until_date=int(asyncio.get_event_loop().time()) + 3600  # мут на 1 час
            )
            warns[user_id] = 0


# --- Команда /warn (для модеров) ---
@dp.message(Command("warn"))
async def warn_user(message: types.Message):
    if not await is_admin(message):
        return await message.reply("🚫 Только для админов.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, чтобы выдать предупреждение.")

    user = message.reply_to_message.from_user
    warns[user.id] = warns.get(user.id, 0) + 1
    count = warns[user.id]
    await message.answer(f"⚠️ {user.first_name} получил предупреждение {count}/3.")

    if count >= 3:
        await message.answer(f"🔇 {user.first_name} замьючен на 1 час.")
        await bot.restrict_chat_member(
            message.chat.id, user.id,
            permissions=types.ChatPermissions(can_send_messages=False),
            until_date=int(asyncio.get_event_loop().time()) + 3600
        )
        warns[user.id] = 0


# --- Команда /mute ---
@dp.message(Command("mute"))
async def mute_user(message: types.Message):
    if not await is_admin(message):
        return await message.reply("🚫 Только для админов.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, чтобы замьютить.")

    user = message.reply_to_message.from_user
    await bot.restrict_chat_member(
        message.chat.id, user.id,
        permissions=types.ChatPermissions(can_send_messages=False)
    )
    await message.answer(f"🔇 {user.first_name} замьючен.")


# --- Команда /unmute ---
@dp.message(Command("unmute"))
async def unmute_user(message: types.Message):
    if not await is_admin(message):
        return await message.reply("🚫 Только для админов.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, чтобы размьютить.")

    user = message.reply_to_message.from_user
    await bot.restrict_chat_member(
        message.chat.id, user.id,
        permissions=types.ChatPermissions(can_send_messages=True)
    )
    await message.answer(f"✅ {user.first_name} размьючен.")


# --- Команда /ban ---
@dp.message(Command("ban"))
async def ban_user(message: types.Message):
    if not await is_admin(message):
        return await message.reply("🚫 Только для админов.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, чтобы забанить.")

    user = message.reply_to_message.from_user
    await bot.ban_chat_member(message.chat.id, user.id)
    await message.answer(f"⛔ {user.first_name} забанен.")


# --- Команда /unban ---
@dp.message(Command("unban"))
async def unban_user(message: types.Message):
    if not await is_admin(message):
        return await message.reply("🚫 Только для админов.")
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Укажи ID пользователя: `/unban 123456789`")

    user_id = int(args[1])
    await bot.unban_chat_member(message.chat.id, user_id)
    await message.answer(f"✅ Пользователь {user_id} разбанен.")


# --- Запуск ---
async def main():
    print("🤖 Бот запущен и следит за порядком...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
