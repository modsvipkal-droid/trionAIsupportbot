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


# ==================================================
# DIRECT VIDEO / POST SENDER FUNCTION
# ==================================================

async def send_direct_guide(bot: Bot, chat_id: int, message_id: int):
    """
    Directly copies or forwards the exact Telegram post/video with its original caption.
    No extra promotional/fallback text.
    """
    try:
        # Direct Copy (video + original caption + back button attached)
        await bot.copy_message(
            chat_id=chat_id,
            from_chat_id=config.GUIDE_CHAT_ID,
            message_id=message_id,
            reply_markup=get_back_keyboard()
        )
    except TelegramAPIError as e:
        config.logger.info(f"copy_message attempt: {e}. Trying direct forward...")
        try:
            # Direct Forward of original post
            await bot.forward_message(
                chat_id=chat_id,
                from_chat_id=config.GUIDE_CHAT_ID,
                message_id=message_id
            )
            # Send back button below the forwarded post
            await bot.send_message(
                chat_id=chat_id,
                text="━━━━━━━━━━━━━━━━━━",
                reply_markup=get_back_keyboard()
            )
        except TelegramAPIError as err:
            config.logger.error(f"Failed to forward message {message_id}: {err}")


# ==================================================
# COMMAND HANDLERS
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
# CALLBACK QUERY HANDLERS
# ==================================================

@router.callback_query(F.data == "menu_login")
async def cb_login(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await send_direct_guide(
        bot=bot,
        chat_id=callback.message.chat.id,
        message_id=config.LOGIN_MESSAGE_ID
    )


@router.callback_query(F.data == "menu_buy")
async def cb_buy(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await send_direct_guide(
        bot=bot,
        chat_id=callback.message.chat.id,
        message_id=config.BUY_MESSAGE_ID
    )


@router.callback_query(F.data == "menu_play")
async def cb_play(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await send_direct_guide(
        bot=bot,
        chat_id=callback.message.chat.id,
        message_id=config.PLAY_MESSAGE_ID
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

    # Set Telegram commands
    commands = [
        BotCommand(command="start", description="Open main menu"),
        BotCommand(command="help", description="Show simple help"),
        BotCommand(command="support", description="Open support")
    ]
    await bot.set_my_commands(commands)

    # Bot verification
    me = await bot.get_me()
    config.logger.info(f"✅ Bot connected: @{me.username}")

    # Drop pending updates
    await bot.delete_webhook(drop_pending_updates=True)
    config.logger.info("🚀 Polling started...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        config.logger.info("TRION AI Guide Bot stopped.")
