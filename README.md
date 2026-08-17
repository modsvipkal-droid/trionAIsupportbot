# TRION AI Guide Bot

Simple Telegram guide/support bot for TRION AI.

## Features

- `/start` main menu
- `/help` simple help menu
- `/support` support contact menu
- Login, buy, and play guide buttons
- Telegram post copy with URL fallback
- No database, admin panel, payments, referrals, analytics, or web server

## Setup

```bash
cd /storage/emulated/0/trionAIsupportbot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The `.env` file contains the bot configuration:

```env
BOT_TOKEN=your_bot_token
SUPPORT_URL=https://t.me/kal_mods
GUIDE_CHAT_ID=@postkalmoda
LOGIN_MESSAGE_ID=11
BUY_MESSAGE_ID=13
PLAY_MESSAGE_ID=14
```

## Run

```bash
python bot.py
```

## Telegram Guide Posts

The bot tries to copy these official guide posts:

- Login guide: `https://t.me/postkalmoda/11`
- Buy guide: `https://t.me/postkalmoda/13`
- Play guide: `https://t.me/postkalmoda/14`

If Telegram blocks copying because of channel permissions, the bot shows a fallback button that opens the guide post directly.
