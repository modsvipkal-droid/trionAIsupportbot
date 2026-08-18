import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand
)
from aiogram.exceptions import TelegramAPIError

import config

router = Router()

# ==================================================
# KEYBOARDS & TEXT TEMPLATES
# ==================================================

START_TEXT = (
    "━━━━━━━━━━━━━━━━━━\n"
    "🤖 <b>TRION AI</b>\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    "👋 Welcome to <b>TRION AI</b>!\n\n"
    "Your simple guide for accessing and using TRION AI.\n\n"
    "Choose an option below to get started.\n\n"
    "⚡ Fast • Simple • Easy\n"
    "━━━━━━━━━━━━━━━━━━"
)

HELP_TEXT = (
    "🤖 <b>TRION AI GUIDE BOT</b>\n\n"
    "Use the buttons below to access:\n\n"
    "🔐 Login Guide\n"
    "💳 Purchase Guide\n"
    "🎮 Gameplay Guide\n"
    "🆘 Support"
)

SUPPORT_TEXT = (
    "🆘 <b>TRION AI SUPPORT</b>\n\n"
    "Need help?\n\n"
    "For login, purchase or technical assistance,\n"
    "contact our support team."
)

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔐 How to Login", callback_data="menu_login"),
                InlineKeyboardButton(text="💳 How to Buy", callback_data="menu_buy"),
            ],
            [
                InlineKeyboardButton(text="🎮 How to Play", callback_data="menu_play"),
                InlineKeyboardButton(text="🆘 Support", callback_data="menu_support"),
            ]
        ]
    )

def get_support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨‍💻 Contact Support", url=config.SUPPORT_URL)
            ],
            [
                InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_menu")
            ]
        ]
    )

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_menu")
            ]
        ]
    )

def get_fallback_guide_keyboard(button_text: str, message_id: int) -> InlineKeyboardMarkup:
    direct_post_url = f"https://t.me/{config.CLEAN_CHANNEL_NAME}/{message_id}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=button_text, url=direct_post_url)
            ],
            [
                InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_menu")
            ]
        ]
    )


# ==================================================
# HELPER FUNCTIONS
# ==================================================

async def send_or_fallback_guide(
    bot: Bot,
    chat_id: int,
    message_id: int,
    fallback_button_text: str,
    guide_name: str
):
    try:
        await bot.copy_message(
            chat_id=chat_id,
            from_chat_id=config.GUIDE_CHAT_ID,
            message_id=message_id,
            reply_markup=get_back_keyboard()
        )
    except TelegramAPIError as e:
        config.logger.warning(f"Copy failed for post {message_id}: {e}. Sending fallback.")
        await bot.send_message(
            chat_id=chat_id,
            text=f"📖 <b>TRION AI: {guide_name}</b>\n\nClick the button below to view the official guide:",
            reply_markup=get_fallback_guide_keyboard(fallback_button_text, message_id)
        )


# ==================================================
# COMMAND HANDLERS (Using Official aiogram 3.x Filters)
# ==================================================

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        text=START_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        text=HELP_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("support"))
async def cmd_support(message: Message):
    await message.answer(
        text=SUPPORT_TEXT,
        reply_markup=get_support_keyboard()
    )


# ==================================================
# CALLBACK HANDLERS
# ==================================================

@router.callback_query(F.data == "menu_login")
async def cb_login(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await send_or_fallback_guide(
        bot=bot,
        chat_id=callback.message.chat.id,
        message_id=config.LOGIN_MESSAGE_ID,
        fallback_button_text="🎥 Open Login Guide",
        guide_name="How to Login"
    )


@router.callback_query(F.data == "menu_buy")
async def cb_buy(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await send_or_fallback_guide(
        bot=bot,
        chat_id=callback.message.chat.id,
        message_id=config.BUY_MESSAGE_ID,
        fallback_button_text="💳 Open Buy Guide",
        guide_name="How to Buy"
    )


@router.callback_query(F.data == "menu_play")
async def cb_play(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await send_or_fallback_guide(
        bot=bot,
        chat_id=callback.message.chat.id,
        message_id=config.PLAY_MESSAGE_ID,
        fallback_button_text="🎮 Open Play Guide",
        guide_name="How to Play"
    )


@router.callback_query(F.data == "menu_support")
async def cb_support(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.edit_text(
            text=SUPPORT_TEXT,
            reply_markup=get_support_keyboard()
        )
    except TelegramAPIError:
        await callback.message.answer(
            text=SUPPORT_TEXT,
            reply_markup=get_support_keyboard()
        )


@router.callback_query(F.data == "back_menu")
async def cb_back_menu(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.edit_text(
            text=START_TEXT,
            reply_markup=get_main_menu_keyboard()
        )
    except TelegramAPIError:
        await callback.message.answer(
            text=START_TEXT,
            reply_markup=get_main_menu_keyboard()
        )


# ==================================================
# BOT STARTUP
# ==================================================

async def main():
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    dp.include_router(router)

    # Set commands
    commands = [
        BotCommand(command="start", description="Open main menu"),
        BotCommand(command="help", description="Show simple help"),
        BotCommand(command="support", description="Open support")
    ]
    await bot.set_my_commands(commands)

    # Verify bot token & connection
    me = await bot.get_me()
    config.logger.info(f"✅ Bot successfully connected as: @{me.username} (ID: {me.id})")

    # Drop old pending updates to start fresh
    await bot.delete_webhook(drop_pending_updates=True)
    config.logger.info("🚀 Polling started... Send /start to your bot in Telegram!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        config.logger.info("TRION AI Guide Bot stopped.")
