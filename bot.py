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
# KEYBOARDS & TEXT TEMPLATES (CUSTOM TG-EMOJIS)
# ==================================================

START_TEXT = (
    "━━━━━━━━━━━━━━━━━━\n"
    '<tg-emoji emoji-id="5251299553239398548">🤖</tg-emoji> <tg-emoji emoji-id="6294260862752399683">❗️</tg-emoji><tg-emoji emoji-id="6294105861677656703">❗️</tg-emoji><tg-emoji emoji-id="6293801438690680384">❗️</tg-emoji><tg-emoji emoji-id="6291782786881691498">❗️</tg-emoji><tg-emoji emoji-id="6293832444059596387">❗️</tg-emoji><tg-emoji emoji-id="6291874531678101338">❗️</tg-emoji><tg-emoji emoji-id="6294269697500127103">❗️</tg-emoji><tg-emoji emoji-id="6294060871895228563">❗️</tg-emoji> <tg-emoji emoji-id="6053062818033309122">❗️</tg-emoji>\n'
    "━━━━━━━━━━━━━━━━━━\n\n"
    '<tg-emoji emoji-id="4963072209334567688">👋</tg-emoji> Welcome to TRION AI! <tg-emoji emoji-id="6338899694810307622">🗣️</tg-emoji>\n\n'
    '<tg-emoji emoji-id="6053128350644311646">▶️</tg-emoji> Your simple guide for accessing and using TRION AI. <tg-emoji emoji-id="6338899694810307622">🗣️</tg-emoji>\n\n'
    '<tg-emoji emoji-id="6339306810465327721">🆕</tg-emoji> Choose an option below to get started.\n\n'
    '<tg-emoji emoji-id="5253761703371375423">⚡️</tg-emoji> Fast • Simple • Easy <tg-emoji emoji-id="6338899694810307622">🗣️</tg-emoji>\n'
    "━━━━━━━━━━━━━━━━━━"
)

HELP_TEXT = (
    '<tg-emoji emoji-id="5253733528385912919">🤖</tg-emoji> TRION AI GUIDE BOT <tg-emoji emoji-id="5229011542011299168">👑</tg-emoji>\n\n'
    '<tg-emoji emoji-id="6052879414339837562">☄️</tg-emoji>Use the buttons below to access: <tg-emoji emoji-id="6052991826518873591">📌</tg-emoji>\n\n'
    '<tg-emoji emoji-id="5294404854339345861">🔒</tg-emoji> Login Guide <tg-emoji emoji-id="6338899694810307622">🗣️</tg-emoji>\n'
    '<tg-emoji emoji-id="6134215550781365745">💳</tg-emoji> Purchase Guide <tg-emoji emoji-id="6338899694810307622">🗣️</tg-emoji>\n'
    '<tg-emoji emoji-id="5019285557348401713">🕹️</tg-emoji> Gameplay Guide <tg-emoji emoji-id="6338899694810307622">🗣️</tg-emoji>\n'
    '<tg-emoji emoji-id="5220108512893344933">🆘</tg-emoji> Support <tg-emoji emoji-id="6338899694810307622">🗣️</tg-emoji>'
)

SUPPORT_TEXT = (
    '<tg-emoji emoji-id="5251299553239398548">🤖</tg-emoji> TRION AI SUPPORT <tg-emoji emoji-id="5251623273514435268">🌐</tg-emoji>\n\n'
    '<tg-emoji emoji-id="6053315100117309042">⚠️</tg-emoji> Need help? <tg-emoji emoji-id="6012563681613714763">😭</tg-emoji>\n\n'
    '<tg-emoji emoji-id="6052991826518873591">📌</tg-emoji>For login, purchase or technical assistance,\n'
    'contact our support team. <tg-emoji emoji-id="6053142399482339205">🔔</tg-emoji>'
)

# ==================================================
# KEYBOARDS WITH STYLE = "success" (GREEN)
# ==================================================

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔐 How to Login", callback_data="menu_login", style="success"),
                InlineKeyboardButton(text="💳 How to Buy", callback_data="menu_buy", style="success"),
            ],
            [
                InlineKeyboardButton(text="🎮 How to Play", callback_data="menu_play", style="success"),
                InlineKeyboardButton(text="🆘 Support", callback_data="menu_support", style="success"),
            ]
        ]
    )

def get_support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨‍💻 Contact Support", url=config.SUPPORT_URL, style="success")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_menu", style="success")
            ]
        ]
    )

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_menu", style="success")
            ]
        ]
    )


# ==================================================
# DIRECT VIDEO / POST SENDER FUNCTION
# ==================================================

async def send_direct_guide(bot: Bot, chat_id: int, message_id: int):
    try:
        await bot.copy_message(
            chat_id=chat_id,
            from_chat_id=config.GUIDE_CHAT_ID,
            message_id=message_id,
            reply_markup=get_back_keyboard()
        )
    except TelegramAPIError as e:
        config.logger.info(f"copy_message failed: {e}. Attempting direct forward...")
        try:
            await bot.forward_message(
                chat_id=chat_id,
                from_chat_id=config.GUIDE_CHAT_ID,
                message_id=message_id
            )
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
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        text=HELP_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("support"))
async def cmd_support(message: Message):
    await message.answer(
        text=SUPPORT_TEXT,
        parse_mode=ParseMode.HTML,
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
            parse_mode=ParseMode.HTML,
            reply_markup=get_support_keyboard()
        )
    except TelegramAPIError:
        await callback.message.answer(
            text=SUPPORT_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=get_support_keyboard()
        )


@router.callback_query(F.data == "back_menu")
async def cb_back_menu(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.edit_text(
            text=START_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu_keyboard()
        )
    except TelegramAPIError:
        await callback.message.answer(
            text=START_TEXT,
            parse_mode=ParseMode.HTML,
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

    commands = [
        BotCommand(command="start", description="Open main menu"),
        BotCommand(command="help", description="Show simple help"),
        BotCommand(command="support", description="Open support")
    ]
    await bot.set_my_commands(commands)

    me = await bot.get_me()
    config.logger.info(f"✅ Bot connected: @{me.username}")

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
