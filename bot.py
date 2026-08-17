from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    ErrorEvent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import Config, load_config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

router = Router()
config: Config = load_config()


START_TEXT = """━━━━━━━━━━━━━━━━━━
🤖 TRION AI
━━━━━━━━━━━━━━━━━━

👋 Welcome to TRION AI!

Your simple guide for accessing and using TRION AI.

Choose an option below to get started.

⚡ Fast • Simple • Easy
━━━━━━━━━━━━━━━━━━"""

HELP_TEXT = """🤖 TRION AI GUIDE BOT

Use the buttons below to access:

🔐 Login Guide
💳 Purchase Guide
🎮 Gameplay Guide
🆘 Support"""

SUPPORT_TEXT = """🆘 TRION AI SUPPORT

Need help?

For login, purchase or technical assistance,
contact our support team."""


@dataclass(frozen=True)
class GuidePost:
    title: str
    message_id: int
    url_button_text: str


GUIDES = {
    "menu_login": GuidePost(
        title="Login guide",
        message_id=config.login_message_id,
        url_button_text="🎥 Open Login Guide",
    ),
    "menu_buy": GuidePost(
        title="Buy guide",
        message_id=config.buy_message_id,
        url_button_text="💳 Open Buy Guide",
    ),
    "menu_play": GuidePost(
        title="Play guide",
        message_id=config.play_message_id,
        url_button_text="🎮 Open Play Guide",
    ),
}


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔐 How to Login", callback_data="menu_login"),
                InlineKeyboardButton(text="💳 How to Buy", callback_data="menu_buy"),
            ],
            [
                InlineKeyboardButton(text="🎮 How to Play", callback_data="menu_play"),
                InlineKeyboardButton(text="🆘 Support", callback_data="menu_support"),
            ],
        ]
    )


def back_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_menu")]
        ]
    )


def support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍💻 Contact Support", url=config.support_url)],
            [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_menu")],
        ]
    )


def guide_fallback_keyboard(guide: GuidePost) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=guide.url_button_text, url=guide_post_url(guide))],
            [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_menu")],
        ]
    )


def guide_post_url(guide: GuidePost) -> str:
    chat_id = config.guide_chat_id.strip()

    if chat_id.startswith("@"):
        return f"https://t.me/{chat_id[1:]}/{guide.message_id}"

    if chat_id.startswith("https://t.me/"):
        return f"{chat_id.rstrip('/')}/{guide.message_id}"

    if chat_id.startswith("t.me/"):
        return f"https://{chat_id.rstrip('/')}/{guide.message_id}"

    if chat_id.startswith("-100") and chat_id[4:].isdigit():
        return f"https://t.me/c/{chat_id[4:]}/{guide.message_id}"

    return f"https://t.me/postkalmoda/{guide.message_id}"


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Open main menu"),
            BotCommand(command="help", description="Show simple help"),
            BotCommand(command="support", description="Open support"),
        ]
    )


async def send_main_menu(message: Message) -> None:
    await message.answer(START_TEXT, reply_markup=main_menu_keyboard())


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await send_main_menu(message)


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("support"))
async def support_command_handler(message: Message) -> None:
    await message.answer(SUPPORT_TEXT, reply_markup=support_keyboard())


@router.callback_query(F.data.in_(GUIDES.keys()))
async def guide_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()

    guide = GUIDES[callback.data]
    try:
        await callback.bot.copy_message(
            chat_id=callback.from_user.id,
            from_chat_id=config.guide_chat_id,
            message_id=guide.message_id,
            reply_markup=back_menu_keyboard(),
        )
    except TelegramAPIError as error:
        logger.warning(
            "Could not copy %s message %s from %s: %s",
            guide.title,
            guide.message_id,
            config.guide_chat_id,
            error,
        )
        await send_guide_fallback(callback, guide)


async def send_guide_fallback(callback: CallbackQuery, guide: GuidePost) -> None:
    text = f"{guide.title.title()} is available below."

    if callback.message:
        try:
            await callback.message.edit_text(
                text,
                reply_markup=guide_fallback_keyboard(guide),
            )
            return
        except TelegramAPIError as error:
            logger.warning("Could not edit guide fallback message: %s", error)

    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=guide_fallback_keyboard(guide),
    )


@router.callback_query(F.data == "menu_support")
async def support_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()

    if callback.message:
        try:
            await callback.message.edit_text(SUPPORT_TEXT, reply_markup=support_keyboard())
            return
        except TelegramAPIError as error:
            logger.warning("Could not edit support message: %s", error)

    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=SUPPORT_TEXT,
        reply_markup=support_keyboard(),
    )


@router.callback_query(F.data == "back_menu")
async def back_menu_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer()

    if callback.message:
        try:
            await callback.message.edit_text(START_TEXT, reply_markup=main_menu_keyboard())
            return
        except TelegramAPIError as error:
            logger.warning("Could not edit back menu message: %s", error)

    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=START_TEXT,
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query()
async def unknown_callback_handler(callback: CallbackQuery) -> None:
    await callback.answer("This option is no longer available.", show_alert=False)


@router.errors()
async def global_error_handler(event: ErrorEvent) -> bool:
    logger.exception("Unhandled update error", exc_info=event.exception)
    return True


async def main() -> None:
    bot = Bot(token=config.bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    await set_bot_commands(bot)
    logger.info("TRION AI Guide Bot is starting polling")

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
