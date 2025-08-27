"""
Modern Telegram notification bot library for Python projects.

This library provides a simple and efficient way to send notifications
through Telegram bots with proper error handling and type safety.
"""

__version__ = "0.1.0"

from .bot import TelegramNotificationBot
from .exceptions import (
    TelegramNotificationError,
    ChatNotFoundError,
    BotBlockedError,
    RateLimitError,
    InvalidChatIdError,
)
from .models import NotificationConfig, MessageData, PhotoData, DocumentData

__all__ = [
    "TelegramNotificationBot",
    "TelegramNotificationError",
    "ChatNotFoundError",
    "BotBlockedError",
    "RateLimitError",
    "InvalidChatIdError",
    "NotificationConfig",
    "MessageData",
    "PhotoData",
    "DocumentData",
]
