"""Telegram Notifier Package - Easy Telegram notifications for Python applications."""

from .notification import TelegramNotifier, send_notification, send_notification_sync
from .config import NotifierConfig

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Easy Telegram notifications for Python applications"

__all__ = [
    "TelegramNotifier", 
    "send_notification", 
    "send_notification_sync",
    "NotifierConfig"
]
