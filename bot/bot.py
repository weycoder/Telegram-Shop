import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_IDS, WEBAPP_URL

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Клавиатура с Web App кнопкой
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Открыть магазин", web_app=WebAppInfo(url=f"{WEBAPP_URL}/webapp"))],
        [InlineKeyboardButton(text="👨‍💼 Панель админа", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))]
    ])
    return keyboard


@dp.message(Command("start"))
async def start_command(message: types.Message):
    welcome_text = """
    👋 Добро пожаловать в наш магазин!

    Нажмите кнопку ниже, чтобы открыть каталог товаров и сделать заказ.
    """
    await message.answer(welcome_text, reply_markup=get_main_keyboard())


@dp.message(Command("admin"))
async def admin_command(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Панель администратора:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Управление товарами", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))]
        ]))
    else:
        await message.answer("У вас нет прав администратора")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())