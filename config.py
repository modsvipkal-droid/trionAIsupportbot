from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    support_url: str
    guide_chat_id: str
    login_message_id: int
    buy_message_id: int
    play_message_id: int


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _require_int(name: str) -> int:
    value = _require_env(name)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid integer") from exc


def _normalize_url(value: str) -> str:
    value = value.strip()
    if value.startswith(("http://", "https://", "tg://")):
        return value
    return f"https://{value}"


def load_config() -> Config:
    load_dotenv(Path(__file__).with_name(".env"))

    return Config(
        bot_token=_require_env("BOT_TOKEN"),
        support_url=_normalize_url(_require_env("SUPPORT_URL")),
        guide_chat_id=_require_env("GUIDE_CHAT_ID"),
        login_message_id=_require_int("LOGIN_MESSAGE_ID"),
        buy_message_id=_require_int("BUY_MESSAGE_ID"),
        play_message_id=_require_int("PLAY_MESSAGE_ID"),
    )
