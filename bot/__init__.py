"""Telegram Notification Bot Package."""

from .main import TelegramBot, main
from .services.notification import send_notification, notification_service
from .services.subscription import subscription_service
from .services.monitoring import monitoring_service
from .services.scheduler import scheduler_service
from .config import config

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    'TelegramBot',
    'main',
    'send_notification',
    'notification_service',
    'subscription_service',
    'monitoring_service', 
    'scheduler_service',
    'config'
]
